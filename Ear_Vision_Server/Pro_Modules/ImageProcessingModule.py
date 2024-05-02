import os
def calculate(img, model):
    #print("\t\t2222222222222222222222")
    results = model(img)
    #print("\t\t3333333333333333333333")
    #results.show()
    #results.print()
    #for box in results.xyxy[0]:
    #    x1, y1, x2, y2, conf, cls_id = box
    #    class_name = results.names[int(cls_id)]
    #    width = x2 - x1
    #    height = y2 - y1
    return results
    #print("\t\t44444444444444444444444")
#for box in results.xyxy[0]:
#    # Extract the coordinates
#    x1, y1, x2, y2, conf, cls_id = box
#    # Get the class name using the class id
#    class_name = results.names[int(cls_id)]#
#    Calculate the size of the bounding box
#    width = x2 - x1
#    height = y2 - y1



def checkFiles():
    coordinatesFile, conversationFile= "coordinatesFile.txt", "conversations.txt"
    if(not os.path.isfile(coordinatesFile)):
        with open(coordinatesFile, 'w') as file:
            file.write("000 Coordinates Stack")
    elif(not os.path.isfile(conversationFile)):
        with open(conversationFile, 'w') as file:
            file.write("000 conversation started")
