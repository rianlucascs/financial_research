"""
Utilitário: resource_monitor

Responsabilidades:
    Cronometrar execução e medir pico real de RSS (memória residente) de um
    bloco de código, via amostragem em thread separada.

Notas:
    Diferente de resource.getrusage().ru_maxrss (cumulativo desde o início
    do processo, não reflete corretamente picos abaixo de picos anteriores),
    aqui o pico é local ao bloco medido — correto mesmo com múltiplos
    workers rodando em sequência no mesmo processo.
"""

import threading
import time
from contextlib import contextmanager
from logging import Logger

import psutil


@contextmanager
def resource_monitor(logger: Logger, label: str, sample_interval: float = 0.1):

    process = psutil.Process()
    start_time = time.perf_counter()
    start_rss_mb = process.memory_info().rss / (1024 ** 2)

    peak_rss_mb = start_rss_mb
    stop_event = threading.Event()

    def _sample() -> None:
        nonlocal peak_rss_mb
        while not stop_event.is_set():
            current_rss_mb = process.memory_info().rss / (1024 ** 2)
            peak_rss_mb = max(peak_rss_mb, current_rss_mb)
            stop_event.wait(sample_interval)

    sampler_thread = threading.Thread(target=_sample, daemon=True)
    sampler_thread.start()

    metrics: dict[str, float] = {}

    try:
        yield metrics
    finally:
        stop_event.set()
        sampler_thread.join()

        end_rss_mb = process.memory_info().rss / (1024 ** 2)

        metrics["elapsed_seconds"] = round(time.perf_counter() - start_time, 2)
        metrics["rss_start_mb"] = round(start_rss_mb, 1)
        metrics["rss_end_mb"] = round(end_rss_mb, 1)
        metrics["peak_rss_mb"] = round(peak_rss_mb, 1)

        logger.info(
            f"[{label}] tempo={metrics['elapsed_seconds']}s | "
            f"rss_inicio={metrics['rss_start_mb']}MB | "
            f"rss_fim={metrics['rss_end_mb']}MB | "
            f"pico_rss={metrics['peak_rss_mb']}MB"
        )