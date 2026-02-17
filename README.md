# Hacksagon_AI-ML
Hacksagon AI/ML model 
# Hacksagon_AIML

#  AI Sentinel Pro — Real-Time Smart Surveillance System

AI Sentinel Pro is an intelligent computer-vision based surveillance system that detects intrusions inside restricted zones from video feeds and triggers real-time alerts with sound and visual notifications.

It uses YOLOv8 object detection, multi-object tracking, and zone intelligence to simulate a real-world automated security monitoring solution.

---

##  Features

### Intelligent Detection
- Real-time human detection using YOLOv8
- Multi-object tracking using ByteTrack
- Persistent ID assignment for each person

### Restricted Zone Monitoring
- User-configurable detection area
- Intrusion detection based on feet position (accurate entry detection)
- Adjustable alert sensitivity to avoid false alarms

### Smart Alerts
- Live alert panel
- Timestamped violations
- Automatic beep alarm
- Cooldown system to prevent alert spam

### Interactive Dashboard
- Built using Streamlit
- Real-time calibration preview
- Adjustable AI confidence threshold
- Dark themed UI

---

##  How It Works

1. User uploads a video feed
2. System detects people in each frame
3. Tracker assigns unique IDs
4. Feet position is checked inside restricted zone
5. If a person stays longer than threshold → alert triggered

---

##  Tech Stack

| Component | Technology |
|--------|------|
| Detection | YOLOv8 |
| Tracking | ByteTrack |
| UI | Streamlit |
| Image Processing | OpenCV |
| Annotation | Supervision |
| Alerts | Audio + Visual |
| Language | Python |

---

##  Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/ai-sentinel-pro.git
cd ai-sentinel-pro
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Model Weights
The application will automatically download the YOLOv8 model (`yolov8n.pt`) during first run.

---

##  Run the Application
```bash
streamlit run app.py
```

---

##  Usage

1. Upload a video (mp4 / mov / avi)
2. Adjust settings:
   - Alert Sensitivity
   - Confidence Threshold
   - Detection Zone
3. Click **Initialize Monitoring**
4. Monitor real-time alerts

---

## ⚙️ Parameters

| Setting | Description |
|------|------|
| Alert Sensitivity | Frames required inside zone before alert |
| AI Confidence | Minimum detection confidence |
| Zone Calibration | Defines restricted region |

---

##  Project Structure
```
AI-Sentinel-Pro/
│── app.py
│── alert.wav
│── bg_dark.jpg
│── requirements.txt
│── README.md
```

---

##  Applications
- Smart CCTV surveillance
- Restricted lab monitoring
- Industrial safety zones
- Campus security
- Warehouse monitoring
- Exam hall monitoring

---

##  Future Improvements
- Weapon detection
- Face recognition whitelist
- Live camera streaming
- Multi-zone detection
- Cloud deployment

---

##  Author
AI/ML Computer Vision Surveillance Project
