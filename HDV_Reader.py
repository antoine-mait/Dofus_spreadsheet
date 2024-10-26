import os
import re
import numpy as np
import pytesseract as tess
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()
main_folder= os.environ.get("MAIN_IMG_FOLDER")

def process_image(IMAGE1, user_input, blackout_folder):
    """Process a single image: blackout if needed, extract text."""
    if user_input == "y":
        blackout_img = blackout(IMAGE1, blackout_folder)
        img = Image.open(blackout_img)
        if img is None:
            print(f"Failed to load image: {blackout_img}")
            return None
    else:
        check_blackout_img = os.path.join(blackout_folder, f"BLACKOUT_{os.path.basename(IMAGE1)}")
        img = Image.open(check_blackout_img)
    
    # Instance Text Detector
    img = img.convert('L')  # Convert to grayscale
    img = img.point(lambda x: 0 if x < 128 else 255, '1') 
    custom_config = r'--oem 3 --psm 6'
    text = tess.image_to_string(img, config=custom_config)
    
    results = []
    words = text.splitlines()
    for line in words:
        # Find all letters and numbers
        letters = re.findall(r'[^\d]+', line)  # Extract all non-digit characters
        numbers = re.findall(r'\d+', line)  # Extract all digit sequences

        # Join letters and numbers into a formatted string
        letter_part = ''.join(letters).strip()
        number_part = ' '.join(numbers).replace(" ", "")

        if letter_part and number_part:  # Only print if both parts exist
            results.append(f"{letter_part} : {number_part}")
    
    return results

def screenshot_reader(user_input):
    """Read images and extract text using multithreading."""
    all_results = []

    for directory in ["HDV_CONSUMABLE", "HDV_ITEM", "HDV_RESOURCES", "HDV_RUNES"]:
        print(f"Processing img in {directory} folder")
        path = os.path.join(main_folder, f"{directory}", f"{directory}_PRICE_IMG")  # Construct the full path

        image_files = [f for f in os.listdir(path) if f.endswith('.png')]
        IMAGES_Path = path
        blackout_folder = os.path.join(IMAGES_Path, "BLACKOUT_PRICE")

        with ThreadPoolExecutor() as executor:
            future_to_image = {}
            future_to_image = {executor.submit(process_image, os.path.join(IMAGES_Path, f"{directory}_{i}.png"), user_input, blackout_folder): i for i in range(1, len(image_files) + 1)}
            for future in as_completed(future_to_image):
                try:
                    results = future.result()
                    if results:
                        all_results.extend(results)
                except Exception as e:
                    print(f"Error processing image: {e}")

    # Print all results after processing
    for result in all_results:
        print(result)

def blackout(IMAGE1, blackout_folder):
    """Blackout specific regions of the image."""
    region1 = (350, 0, 610, 1000)
    region2 = (775, 0, 825, 1000)

    try:
        img = Image.open(IMAGE1)
        
        # Convert image to an array for faster pixel manipulation
        img_array = np.array(img)

        # Apply blackouts using numpy slicing
        img_array[region1[1]:region1[3], region1[0]:region1[2]] = 0  # Blackout first region
        img_array[region2[1]:region2[3], region2[0]:region2[2]] = 0  # Blackout second region

        os.makedirs(blackout_folder, exist_ok=True)
        blackout_path = os.path.join(blackout_folder, f"BLACKOUT_{os.path.basename(IMAGE1)}")
        
        # Convert back to an Image object and save
        Image.fromarray(img_array).save(blackout_path)
        print(f"Image saved to {blackout_path}")
        return blackout_path

    except KeyboardInterrupt:
        print("\nScript stopped with Ctrl + C.")
    except Exception as e:
        print(f"Error processing image: {e}")

def main_screenshot_reader():
    user_input = input("Do you want to Blackout the IMAGES(y/n): ")
    screenshot_reader(user_input)

if __name__ == "__main__":
    main_screenshot_reader()
