from ..types.settle_signer_key import SettleSignerKey


def a0gi_to_neuron(value: float) -> int:
    value_str = f"{value:.18f}"
    parts = value_str.split(".")

    # Целая часть
    integer_part = int(parts[0])
    integer_part_as_int = integer_part * 10**18

    # Дробная часть, если есть
    if len(parts) > 1:
        fractional_part = parts[1]
        # Дополняем нулями до 18 знаков
        fractional_part = (fractional_part + "0" * 18)[:18]
        fractional_part_as_int = int(fractional_part)
        integer_part_as_int += fractional_part_as_int

    return integer_part_as_int


def neuron_to_a0gi(value: int) -> float:
    divisor = 10**18
    integer_part = value // divisor
    remainder = value % divisor
    decimal_part = remainder / divisor
    return integer_part + decimal_part


def create_settle_signer_key() -> SettleSignerKey:
    # TODO:
    return {"settleSignerPublicKey": (0, 0), "settleSignerEncryptedPrivateKey": ""}
