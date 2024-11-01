import pyautogui
import random
import time
import cv2
import easyocr
import numpy as np
import os
import re
import pytesseract as tess
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from tmp.correction import correction_dict
from dotenv import load_dotenv

load_dotenv()
main_folder= os.environ.get("MAIN_IMG_FOLDER")
tmp_folder= os.environ.get("folder_dir_tmp")

def HDV_Reader():
    """
    Processes images of market prices for items in the game Dofus.

    This function reads images from specified directories, optionally applies a blackout effect to 
    obscure certain areas, and extracts text using Tesseract (Tess) for Optical Character Recognition (OCR). 
    The extracted text is corrected based on a predefined dictionary and saved to a text file.

    The process is divided into several internal functions:
    - `process_image`: Applies blackout to images and extracts text using Tesseract OCR.
    - `screenshot_reader`: Reads images from directories, processes them in parallel, 
      and compiles the results into a text file.
    - `blackout`: Obscures specific regions of the image.
    - `main_screenshot_reader`: Initiates the screenshot reading process based on user input (Optionnal).
    """
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
        custom_config = r'--oem 3 --psm 6 -l fra'
        text = tess.image_to_string(img, config=custom_config)
        
        results = []
        words = text.splitlines()
        for line in words:
            for wrong, correct in correction_dict.items():
                line = line.replace(wrong, correct)
            # Find all letters and numbers
            letters = re.findall(r'[^\d]+', line)  # Extract all non-digit characters
            numbers = re.findall(r'\d+', line)  # Extract all digit sequences

            # Join letters and numbers into a formatted string
            letter_part = ''.join(letters).strip()
            number_part = ' '.join(numbers).replace(" ", "")

            if letter_part and number_part:  # Only print if both parts exist
                results.append(f"{letter_part}, {number_part}")
        
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
                future_to_image = ({executor.submit(process_image, 
                                                    os.path.join(IMAGES_Path, f"{directory}_{i}.png"), 
                                                    user_input, blackout_folder):
                                                      i for i in range(1, len(image_files) + 1)})
                for future in as_completed(future_to_image):
                    try:
                        results = future.result()
                        if results:
                            all_results.extend(results)
                    except Exception as e:
                        print(f"Error processing image: {e}")

        # Print all results after processing
        dir_path = os.path.join("tmp","HDV_Price.txt")
        with open(dir_path, "w" , encoding="utf-8") as file:
            for results in all_results : 
                file.write(f"{results}\n")

        print(f"All price written on {dir_path}")

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
        user_input = "y" #input("Do you want to Blackout the screenshot ? (y/n)")
        screenshot_reader(user_input)

    main_screenshot_reader()

