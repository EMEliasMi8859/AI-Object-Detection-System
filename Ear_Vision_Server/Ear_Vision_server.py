import torch
from PIL import Image
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_socketio import SocketIO
# from flask_sockets import Sockets
import os, threading, time, asyncio
from Pro_Modules import ImageProcessingModule as IMPI
from matplotlib import pyplot as plt
import matplotlib.image as mpimage
from concurrent.futures import ThreadPoolExecutor
import shutil
# # Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='TorchYoloV5xPT/yolov5x.pt')

# # CustomModel = torch.hub.load('ultralytics/yolov5', 'custom', path='TorchYoloV5xPT/best.pt')

i = 0
imagefilepath =""
detectedImage = ""

ProcessImageIsFree = True
conversationIsFree = True

# IMPI.checkFiles()

app = Flask(__name__)
# sockets = Sockets(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/', methods=['GET'])
def mainRout():
    # imagefilepath = session.get('uploaded_image')
    return render_template("index.html"), 200

@app.route('/upload-image', methods=['POST'])
def upload_image():
    global ProcessImageIsFree
    if(ProcessImageIsFree):        
        ProcessImageIsFree = False
        image_file = request.files
        GyroData = [request.form.get('gyroscope_x'), request.form.get('gyroscope_y'), request.form.get('gyroscope_z')]
        processImage = threading.Thread(target=start_Image_Processing_thread, args=(image_file, GyroData,))
        processImage.start()
        return '''<script></script>'''
    return '''<script></script>'''


def start_Image_Processing_thread(image_file, GyroData):
    global  ProcessImageIsFree
    if 'image' not in image_file:
        return jsonify({'error': 'No image part'}), 400
    image = image_file['image']
    savedImage = 'static/Raw_Images/image_file.jpg'
    # savedImage = 'received_image' + str(i) + '.jpg'
    image.save(savedImage) 

    try:
        asyncio.get_running_loop() # Triggers RuntimeError if no running event loop
        # Create a separate thread so we can block before returning
        with ThreadPoolExecutor(1) as pool:
            result = pool.submit(lambda: asyncio.run(process_images())).result()
    except RuntimeError:
        result = asyncio.run(process_images())
    # asyncio.create_task(process_images())

        # process_images()
        # break
    # text_data = process_image(request, image)
    # gyroscope_x, gyroscope_y, gyroscope_z = request.form.get('gyroscope_x'), request.form.get('gyroscope_y'), request.form.get('gyroscope_z')
    print(f"one image recieved")
    # strfinal = text_data  + "Image Received and Processed\n the gyro \t\t\X=" + str(gyroscope_x) + 'Y=' + str(gyroscope_y) + "Z=" + str(gyroscope_z)
    # strfinal =  "Image Received and Processed\n the gyro \t\tX=" + str(gyroscope_x) + 'Y=' + str(gyroscope_y) + "Z=" + str(gyroscope_z)

    predloc="static/Raw_Images/prediction_file.jpg"
    while True:
        print("checking file .....")
        if(os.path.exists("runs/detect/exp/image_file.jpg")):
            shutil.move("runs/detect/exp/image_file.jpg", predloc)
            os.rmdir("runs/detect/exp")
            break;
        else: time.sleep(0.1)
    print("near results .......")
    ProcessImageIsFree = True

@socketio.on('connect')
def onconnect():
    #processImage = threading.Thread(target=process_images)
    #sendResults = threading.Thread(target=startConversation)
    #processImage.start()
    #sendResults.start()
    print("the app is connected through a socket")
    ProcessImageIsFree = True
    conversationIsFree = True
# WebSocket event handler
@socketio.on('message')
def handle_message(data):
    print('Received message:', data)





async def process_images():
    print('Threading image process started')
    #IMPI.checkFiles()

    x = 0
    savedImage = 'static/Raw_Images/image_file.jpg'
    #if(imagetoprocess.()):
    predictions = model(savedImage)
    predictions.save()
    # predictions.save(predloc)
    # cv2.imsave(predloc, predictions)

    # predictions.show(save=True, show=False, save_dir="static/Raw_Images/", save_file="prediction_file.jpg")
    #time.sleep(4)
    imagefile = mpimage.imread(savedImage)
    image_height, image_width, _ = imagefile.shape
    # Define grid boundaries
    grid_width = image_width / 3
    grid_height = image_height / 3

    # Analyze detected objects
    # object_positions = []
    print(predictions)
    message = generate_text_messages(results = predictions, grid_width = grid_width, grid_height = grid_height, device_orientation = 0, gyroscope_data = 0 )
    print("1-1-1-1-1-1-1-1-1-1-1-1-1-1" + ' '.join(message))
    # for detection in predictions:
    #     # Assuming detection is a bounding box: [x1, y1, x2, y2] 
    #     bbox = detection['bbox']
    #     # Calculate the centroid of the bounding box
    #     center_x = (bbox[0] + bbox[2]) / 2
    #     center_y = (bbox[1] + bbox[3]) / 2

    # for box in predictions.xyxy[0]:
    #     # Determine the object's position
    #     x1, y1, x2, y2, conf, cls_id = box
    #     # Get the class name using the class id
    #     class_name = predictions.names[int(cls_id)]#
    #     #    Calculate the size of the bounding box
    #     width = x2 - x1
    #     height = y2 - y1
    #     center_x = (x1 + x2) / 2
    #     center_y = (y1 + y2) / 2


    #     object_position = get_object_position(center_x, center_y, grid_width, grid_height)
    #     tempList = [class_name,object_position,width,height]
    #     object_positions.append(tempList)
    print("11111111111111111111111111")
    await startConversation(message)
    print("222222222222222222222222222")
    #else: time.sleep(5)

    # Respond with text, acknowledging the image was received and processed
    return message

