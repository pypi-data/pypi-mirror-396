from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import primitive.client


class BaseAction:
    def __init__(self, primitive: "primitive.client.Primitive") -> None:
        self.primitive = primitive
