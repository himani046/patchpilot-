import shutil, tempfile, zipfile
from pathlib import Path, PurePosixPath
from uuid import uuid4
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.config import settings
from app.workflow.orchestrator import investigate
router=APIRouter(); MAX_ENTRIES=2000

def safe_extract(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(archive_path) as archive:
        members=archive.infolist()
        if len(members)>MAX_ENTRIES: raise ValueError("Archive contains too many entries.")
        if sum(x.file_size for x in members)>settings.max_uncompressed_mb*1024*1024: raise ValueError("Expanded archive is too large.")
        for item in members:
            raw=item.filename; rel=PurePosixPath(raw); mode=item.external_attr>>16
            if rel.is_absolute() or ".." in rel.parts or "\\" in raw: raise ValueError("Archive contains an unsafe path.")
            if (mode&0o170000)==0o120000: raise ValueError("Symbolic links are not allowed.")
            if item.file_size>2*1024*1024: raise ValueError("Archive member is too large.")
        for item in members:
            target=destination.joinpath(*PurePosixPath(item.filename).parts); target.resolve().relative_to(destination.resolve())
            if item.is_dir(): target.mkdir(parents=True,exist_ok=True)
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                with archive.open(item) as src, target.open("wb") as dst: shutil.copyfileobj(src,dst,length=1024*1024)

@router.post("/api/investigations")
async def create_investigation(file: UploadFile=File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".zip"): raise HTTPException(status_code=400,detail="Upload a ZIP archive.")
    base=Path(settings.workspace_root).resolve(); base.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix=f"{uuid4()}-",dir=base)); archive_path=staging/"upload.zip"; extract_root=staging/"project"
    try:
        size=0
        with archive_path.open("wb") as out:
            while chunk:=await file.read(1024*1024):
                size+=len(chunk)
                if size>settings.max_upload_mb*1024*1024: raise HTTPException(status_code=413,detail="Archive exceeds upload limit.")
                out.write(chunk)
        try: safe_extract(archive_path,extract_root)
        except (zipfile.BadZipFile,ValueError,OSError) as exc: raise HTTPException(status_code=400,detail=f"Invalid archive: {exc}") from exc
        children=list(extract_root.iterdir()); project_root=children[0] if len(children)==1 and children[0].is_dir() else extract_root
        # For public deployment, move code execution to a dedicated isolated worker queue.
        return investigate(str(project_root))
    finally:
        await file.close(); shutil.rmtree(staging,ignore_errors=True)
