import time
import re
import os
import requests
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#For Loader Animation
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep

#Loader Animation
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
options.add_argument("--window-size=400,720")
#options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument('headless')
options.add_argument('--log-level=3')
options.add_experimental_option('excludeSwitches', ['enable-logging'])


#Browser Files
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options, service_args=['CREATE_NO_WINDOW'])

try:
    #Taking Input
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n")
    takeinput = input("Enter the video link of person which must be scraped : ")
    if re.match(r"(?:https:\/\/)?([vt]+)\.([tiktok]+)\.([com]+)\/([\/\w@?=&\.-]+)", takeinput):
        r = requests.head(takeinput, allow_redirects=False)
        URLS = r.headers['Location']
    else:
        URLS = takeinput

    #Loading Page For First Time
    driver.get(URLS)
    title = driver.title
    print("Video Found : "+ title)
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

    print("%20s"%"Might Take few minutes....")

    with Loader("Scolling Through Comments ", "Comments HTML Extract was Successful."):
        scroll_down()

    #Finding all videos
    
    #ecomment = driver.find_elements(by=By.XPATH,value='//*[@id="app"]/div[2]/div[2]/div[1]/div[3]/div/div[4]/div[2]')
    try:
        videodata = driver.find_element(by=By.XPATH,value='//*[@id="app"]/div[2]/div[2]/div[1]/div[3]/div[1]/div[1]')
    except BaseException:
        print("Video doesn't exist!")
        driver.close()
        quit()
    try:
        ecomment = driver.find_element(by=By.XPATH,value='//*[@id="app"]/div[2]/div[2]/div[1]/div[3]/div/div[4]/div[2]')
    except BaseException:
        print("Comments are Turned off !")
        print("Quitting Process!")
        driver.close()
        quit()
    
    metdatavid = videodata.get_attribute('outerHTML')
    cchtm = ecomment.get_attribute('outerHTML')

    #Closing Browser windows
    driver.close()
except KeyboardInterrupt:
    driver.close()
except BaseException:
    driver.close()

def metadatadict(videomethtml,title,URLS):
    likescountre = '<strong data-e2e="like-count" class="tiktok-[\w]+-[\w]+ [\w]+">[\d.KMB]+<\/strong>'
    commentscountre = '<strong data-e2e="comment-count" class="tiktok-[\w]+-[\w]+ [\w]+">[\d.KMB]+<\/strong>'
    sharecountre = '<strong data-e2e="share-count" class="tiktok-[\w]+-[\w]+ [\w]+">[\d.KMB]+<\/strong>'
    musicre = '<h4 data-e2e="browse-music" class="tiktok-[\w]+-[\w]+ [\w]+">[\w\W]+<\/h4>'

    likes =  re.sub('<strong data-e2e="like-count" class="tiktok-[\w]+-[\w]+ [\w]+">','',re.sub('<\/strong>','',(re.search(likescountre, videomethtml)).group()))
    comments =  re.sub('<strong data-e2e="comment-count" class="tiktok-[\w]+-[\w]+ [\w]+">','',re.sub('<\/strong>','',(re.search(commentscountre, videomethtml)).group()))
    shares =  re.sub('<strong data-e2e="share-count" class="tiktok-[\w]+-[\w]+ [\w]+">','',re.sub('<\/strong>','',(re.search(sharecountre, videomethtml)).group()))

    musicpart = (re.search(musicre, videomethtml)).group()
    musiclink = (re.search(r'\/music\/[\w]+-[\w]+-[\d]+',musicpart)).group()
    musicname = re.sub(r'<\/a>','',re.sub(r'<use xlink:href="#svg-music-note"><\/use><\/svg>','',(re.search(r'<use xlink:href="#svg-music-note"><\/use><\/svg>[\w\W-]+<\/a>',musicpart)).group()))


    metdadatadic ={'videotitle':title,'videolink': URLS, 'likes':likes, 'comments' : comments,'shares':shares,'musiclink':musiclink,'musicname':musicname}
        
    return metdadatadic
    #print(metdadatadic)

