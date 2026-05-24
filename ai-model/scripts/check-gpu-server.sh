#!/usr/bin/env bash
# Run on the VPS (host), not inside a container.
set -euo pipefail

echo "=== PCI GPU devices ==="
lspci 2>/dev/null | grep -iE 'vga|3d|nvidia|amd' || echo "(no discrete GPU in lspci)"

echo
echo "=== NVIDIA driver (host) ==="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
else
  echo "nvidia-smi not found — driver not installed or not in PATH"
fi

echo
echo "=== NVIDIA device nodes ==="
ls -la /dev/nvidia* 2>/dev/null || echo "(no /dev/nvidia*)"

echo
echo "=== Docker NVIDIA runtime ==="
docker info 2>/dev/null | grep -iE 'nvidia|runtime' || true
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi 2>&1 | head -20 || \
  echo "docker --gpus all failed (install nvidia-container-toolkit?)"

echo
echo "=== startflow-ai-model env / image ==="
docker inspect startflow-ai-model --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep -E 'N_GPU|N_CTX' || true

echo
echo "=== GPU support inside running ai-model container ==="
docker exec startflow-ai-model python3 -c "
from llama_cpp.llama_cpp import load_shared_library
import pathlib
pkg = pathlib.Path(__import__('llama_cpp').__file__).parent
lib = load_shared_library('llama', pkg / 'lib')
print('llama_supports_gpu_offload:', bool(lib.llama_supports_gpu_offload()))
" 2>&1 || echo "(container check failed)"
