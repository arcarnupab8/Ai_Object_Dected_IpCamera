import socket
import re

def broadcast_for_cameras():
    # ---------------------------------------------------------
    # 🔴 จุดที่ 1: แก้ Payload
    # XML ใช้ไม่ได้กับ Port 8600 ครับ ต้องใช้ Hex ที่เป็นคำสั่งค้นหา
    # ---------------------------------------------------------
    
    # สิ่งนี้ต้องมาจากการ Copy "Packet ขาไป" (Request) ใน Wireshark
    # (Source: คอมคุณ -> Dest: 255.255.255.255 ที่ Port 8600)
    # ถ้ายังหาไม่เจอ ลองใช้คำสั่ง VStarcam มาตรฐานดูก่อน (อาจจะฟลุ๊คได้)
    REAL_PAYLOAD = b'LAN_SEARCH_STRUCT' 
    # หรือถ้าหาเจอแล้ว ให้ใส่แบบนี้: b'\x01\x00\x00\x00' (ตัวอย่าง)

    # ---------------------------------------------------------
    
    DEST_PORT = 8600 # ✅ ถูกต้องแล้ว
    DEST_IP = "255.255.255.255"

    print(f"📡 Sending Binary Probe to Port {DEST_PORT}...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(10)
    
    # เพิ่ม: หา IP เครื่องตัวเองเพื่อกันเสียงสะท้อน (Optional)
    try:
        dummy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dummy.connect(('8.8.8.8', 80))
        my_ip = dummy.getsockname()[0]
        dummy.close()
    except:
        my_ip = '127.0.0.1'

    found_cameras = []

    try:
        for i in range(3):
            sock.sendto(REAL_PAYLOAD, (DEST_IP, DEST_PORT))
            print(f"   🚀 Sent packet #{i+1}")

        while True:
            try:
                data, addr = sock.recvfrom(65536)
                
                # กรองตัวเองทิ้ง
                if addr[0] == my_ip:
                    continue

                print(f"✅ ได้รับข้อมูลจาก {addr[0]} (Port {addr[1]})")

                # 🔴 จุดที่ 2: แก้การแกะข้อมูล (Parsing)
                # ข้อมูลเป็น Binary ผสม Text เราจะหา Pattern ของ IP Address โดยตรง
                # ไม่หา http:// แล้ว เพราะ Port 8600 ไม่ส่งมาแบบนั้น
                
                # Regex ค้นหา IP Address (เช่น 192.168.1.160) ในก้อนข้อมูล
                ip_match = re.search(b'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', data)
                
                found_ip = addr[0] # ถ้าหาไม่เจอจริงๆ ให้ใช้ IP คนส่ง
                
                if ip_match:
                    # แปลง bytes เป็น string
                    extracted_ip = ip_match.group(1).decode('utf-8')
                    # กรองพวก 0.0.0.0 หรือ 255.255.255.0 ทิ้ง
                    if extracted_ip != "0.0.0.0" and not extracted_ip.startswith("255"):
                        found_ip = extracted_ip
                        print(f"   🎉 แกะเจอ IP ในเนื้อหา: {found_ip}")

                # Port ใช้งานจริง (ไม่ใช่ 8600)
                # ปกติ VStarcam ถ้าหาเจอแล้ว Port สั่งงานจะเป็น 80 หรือ 81 หรือ 14042
                # ตรงนี้คุณอาจต้องลองใส่ Logic หรือตั้ง Default ไว้
                found_port = 81 # ลองตั้ง 81 หรือตามที่คุณเคยเข้าได้
                
                cam_info = {'ip': found_ip, 'port': found_port}
                
                # เช็คกันซ้ำ
                is_new = True
                for cam in found_cameras:
                    if cam['ip'] == found_ip:
                        is_new = False
                        break
                
                if is_new:
                    found_cameras.append(cam_info)

            except socket.timeout:
                print("⏳ หมดเวลารอ (Timeout)")
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

    return found_cameras

if __name__ == "__main__":
    cams = broadcast_for_cameras()
    print("\nสรุปผลการค้นหา:", cams)