from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import gatekeeper_cdr
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/disarm")
async def disarm(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    raw_buffer = await file.read()
    
    try:
        format_detected = gatekeeper_cdr.sniff_format(raw_buffer)
        clean_buffer = gatekeeper_cdr.disarm(raw_buffer)
        
        print(f"[Python] Disarmed file | Format: {format_detected} | Original: {len(raw_buffer)} bytes | Clean: {len(clean_buffer)} bytes")
        
        return {
            "success": True,
            "originalSize": len(raw_buffer),
            "finalSize": len(clean_buffer),
            "format": format_detected,
            "disarmedFileBase64": base64.b64encode(clean_buffer).decode('utf-8')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Python Backend listening on port 3005")
    uvicorn.run(app, host="0.0.0.0", port=3005)
