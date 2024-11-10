from microdot import Microdot, send_file
from microdot.websocket import with_websocket
import asyncio
import json

app = Microdot()


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
        try:
            message = json.loads(data)
        except json.JSONDecodeError:
            message = data
        print(message)
        # await ws.send(json.dumps(message))


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
