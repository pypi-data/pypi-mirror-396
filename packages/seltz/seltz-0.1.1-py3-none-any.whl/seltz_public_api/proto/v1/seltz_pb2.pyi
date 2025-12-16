from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class Includes(_message.Message):
    __slots__ = ()
    MAX_DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    max_documents: int
    def __init__(self, max_documents: _Optional[int] = ...) -> None: ...

class SearchRequest(_message.Message):
    __slots__ = ()
    QUERY_FIELD_NUMBER: _ClassVar[int]
    INCLUDES_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    query: str
    includes: Includes
    context: str
    profile: str
    def __init__(self, query: _Optional[str] = ..., includes: _Optional[_Union[Includes, _Mapping]] = ..., context: _Optional[str] = ..., profile: _Optional[str] = ...) -> None: ...

class Document(_message.Message):
    __slots__ = ()
    URL_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    url: str
    content: str
    def __init__(self, url: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ()
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    documents: _containers.RepeatedCompositeFieldContainer[Document]
    def __init__(self, documents: _Optional[_Iterable[_Union[Document, _Mapping]]] = ...) -> None: ...
