import torch
from PIL import Image

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='TorchYoloV5xPT/yolov5x.pt')  # Make sure to adjust the path if necessary
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
# from flask_sockets import Sockets
import os

i = 0


from Pro_Modules import ImageProcessingModule as IMPI






















app = Flask(__name__)
# sockets = Sockets(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/', methods=['GET'])
def mainRout():
    return "main route", 200
@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    image = request.files['image']

    # Assuming the image is processed and you have the result
    text_data = process_image(image)

    # You could use the socketio.emit function here if needed
    # socketio.emit('image_processed', {'text': text_data})

    gyroscope_x = request.form.get('gyroscope_x')
    gyroscope_y = request.form.get('gyroscope_y')
    gyroscope_z = request.form.get('gyroscope_z')
    print(f"Gyroscope data: x={gyroscope_x}, y={gyroscope_y}, z={gyroscope_z}")
    strfinal = text_data  + "Image Received and Processed\n the gyro \t\t\X=" + str(gyroscope_x) + 'Y=' + str(gyroscope_y) + "Z=" + str(gyroscope_z)

    return jsonify({'text': strfinal}), 200

# @sockets.route('/echo')
# def echo_socket(ws):
#     while not ws.closed:
#         message = ws.receive()
#         if message:
#             print("recieved message"+message)
#             ws.send("Echo:" + message)
def process_image(image_file):
    global i
    # Dummy process function returning a text representation of the imageglobal i
    image_file = request.files['image']
    i+= 1
    x = 0
    if image_file:
        # Assuming image processing happens here
        # Save the image file, process it, etc.
        savedImage = 'received_image' + str(i) + '.jpg'
        image_file.save(savedImage)
        results = IMPI.calculate(savedImage, model)
        class_names = ""
        for box in results.xyxy[0]:
            # Extract the coordinates
            x1, y1, x2, y2, conf, cls_id = box
            # Get the class name using the class id
            class_names += results.names[int(cls_id)]
            print(class_names)
            # Calculate the size of the bounding box
            width = x2 - x1
        socketio.send("recieved images"  + class_names)
        print(class_names)
        # Respond with text, acknowledging the image was received and processed
        x = 200
    else:
        x = 400
    return "Processed text data from image" + str(x)



@socketio.on('connect')
def onconnect():
    print("the app is connected through a socket")
# WebSocket event handler
@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    # socketio.emmit('response', {'data': 'Received your message!'})

# You could add additional WebSocket event handlers here if needed

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == '__main__':
    # Note that when using SocketIO, use socketio.run instead of app.run
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # Run on all interfaces so it's accessible from the network


# if __name__ == "__main__":
#     from gevent import pywsgi
#     from geventwebsocket.handler import WebSocketHandler
#     server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
#     server.serve_forever()