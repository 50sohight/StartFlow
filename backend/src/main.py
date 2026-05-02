import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.api.columns import router as router_columns
from src.api.api.project_members import router as router_memebers
from src.api.api.projects import router as router_projects
from src.api.api.tasks import router as router_tasks
from src.api.api.users import router as router_users
from src.api.auth import router as router_auth
from src.api.link_endpoints import router as router_links

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_auth)
app.include_router(router_links)
app.include_router(router_users)
app.include_router(router_columns)
app.include_router(router_memebers)
app.include_router(router_projects)
app.include_router(router_tasks)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
