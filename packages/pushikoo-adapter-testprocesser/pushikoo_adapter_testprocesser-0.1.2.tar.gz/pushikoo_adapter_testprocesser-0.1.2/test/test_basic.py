from pathlib import Path

from pushikoo_interface import (
    get_adapter_test_env,
    run_processer_basic_flow,
)


def test_basic_flow():
    processer, ctx = get_adapter_test_env(Path(__file__).parents[1] / "pyproject.toml")
    processed = run_processer_basic_flow(processer, ctx)

    # TODO: Edit this, or add more test cases
    pass
