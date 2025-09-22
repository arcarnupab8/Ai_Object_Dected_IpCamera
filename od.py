import cv2
import numpy as np
import base64

#รายชื่อหมวดหมู่ทั้งหมด เรียงตามลำดับการตรวจจับ
CLASSES = ["BACKGROUND", "AEROPLANE", "BICYCLE", "BIRD", "BOAT",
	"BOTTLE", "BUS", "CAR", "CAT", "CHAIR", "COW", "DININGTABLE",
	"DOG", "HORSE", "MOTORBIKE", "PERSON", "POTTEDPLANT", "SHEEP",
	"SOFA", "TRAIN", "TVMONITOR"]
colors = np.random.uniform(0, 100, size=(len(CLASSES), 3))

net = cv2.dnn.readNetFromCaffe("./MobileNetSSD/MobileNetSSD.prototxt", "./MobileNetSSD/MobileNetSSD.caffemodel")

# การใช้ video path เป็นตัวอ้างอิง
# cap = cv2.VideoCapture("Realistic Highway Car Crashes.mp4")
# การใช้ capture camera เป็นตัวอ้างอิง
# cap = cv2.VideoCapture(0)

# while True:
#     ret, frame = cap.read()
#     if ret:
#         (h, w) = frame.shape[:2]
#         blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
#         net.setInput(blob)
#         detections = net.forward()

#         for i in numpy.arange(0, detections.shape[2]):
#             confidence = detections[0, 0, i, 2]
#             if confidence > 0.5:
#                 class_idx = int(detections[0, 0, i, 1])
#                 box = detections[0, 0, i, 3:7] * numpy.array([w, h, w, h])
#                 (startX, startY, endX, endY) = box.astype("int")

#                 label = "{}: {:.2f}%".format(CLASSES[class_idx], confidence * 100)
#                 cv2.rectangle(frame, (startX, startY), (endX, endY), colors[class_idx], 2)
#                 #cv2.rectangle(frame, (startX-1, startY-30), (endX+1, endY), colors[class_idx], cv2.FILLED)
#                 y = startY - 15 if startY - 15 > 15 else startY + 15
#                 cv2.putText(frame, label, (startX+20, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

#         cv2.imshow("Frame", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#     else:
#         break

# cap.release()
# cv2.destroyAllWindows()

def detect_objects_with_image(image_bytes: bytes, confidence_threshold: float = 0.5):
    """ตรวจจับวัตถุ + คืนผลลัพธ์พร้อมภาพ base64"""
    # Decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    results = []
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            class_idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # วาดกล่อง
            cv2.rectangle(frame, (startX, startY), (endX, endY), colors[class_idx], 2)
            label = "{}: {:.2f}%".format(CLASSES[class_idx], confidence * 100)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            results.append({
                "label": CLASSES[class_idx],
                "confidence": round(float(confidence), 2),
                "box": [int(startX), int(startY), int(endX), int(endY)]
            })

    # แปลงภาพเป็น base64
    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    return results, img_base64