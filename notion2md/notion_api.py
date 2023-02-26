import os

from notion_client import Client

from notion2md.exceptions import MissingTokenError


def singleton(cls):
    instance = {}

    def get_instance():
        if cls not in instance:
            instance[cls] = cls()
        return instance[cls]

    return get_instance


@singleton
class NotionClient:
    def __init__(self):
        token = self._get_env_variable()
        self._client = Client(auth=token)

    def _get_env_variable(self):
        try:
            return os.environ["NOTION_TOKEN"]
        except Exception:
            raise MissingTokenError() from None

    def get_children(self, parent_id):
        # Most pages are small
        results = []
        start_cursor = None
        # Avoid infinite loops
        for _ in range(100):
            resp = self._client.blocks.children.list(parent_id, start_cursor=start_cursor, page_size=100)
            results.extend(resp["results"])
            start_cursor = resp["next_cursor"] if resp["has_next"] else None
            if start_cursor is None:
                return results
        raise Exception(f"Can't parse notion page of > 10,000 children! (e.g. blocks)")