def map(
    x: float, in_min: float, in_max: float, out_min: float, out_max: float
) -> float:
    """
    Map a value from one range to another.

    :param x: Value to map
    :param in_min: Minimum value of the input range
    :param in_max: Maximum value of the input range
    :param out_min: Minimum value of the output range
    :param out_max: Maximum value of the output range
    :return: Mapped value
    """
    return float(x - in_min) * (out_max - out_min) / float(in_max - in_min) + out_min
