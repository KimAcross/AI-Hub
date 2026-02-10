"""Assistant API endpoints."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_assistant_service, require_admin_role, require_any_role
from app.core.exceptions import AssistantNotFoundError
from app.schemas.assistant import (
    AssistantCreate,
    AssistantListResponse,
    AssistantResponse,
    AssistantTemplate,
    AssistantUpdate,
)
from app.services.assistant_service import AssistantService, assistant_to_response

router = APIRouter(prefix="/assistants", tags=["assistants"])


@router.post(
    "",
    response_model=AssistantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new assistant",
)
async def create_assistant(
    data: AssistantCreate,
    service: Annotated[AssistantService, Depends(get_assistant_service)],
    _auth: dict = Depends(require_admin_role),
) -> AssistantResponse:
    """Create a new AI assistant with custom instructions."""
    assistant = await service.create_assistant(data)
    return assistant_to_response(assistant)


@router.post(
    "/from-template/{template_id}",
    response_model=AssistantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an assistant from a template",
)
async def create_from_template(
    template_id: str,
    service: Annotated[AssistantService, Depends(get_assistant_service)],
    _auth: dict = Depends(require_admin_role),
) -> AssistantResponse:
    """Create a new assistant from a predefined template."""
    try:
        assistant = await service.create_from_template(template_id)
        return assistant_to_response(assistant)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "",
    response_model=AssistantListResponse,
    summary="List all assistants",
)
async def list_assistants(
    service: Annotated[AssistantService, Depends(get_assistant_service)],
    _auth: dict = Depends(require_any_role),
    include_deleted: bool = False,
) -> AssistantListResponse:
    """Get a list of all assistants."""
    assistants, total = await service.list_assistants(include_deleted=include_deleted)
    return AssistantListResponse(
        assistants=[assistant_to_response(a) for a in assistants],
        total=total,
    )


@router.get(
    "/templates",
    response_model=list[AssistantTemplate],
    summary="Get available assistant templates",
)
async def get_templates(
    service: Annotated[AssistantService, Depends(get_assistant_service)],
    _auth: dict = Depends(require_any_role),
) -> list[AssistantTemplate]:
    """Get all available assistant templates."""
    return service.get_templates()


@router.get(
    "/templates/{template_id}",
    response_model=AssistantTemplate,
    summary="Get a specific template",
)
async def get_template(
    template_id: str,
    service: Annotated[AssistantService, Depends(get_assistant_service)],
    _auth: dict = Depends(require_any_role),
) -> AssistantTemplate:
    """Get a specific assistant template by ID."""
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template not found: {template_id}",
        )
    return template


@router.get(
    "/{assistant_id}",
    response_model=AssistantResponse,
    summary="Get an assistant by ID",
)
async def get_assistant(
    assistant_id: UUID,
    service: Annotated[AssistantService, Depends(get_assistant_service)],
    _auth: dict = Depends(require_any_role),
) -> AssistantResponse:
    """Get details of a specific assistant."""
    try:
        assistant = await service.get_assistant(assistant_id)
        return assistant_to_response(assistant)
    except AssistantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/{assistant_id}",
    response_model=AssistantResponse,
    summary="Update an assistant",
)
async def update_assistant(
    assistant_id: UUID,
    data: AssistantUpdate,
    service: Annotated[AssistantService, Depends(get_assistant_service)],
    _auth: dict = Depends(require_admin_role),
) -> AssistantResponse:
    """Update an existing assistant's configuration."""
    try:
        assistant = await service.update_assistant(assistant_id, data)
        return assistant_to_response(assistant)
    except AssistantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{assistant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an assistant",
)
async def delete_assistant(
    assistant_id: UUID,
    service: Annotated[AssistantService, Depends(get_assistant_service)],
    _auth: dict = Depends(require_admin_role),
) -> None:
    """Soft delete an assistant (recoverable for 30 days)."""
    try:
        await service.delete_assistant(assistant_id)
    except AssistantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/{assistant_id}/restore",
    response_model=AssistantResponse,
    summary="Restore a deleted assistant",
)
async def restore_assistant(
    assistant_id: UUID,
    service: Annotated[AssistantService, Depends(get_assistant_service)],
    _auth: dict = Depends(require_admin_role),
) -> AssistantResponse:
    """Restore a previously deleted assistant."""
    try:
        assistant = await service.restore_assistant(assistant_id)
        return assistant_to_response(assistant)
    except AssistantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
