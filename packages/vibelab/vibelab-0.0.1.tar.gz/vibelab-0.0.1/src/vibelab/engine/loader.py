"""Code loader for scenarios."""

import os
import subprocess
import tempfile
from pathlib import Path

from ..models.scenario import CodeType, GitHubCodeRef, LocalCodeRef, Scenario


class CodeLoader:
    """Loads code for scenarios."""

    def load(self, scenario: Scenario, workdir: Path) -> None:
        """Load code into workdir based on scenario type."""
        if scenario.code_type == CodeType.GITHUB:
            self._load_github(scenario.code_ref, workdir)  # type: ignore
        elif scenario.code_type == CodeType.LOCAL:
            self._load_local(scenario.code_ref, workdir)  # type: ignore
        elif scenario.code_type == CodeType.EMPTY:
            self._load_empty(workdir)
        else:
            raise ValueError(f"Unknown code type: {scenario.code_type}")

    def _load_github(self, code_ref: GitHubCodeRef, workdir: Path) -> None:
        """Clone GitHub repository."""
        url = f"https://github.com/{code_ref.owner}/{code_ref.repo}.git"
        subprocess.run(
            ["git", "clone", url, str(workdir)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", code_ref.commit_sha],
            cwd=workdir,
            check=True,
            capture_output=True,
        )

    def _load_local(self, code_ref: LocalCodeRef, workdir: Path) -> None:
        """Copy local directory."""
        import shutil

        source = Path(code_ref.path).expanduser()
        if not source.exists():
            raise ValueError(f"Local path does not exist: {source}")
        shutil.copytree(source, workdir, dirs_exist_ok=True)

    def _load_empty(self, workdir: Path) -> None:
        """Create empty directory."""
        workdir.mkdir(parents=True, exist_ok=True)
