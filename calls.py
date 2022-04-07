from ratelimit import limits,sleep_and_retry
import requests
import os
from dotenv import load_dotenv

load_dotenv()
USER = os.getenv("USER")

@sleep_and_retry
@limits(calls=45, period=30)
def api_call(url):
    headers = {"User-Agent": USER}
    r = requests.get(url, headers=headers, allow_redirects=True)

    if r.status_code != 200:
        raise Exception(f'API Response: {r.status_code}')
    return r

def updated():
    r = open("update.txt", "r")
    num = r.read()
    r.close()
    return "<t:{}:R>".format(num)