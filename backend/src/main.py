import uvicorn
from fastapi import FastAPI

from api.auth import router as router_auth
from api.link_endpoints import router as router_links

app = FastAPI()

app.include_router(router_auth)
app.include_router(router_links)



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)