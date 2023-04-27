import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import tempfile
from datetime import datetime
from typing import Dict, Any, Union, List
from pathlib import Path
import yaml
import pytz
import shutil

from PIL import Image
from mutagen.mp4 import MP4, MP4Tags, MP4Cover
from io import BytesIO
import piexif


def get_auth_token(driver_path: str, 
                   username: str, 
                   password: str) -> str:
    """Get Auth Token from Procare Web  

    :param driver_path: chromedriver path
    :type driver_path: str
    :param username: Procare login email
    :type username: str
    :param password: Procare login password
    :type password: str
    :param fp: filepath to save secret
    :type fp: str
    :return: Auth token
    :rtype: str
    """
    # Configure the driver (replace with the path to your ChromeDriver executable)
    driver = webdriver.Chrome(executable_path=driver_path)

    # Navigate to the login page (replace with the actual login URL)
    login_url = "https://schools.procareconnect.com/"
    driver.get(login_url)

    # Enter your username and password (replace with the actual input field IDs or names)
    username_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "password")
    username_input.send_keys(str(username))
    password_input.send_keys(str(password))

    # Click the login button (replace with the actual login button ID or class)
    login_button = driver.find_element(By.CLASS_NAME, "auth__submit-button")
    login_button.click()

    # Wait for the page to load (you may need to adjust the sleep time)
    import time
    time.sleep(5)

    # Extract the auth_token from localStorage
    auth_token = driver.execute_script("return localStorage.getItem('persist:kinderlime');")
    auth_token = json.loads(json.loads(auth_token)["currentUser"])["data"]["auth_token"]

    # Close the browser
    driver.quit()

    return auth_token


def uct2est(t: str, in_fmt: str = "%Y-%m-%dT%H:%M:%S.%f%z", out_fmt: str="%Y-%m-%dT%H-%M-%S") -> str:
    """
    Convert UTC time string to EST time
    """
    utc_time = datetime.strptime(t, in_fmt)
    utc_time = utc_time.replace(tzinfo=pytz.UTC)
    est_time = utc_time.astimezone(pytz.timezone("US/Eastern"))
    return datetime.strftime(est_time, out_fmt)


def format_dt(t: str, in_fmt: str = "%Y-%m-%dT%H:%M:%S.%f%z", out_fmt: str="%Y-%m-%dT%H-%M-%S") -> str:
    """
    Reformat datetime string
    """
    dt = datetime.strptime(t, in_fmt)
    return datetime.strftime(dt, out_fmt)


def download_video(content: bytes, 
                   fp: Union[Path, str],
                   title:str="", 
                   tags: List[str]=["daycare"]) -> None:
    """Download video

    :param content: video stream
    :type content: bytes
    :param content: video output filename
    :type content: Union[Path, str]
    :param title: video title, defaults to ""
    :type title: str, optional
    :param tags: video apple tags, defaults to ["daycare"]
    :type tags: list, optional
    """
    # save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name
    # Load the MP4 file from the temporary path
    mp4_file = MP4(temp_path)
    # Set the title metadata
    mp4_file["\xa9nam"] = [title]
    # Set the tags metadata
    mp4_file["----:com.apple.iTunes:Keywords"] = [f.encode() for f in tags]
    # Save the changes
    mp4_file.save()
    # Save the MP4 file with metadata to the final destination
    shutil.move(temp_path, fp)


def download_photo(content: bytes, 
                   fp: Union[Path, str],
                   title: str="", 
                   tags: List[str]=["daycare"]) -> None:
    """Download photo

    :param content: photo bytes
    :type content: bytes
    :param content: photo output filename
    :type content: Union[Path, str]
    :param title: photo title, defaults to ""
    :type title: str, optional
    :param tags: photo tags, defaults to ["daycare"]
    :type tags: list, optional
    """
    # Load the image into a PIL.Image object
    image_data = content
    image = Image.open(BytesIO(image_data))
    # Prepare the Exif metadata with the desired properties
    exif_dict = {
        "0th": {
            piexif.ImageIFD.XPTitle: title.encode("utf-16le"),
            piexif.ImageIFD.XPKeywords: ",".join(tags).encode("utf-16le")
        }
    }
    exif_bytes = piexif.dump(exif_dict)
    # Save the image with the modified Exif metadata
    with open(fp, "wb") as f:
        image.save(f, "JPEG", exif=exif_bytes)