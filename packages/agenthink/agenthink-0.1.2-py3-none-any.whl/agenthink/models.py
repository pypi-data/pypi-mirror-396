from pydantic import BaseModel
from typing import List, Optional

class ConnectionRequest(BaseModel):
    query: str
    user_id: str
    session_id: str
    workflow_id: str
    datastore: Optional[List] = []
    tools: Optional[List] = []
