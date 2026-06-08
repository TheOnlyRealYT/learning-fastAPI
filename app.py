from fastapi import FastAPI
from .lifespans import life_span

app = FastAPI(debug=True, lifespan=life_span)