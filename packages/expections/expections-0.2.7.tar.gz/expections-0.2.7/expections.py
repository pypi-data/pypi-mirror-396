def ExceptionErr(message):
    raise Exception(message)

def NameErr(message):
    raise NameError(message)

def KeyErr(message):
    raise KeyError(message)

def OSErr(message):
    raise OSError(message)

def ArithmeticErr(message):
    raise ArithmeticError(message)

def OverflowErr(message):
    raise OverflowError(message)

def ZeroDivisionErr(message):
    raise ZeroDivisionError(message)

def FloatingPointErr(message):
    raise FloatingPointError(message)

def AssertionErr(message):
    raise AssertionError(message)

def AttributeErr(message):
    raise AttributeError(message)

def BufferErr(message):
    raise BufferError(message)

def EOFErr(message):
    raise EOFError(message)

def ImportErr(message):
    raise ImportError(message)

def ModuleNotFoundErr(message):
    raise ModuleNotFoundError(message)

def LookupErr(message):
    raise LookupError(message)

def IndexErr(message):
    raise IndexError(message)

def MemoryErr(message):
    raise MemoryError(message)

def NotImplementedErr(message):
    raise NotImplementedError(message)

def BlockingIOErr(message):
    raise BlockingIOError(message)

def BrokenPipeErr(message):
    raise BrokenPipeError(message)

def ChildProcessErr(message):
    raise ChildProcessError(message)

def ConnectionErr(message):
    raise ConnectionError(message)

def ConnectionAbortedErr(message):
    raise ConnectionAbortedError(message)

def ConnectionRefusedErr(message):
    raise ConnectionRefusedError(message)

def ConnectionResetErr(message):
    raise ConnectionResetError(message)

def FileExistsErr(message):
    raise FileExistsError(message)

def FileNotFoundErr(message):
    raise FileNotFoundError(message)

def InterruptedErr(message):
    raise InterruptedError(message)

def IsADirectoryErr(message):
    raise IsADirectoryError(message)

def NotADirectoryErr(message):
    raise NotADirectoryError(message)

def PermissionErr(message):
    raise PermissionError(message)

def ProcessLookupErr(message):
    raise ProcessLookupError(message)

def TimeoutErr(message):
    raise TimeoutError(message)

def RecursionErr(message):
    raise RecursionError(message)

def StopIterationErr(message):
    raise StopIteration(message)

def StopAsyncIterationErr(message):
    raise StopAsyncIteration(message)

def SyntaxErr(message):
    raise SyntaxError(message)

def IndentationErr(message):
    raise IndentationError(message)

def TabErr(message):
    raise TabError(message)

def SystemErr(message):
    raise SystemError(message)

def TypeErr(message):
    raise TypeError(message)

def ValueErr(message):
    raise ValueError(message)

def WarningErr(message):
    raise Warning(message)

def GeneratorExitErr(message):
    raise GeneratorExit(message)

def KeyboardInterruptErr(message):
    raise KeyboardInterrupt(message)

def SystemExitErr(message):
    raise SystemExit(message)

def help():
    print("For futher information about error's - check the official documentation, and add to every error without Error, add Err in end, or if it has it, then just delete or in end of Error.")