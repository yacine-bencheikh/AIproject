from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import router


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
def read_root():
    return {"request": Request}
