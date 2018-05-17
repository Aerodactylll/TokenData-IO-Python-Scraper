import sys
import os
import argparse
import time
from datetime import datetime
from random import random
import logging
import pandas as pd
import lxml.html #Faster than Beatuiful Soup
from lxml import etree
from bs4 import BeautifulSoup

import urllib
import PyPDF2
import io

from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
# Configuration
timestamp_0 = 1367174841000
timestamp_1 = int(round(time.time() * 1000))
logging.basicConfig(
    filename="logging.log", 
    level=logging.INFO, 
    format='%(asctime)s:%(name)s:%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')

BASE_URL = "https://www.tokendata.io"

countRequested = 0
interReqTime = 23
lastReqTime = None

def htmlRequest(targetURL):
    global countRequested
    global lastReqTime
    if lastReqTime is not None and time.time() - lastReqTime < interReqTime:
        timeToSleep = random()*(interReqTime-time.time()+lastReqTime)*2
        logging.info("Sleeping for {0} seconds before request.".format(timeToSleep))
        time.sleep(timeToSleep)

    option = webdriver.ChromeOptions()
    option.add_argument('--incognito')

    browser = webdriver.Chrome(executable_path='chromedriver', chrome_options=option)
    browser.get(targetURL)
    wait = WebDriverWait(browser, 3)
    time.sleep(2)

    data = []
    while True:
        rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='sample_1']/tbody/tr")))
        index = 0
        
        for row in rows:
            if index > 0: 
                datum = {}
                info = row.find_elements(By.TAG_NAME, "td")
                datum["name"] = info[1].text
                datum['USD Raised'] = info[4].text
                datum['Month'] = info[5].text
                datum['Return'] = info[8].text
                datum["whitepaper"] = info[9].text
            else:
                index = 1

        data.append(datum)
        elm = browser.find_element_by_class_name('next')
        if 'disabled' in elm.get_attribute('class'):
            break;
        elm.click()

        time.sleep(1)
    #print(rows[0].find_elements(By.TAG_NAME, "td")[1].text)
    #print(rows[len(rows)-1].find_elements(By.TAG_NAME, "td")[1].text)
    return data

def scrapeWhitePaperLink():
    URL = "{0}".format(BASE_URL)
    data = htmlRequest(URL)
    return data

def processPDFLink(df):
    #testing
    #url = "http://www.silicontao.com/ProgrammingGuide/other/beejnet.pdf"

    for datarow in df:
        if datarow['whitepaper'][-3:] == 'pdf':
            URL = datarow['whitepaper']
            req = urllib.request(URL, headers={'User-Agent' : "Magic Browser"}) 
            remote_file = urllib.urlopen(req).read()
            memory_file = io.BytesIO(remote_file)

            read_pdf = PyPDF2.PdfFileReader(memory_file)
            number_of_pages = read_pdf.getNumPages()
            for i in range(0, number_of_pages):
                pageObj = read_pdf.getPage(i)
                page = pageObj.extractText()
                #print (page)
        elif datarow['whitepaper']:
            URL = datarow['whitepaper']
            htmlString = urllib.request.urlopen(URL).read()
            html = BeautifulSoup(htmlString, 'html.parser')
            texts = html.findAll(text=True)
            visible_texts = filter(tag_visible, texts)
            page = " ".join(t.strip() for t in visible_texts)
        else:
            print("{0} has no whitepaper!".format(datarow['name']))

    outputStream = open("output.pdf","wb")
    writer.write(outputStream)
    outputStream.close()

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def partOne():
    data = scrapeWhitePaperLink()
    df = pd.DataFrame(data)
    df.to_csv("{0}.csv".format("dataWhitePaper"), sep=',', index=False)

def partTwo():
    data = pd.read_csv('dataWhitePaper.csv')
    processPDFLink(data)

if __name__=='__main__':
    #partOne()
    partTwo()