with Loader("Getting Basic Video Information","Video Info Extract Successful"):
    metadatadics = metadatadict(metdatavid,title,URLS)




#print(cchtm)
print("All comments Extraction on Process...")
def commentdict(outerhtml):
#a= open('comments.html', 'r',encoding="utf-8").read()
    a= outerhtml
    percomment = a.split("</path></svg></div></div></div></div></div>")
    percomment.remove(percomment[len(percomment)-1])

    allcomdic =[]
    commentsqnt = 0
    for acom in percomment:
        try:
            #print(acom)
            nicknamere = '<span data-e2e="comment-username-1" class="[\w -]+">[\w\W]+<\/span><\/a><p data-e2e="comment-level-1" class="'
            usernamere ='@([\w.]{1,24})'
            commenttextre='((<p data-e2e="comment-level-1" class="[\w -]+">)(((<a class="[\w -]+" href="[\w\W]+">@([\w.]{1,24})<\/a>)*)?((<span>[\s\S]*<\/span>)*)?)(<\/p><p class="))'
            commentidre = 'id="[\d]+"'

            
            commentid = (re.search(commentidre,acom).group().split('"'))[1]
            username = (re.search(usernamere, acom)).group()
            nickname =  re.sub('<span data-e2e="comment-username-1" class="[\w -]+">','',re.sub('<\/span><\/a><p data-e2e="comment-level-1" class="','',(re.search(nicknamere, acom)).group()))
            nickname = ((nickname[:100]).split('<'))[0] if len(nickname)>100 else nickname
            nickname = re.sub(r'tiktok-[\w]+-[\w]+ [\w]+">','',nickname)
            commenthtml = re.search(commenttextre,acom).group()
            commentmentions = re.findall('>@([\w.]{1,24})<',commenthtml)
            cmn = 0
            commentmentions = ' '.join(commentmentions)
            commenttexts = re.findall('<span>[\s\S]*<\/span>',commenthtml)
            cmttexn = 0
            for allcomments in commenttexts:
                commenttexts[cmttexn]=allcomments[6:-7]
                cmttexn += 1
            commenttexts = ' '.join(commenttexts)
            finalcomment = commentmentions+commenttexts
            commenttext = ((finalcomment[:150]).split('<'))[0] if len(finalcomment)>160 else finalcomment
            #commenttext = re.sub(r'"tiktok-[\w]+-[\w]+ [\w]+">','',commenttext)
            commentdatadic ={'commentid':commentid,
            'username' : username,
            'nickname':nickname,
            'commenttext':commenttext}
            allcomdic.append(commentdatadic)
            #print (comdiccount)
            commentsqnt +=1
        except BaseException:
            print("\n\n Few comments were not extracted.")
    #print(allcomdic)
    return allcomdic,commentsqnt

with Loader("Extracting Comments","All possible comments Extracted successfully"):
    commentsdics,noofcomments = commentdict(cchtm)

print("Extracted {} Comments.".format(str(noofcomments)))

#print(comments)

def save_to_xls(metadatadics,commentsdics,title):
    
    # convert into dataframe
    df1=pd.DataFrame(list(metadatadics.items()),columns=["Video Data","Values"])
    df2 = pd.DataFrame(data=commentsdics)

    #print(df1)
    #print(df2)

    filenamehere =re.search('[\w# ]+',(title[:30])).group()
    filenamehere = 'ScrapedData of video' if (filenamehere ==None or filenamehere=='') else filenamehere

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    os.makedirs('./Tiktok-Scraper', exist_ok=True)
    writer = pd.ExcelWriter('./{}/{}.xlsx'.format("Tiktok-Scraper",filenamehere), engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    df1.to_excel(writer, sheet_name='VideoData')
    df2.to_excel(writer, sheet_name='All Comments')


    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

with Loader("Saving to Excel format (.xslx)","Saved!"):
    save_to_xls(metadatadics,commentsdics,title)


print("\n\n\n")
print("%50s"%"Scraping Completed")
print("\n\n\n")