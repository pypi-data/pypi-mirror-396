"""
Build hook to vendor backend API models into the client package during packaging.
"""

from pathlib import Path
import shutil
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Copy backend API model files into the client package for wheel/sdist builds."""

    def initialize(self, version, build_data):
        project_root = Path(self.root)
        # Prefer vendored api_models inside the project (for builds from an sdist),
        # and fall back to the monorepo backend path when available.
        bundled_backend = project_root / "src" / "cat" / "cafe" / "api_models"
        repo_backend = project_root.parent.parent / "src" / "cat" / "cafe" / "api_models"
        backend_root = bundled_backend if bundled_backend.exists() else repo_backend
        target_root = project_root / "src" / "cat" / "cafe" / "api_models"

        self._created = False

        if not backend_root.exists():
            print(f"⚠️ Backend api_models not found at {backend_root}, skipping copy")
            return

        # When building from an sdist, the backend files are already present in target_root.
        # Avoid copying a directory onto itself (which raises in copytree).
        if backend_root.resolve() == target_root.resolve():
            build_data.setdefault("artifacts", []).append("src/cat/cafe/api_models")
            return

        if not target_root.exists():
            self._created = True
            target_root.mkdir(parents=True, exist_ok=True)

        shutil.copytree(backend_root, target_root, dirs_exist_ok=True)

        # Ensure packaged artifacts include the vendored files
        build_data.setdefault("artifacts", []).append("src/cat/cafe/api_models")

    def finalize(self, version, build_data, artifact_path):
        if getattr(self, "_created", False):
            target_root = Path(self.root) / "src" / "cat" / "cafe" / "api_models"
            shutil.rmtree(target_root, ignore_errors=True)
