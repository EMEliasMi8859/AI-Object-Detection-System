import torch
from PIL import Image
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
# from flask_sockets import Sockets
import os, threading, time, asyncio
from Pro_Modules import ImageProcessingModule as IMPI
from matplotlib import pyplot as plt
import matplotlib.image as mpimage
# # Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='TorchYoloV5xPT/yolov5x.pt')
# # CustomModel = torch.hub.load('ultralytics/yolov5', 'custom', path='TorchYoloV5xPT/best.pt')


i = 0

ProcessImageIsFree = True
conversationIsFree = True

# IMPI.checkFiles()

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
    savedImage = '../Raw_Images/received_image' + '1' + '.jpg'
    # savedImage = 'received_image' + str(i) + '.jpg'
    image.save(savedImage)
    # while True:
    if(ProcessImageIsFree):
        asyncio.run(process_images())
        # process_images()
        # break
    else:
        time.sleep(2)
    # text_data = process_image(request, image)
    gyroscope_x, gyroscope_y, gyroscope_z = request.form.get('gyroscope_x'), request.form.get('gyroscope_y'), request.form.get('gyroscope_z')
    print(f"one image recieved")
    # strfinal = text_data  + "Image Received and Processed\n the gyro \t\t\X=" + str(gyroscope_x) + 'Y=' + str(gyroscope_y) + "Z=" + str(gyroscope_z)
    strfinal =  "Image Received and Processed\n the gyro \t\t\X=" + str(gyroscope_x) + 'Y=' + str(gyroscope_y) + "Z=" + str(gyroscope_z)
    return jsonify({'text': strfinal}), 200
@socketio.on('connect')
def onconnect():
    #processImage = threading.Thread(target=process_images)
    #sendResults = threading.Thread(target=startConversation)
    #processImage.start()
    #sendResults.start()
    print("the app is connected through a socket")
# WebSocket event handler
@socketio.on('message')
def handle_message(data):
    print('Received message:', data)





async def process_images():
    ProcessImageIsFree = False
    print('Threading image process started')
    #IMPI.checkFiles()

    x = 0
    savedImage = '../Raw_Images/received_image' + '1' + '.jpg'
    #if(imagetoprocess.()):

    print("\t\t11111111111111111111")
    predictions = model(savedImage)
    #time.sleep(4)
    print("\t\t55555555555555555555")
    imagefile = mpimage.imread(savedImage)
    image_height, image_width, _ = imagefile.shape
    # Define grid boundaries
    grid_width = image_width / 3
    grid_height = image_height / 3

    # Analyze detected objects
    object_positions = []
    print(predictions)

    # for detection in predictions:
    #     # Assuming detection is a bounding box: [x1, y1, x2, y2]
    #     bbox = detection['bbox']
    #     # Calculate the centroid of the bounding box
    #     center_x = (bbox[0] + bbox[2]) / 2
    #     center_y = (bbox[1] + bbox[3]) / 2

    for box in predictions.xyxy[0]:
        # Determine the object's position
        x1, y1, x2, y2, conf, cls_id = box
        # Get the class name using the class id
        class_name = predictions.names[int(cls_id)]#
        #    Calculate the size of the bounding box
        width = x2 - x1
        height = y2 - y1
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2


        object_position = get_object_position(center_x, center_y, grid_width, grid_height)
        tempList = [class_name,object_position,width,height]
        object_positions.append(tempList)
    if(os.path.isfile('conversations.txt')):
        with open("conversations.txt", 'w') as file:
            file.write(str(object_positions))
    print("one iteratinon of process image")
    await startConversation()
    #else: time.sleep(5)

    # Respond with text, acknowledging the image was received and processed
    x = 200
    # else:
    #     x = 400
    ProcessImageIsFree = True
    return "Processed text data from image" + str(x)

async def startConversation():
    conversationIsFree = False
    print('Threading conversation started')
    #IMPI.checkFiles()
    printText = ""
    with open('conversations.txt', 'r') as file:
        printText = file.readlines()
    print("\t\t\t\tconversation: ", printText)
    socketio.send(str(printText))
    timeElapsed = len(str(printText))/10
    time.sleep(4)
    print("one iteration of conversation")
    conversationIsFree = True

# Function to categorize position based on centroid (center_x, center_y)
def get_object_position(center_x, center_y, grid_width, grid_height):
    grid_x = int(center_x // grid_width)
    grid_y = int(center_y // grid_height)

    if grid_x == 1 and grid_y == 1:
        return 'center'
    elif grid_x == 0 and grid_y == 1:
        return 'center left'
    elif grid_x == 2 and grid_y == 1:
        return 'center right'
    elif grid_x == 1 and grid_y == 0:
        return 'far center'
    elif grid_x == 0 and grid_y == 0:
        return 'far left'
    elif grid_x == 2 and grid_y == 0:
        return 'far right'
    elif grid_x == 1 and grid_y == 2:
        return 'near center'
    elif grid_x == 0 and grid_y == 2:
        return 'near left'
    else:  # grid_x == 2 and grid_y == 2
        return 'near right'

if __name__ == '__main__':
    threading.Thread(target=socketio.run(app, host='0.0.0.0', port=5000, debug=True)).start()
    # socketio.run(app, host='0.0.0.0', port=5000, debug=True)







