import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.api.charts import router as router_charts
from src.api.api.columns import router as router_columns
from src.api.api.description import router as router_description
from src.api.api.project_members import router as router_memebers
from src.api.api.projects import router as router_projects
from src.api.api.task_assignees import router as task_assignees_router
from src.api.api.tasks import router as router_tasks
from src.api.api.users import router as router_users
from src.api.auth import router as router_auth
from src.api.link_endpoints import router as router_links

# app = FastAPI(openapi_prefix="/api")
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #     "http://204.12.253.210:8080",
    #     "http://localhost:5173",
    #     "http://localhost:8080",
    # ],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "StartFlow API is running"}


app.include_router(router_auth)
app.include_router(router_links)
app.include_router(router_description)
app.include_router(router_users)
app.include_router(router_columns)
app.include_router(task_assignees_router)
app.include_router(router_memebers)
app.include_router(router_projects)
app.include_router(router_tasks)
app.include_router(router_charts)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
