from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader, PdfWriter
import io

app = FastAPI(title="DocScrub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "online", "service": "DocScrub PDF Sanitizer"}

@app.post("/api/v1/clean-pdf")
async def clean_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF.")
    
    try:
        contents = await file.read()
        input_stream = io.BytesIO(contents)
        
        reader = PdfReader(input_stream)
        writer = PdfWriter()
        
        # Copy pages over without copying the metadata dictionary
        for page in reader.pages:
            writer.add_page(page)
            
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        
        return StreamingResponse(
            output_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=cleaned_{file.filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
