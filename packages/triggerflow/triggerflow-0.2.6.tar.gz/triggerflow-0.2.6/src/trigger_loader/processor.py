import datetime as dt
import hashlib
import json
import os
import time
import uuid
import warnings
from collections.abc import Callable
from typing import Any

import awkward as ak
import pyarrow.parquet as pq
from coffea import processor

warnings.filterwarnings("ignore", message="Found duplicate branch")


class TriggerProcessor(processor.ProcessorABC):
    """
    Coffea processor that applies a user transform to events and writes Parquet files.
    
    This processor transforms event data and writes the results to Parquet files with
    comprehensive metadata tracking for reproducibility and provenance.
    """

    def __init__(
        self,
        output_path: str,
        transform: Callable[[Any], ak.Array],
        compression: str = "zstd",
        compression_level: int | None = None,
        filename_template: str = "{dataset}_{fileuuid}_{start}-{stop}.parquet",
        add_uuid: bool = False,
        write_manifest: bool = True,
        manifest_name: str = "manifest.jsonl",
        run_uuid: str | None = None,
        run_metadata: dict | None = None,
        preserve_event_metadata: bool = True,
    ):
        """
        Initialize the TriggerProcessor.
        
        Args:
            output_path: Directory where output files will be written
            transform: Function to apply to events, returns awkward array
            compression: Parquet compression algorithm
            compression_level: Compression level (None for default)
            filename_template: Template for output filenames
            add_uuid: Whether to add UUID to filenames
            write_manifest: Whether to write manifest file
            manifest_name: Name of the manifest file
            run_uuid: UUID for this processing run (generated if None)
            run_metadata: Additional metadata for the run
            preserve_event_metadata: Whether to preserve event-level metadata
        """
        self.output_path = output_path
        self.transform = transform
        self.compression = compression
        self.compression_level = compression_level
        self.filename_template = filename_template
        self.add_uuid = add_uuid
        self.write_manifest = write_manifest
        self.manifest_name = manifest_name
        self.run_uuid = run_uuid or str(uuid.uuid4())
        self.run_metadata = run_metadata or {}
        self.preserve_event_metadata = preserve_event_metadata

        # Initialize output directory and paths
        os.makedirs(self.output_path, exist_ok=True)
        if write_manifest:
            self._manifest_path = os.path.join(self.output_path, self.manifest_name)

    @property
    def accumulator(self):
        """No aggregation needed (side-effect writing)."""
        return {}

    def process(self, events):
        """
        Process a chunk of events: transform and write to Parquet.
        
        Args:
            events: Input events from Coffea
            
        Returns:
            Empty dict (no accumulation needed)
        """
        # Apply transform and measure time
        data, elapsed_s = self._apply_transform(events)

        # Extract event metadata
        event_meta = self._extract_event_metadata(events)
        output_file = self._generate_output_filename(event_meta)

        # Convert to Arrow table
        table = ak.to_arrow_table(data)

        # Build file metadata
        file_meta = self._build_file_metadata(event_meta, table, elapsed_s)
        table = self._embed_metadata_in_schema(table, file_meta, events.metadata)

        # Write Parquet file
        self._write_parquet(table, output_file)

        # Write manifest entry
        if self.write_manifest:
            self._write_manifest_entry(output_file, file_meta)

        return {}

    def postprocess(self, accumulator):
        """Postprocess accumulated results (no-op for this processor)."""
        return accumulator

    # ==================== Private Helper Methods ====================

    def _apply_transform(self, events) -> tuple[ak.Array, float]:
        """Apply user transform to events and measure execution time."""
        t0 = time.time()
        data = self.transform(events)
        elapsed_s = time.time() - t0
        return data, elapsed_s

    def _extract_event_metadata(self, events) -> dict:
        """Extract metadata from events object."""
        source_file = None
        if hasattr(events, "_events"):
            source_file = getattr(events._events, "files", [None])[0]

        return {
            "start": events.metadata.get("entrystart", 0),
            "stop": events.metadata.get("entrystop", 0),
            "dataset": events.metadata.get("dataset", "unknown"),
            "source_file": source_file,
            "fileuuid": events.metadata.get("fileuuid"),
        }

    def _generate_output_filename(self, event_meta: dict) -> str:
        """Generate output filename based on template and metadata."""
        fname = self.filename_template.format(
            dataset=event_meta["dataset"],
            fileuuid=event_meta.get("fileuuid", "xx"),
            start=event_meta["start"],
            stop=event_meta["stop"]
        )

        if self.add_uuid:
            stem, ext = os.path.splitext(fname)
            fname = f"{stem}_{uuid.uuid4()}{ext}"

        return os.path.join(self.output_path, fname)

    def _build_file_metadata(self, event_meta: dict, table, elapsed_s: float) -> dict:
        """Build comprehensive metadata dictionary for the output file."""
        fileuuid = event_meta["fileuuid"]

        return {
            "run_uuid": self.run_uuid,
            "dataset": event_meta["dataset"],
            "source_root_file": event_meta["source_file"],
            "fileuuid": str(fileuuid) if fileuuid is not None else None,
            "entrystart": event_meta["start"],
            "entrystop": event_meta["stop"],
            "n_events_written": len(table),
            "columns": table.column_names,
            "created_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds") + "Z",
            "compression": self.compression,
            "processing_time_s": round(elapsed_s, 6),
        }

    def _embed_metadata_in_schema(self, table, file_meta: dict, event_metadata: dict):
        """Embed metadata into the Arrow table schema."""
        schema = table.schema
        existing = dict(schema.metadata or {})

        # Add file metadata
        existing[b"x-trigger-meta"] = json.dumps(
            file_meta, separators=(",", ":")
        ).encode()

        # Optionally preserve event-level metadata
        if self.preserve_event_metadata:
            for k, v in event_metadata.items():
                if k not in file_meta:
                    file_meta[f"eventmeta_{k}"] = v

        # Add run metadata hash
        if self.run_metadata:
            existing.setdefault(
                b"x-run-meta-hash",
                hashlib.sha256(
                    json.dumps(self.run_metadata, sort_keys=True).encode()
                ).hexdigest().encode()
            )

        return table.replace_schema_metadata(existing)

    def _write_parquet(self, table, output_file: str):
        """Write Arrow table to Parquet file."""
        pq.write_table(
            table,
            output_file,
            compression=self.compression,
            compression_level=self.compression_level
        )

    def _write_manifest_entry(self, output_file: str, file_meta: dict):
        """Write a single line to the manifest file."""
        manifest_record = {"parquet_file": output_file, **file_meta}
        with open(self._manifest_path, "a") as mf:
            mf.write(json.dumps(manifest_record, separators=(",", ":")) + "\n")
