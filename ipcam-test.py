import av
import time

rtsp_url = "rtsp://admin:@192.168.1.160:554/11"

try:
    container = av.open(rtsp_url)
    start = time.time()
    got_frame = False
    for frame in container.decode(video=0):
        print("✅ ได้ frame จากกล้อง")
        got_frame = True
        break
        if time.time() - start > 5:
            print("⏱ Timeout รอ frame")
            break
    if not got_frame:
        print("❌ ไม่ได้ frame หลังรอ 5 วินาที")
except av.AVError as e:
    print("❌ ไม่สามารถเข้าถึงกล้อง:", e)
