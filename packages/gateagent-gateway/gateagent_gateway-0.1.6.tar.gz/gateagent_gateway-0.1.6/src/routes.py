# gate/ext/routes.py

from fastapi import APIRouter
from models import TrackEvent, StoredEvent, AgentRegistration
from db import insert_event, list_events, register_agent, list_agents
from google_oauth import get_auth_url, load_tokens
import json

router = APIRouter()

# ------------------------------
# Healthcheck
# ------------------------------

@router.get("/healthcheck")
def healthcheck():
    return {"ok": True}

# ------------------------------
# Track Events
# ------------------------------

@router.post("/track")
def track_event(event: TrackEvent):
    insert_event(event)
    return {"ok": True}


# ------------------------------
# Fetch Events
# ------------------------------

@router.get("/events")
def get_events(limit: int = 200):
    rows = list_events(limit)

    result: list[StoredEvent] = []
    for r in rows:
        id_, event, agent, action, timestamp, success, created_at, affected_apps_json = r
        
        affected_apps = []
        if affected_apps_json:
            try:
                affected_apps = json.loads(affected_apps_json)
            except:
                pass

        result.append(StoredEvent(
            id=id_,
            event=event,
            agent=agent,
            action=action,
            timestamp=timestamp,
            success=bool(success) if success is not None else None,
            created_at=created_at,
            affected_apps=affected_apps
        ))

    return result

# ------------------------------
# Agents
# ------------------------------

@router.post("/agents/register")
def register_agent_endpoint(agent: AgentRegistration):
    register_agent(agent)
    return {"ok": True}

@router.get("/agents")
def get_agents():
    return list_agents()


# ------------------------------
# Google OAuth (via hosted auth service)
# ------------------------------

@router.get("/auth/google/url")
def google_auth_url():
    """Return the Google OAuth URL provided by the hosted auth service."""
    return {"auth_url": get_auth_url()}


@router.get("/auth/google/status")
def google_auth_status():
    """Check if this gateway has a valid Google OAuth session via the auth service."""
    tokens = load_tokens()
    return {"authorized": bool(tokens)}
