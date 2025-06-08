from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from models import summarize, transcript, health

app = FastAPI(
    title="YouTube Video Summarizer",
    description="API to summarize YouTube videos using transcripts and LLMs",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include models
# app.include_router(summarize.router, prefix="/summarize", tags=["Summarize"])
# app.include_router(transcript.router, prefix="/api/transcript", tags=["Transcript"])
# app.include_router(health.router, prefix="/health", tags=["Health"])

# Error handling
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred", "error": str(exc)},
    )

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Idea Incubator API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
