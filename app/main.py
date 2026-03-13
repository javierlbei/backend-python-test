from fastapi import FastAPI, status, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Literal
from uuid import uuid4
from requests import router as requests_router
import httpx
import asyncio
import random

app = FastAPI(title='Notification Service (Technical Test)')
app.include_router(requests_router.router)

"""
def modify_request_status(request, new_status):
    request.status = new_status

async def send_notification(request):
    modify_request_status(request, 'processing')

    send_notification_ws = 'http://localhost:3001/v1/notify'
    headers = { 'X-API-Key': 'test-dev-2026' }
    body = { 'to': request.to, 'message': request.message, 'type': request.type }

    retry_count = 0
    max_retries = 3

    min_latency = 0.5
    max_latency = 1

    async with httpx.AsyncClient() as client:
        while retry_count < max_retries:
            try:
                response = await client.post(send_notification_ws, headers = headers, json = body)

                if response.status_code == status.HTTP_200_OK:
                    modify_request_status(request, 'sent')
                    return

                elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                    await asyncio.sleep(random.uniform(min_latency, max_latency))
                    retry_count += 1

                else:
                    break

            except httpx.TimeoutException:
                await asyncio.sleep(random.uniform(min_latency, max_latency))
                retry_count += 1

    modify_request_status(request, 'failed')

@app.post(
    '/v1/requests/{request_id}/process',
    status_code=status.HTTP_202_ACCEPTED
)
async def process_request(request_id: str, background_tasks: BackgroundTasks):
    request = next(
        filter(
            lambda r: r.id == request_id, requests
        ),
        None
    )

    if request is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'Request not found'
        )

    background_tasks.add_task(send_notification, request)
    return {}
"""
