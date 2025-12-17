from __future__ import annotations

from typing import Any, Literal, TypedDict


class VersionedEntry(TypedDict, total=False):
    plan: Any
    script: str | None
    params: list[dict[str, Any]] | None
    meta: dict[str, Any]


class VersionedInstructions(TypedDict):
    currentVersion: int
    data: dict[str, VersionedEntry]


class ResolvedInstructions(TypedDict, total=False):
    currentVersion: int
    plan: Any
    script: str | None
    params: list[dict[str, Any]] | None
    meta: dict[str, Any]


class AgentResponse(TypedDict, total=False):
    id: str
    name: str | None
    description: str | None
    user_id: str
    org_id: str
    instructions: ResolvedInstructions | None
    tools: dict[str, list[str]] | None
    visibility: Literal["private", "readonly", "public"] | None
    job_id: str | None
    job_cron: str | None
    job_enabled: bool | None
    created_at: str
    updated_at: str


class TemplateResponse(TypedDict, total=False):
    id: str
    name: str | None
    description: str | None
    categories: list[str] | None
    user_id: str
    user_name: str | None
    instructions: VersionedInstructions | None
    tools: dict[str, list[str]] | None
    visibility: Literal["private", "readonly", "public"] | None
    job_cron: str | None
    created_at: str
    updated_at: str
