"""
Phase 4: FastAPI Backend - Main Application
Wires QR decoding, heuristics, and AI analysis into REST endpoints
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import io
import json
from typing import Optional

from qr_decoder import QRDecoder
from heuristics import HeuristicAnalyzer
from ai_analyzer import AIAnalyzer

# Initialize components
app = FastAPI(title="QuishGuard", description="QR Code Security Scanner")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
decoder = QRDecoder()
heuristics_analyzer = HeuristicAnalyzer()
ai_analyzer = AIAnalyzer()


# Response models
class AnalysisResult(BaseModel):
    """Response model for QR analysis"""
    decoded_content: str
    content_type: str
    heuristic_signals: list
    verdict: dict
    

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_qr_image(file: UploadFile = File(...)):
    """
    Analyze a QR code from an uploaded image.
    
    Steps:
    1. Decode QR from image
    2. Extract heuristic signals
    3. Get AI verdict
    
    Returns:
        Analysis result with verdict
    """
    try:
        # Read uploaded file
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Step 1: Decode QR
        decoded = decoder.decode_from_bytes(contents)
        
        if not decoded:
            raise HTTPException(status_code=400, detail="No QR code detected in image")
        
        # Step 2: Heuristic analysis
        heuristics = heuristics_analyzer.analyze(decoded)
        
        # Step 3: AI reasoning
        verdict = ai_analyzer.analyze(decoded, heuristics)
        
        return AnalysisResult(
            decoded_content=decoded,
            content_type=heuristics['type'],
            heuristic_signals=heuristics['extracted_signals'],
            verdict=verdict
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /analyze: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


class LinkInput(BaseModel):
    """Input model for direct link/text analysis"""
    content: str


@app.post("/analyze-text", response_model=AnalysisResult)
async def analyze_direct_link(input_data: LinkInput):
    """
    Fallback endpoint: analyze a pasted URL or UPI link directly (no QR decode step).
    
    Useful if:
    - Camera/upload fails during demo
    - User wants to check a link they copied
    
    Steps:
    1. Skip QR decode (assume input is already decoded)
    2. Extract heuristic signals
    3. Get AI verdict
    
    Returns:
        Analysis result with verdict
    """
    try:
        content = input_data.content.strip()
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty content")
        
        if len(content) > 2000:
            raise HTTPException(status_code=400, detail="Content too long")
        
        # Step 1: Skip decode, content is already decoded
        decoded = content
        
        # Step 2: Heuristic analysis
        heuristics = heuristics_analyzer.analyze(decoded)
        
        # Step 3: AI reasoning
        verdict = ai_analyzer.analyze(decoded, heuristics)
        
        return AnalysisResult(
            decoded_content=decoded,
            content_type=heuristics['type'],
            heuristic_signals=heuristics['extracted_signals'],
            verdict=verdict
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /analyze-text: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/")
def root():
    """Root endpoint with API documentation"""
    return {
        "name": "QuishGuard",
        "description": "QR Code Security Scanner for fraud detection",
        "endpoints": {
            "POST /analyze": "Upload an image with a QR code to analyze",
            "POST /analyze-text": "Paste a URL or UPI link directly to analyze",
            "GET /health": "Health check",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
