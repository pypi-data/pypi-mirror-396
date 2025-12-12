import warnings

from classiq.interface.exceptions import ClassiqDeprecationWarning

from classiq.open_library.functions.bit_operations import (
    bitwise_negate,
    cyclic_shift_left,
)
from classiq.open_library.functions.qft_functions import qft
from classiq.open_library.functions.qft_space_arithmetics import modular_add_qft_space
from classiq.open_library.functions.utility_functions import multiswap
from classiq.qmod.builtins.constants import SIGNED
from classiq.qmod.builtins.functions.allocation import free
from classiq.qmod.builtins.functions.standard_gates import X
from classiq.qmod.builtins.operations import (
    allocate,
    bind,
    control,
    if_,
    inplace_add,
    inplace_xor,
    invert,
    repeat,
    within_apply,
)
from classiq.qmod.cparam import CInt
from classiq.qmod.qfunc import qperm
from classiq.qmod.qmod_variable import Const, Output, QArray, QBit, QNum
from classiq.qmod.symbolic import mod_inverse

# Modular Adding and Subtraction


@qperm
def modular_add_inplace(modulus: CInt, x: Const[QNum], y: QNum) -> None:
    """
    [Qmod Classiq-library function]

    Performs the transformation |x>|y> -> |x>|(x + y mod modulus)>.
    Note:
    |x> and |y> should have values smaller than `modulus`.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x> and |y>.

    Implementation based on: https://arxiv.org/pdf/1706.06752 Chapter 3.2 Fig 3

    Args:
        modulus: Classical number modulus (CInt)
        x: 1st quantum number input (unsigned).
        y: 2nd quantum number input (unsigned). Will hold the result after the operation.
    """
    # Use a carry qubit to detect a negative result after subtracting modulus (underflow)
    carry = QBit()
    allocate(carry)
    temp: QNum = QNum("temp", y.size + 1, SIGNED, 0)
    within_apply(
        lambda: bind([y, carry], temp),
        lambda: (
            inplace_add(x, temp),
            inplace_add(-modulus, temp),
        ),
    )
    # If carry is set (negative result), add modulus back to y
    control(carry, lambda: inplace_add(modulus, y))
    # Update carry qubit based on comparison (y >= x after operation)
    carry ^= y >= x
    free(carry)


@qperm
def modular_negate_inplace(modulus: CInt, x: QNum) -> None:
    """
    [Qmod Classiq-library function]

    Performs the transformation |x> -> |(-x mod modulus)>.
    Note:
    |x> should have values smaller than `modulus`.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x>.

    Args:
        modulus: Classical number modulus
        x: Quantum number input (unsigned). Will hold the result after the operation.
    """
    n = x.size
    neg_modulus = 2**n - modulus - 1
    is_all_zeros = QBit()
    allocate(is_all_zeros)
    is_all_zeros ^= x == 0
    control(is_all_zeros, lambda: inplace_add(modulus, x))
    inplace_add(neg_modulus, x)
    # If x=0, then we have neg_modulus + modulus = all ones
    is_all_zeros ^= x == (2**n - 1)
    bitwise_negate(x)
    free(is_all_zeros)


@qperm
def modular_subtract_inplace(modulus: CInt, x: Const[QNum], y: QNum) -> None:
    """
    [Qmod Classiq-library function]

    Performs the transformation |x>|y> -> |x>|(x - y mod modulus)>.
    Note:
    |x> and |y> should have values smaller than `modulus`.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x> and |y>.

    Args:
        modulus: Classical number modulus
        x: 1st quantum number input (unsigned). Const.
        y: 2nd quantum number input (unsigned). In-place target, will hold the result after the operation.
    """
    modular_negate_inplace(modulus, y)
    modular_add_inplace(modulus, x, y)


