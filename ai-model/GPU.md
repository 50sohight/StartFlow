# GPU для startflow-ai-model

**Локальная машина (RTX 5060 8GB и т.п.):** см. [LOCAL-GPU.md](./LOCAL-GPU.md) и `.env.local-gpu.example` + `docker-compose.local-gpu.yml`.

## Почему сейчас медленно

1. `N_GPU_LAYERS=0` — llama.cpp не выгружает слои на GPU.
2. Образ на `python:3.11-slim` ставит **CPU-only** `llama-cpp-python` (без `GGML_CUDA`).

Даже при `N_GPU_LAYERS=-1` на CPU-сборке ускорения не будет.

## Диагностика на VPS

```bash
cd ~/StartFlow/ai-model
bash scripts/check-gpu-server.sh
```

Интерпретация:

| Результат | Действие |
|-----------|----------|
| `nvidia-smi` работает, `llama_supports_gpu_offload: True` | Достаточно поднять с GPU compose и `N_GPU_LAYERS=-1` |
| GPU есть, `nvidia-smi` нет | Установить драйвер NVIDIA на хост |
| `nvidia-smi` есть, `docker --gpus` падает | Установить [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) |
| GPU есть, offload `False` | Пересобрать образ: `Dockerfile.cuda` |

## Деплой только ai-model (остальные контейнеры не трогаем)

```bash
cd ~/StartFlow/ai-model
# .env с MODEL_HOST_PATH как сейчас

sudo docker compose -f docker-compose.yml -f docker-compose.gpu.yml build --no-cache
sudo docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d

sudo docker logs -f startflow-ai-model
```

Проверка после старта:

```bash
docker exec startflow-ai-model printenv N_GPU_LAYERS
docker exec startflow-ai-model python3 -c "from llama_cpp.llama_cpp import load_shared_library; import pathlib, llama_cpp; p=pathlib.Path(llama_cpp.__file__).parent; lib=load_shared_library('llama', p/'lib'); print('gpu_offload', bool(lib.llama_supports_gpu_offload()))"
```

## Про «2048» в задании

- **`N_CTX=2048`** — размер контекста (уже так по умолчанию).
- **`N_GPU_LAYERS`** — число **слоёв** на GPU (для 8B обычно ~32–35), не 2048. Используйте `-1` (все слои) или `35`, если VRAM мало — уменьшайте по логам/CUDA OOM.

## Если нет NVIDIA GPU

Оставьте обычный `docker compose up` без `docker-compose.gpu.yml`. Ускорение только за счёт CPU/OpenBLAS (отдельная оптимизация).
