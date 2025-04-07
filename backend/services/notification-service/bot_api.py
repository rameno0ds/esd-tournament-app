from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from bot_dm import team_assignment
from bot_dm import new_dispute

app = FastAPI()

class TeamAssignRequest(BaseModel):
    player_name: str
    team_id: str

@app.post("/assign_team")
async def assign_team(request: TeamAssignRequest):
    asyncio.create_task(team_assignment(request.player_name, request.team_id))
    return {"status": "DM scheduled"}

# Notify Moderator Request doing by Ranen
class NotifyModeratorRequest(BaseModel):
    matchId: str
    raisedBy: str

@app.post("/notify_moderator")
async def notify_moderator(request: NotifyModeratorRequest):
    try:
        # Schedule the async task to notify the moderator.
        # You could also await new_dispute(req.matchId, req.raisedBy) if you want to block until complete.
        asyncio.create_task(new_dispute(request.matchId, request.raisedBy))
        return {"message": "Moderator notification scheduled."}
    except Exception as e:
        return {"error": str(e)}


