from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from cyberfusion.RabbitMQConsumerLogServer import gui, api
from cyberfusion.RabbitMQConsumerLogServer.settings import settings

app = FastAPI(title="RabbitMQ Consumer Log Server")

app.mount(
    "/static",
    StaticFiles(directory=settings.static_files_directory),
    name="static",
)


app.include_router(gui.router, tags=["Web GUI"])
app.include_router(api.router, tags=["REST API"])
