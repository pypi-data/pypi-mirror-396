from __future__ import annotations
import typing
from . import actions
from . import chunk_store
from . import data
from . import nodes
from . import redis
from . import service
from . import webrtc
from . import websockets
__all__: list[str] = ['actions', 'chunk_store', 'data', 'nodes', 'redis', 'run_threadsafe_if_coroutine', 'save_first_encountered_event_loop', 'service', 'webrtc', 'websockets']
def run_threadsafe_if_coroutine(function_call_result: typing.Any, loop: typing.Any = None, return_future: bool = False) -> typing.Any:
    ...
def save_first_encountered_event_loop() -> None:
    """
    Saves the first encountered event loop globally for later use.
    """
