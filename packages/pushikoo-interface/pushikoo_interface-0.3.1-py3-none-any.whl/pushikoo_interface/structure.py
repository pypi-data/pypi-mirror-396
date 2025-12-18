from abc import ABC

from pydantic import BaseModel, ConfigDict, Field


class StructElement(BaseModel, ABC):
    type: str
    model_config = ConfigDict(keyword_only=True, extra="allow")

    def __str__(self) -> str:
        return ""

    def asmarkdown(self) -> str:
        raise NotImplementedError


class StructText(StructElement):
    type: str = "text"
    text: str
    bold: bool = False
    italic: bool = False

    def __str__(self) -> str:
        return self.text

    def asmarkdown(self) -> str:
        finalstr = self.text.replace("\n", "  \n")
        if self.bold:
            finalstr = f"**{finalstr}**"
        if self.italic:
            finalstr = f"*{finalstr}*"
        return finalstr


class StructTitle(StructText):
    type: str = "title"
    heading: int = 1

    def __str__(self) -> str:
        return self.text + "\n"

    def asmarkdown(self) -> str:
        finalstr = super().asmarkdown()
        return "#" * self.heading + " " + finalstr + "  \n"


class StructImage(StructElement):
    type: str = "image"
    source: str = Field(
        description=(
            "Image URI. Accepts valid URI including:\n"
            "- Local files via 'file://' scheme (e.g., file:///path/to/image.png)\n"
            "- Remote images via 'http://' or 'https://'\n"
            # "- Other standard URI formats (e.g., data URIs)\n"
        )
    )
    alt: str = Field(default="", description="Alternative text for image")

    def __str__(self) -> str:
        return "\n"

    def asmarkdown(self, source=None) -> str:
        if source is None:
            source = self.source
        return f"![{self.alt}]({source})  \n"


class StructURL(StructElement):
    type: str = "url"
    source: str
    title: StructText

    def __str__(self) -> str:
        return self.source

    def asmarkdown(self) -> str:
        return f"[{self.title.asmarkdown()}]({self.source})"


StructElementType = StructText | StructTitle | StructImage | StructURL


class Struct(BaseModel):
    content: list[StructElementType] = Field(default_factory=list)

    def append(self, struct: StructElementType):
        self.content.append(struct)

    def extend(self, another: "Struct") -> "Struct":
        self.content.extend(another.content)
        return self

    def __str__(self) -> str:
        return "".join(str(e) for e in self.content)

    def __repr__(self) -> str:
        return f"Struct(len={len(self.content)}, preview={self.as_preview_str()!r})"

    def asmarkdown(self) -> str:
        return "".join(e.asmarkdown() for e in self.content)

    def as_preview_str(self, max_len=40, ellipsis="...") -> str:
        s = str(self).replace("\n", "\\n")
        if len(s) <= max_len:
            return s
        half = (max_len - len(ellipsis)) // 2
        return s[:half] + ellipsis + s[-half:]
