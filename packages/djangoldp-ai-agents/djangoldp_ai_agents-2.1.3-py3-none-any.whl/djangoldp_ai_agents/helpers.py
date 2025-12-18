from typing import Dict, List

from pydantic import BaseModel


class ObjectList(BaseModel):
    items: List[Dict]
