from __future__ import annotations

import logging
from typing import Any

from dask.distributed import Client, LocalCluster

logger = logging.getLogger(__name__)


class ClusterManager:
    """Context manager to provision and tear down a Dask cluster.

    Parameters
    ----------
    cluster_type : str
        Backend to use ("local", "condor", "cuda", "kubernetes").
    cluster_config : dict | None, optional
        Keyword arguments forwarded to the specific cluster constructor.
    jobs : int, optional
        Desired number of jobs / workers (used for queue / scalable backends).
    """

    def __init__(
        self,
        cluster_type: str,
        cluster_config: dict[str, Any] | None = None,
        jobs: int = 1,
    ) -> None:
        if cluster_config is None:
            cluster_config = {}
        # Copy to avoid mutating caller's dict accidentally.
        self.cluster_config: dict[str, Any] = dict(cluster_config)
        self.cluster_type: str = cluster_type
        self.jobs: int = jobs

        self.cluster: Any | None = None
        self.client: Any | None = None

    # ------------------------------------------------------------------
    # Context manager protocol
    # ------------------------------------------------------------------
    def __enter__(self):  # -> distributed.Client (avoids importing type eagerly)
        self._start_cluster()
        return self.client

    def __exit__(self, exc_type, exc, tb) -> bool:  # noqa: D401 (simple)
        self._close_cluster()
        # Returning False propagates any exception (desired behavior)
        return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _start_cluster(self) -> None:

        ct = self.cluster_type.lower()

        if ct == "local":
            self.cluster = LocalCluster(**self.cluster_config)

        elif ct == "condor":
            from dask_jobqueue import HTCondorCluster
            self.cluster = HTCondorCluster(**self.cluster_config)
            if self.jobs and self.jobs > 0:
                # Scale to the requested number of jobs
                self.cluster.scale(jobs=self.jobs)

        elif ct == "cuda":
            from dask_cuda import LocalCUDACluster
            self.cluster = LocalCUDACluster(**self.cluster_config)

        elif ct == "kubernetes":
            from dask_kubernetes import KubeCluster
            self.cluster = KubeCluster(**self.cluster_config)
            if self.jobs and self.jobs > 0:
                try:
                    # Not all KubeCluster versions expose scale() identically
                    self.cluster.scale(self.jobs)
                except Exception:
                    pass  # Best effort; ignore if unsupported

        else:
            raise ValueError(f"Unsupported cluster type: {self.cluster_type}")

        self.client = Client(self.cluster)
        dash = getattr(self.client, "dashboard_link", None)
        if dash:
            logger.info(f"Dask dashboard: {dash}")

    def _close_cluster(self) -> None:
        # Close client first so tasks wind down before cluster termination.
        if self.client is not None:
            try:
                self.client.close()
            except Exception:
                pass
            finally:
                self.client = None
        if self.cluster is not None:
            try:
                self.cluster.close()
            except Exception:
                pass
            finally:
                self.cluster = None

