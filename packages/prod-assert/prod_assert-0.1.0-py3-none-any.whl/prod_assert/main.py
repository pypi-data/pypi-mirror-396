from typing import Any, Optional


class AssertionFailed(Exception):
    pass


def prod_assert(condition: bool, message: str) -> None:
    """
    Function that takes a condition and checks if it is True.
    If the condition is False the function raises AssertionFailed exception.

    :param condition: Condition to check.
    :type condition: bool
    :param message: Message to display if check fails.
    :type message: str
    :raises ValueError: If condition is not bool.
    :raises ValueError: If message is not str.
    :raises AssertionFailde: If condition is False
    """
    if not isinstance(condition, bool):
        raise ValueError("Paramater condition is not bool")

    if not isinstance(message, str):
        raise ValueError("Paramater message is not bool")

    if condition:
        return

    raise AssertionFailed(message)


def assert_eq(a: Any, b: Any, message: Optional[str]=None) -> None:
    """
    Function that checks if a equals b.
    A custom message can be provided. The default message is 'Condition {a} == {b} is false'.

    :param a: Any value.
    :type a: Any
    :param b: Any value.
    :type b: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a does not equals b.
    """


    if message is None:
        message = f'Condition {a} == {b} is false'
    prod_assert(a == b, message)
    

def assert_not_eq(a: Any, b: Any, message: Optional[str]=None) -> None:
    """
    Function that checks if a does not equals b.
    A custom message can be provided. The default message is 'Condition {a} != {b} is false'.

    :param a: Any value.
    :type a: Any
    :param b: Any value.
    :type b: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a equals b.
    """


    if message is None:
        message = f'Condition {a} != {b} is false'
    prod_assert(a != b, message)

