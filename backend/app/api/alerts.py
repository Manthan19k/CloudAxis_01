from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.alert_service import AlertService
from app.schemas.alert import AlertCreate, AlertUpdate, AlertOut, AlertListResponse
from app.dependencies import get_alert_repo


router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_alert_service(alert_repo = Depends(get_alert_repo)) -> AlertService:
    return AlertService(alert_repo)


@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    alert_service: AlertService = Depends(get_alert_service),
):
    alerts = await alert_service.list_alerts(skip=skip, limit=limit)
    return AlertListResponse(
        items=alerts,
        total=len(alerts),
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=1
    )


@router.get("/{alert_id}", response_model=AlertOut)
async def get_alert(
    alert_id: str,
    alert_service: AlertService = Depends(get_alert_service),
):
    if alert_id.isdigit():
        alert = await alert_service.get_alert(int(alert_id))
    else:
        alert = await alert_service.get_alert_by_alert_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    alert_service: AlertService = Depends(get_alert_service),
):
    return await alert_service.create_alert(alert_data)


@router.put("/{alert_id}", response_model=AlertOut)
async def update_alert(
    alert_id: str,
    alert_data: AlertUpdate,
    alert_service: AlertService = Depends(get_alert_service),
):
    numeric_id = int(alert_id) if alert_id.isdigit() else None
    if numeric_id is None:
        existing = await alert_service.get_alert_by_alert_id(alert_id)
        numeric_id = existing.id if existing else None
    if numeric_id is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert = await alert_service.update_alert(numeric_id, alert_data)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: str,
    alert_service: AlertService = Depends(get_alert_service),
):
    numeric_id = int(alert_id) if alert_id.isdigit() else None
    if numeric_id is None:
        existing = await alert_service.get_alert_by_alert_id(alert_id)
        numeric_id = existing.id if existing else None
    if numeric_id is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    success = await alert_service.delete_alert(numeric_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return None


@router.get("/severity/{severity}", response_model=AlertListResponse)
async def list_alerts_by_severity(
    severity: str,
    skip: int = 0,
    limit: int = 100,
    alert_service: AlertService = Depends(get_alert_service),
):
    alerts = await alert_service.list_alerts_by_severity(severity, skip=skip, limit=limit)
    return AlertListResponse(
        items=alerts,
        total=len(alerts),
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=1
    )
