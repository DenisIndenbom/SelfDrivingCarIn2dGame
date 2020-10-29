import ctypes

__all__ = ["enable"]

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


def enable( value: bool = True ):
    flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED if value else 0
    ctypes.windll.kernel32.SetThreadExecutionState( flags )
