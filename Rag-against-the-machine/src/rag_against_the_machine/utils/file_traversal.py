import os
from pydantic import BaseModel, Field
from ..helper import allowed_file_type


class traversal(BaseModel):
    """
    This func (walk) on all codebase extract all usfaul file
    preaparing it to be indexed.

    Args:
        root (str): root path to start extract on.
        tree (list[tuple[str, list[str]]]): list of files and thier
                                            parent as a tuple.
        allowed_types (list[str]): list of allowed types to chunk
                                   to extract them.
    """

    root: str = "data/raw"
    tree: list[tuple[str, list[str]]] = Field(default_factory=list)
    allowed_types: list[str] = [t.value for t in allowed_file_type]

    def do(self) -> None:
        """
        This func apply the traversal on the provided root path.
        """

        for root, _, files in os.walk(self.root):
            self.tree.append((root, files))

    def filter_and_build(self) -> dict[str, list[str]]:
        """
        This function filter all inappropriate files
        and this use them to build a dict of allowed files path
        each file under it's type as a key.

        Returns:
            dict [str, list[str]]: dict include two key (code, txt) each one
                                  has a list of files paths of it's type.
        """
        files_dict: dict[str, list[str]] = {"code": [], "txt": []}
        new_tree: list[tuple[str, list[str]]] = []

        for level in self.tree:
            if level is None:
                continue

            allowed_file = []
            for file in level[1]:
                ext = os.path.splitext(file)[1]
                if ext in self.allowed_types:
                    allowed_file.append(file)
                    file_path = os.path.join(level[0], file)
                    if ext == ".py" or ext == ".sh":
                        files_dict["code"].append(file_path)
                    else:
                        files_dict["txt"].append(file_path)

            new_level = (level[0], allowed_file)
            new_tree.append(new_level)

        self.tree = new_tree
        return files_dict