@qperm
def modular_double_inplace(modulus: CInt, x: QNum) -> None:
    """
    [Qmod Classiq-library function]

    Performs the transformation |x> -> |(2x mod modulus)>.
    Note:
    |x> should have a value smaller than `modulus`.
    The modulus must be a constant odd integer.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x>.

    Implementation based on: https://arxiv.org/pdf/1706.06752 Chapter 3.2 Fig 4

    Args:
        modulus: Classical number modulus
        x: Quantum number input (unsigned). Will hold the result after the operation.
    """
    carry = QBit()
    allocate(carry)
    res_and_carry: QNum = QNum("res_and_carry", x.size + 1, SIGNED, 0)
    within_apply(
        lambda: bind([x, carry], res_and_carry),
        lambda: (
            cyclic_shift_left(res_and_carry),  # holds 2*x
            inplace_add(-modulus, res_and_carry),
        ),
    )
    control(carry, lambda: inplace_add(modulus, x))
    # Post-fix carry
    carry ^= (x % 2) == 0
    free(carry)


@qperm
def modular_add_constant_inplace(modulus: CInt, a: CInt, x: QNum) -> None:
    """
    [Qmod Classiq-library function]

    Performs the transformation |x> -> |(x + a mod modulus)>.
    Note:
    |x> and `a` should have values smaller than `modulus`.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x>.

    Implementation is based on the logic in: https://arxiv.org/pdf/1706.06752 Chapter 3.2 Fig 3

    Args:
        modulus: Classical number modulus
        a: constant unsigned number input for the addition.
        x: Quantum number input (unsigned). Will hold the result after the operation.
    """
    carry = QBit()
    allocate(carry)
    temp: QNum = QNum("temp", x.size + 1, SIGNED, 0)
    within_apply(
        lambda: bind([x, carry], temp),
        lambda: (
            inplace_add(a, temp),
            inplace_add(-modulus, temp),
        ),
    )
    # If carry is set, we need to add modulus back
    control(carry, lambda: inplace_add(modulus, x))
    carry ^= x >= a
    free(carry)


# Modular Multiplication


@qperm
def modular_multiply(
    modulus: CInt,
    x: Const[QArray[QBit]],
    y: Const[QArray[QBit]],
    z: QArray[QBit],
) -> None:
    """
    [Qmod Classiq-library function]
    Performs the transformation |x>|y>|0> -> |x>|y>|(x*y mod modulus)>
    Note:
    |x>, |y> should have the same size and have values smaller than `modulus`.
    The modulus must be a constant odd integer.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x> and |y>.
    The output register z must be pre-allocated with the same size as x and y.
    Implementation is based on the logic in: https://arxiv.org/pdf/1706.06752 Chapter 3.2 Fig 5
    Args:
        modulus: Classical number modulus
        x: Quantum number input (unsigned), multiplicand.
        y: Quantum number input (unsigned), multiplier.
        z: Quantum number (unsigned), pre-allocated output variable that will hold the result.
    """
    n = x.len
    repeat(
        n,
        lambda idx: [
            control(x[n - idx - 1], lambda: modular_add_inplace(modulus, y, z)),
            if_(idx != (n - 1), lambda: modular_double_inplace(modulus, z)),
        ],
    )


@qperm
def modular_square(modulus: CInt, x: Const[QArray[QBit]], z: QArray[QBit]) -> None:
    """
    [Qmod Classiq-library function]
    Performs the transformation |x>|0> -> |x>|(x^2 mod modulus)>.
    Note:
    |x> should have the same size and have values smaller than `modulus`.
    The modulus must be a constant odd integer.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x>.
    The output register z must be pre-allocated with the same size as x.
    Implementation is based on: https://arxiv.org/pdf/1706.06752 Chapter 3.2 Fig 6
    Args:
        modulus: Classical number modulus
        x: Quantum number input (unsigned), the input to square.
        z: Quantum number (unsigned), pre-allocated output variable to hold the result.
    """
    n = x.len
    repeat(
        n - 1,
        lambda i: [
            control(x[n - i - 1], lambda: modular_add_inplace(modulus, x, z)),
            modular_double_inplace(modulus, z),
        ],
    )
    control(x[0], lambda: modular_add_inplace(modulus, x, z))


