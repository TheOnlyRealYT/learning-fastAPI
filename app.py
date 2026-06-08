from fastapi import FastAPI
from .lifespans import life_span
from .views import router

app = FastAPI(debug=True, lifespan=life_span)
app.include_router(router)