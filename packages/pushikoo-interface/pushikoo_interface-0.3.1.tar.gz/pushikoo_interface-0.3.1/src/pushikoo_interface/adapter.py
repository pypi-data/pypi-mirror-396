from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar, final, get_args, get_origin

from pydantic import BaseModel, ConfigDict, Field

from pushikoo_interface import util
from pushikoo_interface.structure import Struct, StructImage

TADAPTERCONFIG = TypeVar("TADAPTERCONFIG", bound="AdapterConfig")
TADAPTERINSTANCECONFIG = TypeVar(
    "TADAPTERINSTANCECONFIG", bound="AdapterInstanceConfig"
)


class AdapterMeta(BaseModel):
    name: str
    version: str
    author: str | None = None
    summary: str | None = None
    description: str | None = None
    url: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class AdapterFrameworkContext(ABC):
    storage_base_path: Path

    get_proxies: Callable[[], dict[str, str]]
    get_config: Callable[[], BaseModel]
    get_instance_config: Callable[[], BaseModel]


class AdapterConfig(BaseModel): ...


class AdapterInstanceConfig(BaseModel): ...


class Adapter(ABC, Generic[TADAPTERCONFIG, TADAPTERINSTANCECONFIG]):
    _default_config_type: type
    _default_instance_config_type: type

    ctx: AdapterFrameworkContext
    meta: AdapterMeta
    adapter_name: str
    identifier: str
    adapter_storage_path: Path
    instance_storage_path: Path

    @staticmethod
    def _get_meta(cls):
        dist_name, dist_version, dist_metadata = util.get_dist_meta(cls)
        url = dist_metadata.json.get("home_page")
        if url is None:
            url: str | None = dist_metadata.json.get("project_url", [None])[0]
            if url:
                url = url.split(",", 1)[1].strip()

        meta = AdapterMeta(
            name=dist_name,
            version=dist_version,
            author=dist_metadata.get("Author"),
            summary=dist_metadata.get("Summary"),
            description=dist_metadata.get("Description"),
            url=url,
            extra={
                k: v
                for k, v in dist_metadata.items()
                if k
                not in {
                    "Name",
                    "Version",
                    "Summary",
                    "Description",
                    "Author",
                    "Home-page",
                }
            },
        )
        return meta

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.meta = Adapter._get_meta(cls)

    @classmethod
    @final
    def create(cls, *args, identifier: str, ctx: Any, **kwargs):
        obj = cls.__new__(cls)
        obj.ctx = ctx

        obj.adapter_name = obj.meta.name
        obj.identifier = identifier
        storage_base = obj.ctx.storage_base_path
        obj.adapter_storage_path = storage_base / obj.adapter_name
        obj.instance_storage_path = obj.adapter_storage_path / obj.identifier
        obj.adapter_storage_path.mkdir(parents=True, exist_ok=True)
        obj.instance_storage_path.mkdir(parents=True, exist_ok=True)

        cls.__init__(obj, *args, **kwargs)

        return obj

    @property
    def config(self) -> TADAPTERCONFIG:
        return self.ctx.get_config()

    @property
    def instance_config(self) -> TADAPTERINSTANCECONFIG:
        return self.ctx.get_instance_config()

    def __str__(self) -> str:
        return f"{self.adapter_name}.{self.identifier}"

    def __hash__(self) -> int:
        return hash(str(self))


class Detail(BaseModel):
    model_config = ConfigDict(keyword_only=True)

    ts: float = Field(description="10-digit integer Unix timestamp (decimals allowed)")
    content: str | Struct = Field(description="Main content payload")

    title: str | None = Field(
        default=None, description="Title or headline of the content"
    )
    author_id: str | None = Field(
        default=None, description="Unique identifier of the author"
    )
    author_name: str | None = Field(
        default=None, description="Display name of the author"
    )
    url: str | list[str] = Field(
        default_factory=list, description="Primary or related URLs for the content"
    )
    image: list[str | StructImage] = Field(
        default_factory=list,
        description=(
            "List of image resources associated with the content. Each entry must be either:\n"
            "- A string URI\n"
            "- A StructImage object\n"
            "Image URI. Accepts valid URI including:\n"
            "- Local files via 'file://' scheme (e.g., file:///path/to/image.png)\n"
            "- Remote images via 'http://' or 'https://'\n"
        ),
    )

    extra_detail: list[str] = Field(
        default_factory=list,
        description="Structured detailed data for content representation",
    )

    detail: dict = Field(
        default_factory=dict,
        description="Additional descriptive text or metadata details for message",
    )


class GetterConfig(AdapterConfig): ...


