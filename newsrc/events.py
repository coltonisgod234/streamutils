import enum

class events(enum.Enum):
    TERMINATE = "TERMINATE;"
    STRINGEDMESSAGE = "MESSAGE;"
    PICKLEDMESSAGE = "MESSAGESERIAL;"
    NULLEVENT = ""
    