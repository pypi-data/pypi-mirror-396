from .opcode import Opcode
from .message import *
from .event_type import EventType
from .event import *


OpcodeToMessage = {
    Opcode.play: PlayMessage,
    Opcode.pause: PauseMessage,
    Opcode.resume: ResumeMessage,
    Opcode.stop: StopMessage,
    Opcode.seek: SeekMessage,
    Opcode.playback_update: PlaybackUpdateMessage,
    Opcode.volume_update: VolumeUpdateMessage,
    Opcode.set_volume: SetVolumeMessage,
    Opcode.playback_error: PlaybackErrorMessage,
    Opcode.set_speed: SetSpeedMessage,
	Opcode.version: VersionMessage,
    Opcode.ping: PingMessage,
    Opcode.pong: PongMessage,
	Opcode.initial: InitialMessage,
    Opcode.play_update: PlayUpdateMessage,
    Opcode.set_playlist_item: SetPlaylistItemMessage,
    Opcode.subscribe_event: SubscribeEventMessage,
    Opcode.unsubscribe_event: UnsubscribeEvent,
    Opcode.event: EventMessage
}

MessageToOpcode = {v:k for k,v in OpcodeToMessage.items()}


TypeToEventSub = {
    EventType.MediaItemStart: MediaItemStart,
    EventType.MediaItemEnd: MediaItemEnd,
    EventType.MediaItemChange: MediaItemChange,
    EventType.KeyDown: KeyDown,
    EventType.KeyUp: KeyUp
}

EventSubToType = {v:k for k,v in TypeToEventSub.items()}

#Leap of faith
TypeToEvent = {
    EventType.MediaItemStart: MediaItemEvent,
    EventType.MediaItemEnd: MediaItemEvent,
    EventType.MediaItemChange: MediaItemEvent,
    EventType.KeyDown: KeyEvent,
    EventType.KeyUp: KeyEvent,
}