from enum import StrEnum


class SystemType(StrEnum):
    CRM = "crm"
    LOGIS = "logis"


class TelegramHubChatMessageErrorType(StrEnum):
    NO_RECIPIENT = "NO_RECIPIENT"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    MEMBER_NOT_FOUND = "MEMBER_NOT_FOUND"
    BOT_WAS_BLOCKED = "BOT_WAS_BLOCKED"
