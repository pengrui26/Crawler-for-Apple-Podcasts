import os
import ssl
import requests
from time import sleep
import urllib3
from random import randint
import re
from bs4 import BeautifulSoup

# Disable all kinds of warnings
urllib3.disable_warnings()

# Avoid SSL Certificate to access the HTTP website
ssl._create_default_https_context = ssl._create_unverified_context

def retrieve_webpage(url):
    USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

    random_agent = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
    headers = {'User-Agent': random_agent}
    retries = 10
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=(5, 10))
            if response.status_code == 200:
                return response.text
            else:
                print(f"Attempt {attempt}: Failed to retrieve webpage. Status code:", response.status_code)
                sleep(5)
        except Exception as e:
            print(f"Attempt {attempt}: An error occurred:", e)
            sleep(5)
    return None

def find_first_mp3_url(html_content):
    pattern = r'https://traffic\.libsyn\.com[^"]*mp3\?dest-id[^"}]*'
    match = re.search(pattern, html_content)
    if match:
        return match.group()
    return None

import signal

# Define Timeout Exception
class TimeoutException(Exception):
    pass

# Define timeout handler
def timeout_handler(signum, frame):
    raise TimeoutException

def download_mp3(mp3_url, save_path):
    # set signal and timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)  # set time interval as 60 seconds

    try:
        response = requests.get(mp3_url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {save_path}")
        else:
            print("Failed to download the file. Status code:", response.status_code)
    except TimeoutException:
        print("Download timed out after 60 seconds.")
    except Exception as e:
        print(f"An error occurred during download: {e}")
    finally:
        # reset alarm
        signal.alarm(0)
# Main execution part
title = "Pediatrics On Call"
dir_name = f"audios/{title}"
if not os.path.exists(dir_name):
    os.makedirs(dir_name)

with open('kill.html', 'r', encoding='utf-8') as file:
    webpage = file.read()

soup = BeautifulSoup(webpage, 'html.parser')
blocks = soup.find_all("a", class_="link tracks__track__link--block")

for block in blocks:
    page_title = block.text.strip() if block.text else "Unknown"
    link = block['href']
    html_content = retrieve_webpage(link)
    if html_content:
        mp3_url = find_first_mp3_url(html_content)
        if mp3_url:
            save_path = os.path.join(dir_name, f"{page_title}.mp3")
            download_mp3(mp3_url, save_path)
        else:
            print(f"No MP3 URL found in {link}")
    else:
        print(f"Failed to retrieve content from {link}")
