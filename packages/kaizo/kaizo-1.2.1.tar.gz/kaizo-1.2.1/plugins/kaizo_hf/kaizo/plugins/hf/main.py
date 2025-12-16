from asyncio import Future
from pathlib import Path
from typing import Literal

from huggingface_hub import CommitInfo, HfApi

from kaizo import Plugin

from .common import HFCommit, HFDir, HFPatterns


class HFPlugin(Plugin):
    def __init__(
        self,
        token: str,
        repo_id: str,
        repo_type: Literal["dataset", "model", "space"] | None = None,
        revision: str | None = None,
    ) -> None:
        super().__init__()

        self.api = HfApi(token=token)
        self.repo_id = repo_id
        self.repo_type = repo_type
        self.revision = revision

    def upload_file(
        self,
        file_path: Path,
        repo_path: str,
        *,
        run_as_future: bool = True,
        commit: HFCommit | dict[str] | None = None,
    ) -> Future[CommitInfo] | CommitInfo:
        if commit is None:
            commit = HFCommit()

        if isinstance(commit, dict):
            commit = HFCommit(**commit)

        return self.api.upload_file(
            repo_id=self.repo_id,
            repo_type=self.repo_type,
            revision=self.revision,
            path_or_fileobj=file_path,
            path_in_repo=repo_path,
            run_as_future=run_as_future,
            commit_message=commit.message,
            commit_description=commit.description,
        )

    def upload_folder(
        self,
        folder_path: Path,
        repo_path: str,
        *,
        run_as_future: bool = True,
        commit: HFCommit | dict[str] | None = None,
    ) -> Future[CommitInfo] | CommitInfo:
        if commit is None:
            commit = HFCommit()

        if isinstance(commit, dict):
            commit = HFCommit(**commit)

        return self.api.upload_folder(
            repo_id=self.repo_id,
            repo_type=self.repo_type,
            revision=self.revision,
            folder_path=folder_path,
            path_in_repo=repo_path,
            run_as_future=run_as_future,
            commit_message=commit.message,
            commit_description=commit.description,
        )

    def download_file(
        self,
        file_name: str,
        file_dir: HFDir | dict[str] | None = None,
        *,
        force_download: bool = False,
        local_files_only: bool = False,
    ) -> Path:
        if file_dir is None:
            file_dir = HFDir()

        if isinstance(file_dir, dict):
            file_dir = HFDir(**file_dir)

        res = self.api.hf_hub_download(
            repo_id=self.repo_id,
            repo_type=self.repo_type,
            revision=self.revision,
            filename=file_name,
            local_dir=file_dir.local,
            cache_dir=file_dir.cache,
            force_download=force_download,
            local_files_only=local_files_only,
            dry_run=False,
        )

        return Path(res)

    def snapshot_download(
        self,
        folder_dir: HFDir | dict[str] | None = None,
        patterns: HFPatterns | dict[str] | None = None,
        max_workers: int = 8,
        *,
        force_download: bool = False,
        local_files_only: bool = False,
    ) -> Path:
        if folder_dir is None:
            folder_dir = HFDir()

        if isinstance(folder_dir, dict):
            folder_dir = HFDir(**folder_dir)

        if patterns is None:
            patterns = HFPatterns()

        if isinstance(patterns, dict):
            patterns = HFPatterns(**patterns)

        res = self.api.snapshot_download(
            repo_id=self.repo_id,
            repo_type=self.repo_type,
            revision=self.revision,
            local_dir=folder_dir.local,
            cache_dir=folder_dir.cache,
            allow_patterns=patterns.allow,
            ignore_patterns=patterns.ignore,
            max_workers=max_workers,
            force_download=force_download,
            local_files_only=local_files_only,
            dry_run=False,
        )

        return Path(res)
