import base64
import logging
import os
import tempfile
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path


class FileUtils:
    @staticmethod
    def save_base64_file(
        b64_string: str,
        file_name: str,
        allow_types: set[str] | list[str],
        prefix: str = "clappia_file_",
    ) -> tuple[Path, str]:
        if "," not in b64_string:
            raise ValueError("Invalid base64 string format: expected data URI format")

        header, data = b64_string.split(",", 1)
        mime_type = header.replace("data:", "").replace(";base64", "")

        allow_types_set = (
            set(allow_types) if isinstance(allow_types, list) else allow_types
        )
        if mime_type not in allow_types_set:
            raise ValueError(
                f"Invalid file type: {mime_type}. Allowed types: {allow_types_set}"
            )

        try:
            file_bytes = base64.b64decode(data, validate=True)
        except Exception as e:
            raise ValueError(f"Invalid base64 data: {e!s}") from e

        unique_id = uuid.uuid4().hex
        file_extension = file_name.split(".")[-1] if "." in file_name else ""
        suffix = f"_{unique_id}.{file_extension}" if file_extension else f"_{unique_id}"
        temp_file_fd, file_path_str = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        os.close(temp_file_fd)

        file_path = Path(file_path_str)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return file_path, mime_type

    @staticmethod
    def save_text_file(
        text_content: str,
        file_name: str,
        mime_type: str = "text/html",
        prefix: str = "clappia_file_",
    ) -> tuple[Path, str]:
        unique_id = uuid.uuid4().hex
        file_extension = file_name.split(".")[-1] if "." in file_name else ""
        suffix = f"_{unique_id}.{file_extension}" if file_extension else f"_{unique_id}"
        temp_file_fd, file_path_str = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        os.close(temp_file_fd)

        file_path = Path(file_path_str)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        return file_path, mime_type

    @staticmethod
    @contextmanager
    def temporary_files(*file_paths: Path | None) -> Generator[None, None, None]:
        try:
            yield
        finally:
            for file_path in file_paths:
                if file_path and file_path.exists():
                    try:
                        file_path.unlink()
                    except Exception as e:
                        logging.warning(
                            f"Failed to delete temporary file {file_path}: {e}"
                        )
