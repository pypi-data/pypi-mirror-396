from __future__ import annotations
from typing import Type, TypeVar

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SettingsConfigDict = SettingsConfigDict  # used as transitive import
Field = Field  # used as transitive import

ConfigType = TypeVar("ConfigType", bound="BaseConfig")


class BaseConfig(BaseSettings):

    @classmethod
    def find_config_file(cls, directory: Path, name: str) -> Path | None:
        for parent in [directory] + list(directory.parents):
            config_path = parent / name
            if config_path.exists():
                return config_path
            for sub in sorted(parent.iterdir()):
                if sub.is_dir():
                    config_path = sub / name
                    try:
                        exists = config_path.exists()
                    except PermissionError:
                        exists = False
                    if exists:
                        return config_path
        return None

    @classmethod
    def used_env_vars(cls) -> list[tuple[str, str | None]]:
        env_vars = []
        prefix = cls.model_config.get("env_prefix", "")
        for name, field in cls.model_fields.items():
            env_name = f"{prefix}{name}"
            env_vars.append((env_name, field.description))
        return env_vars

    @classmethod
    def from_file(
        cls: Type[ConfigType], path: str | Path, ensure_exists: bool = False
    ) -> ConfigType:
        path = Path(path)
        if ensure_exists and not path.exists():
            raise FileExistsError(path)
        config = cls(_env_file=path.resolve())
        return config

    def to_file(
        self, path: str | Path, allow_overwrite: bool = False, header_text: str = ""
    ):
        header_text = header_text or "tgzr config file"
        lines = [
            f"# {header_text}",
            "",
        ]
        prefix = self.model_config.get("env_prefix", "")
        for name, value in self.model_dump(
            exclude_unset=True,
            exclude_defaults=True,
            exclude_none=True,
            exclude_computed_fields=True,
        ).items():
            lines.append(f"{prefix}{name}={value!r}")

        content = "\n".join(lines)

        path = Path(path)
        if path.exists() and not allow_overwrite:
            raise FileExistsError(path.resolve())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as fp:
            fp.write(content)
