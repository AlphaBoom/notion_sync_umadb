import requests
import os

from src.notion.notion_obj import *
from src.notion.notion_requests import *

_BASE_URL = "https://api.notion.com/v1"

def _headers():
    vars = globals()
    if '__headers' in globals():
        return vars['__headers']
    else:
        vars['__headers'] = {
            "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        return vars['__headers']


def createPage(request: CreatePageRequest) -> Page:
    _post("pages", data=request.to_json())
    return None

def updatePage(request: UpdatePageRequest) -> Page:
    page_id = request.page_id
    request.page_id = None
    return Page.from_json(_patch(f"pages/{page_id}", data=request.to_json()).text)

def updateBlock(request: UpdateBlockRequest) -> None:
    block_id = request.block_id
    block  = request.block
    _patch(f"blocks/{block_id}", data=block.to_json())
    return None

def appendBlockChildren(block_id: str, children: list[Block]) -> None:
    _patch(f"blocks/{block_id}/children", data=AppendBlockRequest(children=children).to_json())
    return None

def createDatabase(request: CreateDatabaseRequest) -> Database:
    return Database.from_json(_post("databases", data=request.to_json()).text)

def updateDatabase(request: UpdateDatabaseRequest) -> Database:
    database_id = request.database_id
    request.database_id = None
    return Database.from_json(_patch(f"databases/{database_id}", data=request.to_json()).text)


def queryDatabase(database_id: str, start_cursor: str = None, page_size: int = 100, filter: dict = None, sorts: list = None) -> NotionList[Page]:
    params = {
        "page_size": page_size
    }
    if start_cursor is not None:
        params["start_cursor"] = start_cursor
    if filter is not None:
        params["filter"] = filter
    if sorts is not None:
        params["sorts"] = sorts
    return NotionList.from_json(_post(f"databases/{database_id}/query", json=params).text)

def retrieveBlockChildren(block_id: str, start_cursor:str = None, page_size:int = 100) -> NotionList[Block]:
    params = {
        "page_size": page_size
    }
    if start_cursor is not None:
        params["start_cursor"] = start_cursor
    return NotionList.from_json(_get(f"blocks/{block_id}/children", params=params).text)


def retrieveDatabase(database_id: str) -> Database:
    ret = _get(f"databases/{database_id}").text
    return Database.from_json(ret)

def deleteBlock(block_id: str) -> None:
    _delete(f"blocks/{block_id}")


def _get(path, params=None):
    r = requests.get(_BASE_URL + "/" + path, params=params, headers=_headers(),timeout=10)
    if not r:
        print(r.text)
    r.raise_for_status()
    return r


def _post(path, data=None, json=None):
    r = requests.post(_BASE_URL + "/" + path, data=data,
                      json=json, headers=_headers(), timeout=10)
    if not r:
        print(r.text)
    r.raise_for_status()
    return r

def _patch(path, data=None, json=None):
    r = requests.patch(_BASE_URL + "/" + path, data=data, json=json, headers=_headers(), timeout=10)
    if not r:
        print(r.text)
    r.raise_for_status()
    return r

def _delete(path):
    r = requests.delete(_BASE_URL + "/" + path, headers=_headers(), timeout=10)
    if not r:
        print(r.text)
    r.raise_for_status()
    return r
