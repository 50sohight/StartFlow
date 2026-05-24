"""CPU / llama.cpp settings from environment."""

from __future__ import annotations

import os


def _parse_int(name: str) -> int | None:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return None
    return int(raw)


def _parse_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def llama_init_kwargs() -> dict:
    """Keyword arguments for llama_cpp.Llama(), driven by env vars."""
    kwargs: dict = {
        "n_gpu_layers": int(os.getenv("N_GPU_LAYERS", "0")),
        "n_ctx": int(os.getenv("N_CTX", "2048")),
        "verbose": _parse_bool("LLAMA_VERBOSE", False),
        "use_mmap": _parse_bool("USE_MMAP", True),
        "use_mlock": _parse_bool("USE_MLOCK", False),
    }

    for key, env_name in (
        ("n_threads", "N_THREADS"),
        ("n_threads_batch", "N_THREADS_BATCH"),
        ("n_batch", "N_BATCH"),
        ("n_ubatch", "N_UBATCH"),
    ):
        value = _parse_int(env_name)
        if value is not None:
            kwargs[key] = value

    return kwargs
