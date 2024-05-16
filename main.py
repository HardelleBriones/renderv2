from fastapi import FastAPI
#from . import models
# from .database import engine
from routers import query, knowledge_base, user, evaluation, ingest_data, auth
#models.Base.metadata.create_all(bind=engine)

from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(query.router)
app.include_router(ingest_data.router)
app.include_router(knowledge_base.router)



