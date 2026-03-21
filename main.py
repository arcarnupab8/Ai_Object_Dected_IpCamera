# fastapi dev main.py  ## command run dev test
from fastapi import FastAPI, HTTPException

import io
import base64
import cv2
import os
import numpy as np
from dotenv import load_dotenv
from typing import Union
from pydantic import BaseModel
import requests
from od import detect_objects_with_image
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from find_camera import broadcast_for_cameras

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

# cached_camera = None
# @app.get("/detect-ipcamera")
# async def detect_ipcamera():
#     global cached_camera

#     # 1. ถ้ายังไม่เจอกล้อง ให้ตะโกนถาม (Broadcast)
#     if cached_camera is None:
#         print("🔍 กำลัง Broadcast หา IP/Port กล้อง...")
#         found_list = broadcast_for_cameras()

#         if not found_list:
#             # ถ้า Broadcast แล้วเงียบกริบ แปลว่า Network บล็อก หรือกล้องไม่รองรับ ONVIF
#             return HTTPException(status_code=404, detail="No cameras responded to broadcast")
        
#         # สมมติเลือกตัวแรกที่ตอบกลับมา (เพราะเราไม่รู้ IP)
#         cached_camera = found_list[0]
#         print(f"🎯 Connected to: {cached_camera}")

#     # 2. ดึงภาพด้วย IP/Port ที่กล้องบอกมาเอง
#     ip = cached_camera['ip']
#     port = cached_camera['port']
    
#     # URL นี้อาจเปลี่ยนตามยี่ห้อกล้อง แต่ส่วนใหญ่ใช้ snapshot.cgi
#     snapshot_url = f"http://{ip}:{port}/snapshot.cgi?user={CAMERA_USER}&pwd={CAMERA_PASSWORD}"

#     try:
#         response = requests.get(snapshot_url, timeout=3)
#         if response.status_code == 200:
#             arr = np.frombuffer(response.content, np.uint8)
#             frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
#             _, buf = cv2.imencode('.jpg', frame)
#             b64 = base64.b64encode(buf).decode()
#             return {"connected": f"{ip}:{port}", "image": b64}
#         else:
#             raise Exception("Status Error")
#     except:
#         cached_camera = None
#         return HTTPException(status_code=502, detail="Connection failed")
