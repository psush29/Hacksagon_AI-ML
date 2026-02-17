import streamlit as st
import cv2
import numpy as np
import tempfile
import time
import os
from datetime import datetime
from collections import defaultdict, deque
from ultralytics import YOLO
import supervision as sv
import base64
from scipy.io import wavfile

# --- 1. STYLING & UI INJECTION (Your Specific Design) ---
def apply_custom_styles():
    # Background Setup
    if os.path.exists("bg_dark.jpg"):
        with open("bg_dark.jpg", "rb") as f:
            img_data = f.read()
        b64_encoded = base64.b64encode(img_data).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{b64_encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
        """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    
    .alert-box {
        background: rgba(30, 10, 10, 0.85);
        color: #ffecec;
        padding: 12px 14px;
        border-radius: 10px;
        border-left: 4px solid #ff4b4b;
        margin-bottom: 10px;
        box-shadow: 0 0 18px rgba(255, 75, 75, 0.35);
        animation: pulseAlert 1.5s infinite;
    }
    
    @keyframes pulseAlert {
        0% { box-shadow: 0 0 8px rgba(255,75,75,0.4); }
        50% { box-shadow: 0 0 18px rgba(255,75,75,0.8); }
        100% { box-shadow: 0 0 8px rgba(255,75,75,0.4); }
    }
    
    section[data-testid="stSidebar"] {
        background: rgba(10, 10, 15, 0.75);
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    
    .header-glass {
        background: rgba(20, 20, 30, 0.55);
        backdrop-filter: blur(14px);
        border-radius: 18px;
        padding: 28px 36px;
        margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 0 40px rgba(120, 90, 255, 0.25);
    }
    
    .header-title { font-size: 2.2rem; font-weight: 800; color: white; }
    
    .status-box {
        display: flex; align-items: center; gap: 12px;
        background: linear-gradient(90deg, rgba(80,70,200,0.25), rgba(20,20,30,0.6));
        border-left: 4px solid #7b6cff; padding: 16px 20px; border-radius: 12px;
        color: #eaeaff; font-weight: 600;
    }
    .status-dot { width: 10px; height: 10px; background: #7b6cff; border-radius: 50%; box-shadow: 0 0 12px #7b6cff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUDIO & ALERTS ---

def play_sound():
    """Restored the original beep functionality"""
    if not os.path.exists("alert.wav"):
        sr = 44100
        t = np.linspace(0, 0.4, int(sr * 0.4))
        audio = (np.sin(2 * np.pi * 1000 * t) * 32767).astype(np.int16)
        wavfile.write("alert.wav", sr, audio)
    
    with open("alert.wav", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        # Original simple beep injection
        st.markdown(f"""
            <audio autoplay="true">
                <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            </audio>
            """, unsafe_allow_html=True)

class AlertSystem:
    def __init__(self):
        self.alert_log = []
        self.alert_cooldown = {}
        self.cooldown_time = 3

    def can_alert(self, alert_type):
        curr = time.time()
        if alert_type in self.alert_cooldown:
            if curr - self.alert_cooldown[alert_type] < self.cooldown_time:
                return False
        self.alert_cooldown[alert_type] = curr
        return True

    def trigger_alert(self, alert_type, message):
        if not self.can_alert(alert_type):
            return None
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {'time': timestamp, 'type': alert_type, 'msg': message}
        self.alert_log.append(entry)
        return entry

class RestrictedZone:
    def __init__(self, pts, color=(0, 0, 255)):
        self.polygon = np.array(pts, dtype=np.int32)
        self.color = color

    def is_inside(self, point):
        return cv2.pointPolygonTest(self.polygon, point, False) >= 0

    def draw(self, frame):
        overlay = frame.copy()
        cv2.fillPoly(overlay, [self.polygon], self.color)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        cv2.polylines(frame, [self.polygon], True, self.color, 2)

# --- 3. MAIN APP ---

st.set_page_config(layout="wide", page_title="AI Sentinel Pro")
apply_custom_styles()

@st.cache_resource
def load_yolo_model():
    return YOLO('yolov8n.pt')

def main():
    st.markdown("""
    <div class="header-glass">
      <div class="header-title">🛡️ AI Sentinel Pro</div>
      <div class="header-subtitle">Real-time Threat Detection • Restricted Zone Intelligence • Smart Alerts</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_video = st.sidebar.file_uploader("📂 LOAD VIDEO FEED", type=['mp4', 'mov', 'avi'])
    
    if uploaded_video:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_video.read())
        tfile.close()

        cap = cv2.VideoCapture(tfile.name)
        width, height = int(cap.get(3)), int(cap.get(4))
        _, first_frame = cap.read()
        cap.release()

        # Sidebar Controls
        st.sidebar.subheader("⚙️ System Settings")
        sens_val = st.sidebar.slider("⚡ Alert Sensitivity", 1, 50, 10, help="[Higher = must stay in zone longer to beep]")
        conf_level = st.sidebar.slider("AI Confidence", 0.1, 1.0, 0.4)
        
        st.sidebar.subheader("📐 Zone Calibration")
        x_r = st.sidebar.slider("Horizontal Range", 0, width, (int(width*0.2), int(width*0.8)))
        y_r = st.sidebar.slider("Vertical Range", 0, height, (int(height*0.2), int(height*0.8)))
        
        pts = [(x_r[0], y_r[0]), (x_r[1], y_r[0]), (x_r[1], y_r[1]), (x_r[0], y_r[1])]
        active_zone = RestrictedZone(pts)

        # Immediate Preview
        preview = first_frame.copy()
        active_zone.draw(preview)
        st.image(preview, channels="BGR", use_container_width=True, caption="CALIBRATION ACTIVE")

        if st.sidebar.button("🚀 INITIALIZE MONITORING"):
            model = load_yolo_model()
            tracker = sv.ByteTrack()
            box_annotator = sv.BoxAnnotator()
            alert_sys = AlertSystem()
            violation_counters = defaultdict(int)
            
            col_main, col_alerts = st.columns([3, 1])
            frame_place = col_main.empty()
            alert_place = col_alerts.empty()
            
            display_alerts = []
            cap_run = cv2.VideoCapture(tfile.name)
            
            while cap_run.isOpened():
                ret, frame = cap_run.read()
                if not ret: break
                
                results = model(frame, conf=conf_level, verbose=False)[0]
                detections = sv.Detections.from_ultralytics(results)
                detections = tracker.update_with_detections(detections)
                
                active_zone.draw(frame)
                
                if detections.tracker_id is not None:
                    for i in range(len(detections)):
                        xyxy, tid = detections.xyxy[i], detections.tracker_id[i]
                        # Feet detection: bottom center
                        feet = (int((xyxy[0] + xyxy[2]) / 2), int(xyxy[3]))

                        if active_zone.is_inside(feet):
                            violation_counters[tid] += 1
                            if violation_counters[tid] >= sens_val:
                                alert = alert_sys.trigger_alert("ZONE_BREACH", f"ID {tid} detected")
                                if alert: 
                                    display_alerts.insert(0, alert)
                                    play_sound() # The original beep sound
                        else:
                            violation_counters[tid] = 0

                annotated = box_annotator.annotate(scene=frame, detections=detections)
                frame_place.image(annotated, channels="BGR", use_container_width=True)
                
                with alert_place.container():
                    st.write("#### 🚨 LIVE ALERTS")
                    for a in display_alerts[:8]:
                        st.markdown(f'<div class="alert-box"><strong>[{a["time"]}]</strong> {a["msg"]}</div>', unsafe_allow_html=True)

            cap_run.release()
            os.remove(tfile.name)
    else:
        st.markdown("""
        <div class="status-box">
          <span class="status-dot"></span>
          SYSTEM IDLE — Awaiting Video Input
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()