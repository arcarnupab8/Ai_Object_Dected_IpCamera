# 1. ใช้ Python Slim เพื่อความเบา
FROM python:3.11-slim

# 2. ตั้งค่าพื้นฐาน
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. กำหนดโฟลเดอร์ทำงาน
WORKDIR /app

# 4. ติดตั้ง System Libraries พื้นฐาน (เหลือน้อยที่สุด)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 5. ติดตั้ง Library ตาม requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. คัดลอกโค้ดและโมเดล AI (ต้องมีโฟลเดอร์ MobileNetSSD ด้วย)
COPY . .

# 7. เปิด Port และรันคำสั่ง
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]