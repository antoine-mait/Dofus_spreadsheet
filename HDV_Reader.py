import cv2
import easyocr
import os

# RUN with PYTHON 3.10 in myenv ! 

# Read image
IMAGES_Path = r"D:\Coding\Dofus\tmp\images"
IMAGE1 = os.path.join(IMAGES_Path, "AMULETTE_200.jpg")

img = cv2.imread(IMAGE1)

# Instance Text Detector

reader = easyocr.Reader(['fr'], gpu=False)

# Detect text on image

data = reader.readtext(img)
cleaned_data = []

# Extract relevant details
for item in data:
    # Take only the elements that are not np.int32 or np.float64
    # Here we are only interested in strings (item names)
    filtered_item = [element for element in item if isinstance(element, str)]
    
    # Extend cleaned_data with the filtered names
    for name in filtered_item:
        name = name.replace("%", "")
        name = name.replace("*", "")
        cleaned_data.append(name)
# Group the cleaned data by 4 entries
grouped_data = []

for i in range(0, len(cleaned_data), 4):
    group = cleaned_data[i:i + 4]
    group[3] = group[3].replace(" ","")
    grouped_data.append(group)

# Print the grouped data
for group in grouped_data:
    print(group)