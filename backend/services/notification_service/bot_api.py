from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from bot_dm import team_assignment

app = FastAPI()

class TeamAssignRequest(BaseModel):
    player_name: str
    team_id: str

@app.post("/assign_team")
async def assign_team(request: TeamAssignRequest):
    asyncio.create_task(team_assignment(request.player_name, request.team_id))
    return {"status": "DM scheduled"}
