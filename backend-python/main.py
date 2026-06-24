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
        result = gatekeeper_cdr.disarm(raw_buffer)
        
        print(f"[Python] Disarmed file | Format: {result.detected_format} | Original: {result.original_size_bytes} bytes | Native: {result.final_size_bytes} bytes")
        
        response = {
            "success": True,
            "originalSize": result.original_size_bytes,
            "finalSize": result.final_size_bytes,
            "format": result.detected_format,
            "outputFormat": result.output_format,
            "disarmedFileBase64": base64.b64encode(result.buffer).decode('utf-8')
        }

        if result.png_buffer is not None:
            response["pngFileBase64"] = base64.b64encode(result.png_buffer).decode('utf-8')

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Python Backend listening on port 3005")
    uvicorn.run(app, host="0.0.0.0", port=3005)
