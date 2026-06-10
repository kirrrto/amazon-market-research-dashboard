from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024
MAX_IMPORT_ROWS = 20_000


class TabularImportError(ValueError):
    """Raised when an uploaded spreadsheet cannot be safely imported."""


def _extension(file_name: str) -> str:
    extension = Path(file_name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise TabularImportError(
            f"Unsupported file type '{extension or 'unknown'}'. "
            f"Supported types: {supported}."
        )
    return extension


def _validate_payload(content: bytes) -> None:
    if not content:
        raise TabularImportError("The uploaded file is empty.")
    if len(content) > MAX_FILE_SIZE_BYTES:
        limit_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise TabularImportError(
            f"The uploaded file exceeds the {limit_mb} MB project limit."
        )


def _excel_engine(extension: str) -> str:
    if extension == ".xlsx":
        return "openpyxl"
    if extension == ".xls":
        return "xlrd"
    raise TabularImportError(f"No Excel engine for extension: {extension}")


def _clean_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        raise TabularImportError("The selected file or worksheet contains no data.")

    frame = frame.copy()
    frame = frame.dropna(axis=0, how="all")
    frame = frame.dropna(axis=1, how="all")

    if frame.empty or len(frame.columns) == 0:
        raise TabularImportError("The selected file or worksheet contains no data.")
    if len(frame) > MAX_IMPORT_ROWS:
        raise TabularImportError(
            f"The worksheet contains {len(frame):,} rows; "
            f"the current limit is {MAX_IMPORT_ROWS:,} rows."
        )

    frame.columns = [str(column).strip() for column in frame.columns]
    blank_columns = [column for column in frame.columns if not column]
    if blank_columns:
        raise TabularImportError("One or more columns have an empty header.")

    return frame.reset_index(drop=True)


def _read_csv(content: bytes) -> pd.DataFrame:
    attempts: list[str] = []
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return pd.read_csv(BytesIO(content), encoding=encoding)
        except UnicodeDecodeError:
            attempts.append(encoding)
        except pd.errors.ParserError as exc:
            raise TabularImportError(f"Unable to parse CSV file: {exc}") from exc

    raise TabularImportError(
        "Unable to decode CSV file. Tried encodings: " + ", ".join(attempts)
    )


def list_worksheets(file_name: str, content: bytes) -> list[str]:
    """Return worksheet names for Excel files; CSV files return an empty list."""

    _validate_payload(content)
    extension = _extension(file_name)
    if extension == ".csv":
        return []

    engine = _excel_engine(extension)
    try:
        with pd.ExcelFile(BytesIO(content), engine=engine) as workbook:
            names = [str(name) for name in workbook.sheet_names]
    except ImportError as exc:
        raise TabularImportError(
            f"Reading {extension} files requires the '{engine}' package."
        ) from exc
    except (ValueError, OSError, KeyError) as exc:
        raise TabularImportError(f"Unable to open Excel workbook: {exc}") from exc

    if not names:
        raise TabularImportError("The Excel workbook contains no worksheets.")
    return names


def read_tabular_file(
    file_name: str,
    content: bytes,
    worksheet: str | None = None,
) -> pd.DataFrame:
    """Read CSV, XLSX or XLS content into a bounded DataFrame."""

    _validate_payload(content)
    extension = _extension(file_name)

    if extension == ".csv":
        return _clean_frame(_read_csv(content))

    engine = _excel_engine(extension)
    try:
        available_sheets = list_worksheets(file_name, content)
        selected_sheet = worksheet or available_sheets[0]
        if selected_sheet not in available_sheets:
            raise TabularImportError(
                f"Worksheet '{selected_sheet}' does not exist. "
                f"Available worksheets: {', '.join(available_sheets)}."
            )
        frame = pd.read_excel(
            BytesIO(content),
            sheet_name=selected_sheet,
            engine=engine,
        )
    except TabularImportError:
        raise
    except ImportError as exc:
        raise TabularImportError(
            f"Reading {extension} files requires the '{engine}' package."
        ) from exc
    except (ValueError, OSError, KeyError) as exc:
        raise TabularImportError(
            f"Unable to read worksheet '{worksheet or ''}': {exc}"
        ) from exc

    return _clean_frame(frame)
