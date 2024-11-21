from enum import Enum, auto
from typing import Union, List, TypeVar
from machine import Pin
import utime as time


class BitOrder(Enum):
    """Enum for bit ordering options."""

    MSB_FIRST = auto()
    LSB_FIRST = auto()


# Define a generic number type for the constrain and map_range functions
Number = TypeVar("Number", int, float)


def constrain(x: Number, min_val: Number, max_val: Number) -> Number:
    """
    Constrains a number between a minimum and maximum value.

    Args:
        x: Value to constrain
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Value constrained between min_val and max_val

    Example:
        >>> constrain(15, 0, 10)
        10
        >>> constrain(-5, 0, 10)
        0
        >>> constrain(5, 0, 10)
        5
    """
    return max(min_val, min(x, max_val))


def map_range(
    x: float, in_min: float, in_max: float, out_min: float, out_max: float
) -> float:
    """
    Maps a value from one range to another.

    Args:
        x: Value to map
        in_min: Input range minimum
        in_max: Input range maximum
        out_min: Output range minimum
        out_max: Output range maximum

    Returns:
        Mapped value in the output range

    Example:
        >>> map_range(5, 0, 10, 0, 100)
        50.0
        >>> map_range(512, 0, 1023, 0, 255)
        127.5
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def reverse_bits(value: int, bits: int = 8) -> int:
    """
    Reverses the bits in a value.

    Args:
        value: Integer value to reverse
        bits: Number of bits to consider

    Returns:
        Integer with reversed bits
    """
    result = 0
    for i in range(bits):
        result = (result << 1) | ((value >> i) & 1)
    return result


def bytes_to_bits(values: List[int]) -> List[int]:
    """
    Converts a list of bytes to a list of bits.

    Args:
        values: List of byte values (0-255)

    Returns:
        List of bits (0 or 1)
    """
    bits = []
    for value in values:
        for i in range(8):
            bits.append((value >> (7 - i)) & 1)
    return bits


def bits_to_bytes(
    bits: List[int], bit_order: BitOrder = BitOrder.MSB_FIRST
) -> List[int]:
    """
    Converts a list of bits to bytes.

    Args:
        bits: List of bits (0 or 1)
        bit_order: Bit ordering to use

    Returns:
        List of byte values (0-255)
    """
    # Pad bits to multiple of 8
    while len(bits) % 8:
        bits.append(0)

    bytes_list = []
    for i in range(0, len(bits), 8):
        byte = 0
        byte_bits = bits[i : i + 8]
        if bit_order == BitOrder.LSB_FIRST:
            byte_bits.reverse()
        for bit in byte_bits:
            byte = (byte << 1) | (bit & 1)
        bytes_list.append(byte)
    return bytes_list


def parallel_to_serial(parallel_data: List[int], num_bits: int = 8) -> List[int]:
    """
    Converts parallel data to serial format.

    Args:
        parallel_data: List of parallel input values
        num_bits: Number of bits per value

    Returns:
        List of serial bits
    """
    serial_data = []
    for value in parallel_data:
        for i in range(num_bits):
            serial_data.append((value >> (num_bits - 1 - i)) & 1)
    return serial_data


def shift_out_multiple(
    data_pin: Pin,
    clock_pin: Pin,
    latch_pin: Pin,
    values: List[int],
    bit_order: Union[BitOrder, str] = BitOrder.MSB_FIRST,
) -> None:
    """
    Shifts out multiple bytes of data with latching.

    Args:
        data_pin: Pin object for data output
        clock_pin: Pin object for clock signal
        latch_pin: Pin object for latch signal
        values: List of bytes to shift out
        bit_order: Bit ordering to use
    """
    latch_pin.value(0)
    for value in values:
        shift_out(data_pin, clock_pin, value, bit_order)
    latch_pin.value(1)
    time.sleep_us(1)
    latch_pin.value(0)


def shift_in_multiple(
    data_pin: Pin,
    clock_pin: Pin,
    latch_pin: Pin,
    num_bytes: int,
    bit_order: Union[BitOrder, str] = BitOrder.MSB_FIRST,
) -> List[int]:
    """
    Shifts in multiple bytes of data with latching.

    Args:
        data_pin: Pin object for data input
        clock_pin: Pin object for clock signal
        latch_pin: Pin object for latch signal
        num_bytes: Number of bytes to read
        bit_order: Bit ordering to use

    Returns:
        List of bytes read
    """
    latch_pin.value(1)
    time.sleep_us(1)
    latch_pin.value(0)

    values = []
    for _ in range(num_bytes):
        values.append(shift_in(data_pin, clock_pin, bit_order))
    return values


def debounce(pin: Pin, delay_ms: int = 20) -> bool:
    """
    Debounces a pin input.

    Args:
        pin: Pin object to debounce
        delay_ms: Debounce delay in milliseconds

    Returns:
        Stable pin value
    """
    initial_state = pin.value()
    time.sleep_ms(delay_ms)
    return pin.value() == initial_state


class ShiftRegister:
    """Class to manage a shift register device."""

    def __init__(
        self,
        data_pin: Pin,
        clock_pin: Pin,
        latch_pin: Pin,
        num_bytes: int = 1,
        bit_order: BitOrder = BitOrder.MSB_FIRST,
    ):
        """
        Initialize shift register.

        Args:
            data_pin: Data pin
            clock_pin: Clock pin
            latch_pin: Latch pin
            num_bytes: Number of bytes the register holds
            bit_order: Bit ordering to use
        """
        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.latch_pin = latch_pin
        self.num_bytes = num_bytes
        self.bit_order = bit_order
        self.current_state = [0] * num_bytes

    def write(self, values: List[int]) -> None:
        """Write values to the shift register."""
        if len(values) != self.num_bytes:
            raise ValueError(f"Expected {self.num_bytes} bytes, got {len(values)}")
        self.current_state = values
        shift_out_multiple(
            self.data_pin, self.clock_pin, self.latch_pin, values, self.bit_order
        )

    def read(self) -> List[int]:
        """Read current values from the shift register."""
        return shift_in_multiple(
            self.data_pin,
            self.clock_pin,
            self.latch_pin,
            self.num_bytes,
            self.bit_order,
        )

    def set_bit(self, byte_index: int, bit_index: int, value: bool) -> None:
        """Set a specific bit in the shift register."""
        if not 0 <= byte_index < self.num_bytes:
            raise ValueError(f"Byte index {byte_index} out of range")
        if not 0 <= bit_index < 8:
            raise ValueError(f"Bit index {bit_index} out of range")

        if value:
            self.current_state[byte_index] |= 1 << bit_index
        else:
            self.current_state[byte_index] &= ~(1 << bit_index)

        self.write(self.current_state)


def shift_out(
    data_pin: Pin,
    clock_pin: Pin,
    value: int,
    bit_order: Union[BitOrder, str] = BitOrder.MSB_FIRST,
) -> None:
    """
    Shifts out a byte of data on a data pin with a clock pin.

    Args:
        data_pin: Pin object for data output
        clock_pin: Pin object for clock signal
        value: Byte to shift out (0-255)
        bit_order: BitOrder enum or string ('MSBFIRST' or 'LSBFIRST')
    """
    # Convert string bit order to enum if necessary
    if isinstance(bit_order, str):
        bit_order = (
            BitOrder.MSB_FIRST if bit_order == "MSBFIRST" else BitOrder.LSB_FIRST
        )

    # Ensure value is in valid range
    value = max(0, min(value, 255))

    def pulse_clock():
        """Helper function to generate clock pulse."""
        clock_pin.value(1)
        time.sleep_us(1)
        clock_pin.value(0)
        time.sleep_us(1)

    for i in range(8):
        if bit_order == BitOrder.MSB_FIRST:
            bit = (value >> (7 - i)) & 1
        else:
            bit = (value >> i) & 1

        data_pin.value(bit)
        pulse_clock()


def shift_in(
    data_pin: Pin, clock_pin: Pin, bit_order: Union[BitOrder, str] = BitOrder.MSB_FIRST
) -> int:
    """
    Shifts in a byte of data using a data pin and clock pin.

    Args:
        data_pin: Pin object for data input
        clock_pin: Pin object for clock signal
        bit_order: BitOrder enum or string ('MSBFIRST' or 'LSBFIRST')

    Returns:
        Integer (0-255) read from the data pin
    """
    # Convert string bit order to enum if necessary
    if isinstance(bit_order, str):
        bit_order = (
            BitOrder.MSB_FIRST if bit_order == "MSBFIRST" else BitOrder.LSB_FIRST
        )

    def read_bit() -> int:
        """Helper function to read a bit with proper timing."""
        clock_pin.value(1)
        time.sleep_us(1)
        bit = data_pin.value()
        clock_pin.value(0)
        time.sleep_us(1)
        return bit

    value = 0
    for i in range(8):
        bit = read_bit()
        if bit_order == BitOrder.MSB_FIRST:
            value = (value << 1) | bit
        else:
            value |= bit << i

    return value
