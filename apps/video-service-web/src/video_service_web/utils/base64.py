import os
import base64
from pathlib import Path
from shared.logger.logger import Logger


class Base64:
    logger = Logger("Base64")

    @staticmethod
    def write_if_missing(file_path: str, env_var: str):
        path = Path(file_path)

        if path.exists():
            Base64.logger.debug(f"{path.name} already exists. Skipping write.")
            return

        base64_str = os.environ.get(env_var)
        if not base64_str:
            raise ValueError(f"{env_var} environment variable is not set")

        try:
            decoded = base64.b64decode(base64_str)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(decoded)
            Base64.logger.success(f"Wrote {env_var} contents to {path}")
        except Exception as e:
            Base64.logger.error(
                f"Failed to decode and write {env_var} to {file_path}: {e}"
            )
            raise
