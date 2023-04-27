import yaml
from pathlib import Path
from datetime import datetime
from typing import Union

from src.daycare import Procare
from src.utils import get_auth_token


def main(start_date: str="2000-01-01", 
         end_date: str=datetime.strftime(datetime.now(), '%Y-%m-%d'),
         media_dir: Union[Path, str]="./photos",
         log_dir: Union[Path, str]="./logs"):

    # get authentication token
    print("login to daycare...")
    with open("credentials.yml", 'r') as file:
        credentials = yaml.safe_load(file)

    if "auth_token" in credentials['daycare']:
        auth_token = credentials['daycare']["auth_token"]
    else:
        driver_path = ".resources/chromedriver.exe"  # Replace with the path to your ChromeDriver executable
        auth_token = get_auth_token(driver_path,
                                    credentials['daycare']['username'],
                                    credentials['daycare']['password'])
        credentials['daycare']["auth_token"] = auth_token
        with open("credentials.yml", 'w') as file:
            yaml.safe_dump(credentials, file)
    
    # download media
    print("download media...")
    dc = Procare(auth_token)
    dc.download_media(media_dir, start_date, end_date, log_dir)
    print("finished!")


if __name__ == "__main__":
    # Download photo
    main()
