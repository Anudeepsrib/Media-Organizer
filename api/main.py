from fastapi import FastAPI
from routers import media, android, files, analysis

app = FastAPI(
    title="Disk Organizer API",
    description="API to control file organization tasks on the local system.",
    version="1.0.0"
)

app.include_router(media.router, prefix="/media", tags=["Media"])
app.include_router(android.router, prefix="/android", tags=["Android"])
app.include_router(files.router, prefix="/files", tags=["Files"])
app.include_router(analysis.router, prefix="/analyze", tags=["Analysis"])

@app.get("/")
def root():
    return {"message": "Disk Organizer API is running. Visit /docs for Swagger UI."}
