#%%
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

def visit_main_page():
    """
    Visit the main page and clicks on the "latest earthquakes" element

    Returns
    -------
    Driver
    """
    driver = webdriver.Chrome('./chromedriver.exe')
    driver.get("https://earthquake.usgs.gov/")
    
    page = driver.find_element_by_xpath("/html/body/main/div/div/div[2]/div[2]/ul[1]/li/a")
    page.click()

    latest_earthquakes = driver.find_element_by_xpath("/html/body/div[6]/div/div/div/div/div[2]/div/nav/div/div/ul/li[2]/ul/li[1]/a")
    latest_earthquakes.click()

    return driver

time.sleep(1)
#%%
driver = visit_main_page()
time.sleep(1)


def selection_settings():
    """
    Selects the desired options step-by-step
    
    Returns
    -------
    Driver
    """
    options = driver.find_element_by_xpath("/html/body/usgs-root/usgs-header/header/usgs-panel-chooser/nav/i[3]")
    options.click()

    earthquake_catalog = driver.find_element_by_xpath("/html/body/usgs-root/div/usgs-settings/section/usgs-earthquakes-filter/a")
    earthquake_catalog.click()

    custom_selection = driver.find_element_by_xpath("/html/body/main/div/form/section/div[2]/section/ul[1]/li[3]/label") 
    custom_selection.click()

    start_datetime = driver.find_element_by_xpath("/html/body/main/div/form/section/div[2]/section/ul[2]/li[1]/input")
    start_datetime.click()
    start_datetime.clear()
    start_datetime.send_keys(input("Datetime:"))
    start_datetime.send_keys(Keys.RETURN)
    time.sleep(1)

    search = driver.find_element_by_xpath("/html/body/main/div/form/footer/button")
    search.click()

    time.sleep(1)

    options = driver.find_element_by_xpath("/html/body/usgs-root/usgs-header/header/usgs-panel-chooser/nav/i[3]")
    options.click()

    time_zone = driver.find_element_by_xpath("/html/body/usgs-root/div/usgs-settings/section/usgs-time-zone/mat-radio-group/mat-list/mat-list-item[2]/div/mat-radio-button")
    time_zone.click()
    time.sleep(3)

    return driver
#%%
# Scraping the data
driver = selection_settings()
time.sleep(3)


data = {"Magnitude": [], "Place": [], "Datetime": [], "Depth": []}
iter = 0

while iter < 400:
    list_eq = driver.find_element_by_xpath('//mat-list[@class="mat-list mat-list-base ng-star-inserted"]')
    earthquakes = list_eq.find_elements_by_xpath('./mat-list-item')
    for earth in earthquakes:
        data["Magnitude"].append(earth.find_element_by_tag_name("span").text)
        data["Place"].append(earth.find_element_by_tag_name("h6").text)
        data["Datetime"].append(earth.find_element_by_class_name("time").text)
        data["Depth"].append(earth.find_element_by_xpath(".//div[2]/div/aside/span").text)
    iter += 1
    ActionChains(driver).move_to_element(earthquakes[-1]).perform()
    time.sleep(1)

# %%
import pandas as pd
df = pd.DataFrame.from_dict(data)

if os.path.isfile('df.csv'):
    df = df.drop_duplicates(subset=["Place", "Datetime"])
    df.to_csv('df.csv', mode='a', header=False)
else:
    df = df.drop_duplicates(subset=["Place", "Datetime"])
    df.to_csv('df.csv', mode='a', header=True)

#%%
from botocore.exceptions import ClientError
import logging
import boto3
import botocore

def upload_file(file_name, bucket, object_name=None):
    """
    Upload a file to an S3 bucket
    
    Parameters
    ----------
    file_name : str
        Name of the file we want to upload
    bucket: str
        Name of the bucket
    object_name:
        Name of the object as we want it to appear in the bucket

    Returns
    -------
    bool
        False if the upload caused an error. True if the upload was successful

    This function is borrowed from Iván Ying Xuan.
    """
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
#%%
upload_file('df.csv', 'earthquakescraper')