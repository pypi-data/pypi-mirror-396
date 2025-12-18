import importlib.metadata as md
import os
import tempfile
import tomllib
from pathlib import Path

from pushikoo_interface.adapter import AdapterConfig
from pushikoo_interface import (
    Adapter,
    AdapterFrameworkContext,
    AdapterInstanceConfig,
    Detail,
    Getter,
    Pusher,
    Processer,
    get_adapter_config_types,
    Struct,
    StructText,
)


def get_adapter_test_env(
    project_toml_path: Path,
    proxies: dict[str, str] | None = None,
    adapter_config: AdapterConfig = None,
    adapter_instance_config: AdapterInstanceConfig = None,
    storage_base_path: Path | None = None,
) -> tuple[type[Adapter], AdapterFrameworkContext]:
    adapter_name = tomllib.loads(project_toml_path.read_text(encoding="utf-8"))[
        "project"
    ]["name"]

    eps = md.entry_points(group="pushikoo.adapter")
    ep = next((e for e in eps if getattr(e.dist, "name", None) == adapter_name), None)
    assert ep, f"No entry point found for {adapter_name}"

    UnderTestAdapterClass = ep.load()
    assert issubclass(UnderTestAdapterClass, Adapter)

    UnderTestAdapterCfg, UnderTestAdapterInstCfg = get_adapter_config_types(
        UnderTestAdapterClass
    )
    assert issubclass(UnderTestAdapterCfg, AdapterConfig), (
        "Config of adapter which is under test is not a subclass of AdapterConfig"
    )
    assert issubclass(UnderTestAdapterInstCfg, AdapterInstanceConfig), (
        "Instance config of adapter which is under test is not a subclass of AdapterInstanceConfig"
    )

    if storage_base_path is None:
        storage_base_path = (
            Path(tempfile.mkdtemp(prefix="pushikoo_adapter_test")) / "adapter_storage"
        )

    class MockCtx(AdapterFrameworkContext):
        @staticmethod
        def get_proxies():
            if proxies:
                return proxies
            if all_proxy := os.environ.get("all_proxy"):
                return {
                    "http": all_proxy,
                    "https": all_proxy,
                }
            if (http_proxy := os.environ.get("http_proxy")) and (
                https_proxy := os.environ.get("https_proxy")
            ):
                return {"http": http_proxy, "https": https_proxy}
            return {}

        @staticmethod
        def get_config():
            if adapter_config:
                return adapter_config
            return UnderTestAdapterCfg()

        @staticmethod
        def get_instance_config():
            if adapter_instance_config:
                return adapter_instance_config
            return UnderTestAdapterInstCfg()

    MockCtx.storage_base_path = storage_base_path

    return UnderTestAdapterClass, MockCtx


def run_getter_basic_flow(
    adapter_type: type[Adapter], context: AdapterFrameworkContext
) -> tuple[list[str], Detail | None, Detail | None]:
    """
    Basic smoke test for a Getter adapter.

    This test verifies that:
    1. The adapter can be instantiated correctly with a mock context.
    2. The `timeline()` method returns a list of IDs.
    3. For the first ID (if available), both:
        - `detail()` returns a valid `Detail` object.
        - `details()` handles a list of IDs and returns an aggregated `Detail`,
          unless the method is not implemented.

    Args:
        adapter_type: The Adapter subclass under test.
        context: An instance of `AdapterFrameworkContext`, providing config and paths.

    Returns:
        A tuple of:
        - list of timeline IDs (`list[str]`),
        - detail of the first ID (`Detail | None`),
        - aggregated detail for all IDs (`Detail | None`)
    """
    UnderTestAdapterClass = adapter_type
    ctx = context

    # assert UnderTestAdapterClass.meta.name == ""
    getter: Getter = UnderTestAdapterClass.create(identifier="123", ctx=ctx)

    ids: list[str] = []
    detail = None
    agg = None

    ids = getter.timeline()
    assert isinstance(ids, list), "getter.timeline return-value is not a list"

    if ids:
        detail = getter.detail(ids[0])
        assert isinstance(detail, Detail), (
            "getter.detail return-value is not a valid Detail object"
        )

        try:
            agg = getter.details(ids)
            assert isinstance(agg, Detail), (
                "getter.details return-value is not a valid Detail object"
            )
        except NotImplementedError:  # pragma: no cover
            pass
    else:  # pragma: no cover
        pass

    return ids, detail, agg


def run_pusher_basic_flow(
    adapter_type: type[Adapter], context: AdapterFrameworkContext
) -> None:
    """
    Basic smoke test for a Pusher adapter.

    This test verifies that:
    1. The adapter can be instantiated correctly with a mock context.
    2. The `push()` method can accept a Struct content and execute without errors.

    Args:
        adapter_type: The Adapter subclass under test.
        context: An instance of `AdapterFrameworkContext`, providing config and paths.

    Returns:
        None
    """
    UnderTestAdapterClass = adapter_type
    ctx = context

    # Import Pusher class to check if it's a Pusher
    assert issubclass(UnderTestAdapterClass, Pusher), (
        "Adapter under test is not a Pusher subclass"
    )

    pusher = UnderTestAdapterClass.create(identifier="123", ctx=ctx)

    # Create a simple test Struct
    test_struct = Struct()
    test_struct.append(StructText(text="Test content for pusher"))

    # Test push method - should not raise any exceptions
    try:
        pusher.push(test_struct)
    except Exception as e:
        raise AssertionError(f"pusher.push() failed with error: {e}")


def run_processer_basic_flow(
    adapter_type: type[Adapter], context: AdapterFrameworkContext
) -> Struct:
    """
    Basic smoke test for a Processer adapter.

    This test verifies that:
    1. The adapter can be instantiated correctly with a mock context.
    2. The `process()` method can accept a Struct content and return a processed Struct.
    3. The returned value is a valid Struct object.

    Args:
        adapter_type: The Adapter subclass under test.
        context: An instance of `AdapterFrameworkContext`, providing config and paths.

    Returns:
        The processed Struct returned by the processer
    """
    UnderTestAdapterClass = adapter_type
    ctx = context

    assert issubclass(UnderTestAdapterClass, Processer), (
        "Adapter under test is not a Processer subclass"
    )

    processer = UnderTestAdapterClass.create(identifier="123", ctx=ctx)

    # Create a simple test Struct
    test_struct = Struct()
    test_struct.append(StructText(text="Test content for processer"))

    # Test process method
    try:
        processed_struct = processer.process(test_struct)
    except Exception as e:
        raise AssertionError(f"processer.process() failed with error: {e}")

    # Verify the returned value is a Struct
    assert isinstance(processed_struct, Struct), (
        "processer.process() return-value is not a valid Struct object"
    )

    return processed_struct
