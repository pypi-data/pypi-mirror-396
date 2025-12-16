from typing import List
from pydantic import BaseModel, Field


class VoiceConfig(BaseModel):
    voice_id: str = Field(..., description="Unique voice identifier")
    path: str = Field(..., description="Path to the prompt audio file")


class VocoderConfig(BaseModel):
    name: str
    type: str
    dtype: str = "float"


class Token2AudioRequest(BaseModel):
    voice_id: str = Field(..., description="Voice ID to use for synthesis")
    tokens: List[int] = Field(..., description="List of audio tokens to synthesize")


class UpdateEnvRequest(BaseModel):
    envs: dict = Field(..., description="Environment variables to update")


class WSCreateTTSData(BaseModel):
    voice_id: str = Field(..., description="Voice ID to use for synthesis")


class WSResponseCreatedData(BaseModel):
    id: str
    object: str = "response.created"


class WSResponseAudioDeltaData(BaseModel):
    response_id: str
    object: str = "response.audio.delta"
    status: str = Field(..., description="Status: unfinished or finished")
    audio: str = Field(..., description="Base64 encoded audio data")
    audio_tokens: List[int] = Field(default=[], description="Audio tokens")
    duration: float = Field(..., description="Audio duration in seconds")
    inference_time: float = Field(
        default=0.0, description="Inference time in milliseconds"
    )


class WSResponseAudioFlushData(BaseModel):
    response_id: str
    object: str = "response.audio.flush"
    audio: str = Field(default="", description="Base64 encoded audio data")
    audio_tokens: str = Field(default="", description="Audio tokens")


class WSResponseAudioDoneData(BaseModel):
    response_id: str
    object: str = "response.audio.done"
    audio: str = Field(default="", description="Base64 encoded audio data")
    audio_tokens: str = Field(default="", description="Audio tokens")


class WSErrorData(BaseModel):
    response_id: str
    object: str = "response.error"
    code: str
    message: str
    details: dict


class WSTokenDeltaData(BaseModel):
    tokens: List[int] = Field(..., description="List of audio tokens to synthesize")


class WSRequest(BaseModel):
    event_id: str
    type: str
    data: dict


class WSEventType:
    TOKEN2AUDIO_CREATE = "token2audio.create"
    TOKEN2AUDIO_DELTA = "token2audio.delta"
    TOKEN2AUDIO_FLUSH = "token2audio.flush"
    TOKEN2AUDIO_DONE = "token2audio.done"
    RESPONSE_CREATED = "response.created"
    RESPONSE_AUDIO_DELTA = "response.audio.delta"
    RESPONSE_AUDIO_FLUSH = "response.audio.flush"
    RESPONSE_AUDIO_DONE = "response.audio.done"
    RESPONSE_ERROR = "response.error"


class WSResponseCreatedEvent(BaseModel):
    event_id: str
    type: str = WSEventType.RESPONSE_CREATED
    data: WSResponseCreatedData


class WSResponseAudioDeltaEvent(BaseModel):
    event_id: str
    type: str = WSEventType.RESPONSE_AUDIO_DELTA
    data: WSResponseAudioDeltaData


class WSResponseAudioFlushEvent(BaseModel):
    event_id: str
    type: str = WSEventType.RESPONSE_AUDIO_FLUSH
    data: WSResponseAudioFlushData


class WSResponseAudioDoneEvent(BaseModel):
    event_id: str
    type: str = WSEventType.RESPONSE_AUDIO_DONE
    data: WSResponseAudioDoneData


class WSErrorEvent(BaseModel):
    event_id: str
    type: str = WSEventType.RESPONSE_ERROR
    data: WSErrorData


# 请求事件结构
class WSCreateTTSRequest(BaseModel):
    event_id: str
    type: str = WSEventType.TOKEN2AUDIO_CREATE
    data: WSCreateTTSData


class WSTokenDeltaRequest(BaseModel):
    event_id: str
    type: str = WSEventType.TOKEN2AUDIO_DELTA
    data: WSTokenDeltaData


class WSTokenFlushRequest(BaseModel):
    event_id: str
    type: str = WSEventType.TOKEN2AUDIO_FLUSH
    data: dict = Field(default_factory=dict)


class WSTokenDoneRequest(BaseModel):
    event_id: str
    type: str = WSEventType.TOKEN2AUDIO_DONE
    data: dict = Field(default_factory=dict)


