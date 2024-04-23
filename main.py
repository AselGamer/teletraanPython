from aiohttp import web
from ultralytics import YOLO
from PIL import Image
import io
import socketio
import base64
import re
import json

 
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def frame(sid, data):
    with open('tmpImg.png', 'wb') as fh:
        base64_data = re.sub('^data:image/.+;base64,', '', data)
        b64 = base64.b64decode(base64_data)
        buf = io.BytesIO(b64)
        img = Image.open(buf)
        results = model(img)
        print(results[0].tojson())
        await sio.emit('frame', results[0].tojson(), room=sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    model = YOLO("best.pt")
    web.run_app(app, port=5000)