from classiq.open_library.functions.utility_functions import apply_to_all
from classiq.qmod.builtins.functions.standard_gates import SWAP, X
from classiq.qmod.builtins.operations import invert, repeat
from classiq.qmod.qfunc import qperm
from classiq.qmod.qmod_variable import QArray, QBit


@qperm
def cyclic_shift_left(reg: QArray[QBit]) -> None:
    """
    Performs a left shift on the quantum register array `reg` using SWAP gates.
    """
    n = reg.size
    repeat(n - 1, lambda i: SWAP(reg[n - i - 1], reg[n - i - 2]))


@qperm
def cyclic_shift_right(reg: QArray[QBit]) -> None:
    """
    Performs a right shift on the quantum register array `reg` by inverting cyclic_shift_left.
    """
    invert(lambda: cyclic_shift_left(reg))


@qperm
def bitwise_negate(x: QArray[QBit]) -> None:
    """
    Negates each bit of the input x.
    """
    apply_to_all(X, x)
