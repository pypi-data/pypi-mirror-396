"""Hatchling build hook to include frontend static files."""

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Build hook to copy frontend dist files into package."""

    def initialize(self, version: str, build_data: dict) -> None:
        """Copy web/dist files into the package."""
        from pathlib import Path
        import shutil

        # Get project root (parent of src)
        project_root = Path(__file__).parent.parent.parent
        web_dist = project_root / "web" / "dist"
        
        # Target is in the package directory (vibelab/web/dist)
        target_dir = Path(__file__).parent / "web" / "dist"

        # Copy dist files if they exist
        if web_dist.exists() and web_dist.is_dir():
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(web_dist, target_dir)
            if hasattr(self, "app"):
                self.app.display_info("Copied frontend dist files to package")
        else:
            if hasattr(self, "app"):
                self.app.display_warning(f"Frontend dist not found at {web_dist}, skipping static files")

