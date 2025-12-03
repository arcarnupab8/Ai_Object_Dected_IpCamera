# 1. เลือก Base Image เป็น Python 3.11 แบบ Slim (ขนาดเล็ก เหมาะกับ RPi)
FROM python:3.11-slim

# 2. ตั้งค่าเพื่อประสิทธิภาพ
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. กำหนดโฟลเดอร์ทำงานข้างใน Container
WORKDIR /app

# 4. ติดตั้ง System Libraries ที่จำเป็นสำหรับ OpenCV และการจัดการภาพ
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

# 5. คัดลอก requirements.txt เข้าไปก่อน (เพื่อใช้ Cache ช่วยให้ Build เร็ว)
COPY requirements.txt .

# 6. อัปเกรด pip และติดตั้ง Library ตามรายการ
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. คัดลอกโค้ดทั้งหมดในโปรเจกต์เข้าไปใน Container
COPY . .

# 8. เปิด Port 8000 (แค่แจ้งไว้)
EXPOSE 8000

# 9. คำสั่งรัน FastAPI เมื่อ Container เริ่มทำงาน
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]