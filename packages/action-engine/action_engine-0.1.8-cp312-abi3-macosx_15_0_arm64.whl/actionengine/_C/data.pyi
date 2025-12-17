"""
ActionEngine data structures, as PODs.
"""
from __future__ import annotations
import collections.abc
import typing
__all__: list[str] = ['ActionMessage', 'ActionMessageList', 'Chunk', 'ChunkMetadata', 'NodeFragment', 'NodeFragmentList', 'Port', 'PortList', 'SerializerRegistry', 'WireMessage', 'from_chunk', 'get_global_serializer_registry', 'to_bytes', 'to_chunk']
class ActionMessage:
    """
    An ActionEngine ActionMessage definition.
    """
    id: str
    inputs: PortList
    name: str
    outputs: PortList
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, *, name: str, inputs: PortList = ..., outputs: PortList = ...) -> None:
        ...
    def __repr__(self) -> str:
        ...
class ActionMessageList:
    __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: ActionMessage) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: typing.SupportsInt) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: ActionMessageList) -> bool:
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> ActionMessageList:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: typing.SupportsInt) -> ActionMessage:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: ActionMessageList) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: collections.abc.Iterable) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[ActionMessage]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: ActionMessageList) -> bool:
        ...
    @typing.overload
    def __setitem__(self, arg0: typing.SupportsInt, arg1: ActionMessage) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: ActionMessageList) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: ActionMessage) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: ActionMessage) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: ActionMessageList) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: collections.abc.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: typing.SupportsInt, x: ActionMessage) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> ActionMessage:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: typing.SupportsInt) -> ActionMessage:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: ActionMessage) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class Chunk:
    """
    An ActionEngine Chunk containing metadata and either a reference to or the data themselves.
    """
    data: bytes
    metadata: actionengine._C.data.ChunkMetadata | None
    ref: str
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, *, metadata: ChunkMetadata = ..., data: bytes = b'', ref: str = '') -> None:
        ...
    def __repr__(self) -> str:
        ...
class ChunkMetadata:
    """
    Metadata for an ActionEngine Chunk.
    """
    attributes: dict
    mimetype: str
    timestamp: ... | None
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, *, mimetype: str = 'text/plain') -> None:
        ...
    def __repr__(self) -> str:
        ...
    def get_attribute(self, key: str) -> bytes:
        ...
    def has_attribute(self, arg0: str) -> bool:
        ...
    @typing.overload
    def set_attribute(self, key: str, value: bytes) -> None:
        ...
    @typing.overload
    def set_attribute(self, arg0: str, arg1: str) -> None:
        ...
class NodeFragment:
    """
    An ActionEngine NodeFragment.
    """
    chunk: Chunk
    continued: bool
    id: str
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, *, id: str = '', chunk: Chunk = ..., seq: typing.SupportsInt = 0, continued: bool = False) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def seq(self) -> int | None:
        ...
    @seq.setter
    def seq(self, arg0: typing.SupportsInt | None) -> None:
        ...
class NodeFragmentList:
    __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: NodeFragment) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: typing.SupportsInt) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: NodeFragmentList) -> bool:
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> NodeFragmentList:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: typing.SupportsInt) -> NodeFragment:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: NodeFragmentList) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: collections.abc.Iterable) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[NodeFragment]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: NodeFragmentList) -> bool:
        ...
    @typing.overload
    def __setitem__(self, arg0: typing.SupportsInt, arg1: NodeFragment) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: NodeFragmentList) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: NodeFragment) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: NodeFragment) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: NodeFragmentList) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: collections.abc.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: typing.SupportsInt, x: NodeFragment) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> NodeFragment:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: typing.SupportsInt) -> NodeFragment:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: NodeFragment) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class Port:
    """
    An ActionEngine Port for an Action.
    """
    id: str
    name: str
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, *, name: str = '', id: str = '') -> None:
        ...
    def __repr__(self) -> str:
        ...
class PortList:
    __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: Port) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: typing.SupportsInt) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: PortList) -> bool:
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> PortList:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: typing.SupportsInt) -> Port:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: PortList) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: collections.abc.Iterable) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[Port]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: PortList) -> bool:
        ...
    @typing.overload
    def __setitem__(self, arg0: typing.SupportsInt, arg1: Port) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: PortList) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: Port) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: Port) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: PortList) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: collections.abc.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: typing.SupportsInt, x: Port) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> Port:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: typing.SupportsInt) -> Port:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: Port) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class SerializerRegistry:
    """
    A registry for serialization functions.
    """
    def __del__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: SerializerRegistry) -> None:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    def deserialize(self, data: bytes, mimetype: str = '') -> typing.Any:
        ...
    def register_deserializer(self, arg0: str, arg1: collections.abc.Callable, arg2: typing.Any) -> None:
        ...
    def register_serializer(self, mimetype: str, serializer: collections.abc.Callable, obj_type: typing.Any = None) -> None:
        ...
    def serialize(self, value: typing.Any, mimetype: str = '') -> bytes:
        ...
    @property
    def _mimetype_to_type(self) -> dict:
        ...
    @property
    def _type_to_mimetype(self) -> dict:
        ...
class WireMessage:
    """
    An ActionEngine WireMessage data structure.
    """
    actions: ActionMessageList
    node_fragments: NodeFragmentList
    @staticmethod
    def from_msgpack(data: bytes) -> WireMessage:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, *, node_fragments: NodeFragmentList = ..., actions: ActionMessageList = ...) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def pack_msgpack(self) -> bytes:
        ...
def from_chunk(chunk: Chunk, mimetype: str = '', registry: SerializerRegistry = None) -> typing.Any:
    ...
def get_global_serializer_registry() -> SerializerRegistry:
    ...
def to_bytes(obj: typing.Any, mimetype: str = '', registry: SerializerRegistry = None) -> bytes:
    ...
@typing.overload
def to_chunk(obj: typing.Any, mimetype: str = '', registry: SerializerRegistry = None) -> Chunk:
    ...
@typing.overload
def to_chunk(arg0: NodeFragment) -> Chunk:
    ...
@typing.overload
def to_chunk(arg0: None) -> Chunk:
    ...
