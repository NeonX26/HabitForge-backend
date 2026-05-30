import json
import re
from typing import Literal

import httpx
from pydantic import BaseModel

from app.config import settings


class HabitInput(BaseModel):
    name: str
    category: str


class TaskInput(BaseModel):
    title: str
    priority: str
    category: str


class PlanBlock(BaseModel):
    time: str
    title: str
    detail: str | None = None


class PlanRequest(BaseModel):
    habits: list[HabitInput] = []
    tasks: list[TaskInput] = []


class PlanResponse(BaseModel):
    blocks: list[PlanBlock]
    source: Literal["ai", "local"]


def local_plan(body: PlanRequest) -> list[PlanBlock]:
    blocks: list[PlanBlock] = []
    times = ["8:00 AM", "10:00 AM", "12:00 PM", "2:00 PM", "4:00 PM"]

    for i, h in enumerate(body.habits[:2]):
        blocks.append(PlanBlock(time=times[i] if i < len(times) else "Morning", title=h.name, detail=h.category))

    remaining = 5 - len(blocks)
    for i, t in enumerate(body.tasks[:remaining]):
        blocks.append(
            PlanBlock(
                time=times[len(blocks)] if len(blocks) < len(times) else "Afternoon",
                title=t.title,
                detail=f"{t.category} · {t.priority}",
            )
        )

    if blocks:
        return blocks

    return [
        PlanBlock(time="Morning", title="Review habits", detail="Add habits to get started"),
        PlanBlock(time="Afternoon", title="Plan tasks", detail="Add tasks due today"),
    ]


async def generate_daily_plan(body: PlanRequest) -> PlanResponse:
    if not settings.anthropic_api_key:
        return PlanResponse(blocks=local_plan(body), source="local")

    prompt = (
        "Create a concise daily plan (3-5 time blocks) for:\n"
        f"Habits: {json.dumps([h.model_dump() for h in body.habits])}\n"
        f"Tasks: {json.dumps([t.model_dump() for t in body.tasks])}\n"
        'Respond as JSON only: {"blocks":[{"time":"8:00 AM","title":"...","detail":"..."}]}'
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
        res.raise_for_status()
        data = res.json()
        text = data.get("content", [{}])[0].get("text", "")
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            parsed = json.loads(match.group())
            blocks = [PlanBlock(**b) for b in parsed.get("blocks", [])]
            if blocks:
                return PlanResponse(blocks=blocks, source="ai")
    except Exception:
        pass

    return PlanResponse(blocks=local_plan(body), source="local")
