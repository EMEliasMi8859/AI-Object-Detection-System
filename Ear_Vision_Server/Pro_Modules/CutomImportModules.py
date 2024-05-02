import torch
from models.yolo import Model
from utils.general import check_img_size

# Ensure that you are in the root of the yolov5 directory for this to work

# Load the model architecture from models/yolo.py
model = Model(cfg='yolov5/models/yolov5x.yaml')

# Load the pretrained weights
weights_path = '../TorchYoloV5xPT/yolov5x.pt'  # Adjust if necessary to match the location of yolov5x.pt
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

ckpt = torch.load(weights_path, map_location=device)  # Load to appropriate device
model.load_state_dict(ckpt['yolov5/model'].state_dict())

# Check the image size
imgsz = check_img_size(640, s=model.stride.max())  # Adjust 640 to your desired image size if different

# If you want to deploy the model for inference, set it to evaluation mode
model.eval()
