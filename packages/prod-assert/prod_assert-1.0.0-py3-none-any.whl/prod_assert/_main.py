from typing import Any, Optional, Union
from collections.abc import Container


class AssertionFailed(Exception):
    pass


AssertionException = Union[AssertionFailed, AssertionError]


def prod_assert(
    condition: bool,
    message: str,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
    """
    Function that takes a condition and checks if it is True.
    If the condition is False the function raises AssertionFailed exception.

    :param condition: Condition to check.
    :type condition: bool
    :param message: Message to display if check fails.
    :type message: str
    :param assertion_exception: Exeption to be raised when the assertion fails.
    :type assertion_exception: AssertionException
    :raises ValueError: If condition is not bool.
    :raises ValueError: If message is not str.
    :raises ValueError: If assertion_exception is not AssertionFailed or AssertionError
    :raises AssertionException: If condition is False
    """
    if not isinstance(condition, bool):
        raise ValueError("Paramater condition is not bool")

    if not isinstance(message, str):
        raise ValueError("Paramater message is not bool")

    if (assertion_exception != AssertionFailed) and (assertion_exception != AssertionError):
        raise ValueError("Parameter assertion_exception in not AssertionFalied or AssertionError")

    if condition:
        return

    raise assertion_exception(message)


def assert_eq(
    a: Any,
    b: Any,
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
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
    prod_assert(a == b, message, assertion_exception)
   

def assert_not_eq(
    a: Any,
    b: Any,
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
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
    prod_assert(a != b, message=message, assertion_exception=assertion_exception)


def assert_true(
    a: Any,
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
    """
    Function that checks if a is True.
    A custom message can be provided. The default message is 'Condition {a} == True is false'.

    :param a: Any value.
    :type a: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a does not equals True.
    """


    if message is None:
        message = f'Condition {a} == True is false'
    prod_assert(a == True, message, assertion_exception)
 

def assert_false(
    a: Any,
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
    """
    Function that checks if a is False.
    A custom message can be provided. The default message is 'Condition {a} == False is false'.

    :param a: Any value.
    :type a: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a does not equals False.
    """


    if message is None:
        message = f'Condition {a} == False is false'
    prod_assert(a == False, message, assertion_exception)


def assert_is(
    a: Any,
    b: Any,
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
    """
    Function that checks if a is b.
    A custom message can be provided. The default message is 'Condition {a} is {b} is false'.

    :param a: Any value.
    :type a: Any
    :param b: Any value.
    :type b: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a is not b.
    """


    if message is None:
        message = f'Condition {a} is {b} is false'
    prod_assert(a is b, message, assertion_exception)


def assert_is_not(
    a: Any,
    b: Any,
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
    """
    Function that checks if a is not b.
    A custom message can be provided. The default message is 'Condition {a} is not {b} is false'.

    :param a: Any value.
    :type a: Any
    :param b: Any value.
    :type b: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a is b.
    """


    if message is None:
        message = f'Condition {a} is not {b} is false'
    prod_assert(a is not b, message, assertion_exception)


def assert_is_none(
    a: Any,
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
    """
    Function that checks if a is None.
    A custom message can be provided. The default message is 'Condition {a} is None is false'.

    :param a: Any value.
    :type a: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a is not None.
    """


    if message is None:
        message = f'Condition {a} is None is false'
    prod_assert(a is None, message, assertion_exception)


def assert_is_not_none(
    a: Any,
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
    """
    Function that checks if a is not None.
    A custom message can be provided. The default message is 'Condition {a} is not None is false'.

    :param a: Any value.
    :type a: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a is None.
    """


    if message is None:
        message = f'Condition {a} is not None is false'
    prod_assert(a is not None, message, assertion_exception)



def assert_in(
    a: Any,
    b: Container[Any],
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
    """
    Function that checks if a is in b.
    A custom message can be provided. The default message is 'Condition {a} in {b} is false'.

    :param a: Any value.
    :type a: Any
    :param b: Any value.
    :type b: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a is not in b.
    """


    if message is None:
        message = f'Condition {a} in {b} is false'
    prod_assert(a in b, message, assertion_exception)



def assert_not_in(
    a: Any,
    b: Container[Any],
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
    """
    Function that checks if a is not in b.
    A custom message can be provided. The default message is 'Condition {a} not in {b} is false'.

    :param a: Any value.
    :type a: Any
    :param b: Any value.
    :type b: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a is in b.
    """


    if message is None:
        message = f'Condition {a} not in {b} is false'
    prod_assert(a not in b, message, assertion_exception)


def assert_is_instance(
    a: Any,
    b: Any,
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
    """
    Function that checks if a is instance of b.
    A custom message can be provided. The default message is 'Condition isinstance({a}, {b}) is false'.

    :param a: Any value.
    :type a: Any
    :param b: Any value.
    :type b: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a is not instance of b.
    """


    if message is None:
        message = f'Condition isinstance({a}, {b}) is false'
    prod_assert(isinstance(a, b), message, assertion_exception)


def assert_not_is_instance(
    a: Any,
    b: Any,
    message: Optional[str]=None,
    assertion_exception: AssertionException=AssertionFailed
) -> None:
    """
    Function that checks if a is not instance of b.
    A custom message can be provided. The default message is 'Condition not isinstance({a}, {b}) is false'.

    :param a: Any value.
    :type a: Any
    :param b: Any value.
    :type b: Any
    :param message: Optional custom message.
    :type message: Optional[str]
    :raises AssertionFailed: If a is instance of b.
    """


    if message is None:
        message = f'Condition not isinstance({a}, {b}) is false'
    prod_assert(not isinstance(a, b), message, assertion_exception)