async def startConversation(message , urgent = False):
    global conversationIsFree
    strmessage = ','.join(message)
    if(conversationIsFree and not urgent):
        conversationIsFree = False
        socketio.send(str(strmessage))
        # timeElapsed = len(str(printText))/10
        # time.sleep(4)
        speach_rate = 120
        estimated_time = (len(strmessage.split(' ')) / speach_rate) * 60
        # time.sleep(estimated_time)
        conversationIsFree = True
    else:
        socketio.send(str(message))

    

# Function to categorize position based on centroid (center_x, center_y)
# def get_object_position(center_x, center_y, grid_width, grid_height):
#     grid_x = int(center_x // grid_width)
#     grid_y = int(center_y // grid_height)

#     if grid_x == 1 and grid_y == 1:
#         return 'center'
#     elif grid_x == 0 and grid_y == 1:
#         return 'center left'
#     elif grid_x == 2 and grid_y == 1:
#         return 'center right'
#     elif grid_x == 1 and grid_y == 0:
#         return 'far center'
#     elif grid_x == 0 and grid_y == 0:
#         return 'far left'
#     elif grid_x == 2 and grid_y == 0:
#         return 'far right'
#     elif grid_x == 1 and grid_y == 2:
#         return 'near center'
#     elif grid_x == 0 and grid_y == 2:
#         return 'near left'
#     else:  # grid_x == 2 and grid_y == 2
#         return 'near right'# Function to categorize position based on centroid (center_x, center_y)


def get_object_position(center_x, center_y, grid_width, grid_height):
    grid_x = int(center_x // grid_width)
    grid_y = int(center_y // grid_height)

    if grid_x == 1 and grid_y == 1:
        return 'front'
    elif grid_x == 0 and grid_y == 1:
        return 'left'
    elif grid_x == 2 and grid_y == 1:
        return 'right'
    elif grid_x == 1 and grid_y == 0:
        return 'front'
    elif grid_x == 0 and grid_y == 0:
        return 'left'
    elif grid_x == 2 and grid_y == 0:
        return 'right'
    elif grid_x == 1 and grid_y == 2:
        return 'front'
    elif grid_x == 0 and grid_y == 2:
        return 'left'
    else:  # grid_x == 2 and grid_y == 2
        return 'right'


def get_object_distance(prd_width, prd_height, obj_width, obj_height):


    return None

def generate_text_messages(results, grid_width, grid_height, device_orientation, gyroscope_data):

    text_messages = []
    class_name_LSTM = ""
    num_same_class = 1
    directions_same_classes = ""
    distance_same_classes = 0
    i = 0
    for box in results.xyxy[0]:
        i+=1
        # Determine the object's position
        x1, y1, x2, y2, conf, cls_id = box
        # Get the class name using the class id
        class_name = results.names[int(cls_id)]#
        #    Calculate the size of the bounding box
        width = x2 - x1
        height = y2 - y1
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2


        object_position = get_object_position(center_x, center_y, grid_width, grid_height)
        objetc_distance = 5
        # if(box is in a list of lists):
            # objetc_distance = get_object_distance(width, height, list[class_name][0], list[class_name][1])
        print(class_name)
        # Generate the text message for the object
        if(' '.join(text_messages).find(class_name) != -1):
            num_same_class += 1
            if(directions_same_classes.find(object_position) == -1):
                directions_same_classes += " " + object_position
            if(objetc_distance < 2):
                startConversation(messsage = "stop", urgent = True)

        else:
            print("9999999999999999999999999999999999")
            if(num_same_class > 1):
                # directions_same_classes = directions_same_classes.subString(0, directions_same_classes.length())
                if(directions_same_classes.find(" ") != -1):
                    directions_same_classes = directions_same_classes[:directions_same_classes.rindex(' ')]  + " and " + directions_same_classes[directions_same_classes.rindex(' '):]
                text_message = f"{num_same_class} {class_name_LSTM}s on your {directions_same_classes}"
                num_same_class, directions_same_classes = 1, ""
            else:
                # text_message = f"a {class_name} on your {object_position}, {objetc_distance}."
                text_message = f"a {class_name} on your {object_position}"
            if(i == 1):
                if(len(results.xyxy[0]) > 1):
                    text_messages.append("There are ")
                elif(len(results.xyxy[0]) == 1):
                    text_messages.append("There is ")
            if(i == len(results.xyxy[0]) and i != 1):
                text_message = " and " + text_message
                text_messages.append(text_message)
            else:
                text_messages.append(text_message)

        class_name_LSTM = class_name

    if(num_same_class > 1 and (directions_same_classes != "" and directions_same_classes != None)):
        try:
            directions_same_classes = directions_same_classes[:directions_same_classes.rindex(' ')]  + " and " + directions_same_classes[directions_same_classes.rindex(' '):]
            text_message = f"{num_same_class} {class_name_LSTM}s on your {directions_same_classes}"
            num_same_class, directions_same_classes = 1, ""
            if(i > 1):
                text_messages.append("There are ")
            elif(i == 1):
                text_messages.append("There is ")
            text_messages.append(text_message)
        except:
            pass

    return text_messages





if __name__ == '__main__':
    threading.Thread(target=socketio.run(app, host='0.0.0.0', port=5000, debug=True)).start()
    # socketio.run(app, host='0.0.0.0', port=5000, debug=True)





