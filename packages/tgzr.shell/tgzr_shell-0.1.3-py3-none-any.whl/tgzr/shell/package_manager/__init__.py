import os
import platform
from pathlib import Path
import subprocess
import importlib.metadata
import tempfile
import json

import uv


class Venv:
    def __init__(self, path: Path) -> None:
        self._path = path
        if platform.system() == "Windows":
            self._bin_path = self._path / "Scripts"
        else:
            self._bin_path = self._path / "bin"

    @property
    def path(self) -> Path:
        return self._path

    def exists(self) -> bool:
        return self.path.exists() and self._bin_path.exists()

    def create(self, prompt: str | None = None, clear_existing: bool = False):
        uv_exe = uv.find_uv_bin()

        prompt_option = ""
        if prompt:
            prompt_option = f"--prompt {prompt}"

        clear_option = ""
        if clear_existing:
            clear_option = f"--clear"

        cmd = f"{uv_exe} venv --seed {clear_option} {prompt_option} {self.path}"
        print(f"Creating venv {self.path}: {cmd}")
        os.system(cmd)

    def get_exe(self, name: str):
        exe = self._bin_path / name
        if platform.system() == "Windows":
            # the '.exe' suffix is not needed to execute
            # but the caller may want to use `exe.exists()``
            # so we need to add the extension if on windows :/
            exe_suffix = exe.with_suffix(".exe")
            if exe_suffix.exists():
                # special case for .bat files
                exe = exe_suffix
        return exe

    def install_uv(self):
        return self.install_packages("uv", use_uv=False)

    def install_packages(
        self,
        requirements,
        update: bool = True,
        use_uv: bool = True,
        index: str | None = None,
        find_links: str | None = None,
        allow_prerelease: bool = False,
    ) -> bool:
        """
        Returns True if the package has been successfully installed.

        if `index` is given, it will be passed to pip:
            - as -f/--find-links it it is a path (Note: relative path are discouraged).
            - as -i/--index-url otherwise
        """
        if use_uv:
            # NB: we're using python -m uv instead of uv directly so that uv pip installs in the same env
            # see "If uv is installed in a Python environment" in https://docs.astral.sh/uv/pip/environments/#using-arbitrary-python-environments
            exe = f'{self.get_exe("python")} -m uv pip'
        else:
            exe = f'{self.get_exe("python")} -m pip'

        index_flags = ""
        if index is not None:
            if "://" in index:
                index_flags = f"--default-index {index}"
            else:
                index_flags = f"--find-links {index}"

        find_links_options = ""
        if find_links:
            find_links_options = f"--find-links {find_links}"

        prerelease_options = ""
        if allow_prerelease:
            prerelease_options = "--prerelease=allow"

        update_flag = ""
        if update:
            update_flag = "-U"

        cmd = f"{exe} install {index_flags} {update_flag} {find_links_options} {prerelease_options} {requirements}"
        print(f"Installing package(s) {requirements}: {cmd}")
        ret = os.system(cmd)
        return not ret

    def execute_cmd(self, cmd: str) -> bool:
        """
        Returns True if the command was been successfully executed.
        """
        print("Executing venv cmd:", cmd)
        ret = os.system(cmd)
        return not ret

    def get_cmd_output(self, cmd_name: str, cmd_args: list[str]) -> tuple[str, str]:
        """
        Returns the stdout and stderr of a the command.
        """
        # TODO: thread this.
        exe = str(self.get_exe(cmd_name))
        # subprocess.Popen(text=True)
        result = subprocess.run(
            [exe] + cmd_args, capture_output=True, check=True, text=True
        )
        print("CMD", " ".join([exe] + cmd_args), "->", result.returncode)
        return result.stdout, result.stderr

    def run_cmd(self, cmd_name: str, cmd_args: list[str]) -> bool:
        """
        Returns True if the command was been successfully executed.
        """
        # TODO: thread this.
        exe = self.get_exe(cmd_name)
        cmd = str(exe) + " " + " ".join(cmd_args)
        return self.execute_cmd(cmd)

    def get_cmd_names(self) -> list[str]:
        raise NotImplementedError()

    def get_packages(self) -> list[tuple[str, str, str]]:
        stdout, stderr = self.get_cmd_output(
            cmd_name="uv",
            # cmd_args=["pip", "tree", "-d", "0"],
            cmd_args=["pip", "list", "--format", "json"],
        )
        try:
            data = json.loads(stdout)
        except Exception as err:
            raise ValueError(f"Error parsing pip list output: {err}")
        ret = []
        for entry in data:
            ret.append(
                (
                    entry["name"],
                    entry["version"],
                    entry.get("editable_project_location"),
                )
            )
        return ret

    def get_plugins(
        self, group_filter: str | None
    ) -> list[importlib.metadata.EntryPoint]:
        cmd_args = ["studio", "plugins-here", "--format", "json"]
        if group_filter:
            cmd_args.extend(["--group-filter", group_filter])
        stdout, stderr = self.get_cmd_output("tgzr", cmd_args)
        # print("???", [stdout, stderr])
        stdout = stdout.split(">>> JSON:", 1)[-1]

        data = json.loads(stdout)
        # print("-->", data)
        ret = []
        for entry in data:
            # print(entry)
            ep = importlib.metadata.EntryPoint(
                entry["name"], entry["value"], entry["group"]
            )
            ep.module
            ret.append(ep)
        return ret


class PackageManager:
    def __init__(self, root: Path) -> None:
        self._root = root

    @property
    def root(self) -> Path:
        return self._root

    def get_venv(self, venv_name: str, group: str) -> Venv:
        return Venv(self.root / group / venv_name)

    def _create_bat_shortcut(self, exe_path: Path | str, shortcut_path: Path | str):
        exe_path = Path(exe_path)
        if not exe_path.is_absolute() and not str(exe_path).startswith("./"):
            exe_path = f".\\{exe_path}"

        shortcut_path = Path(shortcut_path)
        if shortcut_path.suffix != ".bat":
            shortcut_path = f"{shortcut_path}.bat"

        content = [
            "@echo off",
            f"REM Shortcut to {exe_path}",
            "",
            f"{exe_path} %*",
        ]
        with open(shortcut_path, "w") as fp:
            fp.write("\n".join(content))

    def create_shortcut(
        self, exe_path: Path | str, shortcut_path: Path | str, relative: bool = True
    ):
        """
        Create a shortcut to exe_path at shortcut_path.

        If `relative` is True, `exe_path` will be modified to be relative
        to `shortcut_path`.

        The shortcut will be a symlink to the exe, unless the OS does not
        allow it in which case a .bat file is created.
        """
        if relative:
            exe_path = Path(exe_path).relative_to(Path(shortcut_path).parent)

        if platform.system() == "Linux":
            os.symlink(exe_path, shortcut_path, target_is_directory=False)
        else:
            self._create_bat_shortcut(exe_path, shortcut_path)

    def create_venv(
        self,
        venv_name: str,
        group: str,
        exist_ok: bool = False,
        prompt: str | None = None,
    ) -> Venv:
        venv = self.get_venv(venv_name, group)
        if venv.exists() and not exist_ok:
            raise ValueError(f"Virtual Env {venv.path} already exists!")

        venv.create(prompt, clear_existing=exist_ok)
        venv.install_uv()
        return venv
