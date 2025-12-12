from classiq.open_library.functions.qft_functions import qft_no_swap
from classiq.qmod.builtins.classical_functions import qft_const_adder_phase
from classiq.qmod.builtins.functions.allocation import free
from classiq.qmod.builtins.functions.standard_gates import PHASE, X
from classiq.qmod.builtins.operations import (
    allocate,
    control,
    invert,
    repeat,
    skip_control,
    within_apply,
)
from classiq.qmod.cparam import CInt
from classiq.qmod.qfunc import qfunc, qperm
from classiq.qmod.qmod_variable import QArray, QBit


@qfunc
def _check_msb(ref: CInt, x: QArray[QBit], aux: QBit) -> None:
    within_apply(
        lambda: invert(lambda: qft_no_swap(x)),
        lambda: control(x[0] == ref, lambda: X(aux)),
    )


@qfunc
def qft_space_add_const(value: CInt, phi_b: QArray[QBit]) -> None:
    """
    [Qmod Classiq-library function]

    Adds a constant to a quantum number (in the Fourier space) using the Quantum Fourier Transform (QFT) Adder algorithm.
    Assuming that the input `phi_b` has `n` qubits, the result will be $\\phi_b+=value \\mod 2^n$.

    To perform the full algorithm, use:
    within_apply(lambda: QFT(phi_b), qft_space_add_const(value, phi_b))

    Args:
        value: The constant to add to the quantum number.
        phi_b: The quantum number (at the aft space) to which the constant is added.

    """
    repeat(
        count=phi_b.len,
        iteration=lambda index: PHASE(
            theta=qft_const_adder_phase(
                index, value, phi_b.len  # type:ignore[arg-type]
            ),
            target=phi_b[index],
        ),
    )


@qperm(disable_perm_check=True)
def modular_add_qft_space(n: CInt, a: CInt, phi_b: QArray[QBit]) -> None:
    """
    [Qmod Classiq-library function]

    Adds a constant `a` to a quantum number `phi_b` modulo the constant `n`.
    The quantum number `phi_b` is assumed to be in the QFT space.

    Args:
        n: The modulo number.
        a: The constant to add to the quantum number.
        phi_b: The quantum number to which the constant is added.

    """
    aux = QBit()

    allocate(aux)
    qft_space_add_const(a, phi_b),
    skip_control(
        lambda: (
            invert(lambda: qft_space_add_const(n, phi_b)),
            _check_msb(1, phi_b, aux),
            control(aux, lambda: qft_space_add_const(n, phi_b)),
        )
    )
    invert(lambda: qft_space_add_const(a, phi_b))
    skip_control(lambda: _check_msb(0, phi_b, aux))
    qft_space_add_const(a, phi_b)
    free(aux)
