import os

BASE_URL = "https://tutorialsninja.com/demo/index.php?route=account/login"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)