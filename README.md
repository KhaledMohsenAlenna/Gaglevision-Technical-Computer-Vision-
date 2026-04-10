Autonomous Industrial Equipment Monitoring & Activity Analytics


🎯 Executive Summary
This project implements an end-to-end Computer Vision pipeline designed for the real-time monitoring of heavy industrial machinery (excavators) in mining and construction environments. The core innovation lies in its ability to differentiate between "Idle" and "Productive" states by analyzing Articulated Motion—detecting mechanical operations even when the vehicle's chassis remains stationary.

⚙️ Core Technical Features
Object Detection & Temporal Tracking: Leverages YOLOv8 with BoT-SORT/ByteTrack to maintain consistent ID assignment across frames, even under partial occlusion.

Articulated Motion Analysis: Employs Dense Optical Flow (Farneback Algorithm) within localized bounding box regions. This bypasses the limitations of centroid-based tracking by quantifying pixel-level velocity vectors to identify digging, swinging, and dumping cycles.

State-Aware Utilization Engine: A rolling-window buffer logic calculates real-time Utilization (U%), filtering out transient noise to provide stable operational metrics.

Dual-Tier Deployment Architecture:

Enterprise: Scalable microservices orchestrated via Docker, using Apache Kafka for high-throughput messaging and PostgreSQL for persistence.

Evaluation (Lite): High-speed local synchronization via JSON buffers and a Streamlit-based analytics dashboard for rapid prototyping and edge deployment.

🧠 The Articulated Motion Challenge
Standard tracking algorithms often misclassify stationary heavy equipment as "Inactive." By integrating Optical Flow within the ROI (Region of Interest), this system extracts motion magnitude and angular orientation. This enables the distinction between:

Vertical Displacement: Digging/Dumping cycles.

Angular Displacement: Swinging operations.

Zero Magnitude: True Idle state.

🛠️ Deployment & Execution
1. Environment Configuration
Ensure you are using a virtual environment (Python 3.9+) to isolate dependencies:

Bash

# Initialize and activate environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1

# Install production-grade dependencies
pip install --upgrade pip
pip install -r requirements.txt
2. Standalone Demonstration (Local Mode)
To execute the lightweight pipeline for evaluation:

Inference Engine: Process video frames and generate telemetry.

Bash

python cv_producer_local.py
Analytics Dashboard: Visualize real-time metrics and equipment status.

Bash

streamlit run app_local.py


👨‍💻 Author
Khaled Mohsen Abdellatif B.Sc. in Data Science and Artificial Intelligence, Zewail City. Specialized in Deep Learning, Computer Vision, and Distributed Systems.
