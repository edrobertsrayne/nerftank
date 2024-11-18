from microdot import Microdot, send_file
from microdot.websocket import with_websocket
from robot import RobotController
import asyncio
import json

app = Microdot()
robot = RobotController(
    right_motor_pins=[(33, 25, 32), (33, 25, 26)],
    left_motor_pins=[(16, 17, 15), (16, 17, 5)],
)


@app.route("/")
async def index(_):
    return send_file("/static/index.html")


@app.route("/static/<path:path>")
def static(_, path):
    if ".." in path:
        # Prevent directory traversal
        return "Not found", 404
    return send_file(f"/static/{path}")


@app.route("/ws")
@with_websocket
async def websocket(_, ws):
    while True:
        data = await ws.receive()
        message = json.loads(data)
        if message["type"] == "stick_data":
            # print(message["data"])
            robot.update(message["data"])


async def main():
    print("Starting web server")
    server = asyncio.create_task(app.start_server(port=80))
    print("Server successfully started on port 80")

    await server


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down.")
