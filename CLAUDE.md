# recovery-ia — guía para Claude Code

Sistema RAG de apoyo a la decisión clínica en ortopedia: dado un paciente nuevo (informe médico, analítica y opcionalmente radiografía), recupera casos históricos similares de una base de datos vectorial y genera con un LLM un informe de tratamiento, tiempo de recuperación, dieta y hábitos recomendados. Ver [README.md](README.md) y [ai/docs/architecture.md](ai/docs/architecture.md) (diagrama + flujo detallado) antes de tocar el pipeline de RAG.

## Dónde vive el código (importante)

El repo tiene carpetas sueltas en la raíz (`src/`, `tests/`, `backend/`, `.venv/`, `.pytest_cache/`) que **no son el servicio activo**:

- **`ai/`** es el backend real: FastAPI + RAG, construido por `docker-compose.yml` y documentado en el README. Todo el código Python a modificar está en `ai/src/recovery_ia/`, `ai/scripts/`, `ai/tests/`.
- **`backend/`** (`app.py`) es un stub de proxy httpx sin usar por el `docker-compose.yml` actual (que construye `./ai` directamente). No lo edites salvo que el usuario pida explícitamente trabajar en ese proxy.
- **`src/recover_ia/`** y **`tests/`** en la raíz son restos de una reorganización previa (solo contienen `__pycache__`, sin `.py` propios ni tracking en git). Ignóralos; el código vive en `ai/src/recovery_ia/`.
- **`frontend/`** es la UI (React + Vite), servida en `:8080` y habla directamente con `ai` en `:8000` (ver `frontend/src/lib/api.js`).

Antes de "arreglar" algo que parece duplicado, comprueba con `git ls-files` si esa ruta está trackeada — si no lo está, probablemente es un artefacto local, no código del proyecto.

## Estructura de `ai/src/recovery_ia/`

- `api/main.py` — app FastAPI, monta routers y sirve `/images` (radiografías indexadas) como estáticos.
- `api/routes/` — `auth.py` (login único admin/admin vía `.env`, JWT-like token), `query.py` (`/cases/similar`, `/cases/report`, `/cases/reports`), `patients.py` (`/patients`, dataset histórico para tabla en frontend), `sms.py` (`/sms/appointment`, recordatorios Vonage), `transcription.py` (`/transcription`, dictado por voz vía SLNG/Deepgram).
- `api/security.py` — emisión/verificación del token de sesión; todas las rutas salvo `/auth` y `/health` requieren `Depends(require_auth)`.
- `agent/` — `extraction.py` (LLM: informe + analítica → factores estructurados), `chat_agent.py` (LLM: casos similares → informe final), `llm.py` (cliente Nebius/Claude).
- `retrieval/` — `similarity_search.py` (búsqueda semántica + filtros estructurados), `weights.py` (re-ranking ponderado por factores clínicos).
- `vectorstore/` — cliente Qdrant.
- `embeddings/` — `text_embedder.py` (activo); `image_embedder.py` **pendiente** (las radiografías/PDFs subidos se guardan en `data/uploads/` pero su contenido aún no alimenta la búsqueda, solo el texto).
- `storage/mongo.py` — persistencia en MongoDB de los informes generados (colección `reports`) y del dataset histórico de pacientes sintéticos (colección `patients`).
- `sms/` — recordatorios de citas por SMS (Vonage) con `apscheduler`.
- `transcription/` — cliente SLNG para transcribir audio a texto.
- `schemas/` — modelos Pydantic; **toda entrada/salida de la API pasa por aquí** (`patient_case.py`, `query.py`, `report.py`, `report_record.py`, `sms.py`, `transcription.py`). Al añadir un campo nuevo, actualízalo aquí primero.
- `config/settings.py` — `pydantic_settings.BaseSettings`, lee `ai/.env`. Añadir variables de configuración nuevas aquí, no hardcodear.

## Comandos

```bash
make up              # docker compose up -d --build (qdrant + mongo + backend=ai)
make watch           # como up, pero con hot-reload sincronizando ai/src y ai/scripts
make dev-backend     # uv run uvicorn recovery_ia.api.main:app --reload (sin Docker)
make dev-frontend    # npm --prefix frontend run dev (puerto 8080)
make sync            # uv sync --extra dev (entorno Python, gestionado con uv)
make ingest          # uv run scripts/ingest_vector_db.py (indexa casos históricos en Qdrant)
make test            # uv run pytest
make lint            # uv run ruff check . && npm --prefix frontend run lint (oxlint)
```

