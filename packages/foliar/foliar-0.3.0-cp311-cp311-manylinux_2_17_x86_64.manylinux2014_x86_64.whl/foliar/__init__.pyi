# pylint: disable=unused-argument

from typing import Any

class Pretty:
    """A class for pretty-printing Python objects."""

    def __init__(self, indent: int = 4) -> None:
        """Initialize the Pretty printer instance.

        Args:
            indent (int, optional): The number of spaces to use for indentation. Defaults to 4.
        """

    @property
    def indent(self) -> int:
        """Get the current indentation level.

        Returns:
            int: The number of spaces used for indentation.
        """

    @indent.setter
    def indent(self, value: int) -> None:
        """Set the indentation level.

        Args:
            value (int): The number of spaces to use for indentation.
        """

    def format(self, obj: Any) -> str:
        """Pretty-format the given object and return it as a string.

        Args:
            obj (Any): The object to pretty-format.

        Returns:
            str: A string containing the pretty-formatted representation of the object.
        """

    def print(self, obj: Any) -> None:
        """Pretty-print the given object to standard output.

        Args:
            obj (Any): The object to pretty-print.
        """

def pretty_format(obj: Any, indent: int = 4) -> str:
    """Pretty-format the given object and return it as a string.

    Args:
        obj (Any): The object to pretty-format.
        indent (int, optional): The number of spaces to use for indentation. Defaults to 4.

    Returns:
        str: A string containing the pretty-formatted representation of the object.
    """

def pretty_print(obj: Any, indent: int = 4) -> None:
    """Pretty-print the given object to standard output.

    Args:
        obj (Any): The object to pretty-print.
        indent (int, optional): The number of spaces to use for indentation. Defaults to 4.
    """