@qperm(disable_perm_check=True)
def modular_multiply_constant(modulus: CInt, x: Const[QNum], a: CInt, y: QNum) -> None:
    """
    [Qmod Classiq-library function]
    Performs the transformation |x>|y> -> |x>|(x * a mod modulus)>.
    Note:
    |x> and |y> should have values smaller than `modulus`.
    The modulus must be a constant odd integer.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x> and |y>.

    Args:
        modulus: Classical number modulus
        x: Quantum number (unsigned), input variable.
        a: Classical number constant
        y: Quantum number (unsigned), output variable that will hold the result.
    """
    x_arr: QArray[QBit] = QArray()
    within_apply(
        lambda: [bind(x, x_arr), qft(y)],
        lambda: repeat(
            count=x_arr.len,
            iteration=lambda index: control(
                x_arr[index],
                lambda: modular_add_qft_space(modulus, (a * (2**index)) % modulus, y),
            ),
        ),
    )


@qperm
def modular_multiply_constant_inplace(modulus: CInt, a: CInt, x: QNum) -> None:
    """
    [Qmod Classiq-library function]
    In-place modular multiplication of x by a classical constant modulo a symbolic modulus.
    Performs |x> -> |(x * a mod modulus)>.
    Note:
    |x> should have values smaller than `modulus`.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x>.
    The constant `a` should have an inverse modulo `modulus`, i.e. gcd(a, modulus) = 1.
    The constant `a` should satisfy 0 <= a < modulus.

    Args:
        modulus: Classical number modulus
        a: Classical number constant
        x: Quantum number (unsigned), in-place input/output.
    """
    y: QNum = QNum("y", x.size + 1)
    allocate(y)
    modular_multiply_constant(modulus, x, a, y)
    multiswap(x, y)
    invert(lambda: modular_multiply_constant(modulus, x, mod_inverse(a, modulus), y))
    free(y)


@qperm
def inplace_modular_multiply(n: CInt, a: CInt, x: QArray[QBit]) -> None:
    """
    [Qmod Classiq-library function]

    Performs multiplication of a quantum number `x` by a classical number `a` modulo classical number `n`
    (Applies $x=xa \\mod n$).

    Args:
        n: The modulo number. Should be non-negative.
        a: The classical factor. Should be non-negative.
        x: The quantum factor.

    Comment: It is assumed that `a` has an inverse modulo `n`
    """
    warnings.warn(
        "Function 'inplace_modular_multiply' is deprecated. Use 'modular_multiply_constant_inplace' instead.",
        ClassiqDeprecationWarning,
        stacklevel=1,
    )
    modular_multiply_constant_inplace(n, a, x)


@qperm
def modular_exp(n: CInt, a: CInt, x: QArray[QBit], power: QArray[QBit]) -> None:
    """
    [Qmod Classiq-library function]
    Raises a classical integer `a` to the power of a quantum number `power` modulo classical integer `n`
    times a quantum number `x`. Performs $x=(a^{power} \\mod n)*x$ in-place.
    (and specifically if at the input $x=1$, at the output $x=a^{power} \\mod n$).
    Args:
        n: The modulus number. Should be non-negative.
        a: The base of the exponentiation. Should be non-negative.
        x: A quantum number that multiplies the modular exponentiation and holds the output. It should be at least the size of $\\lceil \\log(n) \rceil$.
        power: The power of the exponentiation.
    """
    warnings.warn(
        "Function 'modular_exp' is deprecated. Use 'modular_exponentiate_inplace' instead.",
        ClassiqDeprecationWarning,
        stacklevel=1,
    )
    repeat(
        count=power.len,
        iteration=lambda index: control(
            power[index],
            lambda: modular_multiply_constant_inplace(n, (a ** (2**index)) % n, x),
        ),
    )


@qperm
def modular_exponentiate_inplace(modulus: CInt, a: CInt, x: QNum, p: QNum) -> None:
    """
    [Qmod Classiq-library function]

    Raises a classical integer `a` to the power of a quantum number `p` modulo classical integer `modulus`
    times a quantum number `x`. Performs $x=(a^{p} \\mod modulus)*x$ in-place.
    (and specifically if at the input $x=1$, at the output $x=a^{p} \\mod modulus$).

    Args:
        modulus: The modulus number. Should be non-negative.
        a: The base of the exponentiation. Should be non-negative.
        x: A quantum number that multiplies the modular exponentiation and holds the output. It should be at least the size of $\\lceil \\log(modulus) \rceil$.
        p: The power of the exponentiation.
    """
    p_arr: QArray[QBit] = QArray(length=p.size)
    within_apply(
        lambda: bind(p, p_arr),
        lambda: repeat(
            count=p_arr.len,
            iteration=lambda index: control(
                p_arr[index],
                lambda: modular_multiply_constant_inplace(
                    modulus, (a ** (2**index)) % modulus, x
                ),
            ),
        ),
    )


