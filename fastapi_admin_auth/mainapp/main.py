from fastapi import FastAPI
from mainapp.core.iam.view import add_swagger_config, router

app = FastAPI()
app = add_swagger_config(app)

app.include_router(router)
