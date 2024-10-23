import pyautogui
import random
import time
import cv2
import numpy as np
import os

def move_with_jitter(start_pos, end_pos, steps=10):
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
        time.sleep(0.01)

def find_and_click_image(image_path, scale_range=np.linspace(0.25, 2, 8)):# Value add / Value MAX / Steps
    # transform in grey value for compute power
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img_lf = image_path.replace("D:\\Coding\\Dofus\\HDV_IMG\\HDV_ITEM\\", "")
    print(f"Looking for {img_lf}")
    if img is None:
        print(f"Image {image_path} not found.")
        return False

    # As it compare pixel , light blur to help found some picture 
    img_blurred = cv2.GaussianBlur(img, (5, 5), 0)
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
    screenshot_blurred = cv2.GaussianBlur(screenshot_gray, (5, 5), 0)

    for scale in scale_range:
        resized_template = cv2.resize(img_blurred, (0, 0), fx=scale, fy=scale)
        result = cv2.matchTemplate(screenshot_blurred, resized_template, cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= 0.85:  # Adjust threshold as needed
            img_strip = image_path.replace("D:\\Coding\\Dofus\\HDV_IMG\\HDV_ITEM\\", "")
            print(f"Match found for {img_strip}")
            
            h, w = resized_template.shape
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            start_pos = pyautogui.position()
            end_pos = (center_x, center_y)
            
            if image_path != r"D:\Coding\Dofus\HDV_IMG\HDV_ITEM\STOP.jpg" :
                # Move in an arc to the detected position
                move_with_jitter(start_pos, end_pos, steps=5)
                pyautogui.click()
                print(f"Clicked at {end_pos}")
                print("wait")
                time.sleep(random.uniform(0.5, 1.5))
                return False

            elif image_path == r"D:\Coding\Dofus\HDV_IMG\HDV_ITEM\STOP.jpg" : 
                print("All Item Screenshot")
                return True

def screen_shot_items(img_stop):
    Folder_name = "ITEM_PRICE_IMG"
    save_path = os.path.join(r"D:\Coding\Dofus\HDV_IMG\HDV_ITEM", Folder_name)
    os.makedirs(save_path, exist_ok=True)

    for i in range(1000):
        i += 1
        stopscreenshot = find_and_click_image(img_stop)
        if stopscreenshot:
            print("Last Screenshot for ITEM")
            pyautogui.moveTo(469, 647 , duration= random.uniform(0.2, 0.5))
            screenshot = pyautogui.screenshot(region=(510, 575, 820, 960))
            screenshot.save(os.path.join(save_path, f"HDV_ITEM_{i}.png"))
            return True
        else:
            pyautogui.moveTo(469, 647 , duration= random.uniform(0.2, 0.5))
            screenshot = pyautogui.screenshot(region=(510, 575, 820, 960))
            screenshot.save(os.path.join(save_path, f"HDV_ITEM_{i}.png"))
            print(f"Screenshot HDV_ITEM_{i}")
            for _ in range(4):
                time.sleep(random.uniform(0.2, 0.5))
                pyautogui.scroll(-125)

def main():

    img_name = ['HDV_ITEM','ICON_AMULETTE','ICON_SWORD', 'ICON_RING','ICON_BELT','ICON_BOOTS','ICON_SHIELD','ICON_HAT','ICON_CLOAK','ICON_DOFUS']
    nb_img = (len(img_name))
    i = 0
    img_stop = r"D:\Coding\Dofus\HDV_IMG\HDV_ITEM\STOP.jpg"
    for name in img_name :
        i += 1
        image_paths = [fr"D:\Coding\Dofus\HDV_IMG\HDV_ITEM\{name}.jpg"]
        for img_path in image_paths:
            find_and_click_image(img_path)
            if i >= nb_img:
                print("All type activated")
                break
  
    if image_paths != "D:\Coding\Dofus\HDV_IMG\HDV_ITEM\HDV_ITEM.jpg" :
        time.sleep(random.uniform(0.5, 1.5))
        all_item = screen_shot_items(img_stop)
        if all_item:
            return
    else:
        print(f"Skipping to next image after {name}")
        

main()