# GAGLEVISION Technical Assessment

## Project Architecture
This project is a real-time microservices pipeline:
1. **cv_producer.py**: YOLOv8 + Optical Flow tracker. Sends JSON payloads to Kafka.
2. **db_consumer.py**: Consumes Kafka messages and writes analytics to PostgreSQL.
3. **app.py**: Streamlit Dashboard displaying the live video feed and metrics.

## Solving Articulated Motion
To detect "ACTIVE" states when only the excavator arm is moving (while tracks are stationary), the system applies **Dense Optical Flow (Farneback)** strictly within the equipment's bounding box. By tracking pixel movement magnitude and angles, it successfully distinguishes between stationary states, digging (vertical/diagonal vectors), and swinging (horizontal vectors) without requiring computationally heavy 3D-CNNs, ensuring real-time performance.
