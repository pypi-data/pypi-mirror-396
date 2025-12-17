from __future__ import annotations

from typing import Optional, Tuple, Any, Dict
import logging
import sys
import os
from pathlib import Path

from mlops.core.workspace import get_workspace_root, infer_source_root


class ClusterProvider:
    """Abstract interface for provisioning a Dask distributed cluster.

    Implementations should provision a scheduler and workers on the target
    infrastructure and return a connected dask.distributed.Client (or None)
    and the scheduler address string.
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def start(self, num_workers: int, options: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Any], Optional[str]]:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError


class SlurmClusterProvider(ClusterProvider):
    """Provision a Dask cluster on SLURM using dask-jobqueue's SLURMCluster.

    Note: This provider requires the optional dependency 'dask-jobqueue'.
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(logger)
        self._cluster = None
        self._client = None

    def start(self, num_workers: int, options: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Any], Optional[str]]:
        options = options or {}
        try:
            # Prefer importing Client from the 'distributed' package to avoid
            # reliance on the 'dask' namespace being present. Fallback to
            # 'dask.distributed' for older setups.
            try:
                from distributed import Client
            except Exception:
                from dask.distributed import Client
            from dask_jobqueue import SLURMCluster
        except Exception as e:
            # If dask-jobqueue or dask import fails, fall back to a local
            # in-process distributed cluster so execution can proceed.
            self.logger.error(f"SLURM provider unavailable (missing deps?): {e}")
            try:
                try:
                    from distributed import Client, LocalCluster  # type: ignore
                except Exception:
                    from dask.distributed import Client, LocalCluster  # type: ignore
                self._cluster = LocalCluster(n_workers=max(1, int(options.get('worker_processes', 1) * num_workers)),
                                             threads_per_worker=int(options.get('worker_cores', 1)))
                self._client = Client(self._cluster)
                addr = getattr(self._cluster, 'scheduler_address', None) or getattr(self._client.scheduler, 'address', None)
                self.logger.warning(f"Falling back to LocalCluster at {addr} (threads_per_worker={int(options.get('worker_cores', 1))}, n_workers={max(1, int(options.get('worker_processes', 1) * num_workers))})")
                return self._client, addr
            except Exception as e2:
                self.logger.error(f"Failed to start LocalCluster fallback: {e2}")
                return None, None

        worker_cores = int(options.get('worker_cores', 1))
        worker_memory = options.get('worker_memory', '2GB')
        worker_processes = int(options.get('worker_processes', 1))
        queue = options.get('queue')
        walltime = options.get('walltime', '00:30:00')
        # Optional: additional sbatch directives passed through to SLURMCluster
        # Accept both 'job_extra' and legacy 'job_extra_directives'
        job_extra = options.get('job_extra') or options.get('job_extra_directives') or []
        if isinstance(job_extra, str):
            job_extra = [job_extra]

        # Convenience option: when True, ensure each worker is placed on a distinct node
        # by requesting node-level exclusivity for each worker job.
        spread_workers = bool(options.get('spread_workers_across_nodes', False))
        if spread_workers and not any(str(opt).startswith('--exclusive') for opt in job_extra):
            job_extra.append('--exclusive')

        workspace_root = get_workspace_root()
        source_root = infer_source_root()

        # Source-checkout support: allow workers to import from <repo>/src on shared filesystems.
        # For installed packages, this is typically unnecessary and <workspace>/src will not exist.
        src_dir = None
        try:
            if source_root and (source_root / "src").exists():
                src_dir = (source_root / "src")
            elif (workspace_root / "src").exists():
                src_dir = (workspace_root / "src")
        except Exception:
            src_dir = None

        # Allow users to pass custom prologue; map legacy env_extra to job_script_prologue to avoid warnings
        job_script_prologue = []
        if options.get('job_script_prologue'):
            pro = options.get('job_script_prologue')
            job_script_prologue = pro if isinstance(pro, list) else [str(pro)]
        elif options.get('env_extra'):
            pro = options.get('env_extra')
            job_script_prologue = pro if isinstance(pro, list) else [str(pro)]

        # Ensure workers use the same Python interpreter and can import our code
        # Also force a consistent comm compression across client/scheduler/workers
        # to avoid codec mismatches that can break task-graph deserialization.
        requested_compression = (
            options.get('comm_compression')
            or options.get('compression')
            or os.environ.get('MLOPS_DASK_COMPRESSION')
            or os.environ.get('DASK_DISTRIBUTED__COMM__COMPRESSION')
            or 'zlib'
        )
        compression_value = str(requested_compression)
        os.environ.setdefault('DASK_DISTRIBUTED__COMM__COMPRESSION', compression_value)
        job_script_prologue = job_script_prologue + [
            # Always export workspace so workers can find projects/ regardless of CWD.
            f'export MLOPS_WORKSPACE_DIR="{workspace_root}"',
            # Legacy alias (older components may still read it).
            f'export MLOPS_REPO_ROOT="{workspace_root}"',
            f'export DASK_DISTRIBUTED__COMM__COMPRESSION="{compression_value}"',
        ]
        if src_dir:
            job_script_prologue.append(f'export PYTHONPATH="{src_dir}:${{PYTHONPATH:-}}"')

        def _build_kwargs_base() -> Dict[str, Any]:
            base = dict(
                cores=worker_cores,
                memory=worker_memory,
                processes=worker_processes,
                queue=queue,
                walltime=walltime,
                python=sys.executable,
                job_script_prologue=job_script_prologue,
            )
            # Allow arbitrary SLURMCluster kwargs via 'cluster_kwargs'
            base.update(options.get('cluster_kwargs') or {})
            return base

        def _create_cluster(extra_directives: list[str]):
            # Prefer the new parameter name to avoid FutureWarning; fallback if unsupported
            base = _build_kwargs_base()
            try:
                # Newer dask-jobqueue
                base_new = dict(base)
                base_new['job_extra_directives'] = extra_directives
                return SLURMCluster(**base_new)
            except TypeError:
                # Older dask-jobqueue
                base_old = dict(base)
                base_old['job_extra'] = extra_directives
                return SLURMCluster(**base_old)

        # First attempt with requested directives
        self._cluster = _create_cluster(job_extra)
        self._cluster.scale(num_workers)
        self._client = Client(self._cluster)
        address: Optional[str]
        try:
            address = self._client.scheduler.address
        except Exception:
            address = None

        # Wait briefly for at least one worker; if none and we added exclusivity, retry without it
        try:
            if num_workers > 0:
                # 60s should be enough for sbatch to accept or reject worker jobs
                self._client.wait_for_workers(min(1, num_workers), timeout=60)
        except Exception:
            # If spread requested, remove exclusivity and retry once
            if spread_workers and any(str(opt).startswith('--exclusive') for opt in job_extra):
                self.logger.warning("SLURM exclusive allocation not permitted or workers failed to start; retrying without --exclusive")
                try:
                    # Tear down previous cluster before retrying
                    self._client.close()
                except Exception:
                    pass
                try:
                    self._cluster.close()
                except Exception:
                    pass
                # Rebuild without exclusive
                filtered = [opt for opt in job_extra if not str(opt).startswith('--exclusive')]
                self._cluster = _create_cluster(filtered)
                self._cluster.scale(num_workers)
                self._client = Client(self._cluster)
                try:
                    address = self._client.scheduler.address
                except Exception:
                    address = None
                # Don't raise if workers still take long; proceed and let Dask run degrade gracefully
            else:
                self.logger.warning("Workers failed to start within timeout; proceeding anyway")

        self.logger.info(
            f"Started SLURMCluster: workers={num_workers}, cores/worker={worker_cores}, mem/worker={worker_memory}"
        )
        return self._client, address

    def stop(self) -> None:
        try:
            if self._client is not None:
                self._client.close()
        finally:
            self._client = None
            if self._cluster is not None:
                try:
                    self._cluster.close()
                finally:
                    self._cluster = None



class AnsibleClusterProvider(ClusterProvider):
    """Provision a Dask cluster on a set of hosts managed via Ansible or SSH.

    This is a minimal stub that expects an address to be provided via options
    or environment variables and does not itself run Ansible. In a full
    implementation, this class would orchestrate scheduler/worker processes
    across inventory hosts and return a connected Client.
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(logger)
        self._client = None

    def start(self, num_workers: int, options: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Any], Optional[str]]:
        options = options or {}
        scheduler_address = options.get('scheduler_address')
        if not scheduler_address:
            # Try env var
            import os
            scheduler_address = os.environ.get('DASK_SCHEDULER_ADDRESS')
        if not scheduler_address:
            self.logger.error("AnsibleClusterProvider requires 'scheduler_address' in options or DASK_SCHEDULER_ADDRESS env var")
            return None, None
        try:
            try:
                from distributed import Client
            except Exception:
                from dask.distributed import Client
            self._client = Client(scheduler_address)
            self.logger.info(f"Connected to existing Dask scheduler at {scheduler_address}")
            return self._client, scheduler_address
        except Exception as e:
            self.logger.error(f"Failed to connect to scheduler at {scheduler_address}: {e}")
            return None, None

    def stop(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            finally:
                self._client = None
