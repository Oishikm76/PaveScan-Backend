from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
import csv
from datetime import datetime
import os

# ==============================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connected dashboard clients
clients = []

# Create logs folder if needed
if not os.path.exists("logs"):
    os.makedirs("logs")

# CSV log file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
csv_file = f"logs/pavescan_{timestamp}.csv"

with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "timestamp","lat","lon","speed","acc_x","acc_y","acc_z",
        "gyro_x","gyro_y","gyro_z","mag_x","mag_y","mag_z",
        "azimuth","pitch","roll"
    ])

@app.get("/")
def dashboard():
    with open("dashboard.html", "r") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            packet = json.loads(data)

            # Write incoming packet to CSV
            with open(csv_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    packet.get("lat"), packet.get("lon"), packet.get("speed"),
                    packet.get("accel_x"), packet.get("accel_y"), packet.get("accel_z"),
                    packet.get("gyro_x"), packet.get("gyro_y"), packet.get("gyro_z"),
                    packet.get("mag_x"), packet.get("mag_y"), packet.get("mag_z"),
                    packet.get("azimuth"), packet.get("pitch"), packet.get("roll")
                ])

            # Broadcast to dashboards
            for client in clients:
                if client != websocket:
                    await client.send_text(json.dumps(packet))

    except WebSocketDisconnect:
        clients.remove(websocket)
