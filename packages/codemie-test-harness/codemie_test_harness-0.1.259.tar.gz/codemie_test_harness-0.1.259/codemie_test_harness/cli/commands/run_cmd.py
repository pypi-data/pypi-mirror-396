from __future__ import annotations
import click
from typing import Optional, Tuple
from ..runner import run_pytest
from ..utils import get_config_value
from ..constants import (
    KEY_MARKS,
    KEY_XDIST_N,
    KEY_RERUNS,
    KEY_COUNT,
    KEY_TIMEOUT,
    DEFAULT_MARKS,
    DEFAULT_XDIST_N,
    DEFAULT_RERUNS,
    DEFAULT_TIMEOUT,
)


@click.command(name="run")
@click.option("--marks", help="Override pytest -m expression for this run")
@click.option(
    "-n", "workers", type=int, help="Override number of xdist workers for this run"
)
@click.option("--reruns", type=int, help="Override number of reruns for this run")
@click.option(
    "--count",
    type=int,
    help="Number of times to repeat each test (requires pytest-repeat)",
)
@click.option(
    "--timeout",
    type=int,
    help="Per-test timeout in seconds (overrides config/default)",
)
@click.argument("extra", nargs=-1)
@click.pass_context
def run_cmd(
    ctx: click.Context,
    marks: Optional[str],
    workers: Optional[int],
    reruns: Optional[int],
    count: Optional[int],
    timeout: Optional[int],
    extra: Tuple[str, ...],
):
    """Run pytest with configured options.

    Example: codemie-test-harness run --marks "smoke and not ui" -n 8 --reruns 2 -k keyword
    Example with repeat: codemie-test-harness run --marks excel_generation --count 50 -n 10
    Example with timeout: codemie-test-harness run --marks slow --timeout 600 -n 4
    """
    # Resolve options using CLI args -> config -> defaults
    resolved_marks = marks or get_config_value(KEY_MARKS, DEFAULT_MARKS)
    resolved_workers = (
        workers
        if workers is not None
        else int(get_config_value(KEY_XDIST_N, str(DEFAULT_XDIST_N)))
    )
    resolved_reruns = (
        reruns
        if reruns is not None
        else int(get_config_value(KEY_RERUNS, str(DEFAULT_RERUNS)))
    )
    resolved_count = (
        count
        if count is not None
        else (int(get_config_value(KEY_COUNT)) if get_config_value(KEY_COUNT) else None)
    )
    resolved_timeout = (
        timeout
        if timeout is not None
        else int(get_config_value(KEY_TIMEOUT, str(DEFAULT_TIMEOUT)))
    )

    run_pytest(
        int(resolved_workers),
        str(resolved_marks),
        int(resolved_reruns),
        resolved_count,
        resolved_timeout,
        extra,
    )
