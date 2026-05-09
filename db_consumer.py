import json
import psycopg2
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'equipment_topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

conn = psycopg2.connect(dbname="equipment_db", user="user", password="password", host="localhost", port="5432")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS analytics
    (frame_id INT, equipment_id VARCHAR, state VARCHAR, activity VARCHAR, active_sec FLOAT, util_pct FLOAT)''')
conn.commit()

print("Listening to Kafka and writing to PostgreSQL...")
for msg in consumer:
    d = msg.value
    cursor.execute('INSERT INTO analytics VALUES (%s, %s, %s, %s, %s, %s)',
        (d['frame_id'], d['equipment_id'], d['current_state'], d['current_activity'],
         d['time_analytics']['total_active_seconds'], d['time_analytics']['utilization_percent']))
    conn.commit()
    print(f"Saved Frame {d['frame_id']} to DB")
