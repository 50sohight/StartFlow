# CPU: выжать максимум на VPS без GPU

На вашем сервере только QXL (виртуальная «видеокарта»), GPU нет. Ускорение — только CPU, RAM и логика RAG.

## 1. Диагностика (сначала на VPS)

```bash
cd ~/StartFlow/ai-model
bash scripts/check-cpu-server.sh
```

Запишите: **число ядер** (`nproc`), **свободную RAM** (`free -h`), **CPU%** в `docker stats` во время запроса.

---

## 2. Что сейчас «не на максимум»

| Узкое место | Сейчас | Потенциал |
|-------------|--------|-----------|
| **Два прохода LLM (RAG)** | step1 + step2 на каждый запрос | ~**2×** время — главный тормоз |
| **Потоки CPU** | не заданы → дефолт llama.cpp | явно `N_THREADS` = ядра |
| **Сборка llama** | generic pip wheel | **OpenBLAS** (+15–40% tok/s) |
| **mlock** | выкл | держать веса в RAM, меньше swap |
| **n_batch** | дефолт 512 | 512–1024 если хватает RAM |
| **max_tokens** | API до 2048, фронт 512 | для отчёта 512 ок; RAG step2 всё равно тяжёлый |
| **N_CTX=2048** | уже «макс» контекста | **уменьшать** (1024) ускорит и сэкономит RAM |
| **Модель 8B Q4** | ~5 GB + KV cache | Q3_K_M или 3B — быстрее, хуже качество |
| **uvicorn workers** | 1 | **не ставить >1** (копии модели в RAM) |

---

## 3. Рекомендуемые значения env (подставьте своё `nproc`)

В `ai-model/.env` на сервере (пример для **8 vCPU**, **16+ GB RAM**):

```env
N_GPU_LAYERS=0
N_CTX=2048
N_THREADS=8
N_THREADS_BATCH=8
N_BATCH=512
USE_MLOCK=1
USE_MMAP=1
OMP_NUM_THREADS=8
OPENBLAS_NUM_THREADS=8
```

Правила:

- `N_THREADS` + перегруз OpenMP **не больше** числа **физических** ядер (на VPS часто `nproc` = vCPU).
- Если сервер «душится» (load > cores, 527 процессов на хосте) — попробуйте `N_THREADS=4`.
- `USE_MLOCK=1` нужен `cap_add: IPC_LOCK` — есть в `docker-compose.cpu.yml`.
- Не хватает RAM → `USE_MLOCK=0`, `N_CTX=1024`, `N_BATCH=256`.

---

## 4. Деплой с OpenBLAS (только ai-model)

```bash
cd ~/StartFlow/ai-model
# .env с MODEL_HOST_PATH и N_THREADS=...

sudo docker compose -f docker-compose.yml -f docker-compose.cpu.yml build --no-cache
sudo docker compose -f docker-compose.yml -f docker-compose.cpu.yml up -d
sudo docker logs startflow-ai-model 2>&1 | grep "llama.cpp init"
```

Первая сборка **10–30+ минут** (компиляция llama.cpp).

---

## 5. Прикладной уровень (без пересборки образа)

### RAG = 2 вызова модели

Каждый `/ai/generate` в режиме `rag`:

1. step1 — поиск документов (`max_tokens=256`)
2. step2 — ответ (`max_tokens` из запроса)

**Итог:** даже при `max_tokens=512` на фронте вы платите за **два** полных прогона. Самый сильный рычаг — один проход (упростить промпт / убрать step1) — это уже изменение логики, не env.

### Фронт

`frontend/src/lib/ai.js` уже шлёт `max_tokens: 512` — хорошо. Не поднимайте до 2048 без нужды.

### Контейнер

Если на VPS ai-model делит CPU с чужими контейнерами — в `docker-compose.cpu.yml` раскомментируйте `deploy.resources.limits` (cpus/memory), чтобы гарантировать долю ресурсов **только** для `startflow-ai-model`.

---

## 6. Ориентиры по железу (8B Q4_K_M)

| RAM | N_CTX | USE_MLOCK | Комментарий |
|-----|-------|-----------|-------------|
| 8 GB | 1024 | 0 | впритык, возможен swap |
| 16 GB | 2048 | 1 | нормальный минимум для 8B |
| 32 GB | 2048 | 1 | можно `N_BATCH=1024` |

Модель на диске: обычно **~4.5–5 GB** для `q4_k_m`.

---

## 7. Что **нельзя** «выкрутить» на этом VPS

- GPU / `N_GPU_LAYERS > 0`
- Скорость как у GPU без смены железа или модели
- Несколько воркеров uvicorn с одной моделью в памяти

---

## 8. Порядок действий (по отдаче)

1. `check-cpu-server.sh` → выставить `N_THREADS` / `N_THREADS_BATCH`
2. `docker-compose.cpu.yml` (OpenBLAS + mlock)
3. Проверить RAM → при OOM снизить `N_CTX` / `N_BATCH`
4. Если всё ещё медленно — обсудить **одношаговый RAG** или меньшую модель
5. Долгосрочно — GPU-VPS только для `startflow-ai-model`
