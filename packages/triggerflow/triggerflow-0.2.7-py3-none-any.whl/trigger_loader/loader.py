import json
import logging
import platform
import time
import uuid

import awkward as ak
import coffea
from coffea import processor
from coffea.nanoevents import NanoAODSchema

from .cluster_manager import ClusterManager
from .processor import TriggerProcessor

logger = logging.getLogger(__name__)


class TriggerLoader:
    def __init__(self,
        sample_json: str,
        transform: callable,
        output_path: str,
    ):
        self.transform = transform
        self.fileset = self._load_sample_json(sample_json)
        self.output_path = output_path
        self.run_uuid = str(uuid.uuid4())

    def _build_processor(self):
        run_meta = {
            "run_uuid": self.run_uuid,
            "fileset_size": sum(len(v) if isinstance(v, list) else 1 for v in self.fileset.values()),
            "coffea_version": coffea.__version__,
            "awkward_version": ak.__version__,
            "python_version": platform.python_version(),
        }

        return TriggerProcessor(
            output_path=self.output_path,
            transform=self.transform,
            compression="zstd",
            add_uuid=False,
            run_uuid=self.run_uuid,
            run_metadata=run_meta,
        )

    def _load_sample_json(self, sample_json: str) -> dict:
        """
        Loads the JSON and resolves file paths using the priority:
        1. Explicit 'files' list or directory path (Local/Explicit)
        2. 'DAS' query (Remote Fallback)

        Returns the canonical coffea fileset format: {dataset_name: [file_path_list]}.
        """
        import glob
        import os
        
        # Helper function definition needed here if it's not imported:
        # def _fetch_files_from_das(das_query: str) -> list[str]: ... (placeholder or actual implementation)

        with open(sample_json) as f:
            full_data = json.load(f)
            dataset_metadata = full_data.get("samples", full_data)

        fileset = {}
        for ds_name, ds_info in dataset_metadata.items():
            files = []
            
            if "files" in ds_info:
                file_info = ds_info["files"]
                
                if isinstance(file_info, list):
                    files = file_info
                    
                elif isinstance(file_info, str):
                    if os.path.isdir(file_info):
                        path_glob = os.path.join(file_info, "*.root")
                        files = glob.glob(path_glob)
                        logger.info(f"Resolved {len(files)} files from directory {file_info}.")
                    else:
                        files = [file_info]
                
                if files:
                    logger.info(f"Using {len(files)} local/explicit files for {ds_name}.")
 
            if not files and "DAS" in ds_info:
                try:
                    files = _fetch_files_from_das(ds_info["DAS"]) 
                    logger.info(f"Resolved {len(files)} files via DAS for {ds_name}.")
                except NameError:
                    logger.error("DAS fetching skipped: _fetch_files_from_das is not defined.")

            if not files:
                logger.warning(f"No files found for dataset: {ds_name}. Skipping.")
                continue

            fileset[ds_name] = files

        return fileset

    def _write_run_metadata_file(self, path: str, duration_s: float | None = None):
        meta_path = f"{path}/run_metadata.json"
        data = {
            "run_uuid": self.run_uuid,
            "duration_seconds": duration_s,
        }
        with open(meta_path, "w") as f:
            json.dump(data, f, indent=2)

    def _run(self, runner: processor.Runner, label: str):
        logger.log(logging.INFO, f"Starting processing ({label})...")
        start = time.time()
        proc = self._build_processor()
        print(self.fileset)
        
        acc = runner(
            self.fileset,
            treename="Events",
            processor_instance=proc
        )
        elapsed = time.time() - start
        self._write_run_metadata_file(self.output_path, elapsed)
        logger.log(logging.INFO, f"Finished in {elapsed:.2f}s (run_uuid={self.run_uuid})")
        return acc

    def run_distributed(self, cluster_type: str, cluster_config: dict,
                        chunksize: int = 100_000, jobs: int = 1):
        with ClusterManager(cluster_type, cluster_config, jobs) as client:
            executor = processor.DaskExecutor(client=client)
            runner = processor.Runner(
                executor=executor,
                schema=NanoAODSchema,
                chunksize=chunksize
            )
            self._run(runner, f"Distributed ({cluster_type})")

    def run_local(self, num_workers: int = 4, chunksize: int = 100_000):
        """
        Run processing locally using a multi-processing executor.
        """
        executor = processor.FuturesExecutor(workers=num_workers)
        runner = processor.Runner(
            executor=executor,
            schema=NanoAODSchema,
            chunksize=chunksize
        )
        self._run(runner, f"Local ({num_workers} workers)")
