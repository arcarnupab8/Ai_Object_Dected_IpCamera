import av

rtsp_url = "rtsp://admin:@192.168.1.160:554/11"

try:
    container = av.open(rtsp_url)
    for frame in container.decode(video=0):
        print("✅ ได้ frame จากกล้อง")
        break
except av.AVError as e:
    print("❌ ไม่สามารถเข้าถึงกล้อง:", e)
