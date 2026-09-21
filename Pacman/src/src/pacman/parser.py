import json
from typing import Any


class Jsonparser:
    """
    A class used to handle all operation related whith json
    files in this project.

    Args:
        json_path: file path.
    Attributes:
        path -- the json file path
        json_str -- The json after covert to str(readed)
        json_dict -- dict that contain all json details
        score_boards_file -- the file which store the top players score
        sorted_board -- dict of top players names and thier scores

    """

    def __init__(self, json_path: str) -> None:
        self.path = json_path
        with open(self.path, "r") as f:
            self.json_str = self.del_comment(f.read())
            self.json_dict = json.loads(self.json_str)
            self.defaults_filled(self.json_dict)
        self.score_boards_file = self.json_dict["highscore_filename"]
        with open(self.score_boards_file, "r") as f:
            score_dict = json.load(f)
            self.sorted_board = dict(sorted(score_dict.items(),
                                     key=lambda item: item[1], reverse=True))

    def del_comment(self, json_str: str) -> str:
        """
        This function is responsible about clean the json str before loading
        it to avoid all error casses and delete the comments.

        Args:
            json_str (str): the json string
        """
        cleand_str = ""
        need = False
        lines_json = json_str.split("\n")
        for line in lines_json:
            if ":" in line:
                need = False
            if not need:
                if len(line.strip()) != 0:
                    if not line.strip()[0] == "#":
                        cleand_str += line
                    else:
                        need = True
                        continue
        return self.validate_config(cleand_str)

    @staticmethod
    def check(key: str, value: str) -> str:
        """
        This func is responsible to check if a given values is suitbale to the
        corresponding key in terms of type and conditions.

        Args:
            key (str): The key to check if it's value match what expected.
            value (str): what we want to check.
        Returns:
            str: the json string but delete the key, value pair if
            it uncorrect.
        """
        defaults = {
            "highscore_filename": str,
            "lives": 3,
            "pacgum": 22,
            "points_per_pacgum": 10,
            "points_per_super_pacgum": 50,
            "points_per_ghost": 200,
            "seed": 42,
            "level_max_time": 100
        }
        if key not in defaults.keys():
            return ""
        if isinstance(defaults[key], int):
            try:
                _ = int(value)
                if key == "lives" and (int(value) > 0):
                    return f'"{key}":{value},'
                elif not key == 'lives' and int(value) >= 0:
                    return f'"{key}":{value},'
                raise ValueError()
            except Exception:
                return ""
        else:
            if value[0] == '"' and value.endswith('.json"'):
                return f'"{key}":{value},'
            return ""

    def validate_config(self, st: str) -> str:
        """
        This func used to clean the json string by walk on in and pass each
        key, value pain to the check func.

        Args:
            st (str): json string
        Returns:
            str: json string after being cleaned.
        """
        if st.strip()[0] != "{" or st.strip()[-1] != "}":
            return "{}"
        s = st.split(",")
        cleaned_str = "{"
        for pair in s:
            if pair[0] == "{":
                pair = pair[1:]
            if pair[-1] == "}":
                pair = pair[:-1]
            key, value = pair.split(":")
            key = key.strip(" \"")
            value = value.strip(" ")

            cleaned_str += self.check(key, value)
        cleaned_str = cleaned_str[:-1] + "}"
        return cleaned_str

    @staticmethod
    def defaults_filled(json_dict: dict[str, Any]) -> None:
        """
        This func used to fill all keys that does not exist or has an invalid
        value with defaults values.

        Args:
            json_dict (dict[str, Any]): the dict that contain
            the json key,value pair.
        """
        defaults = {
            "highscore_filename": "score_board.json",
            "lives": 3,
            "pacgum": 42,
            "points_per_pacgum": 10,
            "points_per_super_pacgum": 50,
            "points_per_ghost": 200,
            "seed": 42,
            "level_max_time": 90
        }
        for item in defaults.keys():
            try:
                if item not in json_dict.keys():
                    raise Exception(f"key {item} does not exist " +
                                    "or has invalid value, " +
                                    "resorting to default value\n")
            except Exception as e:
                print(f"Error: {str(e)}")
                json_dict[item] = defaults[item]

    def update_board(self, score_list: list[str | int]) -> None:
        """
        This func  update the score board if the new score is
        greater than the minimum.

        Args:
            score_list (list[str|int]): list containt at the first index
            the user name and in the second index the user score.
        """

        if len(self.sorted_board):
            min_key = min(self.sorted_board,
                          key=lambda k: self.sorted_board[k])
        if len(self.sorted_board.keys()) < 10:
            self.sorted_board[score_list[0]] = score_list[1]
            self.save_data()
            return

        elif self.sorted_board[min_key] > score_list[1]:
            return
        else:
            self.sorted_board[score_list[0]] = score_list[1]
            del self.sorted_board[min_key]
            self.save_data()
            return

    def check_names(self, name: str) -> bool:
        """
        This func check if the name the user choose is already exist or not.

        Args:
            name (str): The name.
        Returns:
            bool: True if exist, False otherwise.
        """
        try:
            if self.sorted_board[name]:
                return True
            return False
        except Exception:
            return False

    def save_data(self) -> None:
        """
        This func used to save the updated data into the json file.
        """
        with open(self.score_boards_file, "w") as f:
            json.dump(self.sorted_board, f, indent=4)