def HDV_Screenshot():
    """
    Captures screenshots of items from the HDV (Auction House) in the game Dofus,
    and interacts with the game's user interface to find and click specific images.
    
    This function is designed to:
    1. Navigate the Auction House based on coordinates.
    2. Take screenshots of items within the Auction House based on the type of items being traded.
    3. Locate and click images representing various items types in the Auction House.
    4. Manage mouse movements with jitter for more natural interactions.
    
    Nested Functions:
    - move_with_jitter: Smoothly moves the mouse with slight random variations.
    - find_and_click_image: Searches for a given image on the screen and clicks it.
    - screen_shot_items: Captures and saves screenshots of items.
    - scroll: Performs scrolling action to navigate through item lists.
    - item_type: Determines the type of items based on the current map and clicks on them.
    - map: Coordinates the entire process of taking screenshots and interacting with the Auction House.
    - coordinate: Checks the player's current map and validates it against expected coordinates.
    - start_map: Initializes the starting map for navigation.
    - map_switch: Handles the transition between different Auction House types and their corresponding actions.
    - click_right: Clicks on the right side of the screen with a jitter effect.
    - click_left: Clicks on the left side of the screen with a jitter effect.
    - click_top: Clicks on the top area of the screen with a jitter effect.
    - click_bottom: Clicks on the bottom area of the screen with a jitter effect.
    - loop_main: Repeatedly invokes the main navigation and interaction process.
    - main_bot: Main entry point to start the Auction House interaction process.
    """
    def move_with_jitter(start_pos, end_pos, steps=5):
        """
        Moves the mouse from the start position to the end position with a jitter effect.

        Parameters:
        - start_pos (tuple): The starting (x, y) position of the mouse.
        - end_pos (tuple): The ending (x, y) position to move the mouse to.
        - steps (int): The number of intermediate steps for the movement.
        """
        start_x, start_y = start_pos
        end_x, end_y = end_pos

        for i in range(steps + 1):
            # Calculate the position in a straight line
            x = start_x + (end_x - start_x) * (i / steps)
            y = start_y + (end_y - start_y) * (i / steps)

            # Add jitter to the mouse movement
            jitter_x = random.uniform(-10, 10)
            jitter_y = random.uniform(-10, 10)

            pyautogui.moveTo(x + jitter_x, y + jitter_y, duration=0.01)

    def find_and_click_image(image_path, folder_dir, map_name, scale_range=np.linspace(0.25, 2, 8)): 
        """
        Finds and clicks on an image in the game screenshot.

        Parameters:
        - image_path (str): Path to the image to be found.
        - folder_dir (str): Directory containing the images.
        - map_name (str): Name of the current map for context.
        - scale_range (np.ndarray): Array of scales to check for image matching.

        Returns:
        - bool: True if the STOP image was found, else False.
        """
        # Load image in grayscale for processing
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        img_lf = image_path.replace(folder_dir, "")
        print(f"Looking for {img_lf}")
        if img is None:
            print(f"Image {image_path} not found.")
            return False

        # Preprocess the screenshot for matching
        img_blurred = cv2.GaussianBlur(img, (5, 5), 0)
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
        screenshot_blurred = cv2.GaussianBlur(screenshot_gray, (5, 5), 0)

        for scale in scale_range:
            # Resize template image for matching
            resized_template = cv2.resize(img_blurred, (0, 0), fx=scale, fy=scale)
            result = cv2.matchTemplate(screenshot_blurred, resized_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= 0.85: # Threshold for a match
                img_strip = image_path.replace(folder_dir, "")
                print(f"Match found for {img_strip}")

                h, w = resized_template.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                start_pos = pyautogui.position()
                end_pos = (center_x, center_y)

                if image_path == rf"{folder_dir}{map_name}.jpg":
                    return True
                
                if image_path != rf"{folder_dir}STOP.jpg":
                    move_with_jitter(start_pos, end_pos, steps=2) # Move to the found position
                    pyautogui.click()   # Click the image
                    print(f"Clicked at {end_pos}")
                    if image_path.startswith(rf"{folder_dir}HDV"):
                        print("HDV Found")
                        time.sleep(random.uniform(0.5, 1))

                    # Additional scrolling logic for specific image
                    if (image_path == rf"{folder_dir}CONTENEUR.jpg"
                        or image_path == rf"{folder_dir}PARCHEMIN_Titre.jpg"
                        or image_path == rf"{folder_dir}FLEUR.jpg"
                        or image_path == rf"{folder_dir}METARIA.jpg"
                        or image_path == rf"{folder_dir}PLANCHE.jpg"
                        or image_path == rf"{folder_dir}RACINE.jpg"
                        ):
                        time.sleep(random.uniform(0.1, 0.2))
                        for i in range(4):
                            time.sleep(random.uniform(0.1, 0.2))
                            pyautogui.scroll(-125)
                            if i == 4 or i == 8:
                                time.sleep(random.uniform(0.1, 0.2))

                    time.sleep(random.uniform(0, 0.1))
                    return False

                elif image_path == rf"{folder_dir}STOP.jpg":
                    if not getattr(find_and_click_image, 'stop_clicked', False):
                        print("All Item Screenshot")
                        find_and_click_image.stop_clicked = True  # Mark STOP was clicked
                        return False
                    else:
                        return True # Only return True after STOP was clicked

    def screen_shot_items(img_stop, folder_dir, HDV_name):
        """
        Takes screenshots of items from the HDV and saves them to a folder.

        Parameters:
        - img_stop (str): Path to the STOP image.
        - folder_dir (str): Directory to save the screenshots.
        - HDV_name (str): Name of the HDV category being processed.
        
        Returns:
        - bool: True if the last screenshot was captured, else False.
        """
        Folder_name = f"{HDV_name}_PRICE_IMG"
        save_path = os.path.join(rf"{folder_dir}", Folder_name)
        os.makedirs(save_path, exist_ok=True)# Create directory if it doesn't exist
        nb_loop_mapping = {
            "HDV_RESOURCES": 205,
            "HDV_CONSUMABLE": 85,
            "HDV_ITEM": 245,
            "HDV_RUNES": 15,
        }
        nb_loop = nb_loop_mapping.get(HDV_name)

        for i in range(1000):
            i += 1
            if i == 1:
                pyautogui.moveTo(469, 647, duration=random.uniform(0.1, 0.2))   # Initial mouse position
            screenshot = pyautogui.screenshot(region=(510, 575, 820, 960))      # Screenshot region
            screenshot.save(os.path.join(save_path, f"{HDV_name}_{i}.png"))     # Save screenshot

            if i <= nb_loop:
                print(f"Screenshot {HDV_name}_{i}")
                scroll()# Scroll to the next items
            else:
                print(f"Screenshot {HDV_name}_{i}")
                scroll()# Scroll and check for STOP image
                stopscreenshot = find_and_click_image(img_stop, folder_dir, HDV_name)
                if stopscreenshot:
                    print(f"Last Screenshot for {HDV_name}")
                    return True

    def scroll():
        """
        Scrolls down in the HDV to navigate through the items.
        """
        for _ in range(4):
            pyautogui.scroll(-125)# Scroll down

        return True

    def item_type(map_name, main_folder_dir):
        """
        Determines the type of items based on the current map name and performs clicking actions.

        Parameters:
        - map_name (str): The name of the current map.
        - main_folder_dir (str): Main directory path for images and folders.
        """
        if map_name == "COORDINATE_HDV_RUNES":
            img_name = [
                "HDV_RUNES",
                "GRAVURE_Forgemagie",
                "ORBE_Forgemagie",
                "POTION_Forgemagie",
                "RUNE_Astral",
                "RUNE_Forgemagie",
                "RUNE_Transcendance",
            ]
            folder_dir = f"{main_folder_dir}HDV_RUNES\\"
            HDV_name = "HDV_RUNES"
        if map_name == "COORDINATE_HDV_ITEM":
            img_name = [
                "HDV_ITEM",
                "ICON_AMULETTE",
                "ICON_SWORD",
                "ICON_RING",
                "ICON_BELT",
                "ICON_BOOTS",
                "ICON_SHIELD",
                "ICON_HAT",
                "ICON_CLOAK",
                "ICON_DOFUS",
            ]
            folder_dir = f"{main_folder_dir}HDV_ITEM\\"
            HDV_name = "HDV_ITEM"
        if map_name == "COORDINATE_HDV_CONSUMABLE":
            img_name = [
                "HDV_CONSUMABLE",
                "BALLON",
                "BIERE",
                "BOISSON",
                "BOITE_Fragments",
                "CADEAU",
                "COFFRE",
                "CONTENEUR",
                "DOCUMENT",
                "FEE_Artifice",
                "FRIANDISE",
                "MIMIBIOTE",
                "MOT_Haiku",
                "OBJET_Temporis",
                "PAIN",
                "PARCHEMIN_Attitude",
                "PARCHEMIN_Caracteristique",
                "PARCHEMIN_Sortilege",
                "PARCHEMIN_Titre",
                "PARCHEMIN_Emoticones",
                "PARCHEMIN_Experience",
                "POISSON_Comestible",
                "POPOCHE_Havre_sac",
                "POTION",
                "POTION_Attitude",
                "POTION_Conquete",
                "POTION_Teleportation",
                "PRISME",
                "SAC_Ressources",
                "TATOUAGE_Foire",
                "VIANDE_Comestible",
            ]
            folder_dir = f"{main_folder_dir}HDV_CONSUMABLE\\"
            HDV_name = "HDV_CONSUMABLE"
        if map_name == "COORDINATE_HDV_RESOURCES":
            img_name = [
                "HDV_RESOURCES",
                "AILE",
                "ALLIAGE",
                "BOIS",
                "BOURGEON",
                "CARAPACE",
                "CARTE",
                "CEREALE",
                "CHAMPIGNON",
                "CLEF",
                "COQUILLE",
                "CUIR",
                "ECORCE",
                "ESSENCE_GARDIEN_DONJON",
                "ETOFFE",
                "FLEUR",
                "FRAGMENT_CARTE",
                "FRUIT",
                "GALET",
                "GELEE",
                "GRAINE",
                "HAIKU",
                "HUILE",
                "LAINE",
                "LEGUME",
                "LIQUIDE",
                "MATERIEL_ALCHIMIE",
                "MATERIEL_EXPLORATION",
                "METARIA",
                "MINERAI",
                "NOWEL",
                "OEIL",
                "OEUF",
                "OREILLE",
                "OS",
                "PATTE",
                "PEAU",
                "PIERRE_BRUTE",
                "PIERRE_PRECIEUSE",
                "PLANCHE",
                "PLANTE",
                "PLUME",
                "POIL",
                "POISSON",
                "POUDRE",
                "PREPARATION",
                "QUEUE",
                "RABMABLAGUE",
                "RACINE",
                "RESSOURCE_COMBAT",
                "RESSOURCE_TEMPORIS",
                "RESSOURCE_ANOMALIE",
                "RESSOURCE_SONGE",
                "RESSOURCE_DIVERSE",
                "SEVE",
                "SUBSTRAT",
                "TEINTURE",
                "VETEMENT",
                "VIANDE",
            ]
            folder_dir = f"{main_folder_dir}HDV_RESOURCES\\"
            HDV_name = "HDV_RESOURCES"
        nb_img = len(img_name)
        i = 0
        img_stop = f"{folder_dir}STOP.jpg"
        for name in img_name:
            i += 1
            image_paths = [f"{folder_dir}{name}.jpg"]
            for img_path in image_paths:
                find_and_click_image(img_path, folder_dir, map_name)
                if i >= nb_img:
                    print("All type activated")
                    break

        if image_paths != f"{folder_dir}{HDV_name}.jpg":
            time.sleep(random.uniform(0.1, 0.2))
            all_item = screen_shot_items(img_stop, folder_dir, HDV_name)
            if all_item:
                return True
        else:
            print(f"Skipping to next image after {name}")

    def map(main_folder_dir, folder_dir_tmp, map_name_tmp, starting_map=None):
        """
        Manages the navigation and interaction based on the current map.

        Parameters:
        - current_map (str): The name of the current map being processed.
        """
        img_name = [
            "COORDINATE_HDV_RUNES",
            "COORDINATE_HDV_ITEM",
            "COORDINATE_HDV_CONSUMABLE",
            "COORDINATE_HDV_RESOURCES",
        ]
        folder_dir = f"{main_folder_dir}MAPS\\"
        for name in img_name:
            image_paths = [f"{folder_dir}{name}.jpg"]
            map_name = name

            for _ in image_paths:
                map = coordinate(map_name, folder_dir_tmp, map_name_tmp)
                if map:
                    print(f"Proceed for the map : {name.replace('COORDINATE_','')}")
                    HDV_done = item_type(map_name, main_folder_dir)
                    if HDV_done:
                        print(f"{map_name.replace('COORDINATE_','')} done, proceed to next HDV")
                        if starting_map is None:
                            starting_map = start_map(map_name)
                            map_switch(main_folder_dir,folder_dir_tmp,map_name_tmp,map_name,starting_map,)
                        else:
                            map_switch(main_folder_dir,folder_dir_tmp,map_name_tmp,map_name,starting_map,)
                else:
                    print("Wrong Map")

    def coordinate(map_name, folder_dir_tmp, map_name_tmp):
        """
        Take a screenshot of the player Current map, read it 
        and compare with given coordinate.
        Validates the current coordinates of the player in the game.

        Parameters:
        - current_coordinate (str): The current coordinates of the player.
        """
        if map_name == "COORDINATE_HDV_CONSUMABLE":
            map_coord = ["21,-29,"]
        if map_name == "COORDINATE_HDV_ITEM":
            map_coord = ["19,-29,"]
        if map_name == "COORDINATE_HDV_RESOURCES":
            map_coord = ["21,-28,"]
        if map_name == "COORDINATE_HDV_RUNES":
            map_coord = ["17,-29,"]

        # Take actual map coordinate
        screenshot = pyautogui.screenshot(region=(20, 115, 120, 45))
        screenshot.save(os.path.join(folder_dir_tmp, f"{map_name_tmp}.jpg"))
        try:
            IMAGE1 = os.path.join(folder_dir_tmp, f"{map_name_tmp}.jpg")
            if not os.path.isfile(IMAGE1):
                raise FileNotFoundError(f"File not found: {IMAGE1}")
            img = cv2.imread(IMAGE1)
            if img is None:
                raise ValueError(f"Unable to read the image file: {IMAGE1}")
            # Instance Text Detector
            reader = easyocr.Reader(["fr"], gpu=False)
            # Detect text on image
            data = reader.readtext(img)
            for item in data:
                # Take only the elements that are not np.int32 or np.float64
                img_coordinate = [element for element in item if isinstance(element, str)]
            if img_coordinate == map_coord:
                print(f"You are on the {map_name.replace('COORDINATE_','')} map")
                return True
        except FileNotFoundError as e:
            print(e)
        except ValueError as e:
            print(e)

    def start_map(map_name):
        """
        Initializes the starting map coordinates and actions.
        """
        starting_map = f"{map_name.replace('COORDINATE_','')}"
        print(f"Starting map set to: {starting_map}")
        return starting_map

    def map_switch(main_folder_dir, folder_dir_tmp, map_name_tmp, map_name, starting_map):
        """
        Switches between different HDV types based on the current state.
        """
        pyautogui.press("escape")
        hdv_type = map_name.replace("COORDINATE_", "")
        if starting_map == "HDV_RUNES":
            if hdv_type == "HDV_RUNES" or hdv_type == "HDV_ITEM":
                click_right()
                if hdv_type == "HDV_RUNES":
                    time.sleep(random.uniform(1, 2))
                if hdv_type =="HDV_ITEM":
                    time.sleep(random.uniform(6, 7))
                click_right()
                time.sleep(random.uniform(4, 5))
                loop_main(main_folder_dir, folder_dir_tmp, map_name_tmp, starting_map)
            if hdv_type == "HDV_CONSUMABLE":
                click_bottom()
                time.sleep(random.uniform(4, 5))
                loop_main(main_folder_dir, folder_dir_tmp, map_name_tmp, starting_map)
            if hdv_type == "HDV_RESOURCES":
                pyautogui.press("escape")
                print("All 4 HDV screenshot")
                HDV_Reader()                
        if starting_map == "HDV_RESOURCES":
            if hdv_type == "HDV_RESOURCES":
                click_top()
                time.sleep(random.uniform(1, 2))
                loop_main(main_folder_dir, folder_dir_tmp, map_name_tmp, starting_map)
            if hdv_type == "HDV_CONSUMABLE" or hdv_type == "HDV_ITEM":
                click_left()
                time.sleep(random.uniform(8, 10))
                click_left()
                time.sleep(random.uniform(4, 5))
                loop_main(main_folder_dir, folder_dir_tmp, map_name_tmp, starting_map)
            if hdv_type == "HDV_RUNES":
                pyautogui.press("escape")
                print("All 4 HDV screenshot")
                HDV_Reader()

    def click_right():
        start_pos = pyautogui.position()
        end_pos = (1900, random.uniform(700, 1655))
        move_with_jitter(start_pos, end_pos)
        pyautogui.click()

    def click_left():
        start_pos = pyautogui.position()
        end_pos = (20, random.uniform(300, 1600))
        move_with_jitter(start_pos, end_pos)
        pyautogui.click()

    def click_top():
        start_pos = pyautogui.position()
        end_pos = (random.uniform(120, 1800), 315)
        move_with_jitter(start_pos, end_pos)
        pyautogui.click()

    def click_bottom():
        start_pos = pyautogui.position()
        end_pos = (random.uniform(120, 1800), 1650)
        move_with_jitter(start_pos, end_pos)
        pyautogui.click()

    def loop_main(main_folder_dir, folder_dir_tmp, map_name_tmp, starting_map):
        """
        Main loop for running the HDV screenshot process.
        """
        map(main_folder_dir, folder_dir_tmp, map_name_tmp, starting_map)

    def main_bot():
        """
        Main entry point to start the HDV screenshot and interaction process.
        """
        main_folder_dir = main_folder
        folder_dir_tmp = tmp_folder
        map_name_tmp = "coordinate_tmp"
        map(main_folder_dir, folder_dir_tmp, map_name_tmp)

    main_bot()
    


if __name__ == "__main__":
    try:
        HDV_Screenshot()
        # print("All screenshot done , start post process")
        #HDV_Reader()
    except KeyboardInterrupt:
        print("\nScript stopped with Ctrl + C.")
