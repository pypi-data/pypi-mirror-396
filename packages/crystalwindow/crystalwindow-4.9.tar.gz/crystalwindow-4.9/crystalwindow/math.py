class Mathematics:
    """
    A class used to perform basic mathematical operations.

    Methods:
    --------
    add(num1, num2) : Adds two numbers.
    subtract(num1, num2) : Subtracts two numbers.
    multiply(num1, num2) : Multiplies two numbers.
    divide(num1, num2) : Divides two numbers.
    """

    @staticmethod
    def add(x, y):
        """Adds two numbers together"""
        return x + y

    @staticmethod
    def subtract(num1, num2):
        """Subtracts two numbers."""
        return num1 - num2

    @staticmethod
    def multiply(num1, num2):
        """Multiplies two numbers."""
        return num1 * num2

    @staticmethod
    def divide(num1, num2):
        """
        Divides two numbers.

        Raises:
        ------
        ZeroDivisionError : If num2 is zero.
        """
        if num2 == 0:
            raise ZeroDivisionError("Cannot divide by zero!")
        return num1 / num2

