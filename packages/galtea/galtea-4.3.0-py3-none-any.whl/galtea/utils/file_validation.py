import math
import os
import zipfile
from typing import List

# Constants for validation
MB: int = 1024 * 1024

KNOWLEDGE_BASE_MAX_SIZE: int = 100 * MB
EXISTING_TEST_MAX_SIZE: int = 10 * MB
ZIP_MAX_FILES: int = 1000

KNOWLEDGE_BASE_ALLOWED_EXTENSIONS: List[str] = [
    ".txt",
    ".yaml",
    ".yml",
    ".md",
    ".json",
    ".xml",
    ".pdf",
    ".html",
    ".docx",
    ".zip",
]

ZIP_ALLOWED_EXTENSIONS: List[str] = [
    ".txt",
    ".yaml",
    ".yml",
    ".md",
    ".json",
    ".xml",
    ".pdf",
    ".html",
]

EXISTING_TEST_ALLOWED_EXTENSIONS: List[str] = [".csv"]


def format_bytes(size: float, decimals: int = 2) -> str:
    """Format bytes to human-readable format."""
    if size == 0:
        return "0 Bytes"

    k = 1024
    dm = decimals if decimals >= 0 else 0
    sizes = ["Bytes", "KB", "MB", "GB", "TB"]

    i = math.floor(math.log(size) / math.log(k))

    return f"{size / pow(k, i):.{dm}f} {sizes[i]}"


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def is_extension_allowed(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file extension is allowed."""
    extension = get_file_extension(filename)
    return extension in allowed_extensions


def validate_file_size(file_path: str, max_size: int) -> None:
    """Validate file size."""
    size = os.path.getsize(file_path)
    if size > max_size:
        raise ValueError(
            f"File size ({format_bytes(size)}) exceeds the maximum allowed size of {format_bytes(max_size)}"
        )


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> None:
    """Validate file extension."""
    if not is_extension_allowed(filename, allowed_extensions):
        extensions_list = ", ".join(allowed_extensions)
        raise ValueError(f"File type not allowed. Allowed types: {extensions_list}")


def is_zip_file(filename: str) -> bool:
    """Check if file is a ZIP file."""
    return get_file_extension(filename) == ".zip"


def validate_zip_contents(file_path: str) -> None:
    """Validate ZIP file contents."""
    try:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            # Filter out directories
            file_entries = [info for info in zip_ref.infolist() if not info.is_dir()]

            if not file_entries:
                raise ValueError("ZIP file is empty or contains only directories")

            if len(file_entries) > ZIP_MAX_FILES:
                raise ValueError(
                    f"ZIP file contains {len(file_entries)} files, but the maximum allowed is {ZIP_MAX_FILES}"
                )

            # Check each file's extension
            invalid_files = [
                entry.filename
                for entry in file_entries
                if not is_extension_allowed(entry.filename, ZIP_ALLOWED_EXTENSIONS)
            ]

            if invalid_files:
                invalid_files_list = ", ".join(invalid_files[:5])
                more_files = len(invalid_files) > 5
                prefix = "Some are: " if more_files else "They are: "
                suffix = "..." if more_files else ""
                allowed_str = ", ".join(ZIP_ALLOWED_EXTENSIONS)

                raise ValueError(
                    f"ZIP contains {len(invalid_files)} files with invalid extensions. "
                    f"{prefix}{invalid_files_list}{suffix}. Allowed types: {allowed_str}"
                )

    except zipfile.BadZipFile as e:
        raise ValueError(f"Failed to read ZIP file: {e}") from e


def validate_knowledge_base_file(file_path: str) -> None:
    """Validate Knowledge Base file (Ground Truth)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    filename = os.path.basename(file_path)

    # Check file extension
    validate_file_extension(filename, KNOWLEDGE_BASE_ALLOWED_EXTENSIONS)

    # Check file size
    validate_file_size(file_path, KNOWLEDGE_BASE_MAX_SIZE)

    # If it's a ZIP file, validate its contents
    if is_zip_file(filename):
        validate_zip_contents(file_path)


def validate_existing_test_file(file_path: str) -> None:
    """Validate Existing Test file (CSV)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    filename = os.path.basename(file_path)

    # Check file extension
    validate_file_extension(filename, EXISTING_TEST_ALLOWED_EXTENSIONS)

    # Check file size
    validate_file_size(file_path, EXISTING_TEST_MAX_SIZE)
