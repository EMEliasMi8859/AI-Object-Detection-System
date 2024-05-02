import torch
from PIL import Image

class Model:

    def __init__(self, scripts, method, wieghts):
        self.model = torch.hub.load(scripts,method,wieghts)
        return self.model
    def predict(self, image):
        return self.model(image)
    #load more width change wieght an other functions re load the wieght

class EVB:

    def __init__(self, scripts, method, wieghts):
        #'ultralytics/yolov5', 'custom', path='TorchYoloV5xPT/yolov5x.pt'
        self.model = Model(scripts, method, wieghts)

        #flags
        self.img_ch_free = True
        self.cnv_ch_free = True
        self.urg_cnv = False

        return None

    def ImageProcess(self):
        
        return None

    async def process_images(self, imagePath):
        self.img_ch_free = False

        savedImage = imagePath

        # Analyze detected objects
        predictions = model(savedImage)

        imagefile = mpimage.imread(savedImage)
        image_height, image_width, _ = imagefile.shape

        # Define grid boundaries
        grid_width = image_width / 3
        grid_height = image_height / 3

        object_positions = []
        # predictions[1] are objects


        for box in predictions.xyxy[0]:
            # Determine the object's position
            x1, y1, x2, y2, conf, cls_id = box
            # Get the class name using the class id
            class_name = predictions.names[int(cls_id)]
            #    Calculate the size of the bounding box
            width = x2 - x1
            height = y2 - y1
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            obj_in_image = [x1,y1,x2,y2]

            object_position = self.get_object_position(center_x, center_y, grid_width, grid_height)
            tempList = [class_name,object_position,obj_in_image]
            object_positions.append(tempList)

        if(os.path.isfile('conversations.txt')):
            with open("conversations.txt", 'a') as file:
                file.write(str(object_positions))
    

        if self.cnv_ch_free:
            await self.startConversation()
        elif not self.cnv_ch_free and self.urg_cnv:
            await self.startConversation()
            self.urg_cnv = False
        else:
            time.sleep(1.5)


        # Respond with text, acknowledging the image was received and processed
        x = 200
        # else:
        #     x = 400
        self.img_ch_free = True
        return "Processed text data from image" + str(x)


    async def startConversation():
        self.cnv_ch_free = False
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
        self.cnv_ch_free = True


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
