import logging, json
from glob import glob
from kedro.io import AbstractDataset


METADATA_CONFIG = {"x": 0}


class MetaDataset(AbstractDataset):
    """
    Dataset class to load a json file.
    """

    def __init__(self, filepath: str, sample_key: str):
        self._filepath = filepath
        self._sample_key = sample_key
        # get logger for reporting
        self.logger = logging.getLogger(__name__)

    def get_dasgoclient_metadata(self, das_name: dict, config: dict) -> dict:
        """
        Get metadata from DAS for a given sample.
        """

        self.logger.info(f"Fetching DAS metadata for dataset: {das_name}")

        # # Use sys to run the command and keep the output as a dict
        # cmnd = f'dasgoclient -query="dataset dataset={das_name}" -json'
        # output = sys.command(cmnd)

        # # Parse the output and extract relevant metadata
        # if output:
        #     das_json = json.loads(output)[0]
        #     for k, v in config["metadata"].items():
        #         if k in das_json:
        #             for item in v:
        #                 metadata[item] = das_json[k].get(item)
        #         else:
        #              self.logger.warning(f"{k} not found for dataset: {das_name}")
        # else:
        #     self.logger.warning("No metadata found.")
        #     return {}

        metadata = {"gridpack": "0.0.0"}

        return metadata

    def _load(self) -> dict:
        """
        Load a json file and return a python dict.
        """

        self.logger.info(f"Processing file: {self._filepath}")

        with open(self._filepath, "r") as f:
            data = json.load(f)

        return data

    def _save(self, samples: dict) -> dict:
        """
        Get the meta data from all samples and store the result.
        """

        metadata = {}
        for sample_name, sample_info in samples[self._sample_key].items():
            self.logger.info(f"Processing sample: {sample_name}")

            # Get sample files
            sample_path = sample_info.get("path")
            if len(sample_path) == 0:
                self.logger.warning(f"No files found for sample {sample_name}.")
            sample_info.update({"files": glob(sample_path)})
            self.logger.info(
                f"Found {len(sample_info.get('files', []))} files for sample {sample_name}."
            )

            # Get sample metadata
            metadata[sample_name] = self.get_dasgoclient_metadata(
                sample_info["DAS"], METADATA_CONFIG
            )
            # sample_info.update(metadata)

        with open(self._filepath, "w") as f:
            json.dump(metadata, f)

    def _describe(self) -> dict:
        return {"filepath": self._filepath, "sample_key": self._sample_key}
