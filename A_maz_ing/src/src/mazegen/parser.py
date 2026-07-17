from typing import TypedDict, Optional, Literal, cast
import sys


class ParamDict(TypedDict):
    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool
    SEED: bool


KeyType = Literal["WIDTH", "HEIGHT", "ENTRY",
                  "EXIT", "OUTPUT_FILE", "PERFECT", "SEED"]


class ArgsFillingError(Exception):
    """This Exception raised when some args value or
       the args itself is missing or incorrect.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


def point_vali_checker(args: ParamDict) -> None:
    """

    This function chick if the entry and exit point is proper to
    use or not (eg, not out of range, not has a same value)

    Args:
        args (ParamDict): dict has a value of entry and exit point
    """

    entry = args["ENTRY"]
    exit = args["EXIT"]
    max_hight = args["HEIGHT"] - 1
    max_width = args["WIDTH"] - 1
    if max_hight > 49:
        raise ArgsFillingError("Height is greater than " +
                               "what the window can accommodate")
    if max_width > 109:
        raise ArgsFillingError("Width is greater than " +
                               "what the window can accommodate")
    if entry[0] > max_hight or entry[0] < 0:
        raise ArgsFillingError("Entry point's height is out of range")
    if entry[1] > max_width or entry[1] < 0:
        raise ArgsFillingError("Entry point's width is out of range")
    if exit[0] > max_hight or exit[0] < 0:
        raise ArgsFillingError("Exit point's height is out of range")
    if exit[1] > max_width or exit[1] < 0:
        raise ArgsFillingError("Exit point's width is out of range")
    if exit == entry:
        raise ArgsFillingError("ENTRY point and EXIT point \
                                can not have the same value")


def int_case(value: str) -> int:
    """ This func handle the case when the agrs value is int

        Args:
            value (str): The value before being processed

        Returns:
            int: The processed value, if valid
    """
    striped_value = value.strip()
    int_value = int(striped_value)
    if int_value < 0:
        raise ArgsFillingError(r"The value of HEIGHT\WIDTH is invalid")
    return int_value


def tuple_case(value: str) -> tuple[int, int]:
    """ This func handle the case when the agrs value is x, y

        Args:
            value (str): The value before being processed

        Returns:
            tuple[x, y]: The processed value, if valid
    """
    x, y = value.split(",")
    int_x = int(x.strip())
    int_y = int(y.strip())
    if int_x < 0 or int_y < 0:
        raise ArgsFillingError(r"The value of ENTRY\EXIT is \
                            invalid x, y or both are negative")
    return (int_x, int_y)


def str_case(value: str) -> str:
    """ This func handle the case when the agrs value is str(File path)

        Args:
            value (str): The value before being processed

        Returns:
            str: The processed value, if valid
    """
    string = value.strip()
    return string


def bool_case(value: str) -> bool:
    """ This func handle the case when the agrs value is str(bool)

        Args:
            value (str): The value before being processed

        Returns:
            bool: The processed value, if valid
    """
    processed_value = value.strip().lower()
    if processed_value in ["yes", "true"]:
        return True
    elif processed_value in ["no", "false"]:
        return False
    else:
        raise ValueError("PERFECT values ​​are not recognized")


def value_handler(value: str, key: str
                  ) -> tuple[int, int] | int | str | bool:
    """This function forwards each value to its custom func

        Args:
            value (str): The value before being processed
            key (str): The args type, each value is forwarded based on it

        Returns:
            Union[tuple, int, str, bool]: The processed value, if valid
    """
    keys = {
        "WIDTH": "int",
        "HEIGHT": "int",
        "ENTRY": "tup",
        "EXIT": "tup",
        "OUTPUT_FILE": "str",
        "PERFECT": "bool",
        "SEED": "bool"
    }
    result: int | tuple[int, int] | str | bool
    if keys[key] == "int":
        result = int_case(value)
    elif keys[key] == "tup":
        result = tuple_case(value)
    elif keys[key] == "str":
        result = str_case(value)
    elif keys[key] == "bool":
        result = bool_case(value)
    return result


def parser(file: str = "config.txt") -> Optional[ParamDict]:
    """This function parses the config file and return it as dict

        This function try to read the file passed and search across each line
        about the predefined config and try to process it's value

        Args:
            file (str): File path

        Returns:
            Dict["args_name": value]: dict of args and thier values
    """
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = "config.txt"
    args: ParamDict = {
        "WIDTH": 1,
        "HEIGHT": 1,
        "ENTRY": (0, 0),
        "EXIT": (0, 0),
        "OUTPUT_FILE": "",
        "PERFECT": True,
        "SEED": True
    }
    total_received_args = 0
    try:
        with open(file, "r") as f:
            line_no = 0
            for line in f:
                line_no += 1
                if (line[0] == "#"):
                    continue
                elif (line.count("=") != 1):
                    raise (SyntaxError("only one '=' should exist in a line"))
                key, value = line.split("=")
                key = key.strip().upper()
                if key in args.keys():
                    typed_key = cast(KeyType, key)
                    args[typed_key] = value_handler(value=value, key=key)
                    total_received_args += 1
            if total_received_args < 7:
                raise ArgsFillingError("one of the args is missing")
            point_vali_checker(args=args)
            return args
    except Exception as e:
        print(f"Error in line {line_no}: {e}")
        sys.exit()
        return None


if __name__ == "__main__":
    path = "config.txt"
    my_dict = parser(path)
    print(my_dict)
