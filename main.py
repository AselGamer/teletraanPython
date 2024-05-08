from aiohttp import web
from ultralytics import YOLO
from PIL import Image
import io
import socketio
import base64
import re
import json

sio = socketio.AsyncServer(cors_allowed_origins='*')

class TeletranServer:
    app = web.Application()
    sio.attach(app)
    model = YOLO("models/best.pt")

    async def procesarImagen(self, sid, data):
        base64_data = re.sub('^data:image/.+;base64,', '', data)
        print(base64_data)
        b64 = base64.b64decode(base64_data)
        buf = io.BytesIO(b64)
        img = Image.open(buf)
        results = self.model(img, verbose=False)
        await sio.emit('frame', results[0].tojson(), room=sid)
    # fin de procesarImagen

    @sio.event
    def connect(sid, environ):
        print("connect ", sid)

    
    async def frame(self, sid, data):
        await self.procesarImagen(sid, data)

    @sio.event
    def disconnect(sid):
        print('disconnect ', sid)

    def start(self, port=5000):
        sio.on('frame', self.frame)
        web.run_app(self.app, port=port)

server = TeletranServer()
server.start()
    
 

