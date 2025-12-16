import pytest
from time import perf_counter as _perf_counter
import csv
from pathlib import Path

_fixture_timing_records: list[dict] = []

EXCLUDED_FIXTURES = {"frozen_time"}  # skip problematic fixtures

_enabled: bool = False  # global flag controlled by CLI


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Register our custom CLI option.

    Example:
        pytest --fixture-timing
        pytest --fixture-timing --fixture-timing-top=30
    """
    group = parser.getgroup("fixture-timing")
    group.addoption(
        "--fixture-timing",
        action="store_true",
        default=False,
        help="measure fixture setup durations and report them at the end",
    )


def pytest_configure(config: pytest.Config) -> None:
    """
    Read CLI options and decide whether the plugin is active.
    """
    global _enabled
    _enabled = config.getoption("--fixture-timing")


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    if not _enabled:
        yield
        return

    start = _perf_counter()

    yield  # run real fixture setup

    duration = _perf_counter() - start

    name = fixturedef.argname

    # Ignore frozen-time or other fixtures that break timing
    if name in EXCLUDED_FIXTURES:
        return

    # Skip obviously bogus timings
    if duration < 0 or duration > 60:
        return

    _fixture_timing_records.append(
        {
            "fixture": name,
            "scope": fixturedef.scope,
            "duration": duration,
        }
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    if not _fixture_timing_records:
        return

    summary: dict[str, dict] = {}

    for rec in _fixture_timing_records:
        name = rec["fixture"]
        scope = rec["scope"]
        dur = rec["duration"]

        if name not in summary:
            summary[name] = {
                "fixture": name,
                "scope": scope,
                "durations": [],
            }

        summary[name]["durations"].append(dur)

    # Build rows with avg / max / total
    rows = []
    for data in summary.values():
        durations = data["durations"]
        avg_dur = sum(durations) / len(durations)
        max_dur = max(durations)
        total_dur = sum(durations)
        calls = len(durations)

        rows.append(
            {
                "fixture": data["fixture"],
                "scope": data["scope"],
                "calls": calls,
                "avg_duration_s": avg_dur,
                "max_duration_s": max_dur,
                "total_duration_s": total_dur,
            }
        )

    # Slowest fixtures first by *total* time spent (more useful than avg)
    rows.sort(key=lambda r: r["total_duration_s"], reverse=True)

    path = Path("pytest_fixture_summary.csv")

    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "fixture",
                "scope",
                "calls",
                "avg_duration_s",
                "max_duration_s",
                "total_duration_s",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r["fixture"],
                    r["scope"],
                    r["calls"],
                    f"{r['avg_duration_s']:.6f}",
                    f"{r['max_duration_s']:.6f}",
                    f"{r['total_duration_s']:.6f}",
                ]
            )

    print(f"\n[pytest-duration] Fixture summary written to {path}")
