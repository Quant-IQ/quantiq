from typing import Dict, Any
from fastapi import APIRouter

router = APIRouter()

@router.get("/signals/live")
def get_live_signals() -> Dict[str, Any]:
    """Returns empty list. Blocked on scripting team's logger completion."""
    return {"signals": []}
