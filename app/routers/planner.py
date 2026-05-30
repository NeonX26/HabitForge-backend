from fastapi import APIRouter

from app.services.planner import PlanRequest, PlanResponse, generate_daily_plan

router = APIRouter(tags=["planner"])


@router.post("/daily-plan", response_model=PlanResponse)
async def daily_plan(body: PlanRequest):
    return await generate_daily_plan(body)
