import ctypes

class IndexDataConnectorClass(ctypes.c_void_p):
    # subclassing c_void_p creates an opaque pointer type that is distinct
    # from c_void_p, and can only be instantiated as a pointer
    pass

class ResultTypeConnectorClass(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("text", ctypes.c_char_p),
        ("score", ctypes.c_float),
    ]

class ResultsTypeConnectorClass(ctypes.Structure):
    # subclassing c_void_p creates an opaque pointer type that is distinct
    # from c_void_p, and can only be instantiated as a pointer
    _fields_ = [
        ("num_results", ctypes.c_int),
        ("results", ctypes.POINTER(ResultTypeConnectorClass)),
    ]