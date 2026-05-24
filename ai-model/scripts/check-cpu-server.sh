#!/usr/bin/env bash
# Run on the VPS host to see what you can tune for startflow-ai-model.
set -euo pipefail

echo "=== CPU ==="
nproc --all 2>/dev/null || echo "nproc unavailable"
lscpu 2>/dev/null | grep -E '^CPU\(s\)|Model name|Thread|Core|Socket|MHz' || true

echo
echo "=== RAM ==="
free -h

echo
echo "=== Load / steal (noisy neighbor?) ==="
uptime
if command -v vmstat >/dev/null 2>&1; then
  vmstat 1 3 | tail -3
fi

echo
echo "=== Docker: ai-model limits & usage ==="
docker inspect startflow-ai-model --format 'cpus={{.HostConfig.NanoCpus}} memory={{.HostConfig.Memory}}' 2>/dev/null || true
docker stats startflow-ai-model --no-stream 2>/dev/null || true

echo
echo "=== Inside container: threads env ==="
docker exec startflow-ai-model sh -c 'nproc; printenv | grep -E "N_THREADS|N_BATCH|N_CTX|OMP_|OPENBLAS|GGML" || true' 2>/dev/null || true

echo
echo "=== Model file size ==="
docker exec startflow-ai-model sh -c 'ls -lh "$MODEL_DIR"/"$MODEL_FILENAME" 2>/dev/null || ls -lh /service/models/' 2>/dev/null || true

echo
echo "=== Suggested N_THREADS (physical cores heuristic) ==="
CORES=$(nproc 2>/dev/null || echo 4)
echo "Try N_THREADS=$((CORES)) and N_THREADS_BATCH=$((CORES)) in ai-model/.env"
echo "If VPS is shared and slow, try N_THREADS=$((CORES / 2))"
