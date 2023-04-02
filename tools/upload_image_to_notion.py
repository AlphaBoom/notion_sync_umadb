from notion.block import Block
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
import hashlib
import mimetypes
import requests
import re

Meta = Dict[str, str]
FileType = Union[str, Path]

class NotionError(Exception):
    """Exception raised when a Notion related critical error occurs."""

def get_file_sha256(file_path: Path) -> str:
    hash_sha256 = hashlib.sha256()
    chunk_size = 4096

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):  # noqa: WPS426
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def upload_filetype(parent: Block, filetype: FileType) -> Tuple[str, Meta]:
    if isinstance(filetype, Path):
        url, meta = upload_file(parent, filetype)
    else:
        url = filetype
        meta = {"type": "url", "url": filetype}

    return url, meta


def upload_file(block: Block, file_path: Path) -> Tuple[str, Meta]:
    file_url = _upload_file(block, file_path)

    file_id = get_file_id(file_url)
    if file_id is None:
        raise NotionError(f"Could not upload file {file_path}")

    return file_url, {
        "type": "file",
        "file_id": file_id,
        "sha256": get_file_sha256(file_path),
    }


def _upload_file(block: Block, file_path: Path) -> str:
    file_mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"

    post_data = {
        "bucket": "secure",
        "name": file_path.name,
        "contentType": file_mime,
        "record": {
            "table": "block",
            "id": block.id,
            "spaceId": block.space_info["spaceId"],
        },
    }

    upload_data = block._client.post("getUploadFileUrl", post_data).json()

    with open(file_path, "rb") as f:
        requests.put(
            upload_data["signedPutUrl"],
            data=f,
            headers={"Content-type": file_mime},
        ).raise_for_status()

    return str(upload_data.get("url", ""))


def get_file_id(image_url: str) -> Optional[str]:
    match = re.search("secure.notion-static.com/([^/]+)", image_url)
    if match:
        return match[1]
    return None


def is_meta_different(
    image: Optional[FileType],
    image_url: Optional[str],
    image_meta: Optional[Meta],
) -> bool:
    if not all([image_meta, image_url, image]):
        return True

    if isinstance(image, Path) and image_url is not None and image_meta is not None:
        return _is_file_meta_different(image, image_url, image_meta)

    elif image_meta != {"type": "url", "url": image}:
        return True

    return False


def _is_file_meta_different(image: Path, image_url: str, image_meta: Meta) -> bool:
    if image_meta["type"] != "file":
        return True

    if image_meta["file_id"] != get_file_id(image_url):
        return True

    return image_meta["sha256"] != get_file_sha256(image)

if __name__ == "__main__":
    from notion.client import NotionClient
    from dotenv import load_dotenv
    import json
    import os

    load_dotenv()
    client = NotionClient(token_v2=os.getenv("NOTION_TOKEN"))
    block = client.get_block(os.getenv("UPLOAD_FILE_BLOCK_LINK"))
    mapping = {}
    for root, dirs, files in os.walk("tools/images/skill_icon"):
        for file in files:
            file_path = Path(root) / file
            print(f"Uploading {file_path}...")
            mapping[file] = upload_file(block, file_path)
            with open("output/image_upload.log","a") as f:
                f.write(f"{file} {mapping[file]}")
                f.write('\n')
    with open("output/image_upload.json", "w") as f:
        json.dump(mapping, f, indent=4)