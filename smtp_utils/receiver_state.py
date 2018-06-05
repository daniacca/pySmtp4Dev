import enum


class SmtpReceiverState(enum.Enum):
    INIT = 0
    READY = 1
    RUNNING = 2
    STOPPED = 3