# fastapi dev main.py  ## command run dev test
from fastapi import FastAPI

import io
import base64
import cv2
import os
from dotenv import load_dotenv
from typing import Union
from pydantic import BaseModel
from od import detect_objects_with_image
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse

load_dotenv()

CAMERA_IP = os.getenv("CAMERA_IP")
CAMERA_PORT = os.getenv("CAMERA_PORT")
CAMERA_USER = os.getenv("CAMERA_USER")
CAMERA_PASSWORD = os.getenv("CAMERA_PASSWORD")

app = FastAPI()

@app.get("/hello")
def hello_world():
    return {"message": "Hello World test"}

@app.get("/item/{item_id}")
def get_item(item_id: int, s: Union[str, None] = None):
    return {"item_id": item_id, "s": s}

class Item(BaseModel):
    name: str
    price: float

@app.post("/create_item")
def create_item(item: Item):
    print(item.name, item.price)
    return {"body": item}

@app.post("/detect-image-base64")
async def detect_image_base64(file: UploadFile = File(...)):
    image_bytes = await file.read()
    results, img_base64 = detect_objects_with_image(image_bytes)
    return {
        "objects": results,
        "image_base64": img_base64
    }

@app.post("/detect-image-jpeg")
async def detect_image_jpeg(file: UploadFile = File(...)):
    image_bytes = await file.read()
    results, img_base64 = detect_objects_with_image(image_bytes)

    img_bytes = base64.b64decode(img_base64)
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/jpeg")

@app.get("/detect-camera")
async def detect_camera():
    # เปิดกล้อง
    cap = cv2.VideoCapture(0)
    # บันทึกภาพจากกล้องที่เปิด และเก็บภาพเป็น array Numpy
    ret, frame = cap.read()
    # ปิดกล้อง
    cap.release()

    # ถ้าไม่สามารถเปิดกล้องได้
    if not ret:
        return {"error": "Cannot access camera"}

    # แปลงภาพจาก frame → bytes
    _, buffer = cv2.imencode('.jpg', frame)
    image_bytes = buffer.tobytes()

    # เรียกใช้ฟังก์ชัน AI เดิม
    results, img_base64 = detect_objects_with_image(image_bytes)

    return {
        "objects": results,
        "image_base64": img_base64
    }

@app.get("/detect-camera-jpeg")
async def detect_camera_jpeg():
    # เปิดกล้อง
    cap = cv2.VideoCapture(0)
    # บันทึกภาพจากกล้องที่เปิด และเก็บภาพเป็น array Numpy
    ret, frame = cap.read()
    # ปิดกล้อง
    cap.release()

    # ถ้าไม่สามารถเปิดกล้องได้
    if not ret:
        return {"error": "Cannot access camera"}

    # แปลงภาพจาก frame → bytes
    _, buffer = cv2.imencode('.jpg', frame)
    image_bytes = buffer.tobytes()

    # เรียกใช้ฟังก์ชัน AI เดิม
    results, img_base64 = detect_objects_with_image(image_bytes)

    # แปลง base64 เป็นภาพ JPG
    img_bytes = base64.b64decode(img_base64)

    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/jpeg")

@app.get("/detect-ipcamera")
async def detect_ipcamera():

    snapshot_url = f"http://{CAMERA_IP}:{CAMERA_PORT}/snapshot.cgi?user={CAMERA_USER}&pwd={CAMERA_PASSWORD}"

    cap = cv2.VideoCapture(snapshot_url)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        return {"error": "Cannot fetch snapshot from IP camera"}

    _, buffer = cv2.imencode('.jpg', frame)
    image_bytes = buffer.tobytes()

    img_base64 = base64.b64encode(image_bytes).decode("utf-8")

    results, img_base64 = detect_objects_with_image(image_bytes)

    return {
        "objects": results,
        "image_base64": img_base64
    }