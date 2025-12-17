from typing import TypeAlias

FuncName: TypeAlias = str
LineNo: TypeAlias = int
ExceptionName: TypeAlias = str
ExceptionSet: TypeAlias = set[ExceptionName]
RaisingFunctionsLineno: TypeAlias = dict[FuncName, LineNo]
FunctionExceptionsMap: TypeAlias = dict[FuncName, ExceptionSet]
CallGraph: TypeAlias = dict[FuncName, list[tuple[LineNo, FuncName]]]
ExplicitRaises: TypeAlias = dict[FuncName, list[tuple[LineNo, ExceptionName]]]
ExceptionPropagationMap: TypeAlias = dict[FuncName, ExceptionSet]
