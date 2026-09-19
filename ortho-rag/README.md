# Ortho-RAG: buscador de casos similares para recuperacion ortopedica

Prototipo para el hackathon: indexa casos (sinteticos) de traumatologia en una
base de datos vectorial y permite consultar "pacientes similares a este" con
filtros clinicos + similitud semantica, devolviendo los protocolos de
recuperacion historicos.

> **Los datos son 100% sinteticos** (generados aleatoriamente), no son
> pacientes reales. Sirven para prototipar el pipeline completo (indexacion +
> busqueda + agente) antes de conectar datos reales del hospital bajo
> anonimizacion/seudonimizacion y cumplimiento HIPAA/RGPD.

## Estructura

```
ortho-rag/
├── data/
│   └── patients.json          # 300 casos sinteticos
├── db/
│   ├── chroma/                # base de datos vectorial (ChromaDB, persistente)
│   └── tfidf_vectorizer.pkl   # vectorizador usado para embeddings + consultas
├── scripts/
│   ├── generate_synthetic_data.py   # genera el dataset sintetico
│   ├── build_vector_db.py           # indexa el dataset en ChromaDB
│   └── query_similar_cases.py       # busca casos similares (CLI + funcion importable)
└── README.md
```

## Como funciona (mapeado al planteamiento del hackathon)

1. **Datos de entrada** → `generate_synthetic_data.py` simula, por caso:
   demografia (edad, sexo, altura, peso, IMC), nivel de actividad,
   comorbilidades, tipo/zona/gravedad de fractura, mecanismo de lesion,
   "hallazgos de imagen" (texto simulando el informe radiologico),
   tratamiento aplicado (conservador/quirurgico), plan de recuperacion,
   duracion por fases, hitos y resultado clinico.

2. **Motor de similitud** → `build_vector_db.py`:
   - Convierte cada caso en un **documento de texto** (diagnostico +
     hallazgos + plan de recuperacion) y lo vectoriza (embedding TF-IDF
     local, offline — ver nota de embeddings mas abajo).
   - Guarda ademas toda la info estructurada como **metadata** (edad, IMC,
     tipo de fractura, gravedad, tratamiento, semanas de recuperacion...)
     para poder aplicar **filtros estrictos**.
   - Todo se persiste en ChromaDB (`db/chroma/`), la base de datos vectorial.

3. **Interfaz de consulta** → `query_similar_cases.py`:
   - Recibe atributos estructurados del paciente nuevo (edad, sexo, tipo de
     fractura, IMC, nivel de actividad) + texto libre opcional.
   - Aplica filtros exactos (mismo tipo de fractura, rango de edad ±15 anhos
     por defecto) y luego busca los k=5–10 vecinos mas cercanos por
     similitud semantica dentro de ese subconjunto.
   - Devuelve cada caso con su protocolo de recuperacion, duracion,
     complicaciones y resultado — listo para que un chatbot/agente lo cite
     como fuente (`case_id`).

## Uso rapido

```bash
cd scripts

# 1. (Re)generar el dataset sintetico
python3 generate_synthetic_data.py --n 300 --seed 42 --out ../data/patients.json

# 2. Indexar en la base de datos vectorial
python3 build_vector_db.py --in ../data/patients.json --db ../db/chroma

# 3. Consultar casos similares
python3 query_similar_cases.py \
    --edad 72 --sexo Hombre --fractura "Fractura de cuello femoral" \
    --imc 27.5 --nivel-actividad "moderadamente activo" --k 5
```

Tipos de fractura disponibles en el dataset (usar el nombre exacto en
`--fractura`): revisa `data/patients.json` o ejecuta:

```bash
python3 -c "import json; d=json.load(open('../data/patients.json')); print(sorted(set(p['fractura_tipo'] for p in d)))"
```

### Usarlo como "tool" desde un agente/chatbot

```python
from query_similar_cases import find_similar_cases

casos = find_similar_cases(
    edad=70, sexo="Hombre", fractura="Fractura de humero (diafisaria)",
    imc=28, nivel_actividad="deportista federado", k=8,
)
# casos es una lista de dicts, lista para pasarsela como contexto al LLM
# del chatbot (con case_id como cita/fuente).
```

Esto es exactamente el "Agente: framework de chatbot con RAG" del brief: el
LLM del agente extrae los atributos estructurados de la pregunta en lenguaje
natural del profesional sanitario, llama a `find_similar_cases(...)` como
tool, y redacta la respuesta citando los `case_id` devueltos.

## Nota sobre los embeddings

El entorno de generacion de este proyecto no tenia salida de red hacia
HuggingFace (donde Chroma descarga su modelo de embeddings por defecto,
`all-MiniLM-L6-v2`). Por eso se usa un **vectorizador TF-IDF local
(scikit-learn)**, entrenado sobre el propio corpus de casos — cero
dependencias externas, 100% offline y reproducible, ideal para un
hackathon.

**Para mejorar la calidad semantica** (recomendado si teneis GPU/tiempo):
sustituir el TF-IDF por un modelo de embeddings real, por ejemplo:

```bash
pip install sentence-transformers
```
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")  # o un modelo clinico (ej. PubMedBERT)
vectors = model.encode(documents).tolist()
```
y pasar esos `vectors` a `collection.add(embeddings=...)` en
`build_vector_db.py`. El resto del pipeline (Chroma, filtros de metadata,
logica de consulta) no cambia.

Si quereis ademas usar las **radiografias** (no solo texto), habria que
anhadir un embedding de imagen (ej. un modelo tipo CLIP o uno especifico de
radiologia) y concatenarlo/combinarlo con el embedding de texto, o hacer
busqueda multi-vector.

## Riesgos y limites (recordar en la demo)

- Datos sinteticos: la calidad de "similitud" es artificial; con datos
  reales del hospital, la calidad depende directamente de que los
  historiales esten completos y bien estructurados.
- Cumplimiento normativo: con datos reales, se necesita
  consentimiento, anonimizacion/seudonimizacion y control de accesos
  (HIPAA/RGPD) antes de indexar nada.
- Es una **herramienta de apoyo a la decision**, no debe usarse para
  prescribir tratamientos de forma autonoma sin supervision clinica.
