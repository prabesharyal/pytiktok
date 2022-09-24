import time
import re
import os


import yt_dlp

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#loader modules
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep

#Loader animation
class Loader:
    def __init__(self, desc="Loading...", end="Done!", timeout=0.1):
        """
        A loader-like context manager

        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to "Done!".
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
        """
        self.desc = desc
        self.end = end
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            print(f"\r{self.desc} {c}", flush=True, end="")
            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
        print(f"\r{self.end}", flush=True)

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()


#Clearing Problems in Logs
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument('headless')
options.add_argument('--log-level=3')
options.add_experimental_option('excludeSwitches', ['enable-logging'])


#Browser Files
#os.system('cls' if os.name == 'nt' else 'clear')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options, service_args=['CREATE_NO_WINDOW'])

#Loading Page For First Time
#os.system('cls' if os.name == 'nt' else 'clear')

#Taking Input
os.system('cls' if os.name == 'nt' else 'clear')
print("\n")
takeinput = input("Enter the username(or url) of person whose video you want to download : ")
if re.match(r'^((https:\/\/)([www]+)((\.){1})([tiktok]+)((\.){1})([com]+)((\/){1})(@[\w\.]+))$',takeinput):
    username = (((takeinput.split('/'))[3]).split('@'))[1]
    userlink= takeinput
else:
    username = takeinput
    userlink = "https://www.tiktok.com/@"+username

with Loader("Going to profile : {}".format(username), ""):
    driver.get(userlink)
    driver.implicitly_wait(5)
#os.system('cls' if os.name == 'nt' else 'clear')

def scroll_down():
    """A method for scrolling the page."""

    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:

        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:

            break

        last_height = new_height

with Loader("Looking for all videos of user: {}  ".format(username),"Loading all videos completed!"):
    scroll_down()

#Finding all videos
with Loader("Extracting Video Links ", "All video links extraction completed succesfully !"):

    videos = driver.find_elements(by=By.XPATH,value='//*[@id="app"]/div[2]/div[2]/div/div[2]/div[2]/div//a[@href]')
    URLS = list()
    #print("\n\nGetting all video links ....")
    c=0
    for elem in videos:
        link = elem.get_attribute("href")
        pattern = r'((https:\/\/)([www]+)((\.){1})([tiktok]+)((\.){1})([com]+)((\/){1})(@[\w\.]+)((\/){1})(video)((\/){1})([\d]+))'
        if re.match(pattern, link):
            #print(link)
            URLS.append(link)
            c+=1
    print("\nExtracted {} video links.".format(str(c)))

#Closing Browser windows
driver.close()
#print(URLS)

def yt_dlp_tiktok_dl(URLS,username,c):
    ydl_opts = {'ignoreerrors': True, 'no_warnings':True, 'quiet': True, 'outtmpl': '%(extractor_key)s/{}/%(id)s-%(title)s.%(ext)s'.format(username), 'trim_file_name' : 25}
    i = 1
    for videolinks in URLS:
        try:
            #print(videolinks)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(videolinks)
                video_title = info['title']
            CAPTION = "✨" if video_title == '' else video_title
            print("Downloaded video {}/{}: ".format(str(i),str(c))+ str(CAPTION))
        except KeyboardInterrupt:
            quit()
        except BaseException:
            print("Skipping video {}/{}: >>>>> {} <<<<".format(str(i),str(c), videolinks)+"Some ERROR Occurred")
        i += 1 
    print("\n\n")
    print("%50s"%"Downloaded All {} Videos!".format(str(c)))
    print("\n\n")

with Loader("Downloading each video : ", "Done Downloading all videos in the profile."):
    yt_dlp_tiktok_dl(URLS,username,c)
time.sleep(20)
quit()