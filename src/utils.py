from machine import Pin
import utime as time

# Constants to replace enum
MSB_FIRST = 0
LSB_FIRST = 1

def constrain(x, min_val, max_val):
    """
    Constrains a number between a minimum and maximum value.
    """
    return max(min_val, min(x, max_val))

def map_range(x, in_min, in_max, out_min, out_max):
    """
    Maps a value from one range to another.
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def reverse_bits(value, bits=8):
    """
    Reverses the bits in a value.
    """
    result = 0
    for i in range(bits):
        result = (result << 1) | ((value >> i) & 1)
    return result

def bytes_to_bits(values):
    """
    Converts a list of bytes to a list of bits.
    """
    bits = []
    for value in values:
        for i in range(8):
            bits.append((value >> (7 - i)) & 1)
    return bits

def bits_to_bytes(bits, bit_order=MSB_FIRST):
    """
    Converts a list of bits to bytes.
    """
    while len(bits) % 8:
        bits.append(0)

    bytes_list = []
    for i in range(0, len(bits), 8):
        byte = 0
        byte_bits = bits[i:i + 8]
        if bit_order == LSB_FIRST:
            byte_bits.reverse()
        for bit in byte_bits:
            byte = (byte << 1) | (bit & 1)
        bytes_list.append(byte)
    return bytes_list

def parallel_to_serial(parallel_data, num_bits=8):
    """
    Converts parallel data to serial format.
    """
    serial_data = []
    for value in parallel_data:
        for i in range(num_bits):
            serial_data.append((value >> (num_bits - 1 - i)) & 1)
    return serial_data

def shift_out_multiple(data_pin, clock_pin, latch_pin, values, bit_order=MSB_FIRST):
    """
    Shifts out multiple bytes of data with latching.
    """
    latch_pin.value(0)
    for value in values:
        shift_out(data_pin, clock_pin, value, bit_order)
    latch_pin.value(1)
    time.sleep_us(1)
    latch_pin.value(0)

def shift_in_multiple(data_pin, clock_pin, latch_pin, num_bytes, bit_order=MSB_FIRST):
    """
    Shifts in multiple bytes of data with latching.
    """
    latch_pin.value(1)
    time.sleep_us(1)
    latch_pin.value(0)

    values = []
    for _ in range(num_bytes):
        values.append(shift_in(data_pin, clock_pin, bit_order))
    return values

def debounce(pin, delay_ms=20):
    """
    Debounces a pin input.
    """
    initial_state = pin.value()
    time.sleep_ms(delay_ms)
    return pin.value() == initial_state

class ShiftRegister:
    """Class to manage a shift register device."""
    
    def __init__(self, data_pin, clock_pin, latch_pin, num_bytes=1, bit_order=MSB_FIRST):
        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.latch_pin = latch_pin
        self.num_bytes = num_bytes
        self.bit_order = bit_order
        self.current_state = [0] * num_bytes

    def write(self, values):
        if len(values) != self.num_bytes:
            raise ValueError(f"Expected {self.num_bytes} bytes, got {len(values)}")
        self.current_state = values
        shift_out_multiple(self.data_pin, self.clock_pin, self.latch_pin, values, self.bit_order)

    def read(self):
        return shift_in_multiple(self.data_pin, self.clock_pin, self.latch_pin, 
                               self.num_bytes, self.bit_order)

    def set_bit(self, byte_index, bit_index, value):
        if not 0 <= byte_index < self.num_bytes:
            raise ValueError(f"Byte index {byte_index} out of range")
        if not 0 <= bit_index < 8:
            raise ValueError(f"Bit index {bit_index} out of range")

        if value:
            self.current_state[byte_index] |= 1 << bit_index
        else:
            self.current_state[byte_index] &= ~(1 << bit_index)

        self.write(self.current_state)

def shift_out(data_pin, clock_pin, value, bit_order=MSB_FIRST):
    """
    Shifts out a byte of data on a data pin with a clock pin.
    """
    if isinstance(bit_order, str):
        bit_order = MSB_FIRST if bit_order == "MSBFIRST" else LSB_FIRST

    value = max(0, min(value, 255))

    def pulse_clock():
        clock_pin.value(1)
        time.sleep_us(1)
        clock_pin.value(0)
        time.sleep_us(1)

    for i in range(8):
        if bit_order == MSB_FIRST:
            bit = (value >> (7 - i)) & 1
        else:
            bit = (value >> i) & 1

        data_pin.value(bit)
        pulse_clock()

def shift_in(data_pin, clock_pin, bit_order=MSB_FIRST):
    """
    Shifts in a byte of data using a data pin and clock pin.
    """
    if isinstance(bit_order, str):
        bit_order = MSB_FIRST if bit_order == "MSBFIRST" else LSB_FIRST

    def read_bit():
        clock_pin.value(1)
        time.sleep_us(1)
        bit = data_pin.value()
        clock_pin.value(0)
        time.sleep_us(1)
        return bit

    value = 0
    for i in range(8):
        bit = read_bit()
        if bit_order == MSB_FIRST:
            value = (value << 1) | bit
        else:
            value |= bit << i

    return value
