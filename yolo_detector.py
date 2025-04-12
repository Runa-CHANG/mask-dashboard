# yolo_detector.py
import cv2
from ultralytics import YOLO
import numpy as np
from stats_manager import add_history_entry

def compute_iou(box1, box2):
    xA = max(box1[0], box2[0])
    yA = max(box1[1], box2[1])
    xB = min(box1[2], box2[2])
    yB = min(box1[3], box2[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0:
        return 0.0
    box1Area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2Area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    return interArea / float(box1Area + box2Area - interArea)

def run_detection(shared_data):
    model = YOLO("C:/Users/Runa/runs/detect/train5/weights/best.pt").to("cuda")
    cap = cv2.VideoCapture(0)

    class_map = {
        0: 'Without_Mask',
        1: 'With_Mask',
        2: 'Incorrectly_Worn_Mask',
        3: 'Partially_Worn_Mask'
    }

    color_map = {
        'Without_Mask': (0, 0, 255),
        'With_Mask': (0, 255, 0),
        'Incorrectly_Worn_Mask': (0, 255, 255),
        'Partially_Worn_Mask': (255, 0, 255)
    }

    last_boxes = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)
        current_boxes = []

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                cls_name = class_map.get(cls)
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = xyxy

                this_box = [x1, y1, x2, y2]
                current_boxes.append((this_box, cls_name))

                is_new = True
                for prev_box, _ in last_boxes:
                    if compute_iou(this_box, prev_box) > 0.5:
                        is_new = False
                        break

                if is_new and cls_name:
                    shared_data['stats'][cls_name] += 1
                    add_history_entry(shared_data, cls_name)

                color = color_map.get(cls_name, (0, 255, 0))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, cls_name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        last_boxes = current_boxes
        cv2.imshow("YOLOv8s Mask Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
