import cv2
import numpy as np
import json
import time
from ultralytics import YOLO
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

class MyTracker:
    def __init__(self, fps):
        self.fps, self.history, self.stats, self.buffer = fps, {}, {}, {}

    def get_movement(self, prev, curr):
        flow = cv2.calcOpticalFlowFarneback(prev, curr, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        return float(np.mean(mag)), float(np.mean(ang)) * 180 / np.pi

    def process_crop(self, track_id, crop):
        gray = cv2.resize(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), (100, 100))
        state, action, mag, ang = "INACTIVE", "WAITING", 0.0, 0.0

        if track_id in self.history:
            mag, ang = self.get_movement(self.history[track_id], gray)
            if mag > 1.0: state = "ACTIVE"

        self.history[track_id] = gray
        if track_id not in self.buffer: self.buffer[track_id] = []
        self.buffer[track_id].append(state)
        if len(self.buffer[track_id]) > 15: self.buffer[track_id].pop(0)

        state = "ACTIVE" if self.buffer[track_id].count("ACTIVE") > 7 else "INACTIVE"
        if state == "ACTIVE":
            if mag > 1.5: action = "DIGGING" if (45 < ang < 135) or (225 < ang < 315) else "SWINGING"
            else: action = "DUMPING"

        if track_id not in self.stats: self.stats[track_id] = {"tot": 0, "act": 0, "idl": 0}
        self.stats[track_id]["tot"] += 1
        if state == "ACTIVE": self.stats[track_id]["act"] += 1
        else: self.stats[track_id]["idl"] += 1

        tot_s = round(self.stats[track_id]["tot"] / self.fps, 1)
        act_s = round(self.stats[track_id]["act"] / self.fps, 1)
        idl_s = round(self.stats[track_id]["idl"] / self.fps, 1)
        u_pct = round((act_s / tot_s) * 100, 1) if tot_s > 0 else 0.0

        return state, action, tot_s, act_s, idl_s, u_pct

cap = cv2.VideoCapture("input_video.mp4")
fps = int(cap.get(cv2.CAP_PROP_FPS) or 30)
model, tracker = YOLO('yolov8n.pt'), MyTracker(fps)

f_id = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    f_id += 1

    results = model.track(frame, persist=True, classes=[7], verbose=False)
    if results[0].boxes.id is not None:
        boxes, ids = results[0].boxes.xyxy.cpu().numpy().astype(int), results[0].boxes.id.cpu().numpy().astype(int)
        for box, t_id in zip(boxes, ids):
            x1, y1, x2, y2 = max(0, box[0]), max(0, box[1]), min(frame.shape[1], box[2]), min(frame.shape[0], box[3])
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0: continue

            state, action, tot, act, idl, u_pct = tracker.process_crop(t_id, crop)

            payload = {
                "frame_id": f_id, "equipment_id": f"EX-{t_id:03d}", "equipment_class": "excavator",
                "timestamp": f"00:00:{f_id//fps:02d}.000", "current_state": state, "current_activity": action,
                "time_analytics": {"total_tracked_seconds": tot, "total_active_seconds": act, "total_idle_seconds": idl, "utilization_percent": u_pct}
            }
            producer.send('equipment_topic', value=payload)

            c = (0, 255, 0) if state == "ACTIVE" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), c, 2)
            cv2.putText(frame, f"ID:{t_id} {state} {action} {u_pct}%", (x1, y1-10), 0, 0.5, c, 2)

    cv2.imwrite("shared_data/latest_frame.jpg", frame)
    time.sleep(0.03)

cap.release()
