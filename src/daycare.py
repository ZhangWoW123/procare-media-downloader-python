import json
import yaml
import requests
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Union

from PIL import Image
from mutagen.mp4 import MP4, MP4Tags, MP4Cover
from io import BytesIO
import piexif
from tqdm import tqdm

from src.utils import format_dt, download_photo, download_video


class Procare:
    def __init__(self, auth_token):
        self.auth_token = auth_token

    def curl(self,
             url: str) -> Dict[str, Any]:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Authorization": "Bearer " + self.auth_token,
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "api-school.kinderlime.com",
            "Origin": "https://schools.procareconnect.com",
            "Pragma": "no-cache",
            "Referer": "https://schools.procareconnect.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site",
            "Sec-GPC": "1",
            "TE": "trailers",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
        }

        response = requests.get(url, headers=headers)
        return response.json()

    def list_children(self):
        url = "https://api-school.kinderlime.com/api/web/parent/kids/"
        data = self.curl(url)
        return [x["id"] for x in data["kids"]]

    def extract_child_data(self, 
                           child_id, 
                           page=1, 
                           date_from="2000-01-01",
                           date_to="2031-07-30", 
                           data=[]):
        url = f"https://api-school.kinderlime.com/api/web/parent/daily_activities/?kid_id={child_id}&filters%5Bdaily_activity%5D%5Bdate_to%5D={date_to}&filters%5Bdaily_activity%5D%5Bdate_from%5D={date_from}&page={page}"
        x = self.curl(url)

        if x["daily_activities"]:
            data.extend(x["daily_activities"])
            page += 1
            return self.extract_child_data(child_id, page, date_from, date_to, data)
        else:
            return data
    
    def extract_activity(self, 
                         start_date: str="2000-01-01", 
                         end_date: str=datetime.strftime(datetime.now(), '%Y-%m-%d'),
                         log_dir: Union[Path, str]=None) -> List[Dict]:
        # list all children
        children = self.list_children()
        # extract children activity log
        data = []
        for child in children:
            child_data = self.extract_child_data(child, 1, start_date, end_date, [])
            data.extend(child_data)
        
        # save log
        if log_dir:
            log_dir = Path(log_dir) if type(log_dir) == str else log_dir
            log_dir.mkdir(parents=True, exist_ok=True)
            log_fp = Path(log_dir, f"procare_activity_logs_{start_date}_{end_date}.json")
            with open(log_fp, "w") as outfile:
                json.dump(data, outfile, indent=4)
        
        return data

    def download_media(self,
                       media_dir: Union[Path, str],
                       start_date: str="2000-01-01", 
                       end_date: str=datetime.strftime(datetime.now(), '%Y-%m-%d'),
                       log_dir: Union[Path, str]=None):
        # get photo or video activity
        data = self.extract_activity(start_date, end_date, log_dir)
        multi_media = [x["activiable"] for x in data if x["activity_type"] in ("photo_activity", "video_activity")]
        
        # download media
        media_dir = Path(media_dir) if type(media_dir) == str else media_dir
        media_dir.mkdir(parents=True, exist_ok=True)
        for mm in tqdm(multi_media):
            title = mm["caption"]
            created_at = format_dt(mm["date"])
            media_fp = Path(media_dir, f"daycare-{created_at}.{'mp4' if mm['is_video'] else 'jpg'}")
            media_url = mm["video_file_url"] if mm["is_video"] else mm["main_url"]
            response = requests.get(media_url)
            if mm["is_video"]:
                download_video(response.content, media_fp, title)
            else:
                download_photo(response.content, media_fp, title)