class GetterInstanceConfig(AdapterInstanceConfig): ...


class Getter(
    Adapter[TADAPTERCONFIG, TADAPTERINSTANCECONFIG],
    Generic[TADAPTERCONFIG, TADAPTERINSTANCECONFIG],
):
    _default_config_type = GetterConfig
    _default_instance_config_type = GetterInstanceConfig

    @abstractmethod
    def timeline(self) -> list[str]:
        """Get newest lists. Must be overrided.

        Returns:
            list[str]: Lists of identifiers.
        """
        ...

    @abstractmethod
    def detail(self, identifier: str) -> Detail:
        """Get detail of a specific identifier. Must be overrided.

        Args:
            identifier: identifier

        Returns:
            GetResult: Result
        """
        ...

    def details(self, identifiers: list[str]) -> Detail:
        """Get detail of specific identifiers as a single Detail.

        Different types of messages have different semantic aggregation granularity
        - Some messages (such as long-content game updates) can only be processed separately;
        - Some messages, such as short, frequent updates, can be combined into a single logical message.
        Therefore, adapter developers can implement this method,
        if framework option "getter_instance.prefer_details" is True, this method will be called preferentially.
        This method is not enforced, and if it is not implemented, it will fallback to `detail`.

        Args:
            identifiers: identifiers

        Returns:
            GetResult: Result
        """
        raise NotImplementedError()


class PusherConfig(AdapterConfig): ...


class PusherInstanceConfig(AdapterInstanceConfig): ...


class Pusher(
    Adapter[TADAPTERCONFIG, TADAPTERINSTANCECONFIG],
    Generic[TADAPTERCONFIG, TADAPTERINSTANCECONFIG],
):
    _default_config_type = PusherConfig
    _default_instance_config_type = PusherInstanceConfig

    @abstractmethod
    def push(self, content: Struct) -> None: ...


class TerminateFlowException(Exception): ...


class ProcesserConfig(AdapterConfig): ...


class ProcesserInstanceConfig(AdapterInstanceConfig): ...


class Processer(
    Adapter[TADAPTERCONFIG, TADAPTERINSTANCECONFIG],
    Generic[TADAPTERCONFIG, TADAPTERINSTANCECONFIG],
):
    _default_config_type = ProcesserConfig
    _default_instance_config_type = ProcesserInstanceConfig

    @abstractmethod
    def process(self, content: Struct) -> Struct:
        """Process the content and return modified content.

        This method processes the input content and returns the modified version.
        The processor can transform, filter, or enhance the content as needed.

        Args:
            content: Input content to be processed

        Returns:
            Struct: Processed content

        Raises:
            TerminateFlow: Can be raised to terminate the flow processing
        """
        ...


def get_adapter_config_types(
    cls: type,
) -> tuple[type[AdapterConfig], type[AdapterInstanceConfig]]:
    """Return generic config types for an Adapter subclass.

    Given a class (possibly subclass of Adapter), attempt to
    extract its generic parameters (class-config model, instance-config model).
    Falls back to the class attributes `_default_config_type` and
    `_default_instance_config_type` if generics are not explicitly specified.
    If still unavailable, returns the base `AdapterConfig` and
    `AdapterInstanceConfig`.
    """

    # 1) Inspect generic bases to find concrete args provided to Adapter
    def _find_generic_args(c: type) -> tuple[type | None, type | None]:
        for base in getattr(c, "__orig_bases__", ()):  # type: ignore[attr-defined]
            origin = get_origin(base)
            if origin in {Adapter, Getter, Pusher, Processer}:
                args = get_args(base)
                if len(args) == 2:
                    a0, a1 = args
                    # Ensure these are types
                    if isinstance(a0, type) and isinstance(a1, type):
                        return a0, a1
        return None, None

    # Walk MRO to find first class with explicit generic args
    adapter_cfg_t: type | None = None
    inst_cfg_t: type | None = None
    for c in cls.__mro__:
        a0, a1 = _find_generic_args(c)
        if a0 is not None and a1 is not None:
            adapter_cfg_t, inst_cfg_t = a0, a1
            break

    # 2) Fallback to declared default types on the class hierarchy
    if adapter_cfg_t is None:
        adapter_cfg_t = getattr(cls, "_default_config_type", None)
    if inst_cfg_t is None:
        inst_cfg_t = getattr(cls, "_default_instance_config_type", None)

    # 3) Final fallback to base config models
    if not isinstance(adapter_cfg_t, type):
        adapter_cfg_t = AdapterConfig
    if not isinstance(inst_cfg_t, type):
        inst_cfg_t = AdapterInstanceConfig

    return adapter_cfg_t, inst_cfg_t
