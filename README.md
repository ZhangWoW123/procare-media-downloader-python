# Daycare Media Downloader

This is a simple project that downloads media files (photos and videos) from the Procare daycare platform. It allows you to download media files for a specific date range and stores them in a local directory. Thanks to [JWally](https://github.com/JWally/procare-media-downloader) for the JS code

## Requirements

- Python 3.x
- Dependencies:
  - selenium
  - requests
  - tqdm
  - mutagen
  - piexif
  - pyyaml

## Installation

1. Clone this repository or download the source code.

2. Set up a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Download the appropriate [ChromeDriver](https://chromedriver.chromium.org/downloads) executable for your system and place it in the `resources` directory.

5. Create a `credentials.yml` file in the project root directory with your Procare username and password:

```yaml
daycare:
  username: your_username_here
  password: your_password_here
```

## Usage

Run the `main.py` script to download media files:

```bash
python main.py
```

By default, the script will download media files from `2000-01-01` to the current date and save them in the `./photos` directory. You can change the start date, end date, media directory, and log directory by modifying the `main()` function call in the if `__name__ == "__main__"` block at the end of the `main.py` file.

