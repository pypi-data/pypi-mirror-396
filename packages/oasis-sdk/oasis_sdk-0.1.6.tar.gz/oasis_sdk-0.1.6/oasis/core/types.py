from enum import StrEnum


class ProviderCode(StrEnum):
    """Provider code enum as defined in the database"""
    OPENAI = "OPENAI"
    AOAI = "AOAI"
    ANTHROPIC = "ANTHROPIC"
    GOOGLE = "GOOGLE"
    OASIS = "OASIS"
    XAI = "XAI"


class ProviderType(StrEnum):
    """Provider type enum as defined in the database"""
    PUBLIC = "PUBLIC"
    DEDICATED = "DEDICATED"
    PRIVATE = "PRIVATE"


class ModelType(StrEnum):
    """Model type enum as defined in the database"""
    CHAT = "CHAT"
    EMBEDDING = "EMBEDDING"
    IMG_GEN = "IMG_GEN"
    IMG_EDIT = "IMG_EDIT"
    STT = "STT"
    TTS = "TTS"
    CODE = "CODE"
    CHAT_VISION = "CHAT_VISION"