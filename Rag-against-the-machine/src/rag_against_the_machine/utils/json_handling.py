from pathlib import Path
from ..helper import (RagDataset, StudentSearchResults,
                      StudentSearchResultsAndAnswer, Truth)
from pydantic import BaseModel


class json_handler(BaseModel):
    """this function handel all file interactions (read, write)"""

    def read_RagDataset(self, path: str) -> RagDataset:
        """read a RagDataset schema json file

        Args:
            path (str): the path for the file.

        Returns:
            RagDataset: Object with RagDataset schema.
        """
        file_path = Path(path)
        raw_json = file_path.read_text(encoding="utf-8")

        data = RagDataset.model_validate_json(raw_json)
        return data

    def read_search_results(self, path: str) -> StudentSearchResults:
        """read a StudentSearchResults schema json file

        Args:
            path (str): the path for the file.

        Returns:
            StudentSearchResults: Object with StudentSearchResults schema.
        """
        file_path = Path(path)
        raw_json = file_path.read_text(encoding="utf-8")

        data = StudentSearchResults.model_validate_json(raw_json)
        return data

    def read_truth(self, path: str) -> Truth:
        """read a Truth schema json file

        Args:
            path (str): the path for the file.

        Returns:
            Truth: Object with Truth schema.
        """
        file_path = Path(path)
        raw_json = file_path.read_text(encoding="utf-8")

        data = Truth.model_validate_json(raw_json)
        return data

    def write_searchResult(self, searchResult: StudentSearchResults,
                           path: str,
                           name: str = "dataset_docs_public.json") -> bool:
        """
        This func create a store a StudentSearchResults into json files.

        Args:
            searchResult (StudentSearchResults): Object with
                                                 StudentSearchResults schema.
            path (str): the path for the file.
            name (str): name of file.
        """
        target_dir = Path(path)
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / name
        file_path.write_text(
                    searchResult.model_dump_json(indent=2), encoding="utf-8"
                    )
        return True

    def write_answerResult(self,
                           answerResult: StudentSearchResultsAndAnswer,
                           path: str,
                           name: str = "dataset_docs_public.json") -> bool:
        """
        This func create a store a StudentSearchResults into json files.

        Args:
            searchResult (StudentSearchResultsAndAnswer):
            Object with StudentSearchResultsAndAnswer schema.
            path (str): the path for the file.
            name (str): name of file.

        Returns:
            bool: True if succeed otherwise False
        """
        target_dir = Path(path)
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / name
        file_path.write_text(
                    answerResult.model_dump_json(indent=2), encoding="utf-8"
                    )
        return True
