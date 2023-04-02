import requests
from dotenv import load_dotenv
import os

from src.notion.notion_obj import *
from src.notion.notion_requests import *

load_dotenv()

_BASE_URL = "https://api.notion.com/v1"

_headers = {
    "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def createPage(request: CreatePageRequest) -> Page:
    _post("pages", data=request.to_json())
    return None


def createDatabase(request: CreateDatabaseRequest) -> Database:
    return Database.from_json(_post("databases", data=request.to_json()).text)


def queryDatabase(database_id: str, start_cursor: str = None, page_size: int = 100, filter: dict = None, sorts: list = None) -> NotionList:
    params = {
        "page_size": page_size
    }
    if start_cursor is not None:
        params["start_cursor"] = start_cursor
    if filter is not None:
        params["filter"] = filter
    if sorts is not None:
        params["sorts"] = sorts
    return NotionList.from_json(_post(f"databases/{database_id}/query", json=params).text, infer_missing=True)


def retrieveDatabase(database_id: str) -> Database:
    ret = _get(f"databases/{database_id}").text
    return Database.from_json(ret)


def _get(path, params=None):
    r = requests.get(_BASE_URL + "/" + path, params=params, headers=_headers)
    if not r:
        print(r.text)
    r.raise_for_status()
    return r


def _post(path, data=None, json=None):
    r = requests.post(_BASE_URL + "/" + path, data=data,
                      json=json, headers=_headers)
    if not r:
        print(r.text)
    r.raise_for_status()
    return r
