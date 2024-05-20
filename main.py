from fastapi import FastAPI
from routers import query, knowledge_base, user, evaluation, ingest_data, auth, statistics
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(statistics.router)
app.include_router(user.router)
app.include_router(query.router)
app.include_router(ingest_data.router)
app.include_router(knowledge_base.router)



