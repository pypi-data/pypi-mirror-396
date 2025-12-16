# devices.py
class DeviceError(Exception):
    pass

# core.py
class EngineError(Exception):
    pass

class XAALError(Exception):
    pass

class CallbackError(Exception):
    def __init__(self, code, desc):
        self.code = code
        self.description = desc

# messages.py
class MessageParserError(Exception):
    pass

class MessageError(Exception):
    pass

# binding.py
class UUIDError(Exception):
    pass

__all__ = [
    'DeviceError',
    'EngineError',
    'XAALError',
    'CallbackError',
    'MessageParserError',
    'MessageError',
    'UUIDError',
]