Estos comandos de `uv`/`pytest`/`ruff` se ejecutan con `ai/` como raíz (`pyproject.toml` está en `ai/`, no en la raíz del repo). El frontend usa `npm` dentro de `frontend/`.

## Convenciones de código

**Python (`ai/`)**
- Type hints en firmas de función; modelos de datos como Pydantic (`BaseModel`)/`BaseSettings`, no dicts sueltos.
- Docstrings y comentarios en español, breves, solo cuando aclaran un porqué no evidente (varios módulos ya siguen este estilo).
- Nombres de variables/campos de dominio clínico en español (`edad`, `imc`, `fractura_tipo`, `deportista`, `gravedad`) porque así están en el dataset y en los schemas — mantén la coherencia, no los traduzcas a mitad de camino.
- Routers FastAPI: un router por dominio en `api/routes/`, `prefix` + `tags`, registrado en `api/main.py`. Rutas nuevas que no sean públicas van con `dependencies=[Depends(require_auth)]`.
- No inventar valores clínicos que no estén en el texto de entrada (regla de negocio explícita en `agent/extraction.py`); si añades lógica de extracción, respeta esa restricción.

**Frontend (`frontend/`)**
- Componentes funcionales de React con hooks (`useState`/`useEffect`), sin clases.
- Textos de UI vía `useTranslation()` de `src/i18n/I18nContext.jsx` — no hardcodear strings visibles, añadirlos a `src/i18n/translations.js` en todos los idiomas existentes.
- Llamadas a la API centralizadas en `src/lib/api.js` (incluye manejo de token y evento `UNAUTHORIZED_EVENT`); no hagas `fetch` sueltos en componentes.
- Iconos con `lucide-react`; estilos en `App.css`/`Landing.css` (no CSS-in-JS) más `theme/ThemeContext.jsx` para modo claro/oscuro.
- Lint con `oxlint` (`frontend/.oxlintrc.json`), no ESLint.

## API del backend (`ai`, puerto 8000)

- `POST /auth/login` — único endpoint sin auth junto a `/health`; credenciales en `ADMIN_USERNAME`/`ADMIN_PASSWORD`.
- `POST /cases/similar` — casos similares sin pasar por el LLM.
- `POST /cases/report` (multipart: `medical_report_text`, `lab_results_text?`, `xray?`, `additional_files?`, `top_k`) — pipeline completo (extracción → retrieval → LLM), archiva el resultado en MongoDB.
- `GET /cases/reports`, `GET /cases/reports/{id}` — histórico de informes.
- `GET /patients` — dataset histórico sintético para la tabla del frontend.
- `POST /sms/appointment` — programa SMS de confirmación + recordatorios (Vonage).
- `POST /transcription` — transcribe audio dictado a texto (SLNG/Deepgram).

## Variables de entorno (`ai/.env`, ver `ai/.env.example`)

Qdrant (`QDRANT_URL`, `QDRANT_COLLECTION`), MongoDB (`MONGODB_URI`, `MONGODB_DB`, colecciones de reports/patients), Nebius AI Studio para LLM y embeddings (`NEBIUS_API_KEY`, `LLM_MODEL`, `TEXT_EMBEDDING_MODEL`), Vonage SMS (`VONAGE_API_KEY`, `VONAGE_API_SECRET`, `VONAGE_SMS_FROM`), SLNG Speech-to-Text (`SLNG_API_KEY`, `SLNG_REGION`), y auth (`ADMIN_USERNAME`, `ADMIN_PASSWORD`, `AUTH_SECRET_KEY`, `AUTH_TOKEN_TTL_HOURS`). Nunca commitear `.env` real ni claves.

## Datos y cumplimiento

Todo el dataset histórico (`data/raw/patients.json`) es **sintético/inventado**; solo las radiografías pueden venir del dataset público de Kaggle (sin datos de paciente real asociados). Antes de conectar historiales reales, se requiere revisión de cumplimiento RGPD/datos de salud — no asumas que se puede indexar un dataset real sin ese paso, y no elimines los avisos de "no sustituye el criterio clínico" del informe generado.
