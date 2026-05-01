import os
import shutil
import traceback
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from query_database import query_rag
from populate_database import process_new_file

app = FastAPI()

# Ensure upload directory exists
UPLOAD_DIR = "data_text"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    context: str = ""

from fastapi.responses import FileResponse, StreamingResponse

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    try:
        print(f"Querying: {request.question}")
        result = query_rag(request.question)
        return QueryResponse(
            answer=result["answer"], 
            sources=result["sources"],
            context=result.get("context", "")
        )
    except Exception as e:
        print(f"QUERY ERROR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_endpoint(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        print(f"Uploading file: {file.filename}")
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the file and add to Chroma
        stats = process_new_file(file_path)
        
        return {
            "message": f"Successfully uploaded and processed {file.filename}",
            "stats": stats
        }
    except Exception as e:
        print(f"UPLOAD ERROR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
