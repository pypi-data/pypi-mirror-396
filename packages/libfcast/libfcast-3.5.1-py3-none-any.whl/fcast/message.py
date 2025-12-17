from dataclasses import dataclass
import struct
from enum import Enum
from typing import Optional
import json
from .event import EventSubscribeObject, EventObject
from .media import MetadataType

import logging

l = logging.getLogger(__name__)

class PlaybackState(Enum):
	idle: int = 0
	playing: int = 1
	paused: int = 2


@dataclass
class Message:

	@property
	def opcode(self):
		from .utils import MessageToOpcode
		l.debug(f"{type(self)} opcode: {MessageToOpcode[type(self)]}")
		return MessageToOpcode[type(self)]

	@property
	def header(self):
		size = 1
		if self.body: size += self.size
		if size > 32000: raise ValueError("Message size is bigger than 32000")
		return struct.pack("<I", size) + struct.pack("B", self.opcode)
	
	@property
	def as_bytes(self) -> bytes:
		data = self.header
		if self.body: data += self.body
		return data

	@property
	def size(self):
		return len(self.serialize())
	
	@property
	def body(self) -> bytes:
		return self.serialize()
	
	def serialize(self) -> bytes:
		...


@dataclass
class PlayMessage(Message):
	container: str # The MIME type (video/mp4)
	url: Optional[str] = None # The URL to load (optional)
	content: Optional[str] = None # The content to load (i.e. a DASH manifest, optional)
	time: float = 0 # The time to start playing in seconds
	volume: float = None # The desired volume (0-1)
	speed: float = 1.0 # The factor to multiply playback speed by (defaults to 1.0)
	headers: Optional[dict] = None # HTTP request headers to add to the play request Map<string, string>
	metadata: MetadataType = None

	@property
	def metadata(self) -> MetadataType:
		return self._metadata
	
	@metadata.setter
	def metadata(self, value: dict):
		if type(value) == dict:
			self._metadata = MetadataType(
			title=value.get("title"),
			thumbnailUrl=value.get("thumbnailUrl"),
			custom=value.get("custom"))
		elif isinstance(value, MetadataType) or (value is None):
			self._metadata = value
		elif isinstance(value, property):
			self._metadata = None
		else:
			raise KeyError(f"Invalid value provided for metadata: {value}")	

	def serialize(self):
		res = {
			"container": self.container,
			"time": self.time,
			"speed": self.speed
		}
		if u:=self.url: res["url"] = u
		if c:=self.content: res["content"] = c
		if h:=self.headers: res["headers"] = h
		if m:=self.metadata: res["metadata"] = m.__dict__
		return json.dumps(res).encode(encoding="utf-8")


@dataclass
class SeekMessage(Message):
	time: float = 0 # The time to seek to in seconds

	def serialize(self):
		return json.dumps({"time": self.time}).encode(encoding="utf-8")


@dataclass
class PlaybackUpdateMessage(Message):
	generationTime: float # The time the packet was generated (unix time milliseconds)
	state: PlaybackState # The playback state
	time: int = None # The current time playing in seconds
	duration: int = None # The duration in seconds
	speed: float = None # The playback speed factor
	itemIndex: int = None # The playlist item index currently being played on receiver
	
	@property
	def state(self) -> PlaybackState:
		return self._state
	
	@state.setter
	def state(self, value):
		self._state = PlaybackState(value)

	def serialize(self):
		res = {
			"generationTime": self.generationTime,
			"state": self.state.value,
		}
		if t:=self.time: res["time"] = t
		if d:=self.duration: res["duration"] = d
		if s:=self.speed: res["speed"] = s
		if i:=self.itemIndex: res["itemIndex"] = i
		return json.dumps(res).encode(encoding="utf-8")


@dataclass
class VolumeUpdateMessage(Message):
	generationTime: float # The time the packet was generated (unix time milliseconds)
	volume: float # The current volume (0-1)

	def serialize(self):
		res = {
			"generationTime": self.generationTime,
			"volume": self.volume
		}
		return json.dumps(res).encode(encoding="utf-8")


@dataclass
class SetVolumeMessage(Message):
	volume: float = 0 # The desired volume (0-1)

	def serialize(self):
		return json.dumps({"volume": self.volume}).encode(encoding="utf-8")


@dataclass
class PlaybackErrorMessage(Message):
	message: str

	def serialize(self):
		return json.dumps({"message": self.message}).encode(encoding="utf-8")


@dataclass
class SetSpeedMessage(Message):
	speed: float = 0 # The factor to multiply playback speed by.

	def serialize(self):
		return json.dumps({"volume": self.speed}).encode(encoding="utf-8")


@dataclass
class VersionMessage(Message):
	version: int = 3 # Protocol version number (integer)

	def serialize(self):
		return json.dumps({"version": self.version}).encode(encoding="utf-8")	


@dataclass
class InitialMessage(Message):
	displayName: str = None
	appName: str = None
	appVersion: str = None
	playData: PlayMessage = None

	def serialize(self):
		res = {
			"displayName": self.displayName,
			"appName": self.appName,
			"appVersion": self.appVersion,
		}
		if pd:=self.playData:
			if t:=type(pd) == PlayMessage:
				res["playData"]: json.loads(self.playData.serialize().decode())
			elif t == dict:
				res["playData"] = pd
		return json.dumps(res).encode(encoding="utf-8")


@dataclass
class PlayUpdateMessage(Message):
	generationTime: float # The time the packet was generated (unix time milliseconds)
	playData: PlayMessage = None

	def serialize(self):
		res = {
			"generationTime": self.generationTime,
			"playData": json.loads(self.playData.serialize().decode())
		}
		return json.dumps(res).encode(encoding="utf-8")
	

@dataclass
class SetPlaylistItemMessage(Message):
	itemIndex: int # The playlist item index to play on receiver

	def serialize(self):
		return json.dumps({"itemIndex": self.itemIndex}).encode(encoding="utf-8")


@dataclass
class PauseMessage(Message):
	...


@dataclass
class StopMessage(Message):
	...


@dataclass
class ResumeMessage(Message):
	...


@dataclass
class PingMessage(Message):
	...


@dataclass
class PongMessage(Message):
	...


@dataclass
class SubscribeEventMessage(Message):
	event: EventSubscribeObject

	def serialize(self) -> bytes:
		return json.dumps({"event": self.event.__dict__}).encode(encoding="utf-8")


@dataclass
class UnsubscribeEvent(SubscribeEventMessage):
	...


@dataclass
class EventMessage(Message):
	generationTime: float # The time the packet was generated (unix time milliseconds)
	event: EventObject

	@property
	def event(self) -> EventObject:
		return self._event
	
	@event.setter
	def event(self, value: dict|EventObject):
		if type(value) == dict:
			from .utils import TypeToEvent
			etype = value["type"]
			E = TypeToEvent[etype]
			self._event = E(**value)
		elif isinstance(value, EventObject):
			self._event = value
		else:
			raise KeyError(f"Invalid value provided for event: {value}")

	def serialize(self) -> bytes:
		res = {
			"generationTime": self.generationTime,
			"event": self.event.json
		}
		return json.dumps(res).encode(encoding="utf-8")