import requests 
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# path to input file 
CSVFILE = "input.csv"
# path to chrome driver
CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
# starting a browser 
chromeOptions = Options()
chromeOptions.headless = True
options = Options()
options = webdriver.ChromeOptions()
options.binary_location = '/usr/bin/google-chrome'
service_log_path = "./chromedriver.log"
service_args = ['--verbose']

options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH,
        chrome_options=options,
        service_args=service_args,
        service_log_path=service_log_path)


def make_request(url):
    driver.get(url) # request to specific url of item
    time.sleep(5) 
    soup = BeautifulSoup(driver.page_source, 'lxml') #convert the result into lxml
    products = soup.find_all("div",qa="product") # getting list of products from lxml
    for p in range(0,len(products)): 
        try:
            price_tag = products[p].find("div",qa="price") # getting price tag of item from lxml
            price = price_tag.find("span", class_="discnt-price").text # extract text from price tag
            price = re.findall(r'[\d\.\d]+', price) # modified price text so we could get only numerical value
            weight_tag = products[p].find("div",class_="col-sm-12 col-xs-7 qnty-selection") # getting weight tag of item from lxml
            weight = weight_tag.find("span",class_="ng-binding").text # extract text from weight tag
            weight = weight.split(" ") # split weight text so we could get numercial value and unit seperately
            unit = weight[1] 
            weight = weight[0]
            price = price[0]
            break
        except Exception as e:
            continue
    return price, weight, unit


# method that reads csv file 
def read_csv():
    df = pd.read_csv(CSVFILE) # read csv file and store data in a dataframe name df
    product_list = df['Item Name'] # read a column with name 'Item Name' form df
    for i in range(0,len(product_list)): # loop through all items
        try:
            product_name = product_list[i].lower().replace(" ","%20") #replace spaces in item name with '%20' so that we could use in url
            url = f"https://www.bigbasket.com/ps/?q={product_name}" # url for each item name
            price, weight, unit = make_request(url) # call method make_request that returns item price its weight and unit
            print(i,"",product_list[i], " ", price, " ", weight, unit)
            df['Total Price'][i] = price # replace price of that specific item name in df
            df['Weight'][i] = weight # replace weight of that specific item name in df
            df['Unit'][i] = unit # replace unit of that specific item name in df
        except Exception as e:
            continue
    df.to_csv("output.csv", index=False) # write updated df in output csv file 

read_csv()
