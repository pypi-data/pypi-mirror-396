from __future__ import annotations

import mimetypes
import subprocess
from enum import Enum
from pathlib import Path
from typing import Generator

from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from remotivelabs.cli.topology.cli.topology_cli import run_topology

router = APIRouter(prefix="/api/v1/files", tags=["files"])


class FileType(str, Enum):
    FOLDER = "FILE_TYPE_FOLDER"
    INSTANCE = "FILE_TYPE_INSTANCE"
    PLATFORM = "FILE_TYPE_PLATFORM"
    RECORDING_SESSION = "FILE_TYPE_RECORDING_SESSION"
    RECORDING_MAPPING = "FILE_TYPE_RECORDING_MAPPING"
    RECORDING = "FILE_TYPE_RECORDING"
    VIDEO = "FILE_TYPE_VIDEO"
    AUDIO = "FILE_TYPE_AUDIO"
    IMAGE = "FILE_TYPE_IMAGE"
    UNKNOWN = "FILE_TYPE_UNKNOWN"
    SIGNAL_DATABASE = "FILE_TYPE_SIGNAL_DATABASE"


class ListFilesFile(BaseModel):
    path: str
    type: FileType
    size: int | None
    modified_time: int
    created_time: int


class ListFilesResponse(BaseModel):
    files: list[ListFilesFile]


class PathError(BaseModel):
    message: str
    path: str


def describe_path(root: Path, p: Path) -> ListFilesFile:
    path = "/" + str(p.relative_to(root))
    stat = p.stat()
    file_type = get_file_type(p)
    if file_type == FileType.FOLDER:
        return ListFilesFile(
            path=path,
            type=file_type,
            size=None,
            modified_time=int(stat.st_mtime),
            created_time=int(stat.st_ctime),
        )
    return ListFilesFile(
        path=path,
        type=file_type,
        size=stat.st_size,
        modified_time=int(stat.st_mtime),
        created_time=int(stat.st_ctime),
    )


@router.get("/topology")
def topology_file(
    request: Request,
    path: str = Query(..., description="File path to show topology"),
) -> Response:
    file_path = join_under(request.app.state.topology.workspace, Path(path))
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=PathError(message="File not found", path=str(file_path)).model_dump())
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail=PathError(message="Not a file", path=str(file_path)).model_dump())
    try:
        result = run_topology(request.app.state.topology, ["show", "topology", str(file_path)])
        # TODO: use file output instead of stdout
        return Response(content=result.stdout, media_type="application/yaml")
    except subprocess.CalledProcessError as e:
        if e.stderr:
            raise HTTPException(status_code=400, detail=e.stderr)
        if e.stdout:
            raise HTTPException(status_code=400, detail=e.stdout)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/download")
def download_file(
    request: Request,
    path: str = Query(..., description="File path to download"),
    range: str | None = Header(None),
) -> StreamingResponse:
    file_path = join_under(request.app.state.topology.workspace, Path(path))
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=PathError(message="File not found", path=str(file_path)).model_dump())
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail=PathError(message="Not a file", path=str(file_path)).model_dump())

    file_size = file_path.stat().st_size
    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = "application/octet-stream"

    start = 0
    end = file_size - 1

    if range:
        range_match = range.replace("bytes=", "").split("-")
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1

    chunk_size = 1024 * 1024  # 1MB chunks

    def iter_file() -> Generator[bytes, None, None]:
        with open(file_path, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                read_size = min(chunk_size, remaining)
                data = f.read(read_size)
                if not data:
                    break
                remaining -= len(data)
                yield data

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
        "Content-Disposition": f'inline; filename="{file_path.name}"',
    }

    status_code = 206 if range else 200
    return StreamingResponse(iter_file(), status_code=status_code, media_type=content_type, headers=headers)


@router.get("")
def list_files(
    request: Request,
    path: str = Query(..., description="Directory path to list files from"),
    include_hidden: bool = Query(False, description="Whether to include hidden files"),
) -> ListFilesResponse:
    try:
        root = join_under(request.app.state.topology.workspace, Path(path))
    except ValueError:
        raise HTTPException(status_code=400, detail=PathError(message="Invalid path", path=path).model_dump())

    if not root.exists():
        raise HTTPException(status_code=404, detail=PathError(message="Path not found", path=str(root)).model_dump())
    if not root.is_dir():
        raise HTTPException(status_code=400, detail=PathError(message="Path is not a directory", path=str(root)).model_dump())

    files = [describe_path(request.app.state.topology.workspace, p) for p in root.iterdir() if include_hidden or not p.name.startswith(".")]

    return ListFilesResponse(files=files)


def join_under(root: Path, child: Path) -> Path:
    root = Path(root).resolve()
    child = Path(child).relative_to(Path(child).anchor or ".")

    # Combine and resolve
    final = (root / child).resolve()

    # Security check: final must be inside root
    if root not in final.parents and final != root:
        raise HTTPException(
            status_code=400, detail=PathError(message="E024: Trying to access file outside of workspace", path=str(child)).model_dump()
        )

    return final


def get_file_type(path: Path) -> FileType:  # noqa: PLR0911
    if path.is_dir():
        return FileType.FOLDER

    name = path.name
    if name.endswith(".instance.yaml"):
        return FileType.INSTANCE
    if name.endswith(".platform.yaml"):
        return FileType.PLATFORM
    if name.endswith(".recordingsession.yaml"):
        return FileType.RECORDING_SESSION
    if name.endswith(".mapping.yaml"):
        return FileType.RECORDING_MAPPING
    if name.endswith(".dbc") or name.endswith(".arxml") or name.endswith(".ldf"):
        return FileType.SIGNAL_DATABASE
    if name.endswith(".log"):
        return FileType.RECORDING
    if name.endswith(".mp4"):
        return FileType.VIDEO

    return FileType.UNKNOWN
