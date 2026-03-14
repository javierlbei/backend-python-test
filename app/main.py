from fastapi import FastAPI

from requests import router as requests_router

app = FastAPI(title='Notification Service (Technical Test)')
app.include_router(requests_router.router)
