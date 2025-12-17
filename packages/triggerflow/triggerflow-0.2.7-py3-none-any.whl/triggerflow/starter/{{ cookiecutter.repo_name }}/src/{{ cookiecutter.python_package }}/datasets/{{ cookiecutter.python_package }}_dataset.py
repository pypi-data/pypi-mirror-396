import pandas as pd
from .base_dataset import BaseDataset


class {{ cookiecutter.python_package }}Dataset(BaseDataset):
    """
    A custom dataset example.
    """

    def get_branches_to_keep(self) -> list[str]:
        """
        Define the branches you needed.
        """
        return [
            "PuppiMET_pt",
            "CaloMET_pt",
            "event",  # <-- we need this for meta data
            # "Jet_pt",
            # "Jet_eta",
            # "Jet_phi",
            # "Jet_btag*", # Use a wildcard to get all b-tagging info
            "nJet",
        ]

    def get_cut(self) -> str | None:
        """
        Apply a pre-selection cut to keep only events with exactly 1 jet.
        """
        return "nJet == 1"

    def convert_to_pandas(self, data: dict):
        """
        Logic to convert from dict of (potentially nested) arrays to a pandas DataFrame.
        """
        return pd.DataFrame(data)
