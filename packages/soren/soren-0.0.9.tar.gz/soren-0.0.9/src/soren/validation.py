import json
import csv
import os
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from soren.schema import JSON_SCHEMAS, CSV_SCHEMAS
from jsonschema import validate, ValidationError

# Allowed media types by extension (simple, extensible)
ALLOWED_EXTENSIONS = {
    ".json": "application/json",
    ".csv": "text/csv",
    ".txt": "text/plain",
}

class ValidationResult(Dict[str, Any]):
    """
    Validation result container.
    Keys:
        - valid: bool
        - schema_id: str | None
        - errors: list[str]
        - media_type: str
    """

def sha256_file(path: str) -> str:
    """Compute SHA256 for a file (small helper)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_json(data: Any) -> Tuple[bool, Optional[str], List[str]]:
    """
    Try each JSON schema; return first match.
    """
    errors: List[str] = []
    for schema_entry in JSON_SCHEMAS:
        schema_id = schema_entry["id"]
        try:
            validate(instance=data, schema=schema_entry["schema"])
            return True, schema_id, []
        except ValidationError as e:
            errors.append(f"{schema_id}: {e.message}")
            continue
    return False, None, errors


def validate_csv(headers: List[str]) -> Tuple[bool, Optional[str], List[str]]:
    """
    Validate CSV headers against known schemas (required_headers subset).
    """
    if not isinstance(headers, list):
        return False, None, ["CSV headers are not a list"]

    errors: List[str] = []
    for schema_entry in CSV_SCHEMAS:
        schema_id = schema_entry["id"]
        required = schema_entry.get("required_headers", set())
        missing = required - set(headers)
        if not missing:
            return True, schema_id, []
        errors.append(f"{schema_id}: missing {', '.join(sorted(missing))}" if missing else f"{schema_id}: ok")
    return False, None, errors


def detect_media_type(path: str) -> Tuple[Optional[str], Optional[str]]:
    """Infer media type from extension."""
    _, ext = os.path.splitext(path.lower())
    media_type = ALLOWED_EXTENSIONS.get(ext)
    return ext if media_type else None, media_type


def validate_file(path: str) -> ValidationResult:
    """
    Validate a file against known schemas. Does not raise; returns a structured result.

    The file is always readable (caller handles upload). Validation determines
    schema_id and validity for downstream processing.
    """
    extension, media_type = detect_media_type(path)
    result: ValidationResult = {
        "valid": False,
        "schema_id": None,
        "errors": [],
        "media_type": media_type or "application/octet-stream",
        "sha256": sha256_file(path),
        "size_bytes": os.path.getsize(path),
    }

    if not media_type or not extension:
        result["errors"] = ["Unsupported file extension"]
        return result

    # Try matching registry entries by media_type in order
    try:
        if media_type == "application/json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            valid, schema_id, errors = validate_json(data)
            if valid:
                result.update({"valid": True, "errors": [], "schema_id": schema_id})
                return result
            result["errors"] = errors
            return result

        if media_type == "text/csv":
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
            valid, schema_id, errors = validate_csv(headers)
            if valid:
                result.update({"valid": True, "errors": [], "schema_id": schema_id})
                return result
            result["errors"] = errors
            return result

        if media_type == "text/plain":
            # Generic text handler
            result.update({"valid": True, "schema_id": "generic_text.v1", "errors": []})
            return result

    except Exception as e:
        result["errors"] = [f"Validation error: {e}"]
        return result

    # If we reach here, treat as unsupported
    result["errors"] = ["Unsupported media type"]
    return result


def build_manifest_entry(file_path: str, relative_path: str) -> Dict[str, Any]:
    """
    Build a manifest entry including validation metadata.
    """
    validation = validate_file(file_path)
    return {
        "path": relative_path,
        "media_type": validation["media_type"],
        "size_bytes": validation["size_bytes"],
        "sha256": validation["sha256"],
        "validation": {
            "valid": validation["valid"],
            "schema_id": validation["schema_id"],
            "errors": validation["errors"],
        },
    }
