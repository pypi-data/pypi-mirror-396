from typing import Protocol, Literal, Annotated, Iterator, Any

class ConnlessMessage(Protocol):
    message_type: Literal['connless']
    message_name: str
    message_id: Annotated[list[int], 8]
    def unpack(self, data: bytes) -> bool:
        ...
    def pack(self) -> bytes:
        ...
    def __iter__(self) -> Iterator[tuple[str, Any]]:
        ...
