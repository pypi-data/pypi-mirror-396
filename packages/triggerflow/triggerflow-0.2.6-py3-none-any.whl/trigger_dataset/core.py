import warnings
from abc import ABC, abstractmethod
from fnmatch import filter as fnmatch_filter

import pandas as pd
import uproot


class TriggerDataset(ABC):
    """
    Abstract Base Class for loading data from ROOT files.

    Users must inherit from this class and implement the abstract methods.
    The core processing logic in `process_file` is fixed and cannot be overridden.
    """

    def __init__(self):
        pass

    @abstractmethod
    def get_features(self) -> list[str]:
        """
        Return a list of branch names or patterns to keep from the dataset.
        Accepts wildcards (e.g. Jet_*).
        """
        pass

    @abstractmethod
    def get_cut(self) -> str | None:
        """
        Return a string representing the cuts to apply to the data.
        """
        pass

    @abstractmethod
    def convert_to_pandas(self, data: dict) -> pd.DataFrame:
        """
        Convert the loaded data from a dictionary format to a pandas DataFrame.
        """
        pass

    def _resolve_branches(self, all_branches: list) -> list[str]:
        """Internal method to resolve wildcard patterns."""
        selected = []
        for pattern in self.get_features():
            matched = fnmatch_filter(all_branches, pattern)
            if not matched:
                warnings.warn(f"'{pattern}' did not match any branches.")
            selected.extend(matched)
        return sorted(list(set(selected)))

    def _save_to_parquet(self, df: pd.DataFrame, output_path: str):
        """
        Save the processed DataFrame to a file.
        """
        df.to_parquet(output_path)

    def _save_to_csv(self, df: pd.DataFrame, output_path: str):
        """
        Save the processed DataFrame to a CSV file.
        """
        df.to_csv(output_path, index=False)

    def process_file(self, file_path: str, out_file_path: str) -> pd.DataFrame:
        """
        Loads and processes a single ROOT file.
        """

        with uproot.open(f"{file_path}") as f:
            tree = f[self.get_tree_name()]
            all_branches = tree.keys()
            branches_to_load = self._resolve_branches(all_branches)

            if not branches_to_load:
                return pd.DataFrame()

            data = tree.arrays(branches_to_load, cut=self.get_cut(), how=dict)

        df = self.convert_to_pandas(data)

        if self.output_format == "parquet":
            self._save_to_parquet(df, f"{out_file_path}.parquet")
        elif self.output_format == "csv":
            self._save_to_csv(df, f"{out_file_path}.csv")
        else:
            return pd.DataFrame()

        return pd.DataFrame()
