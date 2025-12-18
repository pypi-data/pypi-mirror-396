import os
from pathlib import Path

from dotenv import load_dotenv
from pushikoo_interface import (
    get_adapter_test_env,
    run_getter_basic_flow,
)

from pushikoo_getter_skland.config import SklandAdapterConfig, SklandInstanceConfig


def test_basic_flow():
    load_dotenv()
    _adapter_config = SklandAdapterConfig()
    instance_config = SklandInstanceConfig(
        phone=os.environ["SKLAND_PHONE"], password=os.environ["SKLAND_PASSWORD"]
    )
    getter, ctx = get_adapter_test_env(
        Path(__file__).parents[1] / "pyproject.toml",
        adapter_instance_config=instance_config,
    )
    ids, detail, details = run_getter_basic_flow(getter, ctx)


if __name__ == "__main__":
    test_basic_flow()
