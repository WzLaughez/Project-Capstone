from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from ultralytics import YOLO
import numpy as np
import io
import os
import gdown
import uvicorn

app = FastAPI()

# CORS biar bisa diakses dari React (frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lokasi dan ID model YOLOv8 (Google Drive link)
file_id = "YOUR_FILE_ID"  # Ganti dengan file_id modelmu
model_path = "model/best.pt"

# Unduh model jika belum ada
if not os.path.exists(model_path):
    os.makedirs("model", exist_ok=True)
    url = f"https://drive.google.com/uc?id={file_id}"
    print("Downloading YOLOv8 model from Google Drive...")
    gdown.download(url, model_path, quiet=False)

# Load model YOLOv8
model = YOLO(model_path)

# Fungsi untuk prediksi dengan YOLOv8
def predict_with_yolo(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    results = model(image)

    result = results[0]
    boxes = result.boxes

    if boxes is None or len(boxes) == 0:
        return {"prediction": "No object detected"}

    # Ambil prediksi dengan confidence tertinggi
    best_box = max(boxes, key=lambda b: float(b.conf[0]))
    cls_id = int(best_box.cls[0])
    predicted_class = model.names[cls_id]

    return {"prediction": predicted_class}


# Endpoint prediksi
@app.post("/predict")
async def predict_yolo(file: UploadFile = File(...)):
    image_bytes = await file.read()
    results = predict_with_yolo(image_bytes)
    return results

# Jalankan server
if __name__ == "__main__":
    uvicorn.run("useyolo:app", host="0.0.0.0", port=8000, reload=True)
