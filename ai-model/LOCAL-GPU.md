# Локальный запуск с GPU (RTX 5060 8GB и аналоги)

Профиль для **Ryzen 5 8400F (6 ядер / 12 потоков), 32 GB RAM, RTX 5060 8 GB** и модели **Vikhr 8B Q4_K_M**.

## Почему такие числа

| Параметр | Значение | Причина |
|----------|----------|---------|
| `N_GPU_LAYERS=-1` | все слои на GPU | Q4 8B ~5 GB VRAM + KV при `N_CTX=2048` обычно влезает в 8 GB |
| `N_CTX=2048` | контекст | баланс скорость/VRAM; `4096` на 8 GB часто OOM |
| `N_THREADS=6` | CPU | 6 физических ядер 8400F |
| `N_THREADS_BATCH=12` | CPU batch | длинный prompt (RAG) — задействовать SMT |
| `USE_MLOCK=0` | RAM | 32 GB достаточно, mlock не нужен |
| `CUDA_WHEEL_TAG=cu124` | сборка | если ошибка CUDA на RTX 50xx → `cu125` |

Ожидаемое время ответа: **секунды–десятки секунд**, не минуты как на CPU-VPS.

---

## 1. Хост: драйвер и Docker GPU

**Windows:** WSL2 + [Docker Desktop](https://docs.docker.com/desktop/features/gpu/) + актуальный NVIDIA driver (Game Ready / Studio, 570+ для RTX 50xx).

**Linux:** драйвер + [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

Проверка:

```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

---

## 2. Модель GGUF

Скачайте `vikhr-llama3.1-8b-instruct-r-21-09-24-q4_k_m.gguf` в папку, например:

- Windows: `D:\AI\models\vikhr\`
- Linux: `/home/you/models/vikhr/`

---

## 3. AI-model

```bash
cd ai-model
cp .env.local-gpu.example .env
# отредактируйте MODEL_HOST_PATH

docker compose -f docker-compose.yml -f docker-compose.local-gpu.yml up -d --build
```

Проверка GPU внутри контейнера:

```bash
docker logs startflow-ai-model 2>&1 | grep "llama.cpp init"
docker exec startflow-ai-model python3 -c "
from llama_cpp.llama_cpp import load_shared_library
import pathlib, llama_cpp
p = pathlib.Path(llama_cpp.__file__).parent
lib = load_shared_library('llama', p / 'lib')
print('gpu_offload', bool(lib.llama_supports_gpu_offload()))
"
```

Тест (как на VPS):

```bash
curl -sS -X POST http://127.0.0.1:8077/ai/generate \
  -H "Content-Type: application/json" \
  -d @/path/to/ai-test.json
```

Во время запроса: `docker stats startflow-ai-model` — должен расти **GPU %** (в `nvidia-smi`), CPU умеренный.

---

## 4. Backend + frontend (все контейнеры)

**Backend** (`backend/`):

```bash
cp .env.example .env   # DB_PASS, JWT_SECRET_KEY
docker compose up -d --build
```

**Frontend** (`frontend/`):

```bash
# порты по умолчанию: API 8078, AI 8077, UI 8080
docker compose up -d --build
```

Открыть: http://localhost:8080

> Страница аналитики в коде может ещё бить в `localhost:8001` — для UI см. задачу на правку `frontend/src/lib/ai.js` (URL `/ai/generate` и `PUBLIC_AI_URL`).

---

## 5. CUDA OOM (8 GB)

В `.env` переключите на fallback:

```env
N_GPU_LAYERS=28
N_CTX=2048
N_BATCH=256
```

Перезапуск:

```bash
docker compose -f docker-compose.yml -f docker-compose.local-gpu.yml up -d
```

---

## 6. VPS vs локальная машина

| | VPS (без GPU) | Локально (5060) |
|--|---------------|-----------------|
| Compose | `docker-compose.cpu.yml` | `docker-compose.local-gpu.yml` |
| Env | `.env` с `N_GPU_LAYERS=0` | `.env` из `.env.local-gpu.example` |
| Образ | `Dockerfile.openblas` | `Dockerfile.cuda` |

Не смешивайте профили на одной машине.
