from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from bot_functions import team_assignment
from bot_functions import new_dispute
from bot_functions import match_making
from bot_functions import resolution_result

app = FastAPI()

#notify player request
class TeamAssignRequest(BaseModel):
    player_name: str
    team_id: str

@app.post("/assign_team")
async def assign_team(request: TeamAssignRequest):
    try:
        asyncio.create_task(team_assignment(request.player_name, request.team_id))
        return {"message": "Player notification scheduled"}
    except Exception as e:
        return {"error": str(e)}    

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

# display match schedule   
class displayMatchRequest(BaseModel):
    tournament_id: str
    team_a: str
    team_b: str
    scheduled_time: str

@app.post("/displayMatch")
async def displayMatch(request: displayMatchRequest):
    try:
        asyncio.create_task(match_making(request.tournament_id, request.team_a, request.team_b, request.scheduled_time))
        return {"message": "Display Match scheduled"}
    except Exception as e:
        return {"error": str(e)}

# notify dispute outcome   
class disputeOutcomeRequest(BaseModel):
    player_name: str
    match_id: str
    score: list
    result: str

@app.post("/dispute_outcome")
async def display_outcome(request: disputeOutcomeRequest):
    try:
        asyncio.create_task(resolution_result(request.player_name, request.match_id, request.score, request.result))
        return {"message": "Dispute Outcome scheduled"}
    except Exception as e:
        return {"error": str(e)}


