from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import screener, dashboard, signals, watchlist, stock

app = FastAPI(title="QuantIQ API")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(screener.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(signals.router, prefix="/api")
app.include_router(watchlist.router, prefix="/api")
app.include_router(stock.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "QuantIQ API is running."}
