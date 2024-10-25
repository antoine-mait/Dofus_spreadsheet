import cv2
import easyocr
import os
from HDV_SCREENSHOT_Bot import folder_dir

def  screenshot_reader():
    # Read image
    try:
        main_folder = folder_dir()# "D:\\Coding\\Dofus\\HDV_IMG\\"
        user_input = input("Do you want to Blackout the IMAGES(y/n)")
        for directory in ["HDV_CONSUMABLE", "HDV_ITEM", "HDV_RESOURCES" , "HDV_RUNES"]:
            print(f"Processing img in {directory} folder")

            path = os.path.join(main_folder,f"{directory}", f"{directory}_PRICE_IMG")  # Construct the full path

            image_files = [f for f in os.listdir(path) if f.endswith('.png')]
            IMAGES_Path = path
            for i, image_files in enumerate(image_files, start=1):

                IMAGE1 = os.path.join(IMAGES_Path, f"{directory}_{i}.png")
                blackout_folder = os.path.join(IMAGES_Path, "BLACKOUT_PRICE")
                check_blackout_img = os.path.join(blackout_folder, f"BLACKOUT_{os.path.basename(IMAGE1)}")
                if check_blackout_img is not None :
                    if user_input == "y" :
                        blackout_img = blackout(IMAGE1,blackout_folder)
                        img = cv2.imread(blackout_img)
                        if img is None:
                            print(f"Failed to load image: {blackout_img}")
                            continue                
                    else :
                        img = cv2.imread(check_blackout_img)
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
                    cleaned_data.extend(filtered_item)

                # Group the cleaned_data by 2 entries and print
                for j in range(0, len(cleaned_data), 2):
                    group1 = cleaned_data[j]
                    group2 = cleaned_data[j + 1] if j + 1 < len(cleaned_data) else ''
                    print(f"{group1} - {group2}")

    except KeyboardInterrupt:
        print("\nScript stopped with Ctrl + C.")

#def main_Data_to_Gsheet():
def blackout(IMAGE1,blackout_folder):

    region1 =(350, 0, 260, 1000)
    region2 = (775, 0, 50, 1000)
    try:
        img = cv2.imread(IMAGE1)
        if img is None : 
            print(f"Failed to load image for {IMAGE1}")
            return None
        if img is not None:
            cv2.imshow("Blackout Image", img)

        x1, y1, w1, h1 = region1  # First region to blackout
        x2, y2, w2, h2 = region2  # Second region to blackout
        img[y1:y1+h1, x1:x1+w1] = (0, 0, 0)  # Black out first region
        img[y2:y2+h2, x2:x2+w2] = (0, 0, 0)  # Black out second region
        os.makedirs(blackout_folder, exist_ok=True)

        blackout_path = os.path.join(blackout_folder, f"BLACKOUT_{os.path.basename(IMAGE1)}")
        if cv2.imwrite(blackout_path, img):
            print(f"Image saved to {blackout_path}")
            return blackout_path
        else:
            print("Failed to save blackout image.")
            return None
    except KeyboardInterrupt:
        print("\nScript stopped with Ctrl + C.")


if __name__ == "__main__":
     screenshot_reader()