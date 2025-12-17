"""
ActionEngine WebRTC interface.
"""
from __future__ import annotations
import actionengine._C.data
import actionengine._C.service
import collections.abc
import typing
__all__: list[str] = ['RtcConfig', 'TurnServer', 'WebRtcServer', 'WebRtcWireStream', 'make_webrtc_stream']
class RtcConfig:
    """
    A WebRTC configuration.
    """
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def enable_ice_udp_mux(self) -> bool:
        """
        Whether to enable ICE UDP multiplexing.
        """
    @enable_ice_udp_mux.setter
    def enable_ice_udp_mux(self, arg0: bool) -> None:
        ...
    @property
    def max_message_size(self) -> int | None:
        """
        The maximum message size for WebRTC data channels.
        """
    @max_message_size.setter
    def max_message_size(self, arg0: typing.SupportsInt | None) -> None:
        ...
    @property
    def port_range_begin(self) -> int:
        """
        The beginning of the port range for WebRTC connections.
        """
    @port_range_begin.setter
    def port_range_begin(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def port_range_end(self) -> int:
        """
        The end of the port range for WebRTC connections.
        """
    @port_range_end.setter
    def port_range_end(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def stun_servers(self) -> list[str]:
        """
        A list of STUN servers to use for WebRTC connections.
        """
    @stun_servers.setter
    def stun_servers(self, arg0: collections.abc.Sequence[str]) -> None:
        ...
    @property
    def turn_servers(self) -> list[TurnServer]:
        """
        A list of TURN servers to use for WebRTC connections.
        """
    @turn_servers.setter
    def turn_servers(self, arg0: collections.abc.Sequence[TurnServer]) -> None:
        ...
class TurnServer:
    """
    A TURN server configuration.
    """
    hostname: str
    password: str
    username: str
    @staticmethod
    def from_string(server: str) -> TurnServer:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def port(self) -> int:
        ...
    @port.setter
    def port(self, arg0: typing.SupportsInt) -> None:
        ...
class WebRtcServer:
    """
    A WebRtcServer interface.
    """
    @staticmethod
    def create(service: actionengine._C.service.Service, address: str = '0.0.0.0', port: typing.SupportsInt = 20000, identity: str = 'server', signalling_url: str = 'wss://actionengine.dev:19001', rtc_config: RtcConfig = ...) -> WebRtcServer:
        ...
    def cancel(self) -> None:
        ...
    def join(self) -> None:
        ...
    def run(self) -> None:
        ...
    def set_signalling_header(self, key: str, value: str) -> None:
        ...
class WebRtcWireStream(actionengine._C.service.WireStreamVirtualBase):
    """
    A WebRtcWireStream interface.
    """
    def __repr__(self) -> str:
        ...
    def abort(self) -> None:
        ...
    def accept(self) -> None:
        ...
    def get_id(self) -> str:
        ...
    def get_status(self) -> None:
        ...
    def half_close(self) -> None:
        ...
    def receive(self, arg0: ...) -> actionengine._C.data.WireMessage | None:
        ...
    def send(self, arg0: actionengine._C.data.WireMessage) -> None:
        ...
    def start(self) -> None:
        ...
def make_webrtc_stream(identity: str = 'client', peer_identity: str = 'server', signalling_address: str = 'wss://actionengine.dev:19001', headers: collections.abc.Mapping[str, str] = {}, port: typing.SupportsInt | None = None) -> WebRtcWireStream:
    ...