# Helper Functions


def get_bit(number: int, index: int) -> int:
    """
    Returns the value (0 or 1) of the bit at the specified index in a non-negative integer number.
    Index 0 is the least significant bit (LSB).
    """
    return (number >> index) & 1


# Montgomery representation


@qperm
def modular_to_montgomery_inplace(modulus: CInt, x: QNum) -> None:
    """
    [Qmod Classiq-library function]
    Converts a quantum integer |x> into its Montgomery representation modulo modulus in place.
    The Montgomery factor is R = 2**n, where n = x.size (the number of qubits in |x>).
    This function performs the transformation |x> -> |(x * R mod modulus)>.
    Note:
    |x> should have values smaller than `modulus`.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x>.
    The modulus must be odd so that R = 2**n is invertible modulo modulus (gcd(R, modulus) = 1).

    Args:
        modulus: Classical number modulus
        x: Quantum number, in-place operand to convert to Montgomery form.
    """
    n = x.size
    mont_factor = 2**n % modulus
    modular_multiply_constant_inplace(modulus, mont_factor, x)


@qperm
def modular_montgomery_to_standard_inplace(modulus: CInt, x: QNum) -> None:
    """
    [Qmod Classiq-library function]
    Converts quantum integer |x> from Montgomery representation to standard form in place modulo modulus.
    The Montgomery factor is R = 2**n, where n = x.size (the number of qubits in |x>).
    This function performs the transformation |x> -> |(x * R^-1 mod modulus)>.
    Note:
    |x> should have values smaller than `modulus`.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x>.
    The modulus must be odd so that R = 2**n is invertible modulo modulus (gcd(R, modulus) = 1).

    Args:
        modulus: Classical number modulus
        x: Quantum number, in-place operand to convert from Montgomery form.
    """
    n = x.size
    modular_multiply_constant_inplace(modulus, mod_inverse(2**n % modulus, modulus), x)


# Modular Inverse


@qperm
def modular_inverse_inplace(modulus: CInt, v: QNum, m: Output[QArray[QBit]]) -> None:
    """
    [Qmod Classiq-library function]
    Computes the modular inverse of a quantum number |v> modulo modulus in place, using the Kaliski algorithm.
    Performs the transformation |v> -> |(v^-1 mod modulus)>.

    Based on: https://arxiv.org/pdf/2302.06639 Chapter 5

    Note:
    |v> should have values smaller than `modulus`.
    If |v> = 0, the output will be 0 (although 0 does not have an inverse modulo `modulus`).
    The modulus should be prime OR at least gcd(v, modulus) = 1.
    The modulus must be a constant odd integer.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |v>.
    The ancilla qubits m are provided as Output, will be allocated to length 2*n.

    Args:
        modulus: Classical number modulus
        v: Quantum number, in-place operand to compute the modular inverse.
        m: Output quantum array (QArray[QBit]) allocated to length 2*n (n = v.size) and used as ancilla during the algorithm.
    """
    n = v.size
    allocate(2 * n, m)
    # Convert v to Montgomery form
    modular_to_montgomery_inplace(modulus, v)
    u: QNum = QNum("u", n)
    r: QNum = QNum("r", n + 1)
    s: QNum = QNum("s", n + 1)
    a: QBit = QBit()
    b: QBit = QBit()
    f: QBit = QBit()
    allocate(u)
    allocate(r)
    allocate(s)
    allocate(a)
    allocate(b)
    allocate(f)
    # Initialize
    u ^= modulus
    r ^= 0
    s ^= 1
    f ^= 1
    # Main loop (2*n iterations)
    repeat(2 * n, lambda i: kaliski_iteration(modulus, i, v, m, u, r, s, a, b, f))
    # Finalization steps
    modular_rsub_inplace(2 * modulus, modulus, r)
    multiswap(v, r)
    m_num: QNum = QNum("m_num", 2 * n)
    bind(m, m_num)
    control(
        m_num == 1,
        stmt_block=lambda: [inplace_xor(1, s), inplace_xor(modulus, u)],  # type: ignore[arg-type]
        else_block=lambda: [inplace_xor(1, u), inplace_xor(modulus, s)],  # type: ignore[arg-type]
    )
    bind(m_num, m)
    modular_montgomery_to_standard_inplace(modulus, v)
    # Free variables
    free(u)
    free(r)
    free(s)
    free(a)
    free(b)
    free(f)


