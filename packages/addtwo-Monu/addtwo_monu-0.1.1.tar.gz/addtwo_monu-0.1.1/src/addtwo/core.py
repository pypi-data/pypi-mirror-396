from typing import Union

Number = Union[int, float]

def add(a: Number, b: Number) -> Number:
    """Return the sum of a and b.

    Raises:
        TypeError: if a or b are not int/float.
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("add() accepts only int or float")
    return a + b

def main():
    # small CLI entrypoint (optional)
    import argparse
    parser = argparse.ArgumentParser(prog="addtwo", description="Add two numbers")
    parser.add_argument("a", type=float, help="first number")
    parser.add_argument("b", type=float, help="second number")
    args = parser.parse_args()
    print("Monu's CLI")
    print(add(args.a, args.b))


