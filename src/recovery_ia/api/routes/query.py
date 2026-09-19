from pathlib import Path

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pymongo import DESCENDING

from recovery_ia.agent import generate_report_from_patient_input
from recovery_ia.retrieval import find_similar_cases
from recovery_ia.schemas import (
    ClinicalReport,
    NewPatientInput,
    ReportRecord,
    SimilarCaseQuery,
    SimilarCaseResult,
    case_ref_from,
)
from recovery_ia.storage import get_reports_collection

router = APIRouter(prefix="/cases", tags=["cases"])

UPLOADS_DIR = Path("data/uploads")


def _save_upload(upload: UploadFile, content: bytes) -> str:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    path = UPLOADS_DIR / upload.filename
    path.write_bytes(content)
    return str(path)


def _save_report_record(patient_input: NewPatientInput, report: ClinicalReport, similar: list[SimilarCaseResult]) -> str:
    record = ReportRecord(
        patient_input=patient_input,
        similar_cases=[case_ref_from(r.case, r.similarity_score) for r in similar],
        report=report,
    )
    result = get_reports_collection().insert_one(record.model_dump(exclude={"id"}))
    return str(result.inserted_id)


@router.post("/similar", response_model=list[SimilarCaseResult])
def similar_cases(query: SimilarCaseQuery) -> list[SimilarCaseResult]:
    """Solo recuperacion: devuelve los casos similares sin pasar por el LLM."""
    return find_similar_cases(query)


@router.post("/report", response_model=ClinicalReport)
async def report(
    medical_report_text: str = Form(..., description="Informe medico del paciente en texto libre"),
    lab_results_text: str | None = Form(
        default=None, description="Analisis clinicos/analitica en texto libre (opcional)"
    ),
    xray: UploadFile | None = File(default=None, description="Radiografia del paciente (opcional)"),
    additional_files: list[UploadFile] = File(
        default=[], description="Otros archivos de diagnostico: informes de laboratorio, otras pruebas de imagen..."
    ),
    top_k: int = Form(default=5),
) -> ClinicalReport:
    """Pipeline completo: informe medico + analitica (opcional) + archivos de
    diagnostico (radiografia u otros) de un paciente nuevo -> extraccion de
    factores -> casos similares en Qdrant -> informe clinico con tratamiento,
    tiempo de recuperacion, dieta y habitos de salud.

    Los archivos se guardan y se referencian en el informe, pero solo el texto
    (medical_report_text / lab_results_text) alimenta hoy la busqueda: el
    embedding de imagen todavia esta pendiente (ver embeddings/image_embedder.py).

    El resultado de salida (informe + casos similares usados) se archiva en
    MongoDB (ver recovery_ia.storage) para dejar constancia de cada consulta."""
    xray_image_path = None
    if xray is not None:
        xray_image_path = _save_upload(xray, await xray.read())

    additional_file_paths = [_save_upload(f, await f.read()) for f in additional_files]

    patient_input = NewPatientInput(
        medical_report_text=medical_report_text,
        lab_results_text=lab_results_text,
        xray_image_path=xray_image_path,
        additional_file_paths=additional_file_paths,
        top_k=top_k,
    )
    clinical_report, similar = generate_report_from_patient_input(patient_input)
    _save_report_record(patient_input, clinical_report, similar)
    return clinical_report


@router.get("/reports", response_model=list[ReportRecord])
def list_reports(limit: int = 20) -> list[ReportRecord]:
    """Historico de resultados de salida guardados en MongoDB, mas recientes primero."""
    docs = get_reports_collection().find().sort("created_at", DESCENDING).limit(limit)
    return [ReportRecord(**{**doc, "id": str(doc["_id"])}) for doc in docs]


@router.get("/reports/{report_id}", response_model=ReportRecord)
def get_report(report_id: str) -> ReportRecord:
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        doc = get_reports_collection().find_one({"_id": ObjectId(report_id)})
    except InvalidId:
        raise HTTPException(status_code=422, detail="report_id invalido")

    if doc is None:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    return ReportRecord(**{**doc, "id": str(doc["_id"])})