@qperm
def kaliski_iteration(
    modulus: CInt,
    i: CInt,
    v: QNum,
    m: QArray[QBit],
    u: QNum,
    r: QNum,
    s: QNum,
    a: QBit,
    b: QBit,
    f: QBit,
) -> None:
    """
    Single iteration of the Kaliski modular inverse algorithm main loop.
    Based on: https://arxiv.org/pdf/2302.06639 Figure 15

    Note:
    Assumes the global inversion constraints (odd modulus, 1 < modulus < 2**n).
    Called with 0 <= v < modulus; per-iteration ancilla bit is m[i].

    Args:
        modulus: Classical number modulus (CInt)
        i: Loop iteration index.
        v: The QNum to invert (quantum number, will be mutated).
        m: Quantum array of ancilla qubits (QArray[QBit]).
        u: QNum (quantum number, auxiliary for algorithm).
        r: QNum (quantum number, auxiliary).
        s: QNum (quantum number, auxiliary).
        a: QBit (ancilla qubit)
        b: QBit (ancilla qubit)
        f: QBit (ancilla qubit)
    """
    # Step 1: Update f, m[i]
    control((v == 0) & f, lambda: X(m[i]))
    f ^= m[i]
    # Step 2: Update a, b, m[i]
    control(f & ((u % 2) == 0), lambda: X(a))
    control(f & ~a & ((v % 2) == 0), lambda: X(m[i]))
    b ^= a
    b ^= m[i]
    # Step 3: Update a, m[i]
    control(
        (u > v) & f & ~b,
        lambda: (
            X(a),
            X(m[i]),
        ),
    )
    # Step 4: Update u, v, r, s
    control(
        a,
        lambda: (
            multiswap(u, v),
            multiswap(r, s),
        ),
    )
    # Step 5: Update u, v, r, s
    control(f & ~b, lambda: (inplace_add(-u, v), inplace_add(r, s)))
    # Step 6: Update a, b, v, r
    b ^= m[i]
    b ^= a
    control(f, lambda: invert(lambda: cyclic_shift_left(v)))
    modular_double_inplace(2 * modulus, r)
    larger_than_modulus = QBit()
    allocate(larger_than_modulus)
    larger_than_modulus ^= r > modulus
    control(larger_than_modulus, lambda: inplace_add(-modulus, r))
    control(((r % 2) == 1), lambda: X(larger_than_modulus))
    free(larger_than_modulus)
    control(
        a,
        lambda: (
            multiswap(u, v),
            multiswap(r, s),
        ),
    )
    control(((s % 2) == 0), lambda: X(a))


@qperm
def modular_rsub_inplace(modulus: CInt, a: CInt, x: QNum) -> None:
    """
    [Qmod Classiq-library function]
    Performs the in-place modular right-subtraction |x> -> |(a - x mod modulus)>.
    Note:
    |x> should have values smaller than `modulus`.
    The modulus should satisfy 1 < modulus < 2**n, where n is the size of |x>.
    The classical constant `a` should be in the range 0 <= a < modulus.

    Args:
        modulus: Classical number modulus
        a: Classical constant to subtract from
        x: Quantum number, in-place operand to perform the modular right-subtraction.
    """
    modular_negate_inplace(modulus, x)
    modular_add_constant_inplace(modulus, a, x)
