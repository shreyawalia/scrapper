# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 19:05:44 2021

@author: Shreya Walia
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 12:33:11 2021

@author: Shreya Walia
"""

from flask import Flask, make_response, request
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import re
import webbrowser
from threading import Timer
import os
app = Flask(__name__)



def transform(file):
   # PATH = "C:\Program Files\chromedriver.exe"
   # driver = webdriver.Chrome(PATH)
    

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    df = pd.read_csv(file) # can also index sheet by name or fetch all sheets
    urls = df['ASIN'].tolist()
    model = df['Model'].tolist()
    supplier = df['Supplier'].tolist()

    def getData(url, asin_file,model_file,supplier_file):
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
    
        def Asin_Title():
    
            asin = url.split("/")[-1]
            title = driver.find_element_by_xpath('//*[@id="productTitle"]').text
    
    
            return(asin, title)
    
        def Price():
             try:
                 price = soup.find("span", attrs={'id':'priceblock_ourprice'}).string.strip()
                 price = price.replace("&nbsp", "")
             except:
                 try:
                     price = soup.find("span", attrs={'id':'price_inside_buybox'}).string.strip()
                     price = price.replace("&nbsp", "")
                 except:
                     price = "Unavailable"
             return(price)
         
            
        def Merchant():
            try:
                merchant_info = driver.find_element_by_xpath('//*[@id="merchant-info"]').text
            except:
                merchant_info = "Unavailable"
             
            return(merchant_info)
         
        def Rating():
            try:
                rating = soup.find("i", attrs={'class':'a-icon a-icon-star a-star-4-5'}).string.strip()
            except:
                try:
                    rating = soup.find("span", attrs={'class':'a-icon-alt'}).string.strip()
                except:
                    rating = "Unavailable"
            return(rating)
        
        
        def Review_count():
            try:
                review_count = soup.find("span", attrs={'id':'acrCustomerReviewText'}).string.strip()
            except:
                review_count = "Unavailable" 
            return(review_count)
        
        def Availability_Condition():
            try:
                available = soup.find("div", attrs={'id':'availability'}).find("span").string.strip()
                condition = "New"
            except:
                available = "Unavailable"
                condition = "Unavailable"
            return(available, condition)
        
        def Manufacturer():
            try:
                table_body=soup.find('table',id="productDetails_techSpec_section_1")
                Manufacturer = table_body.find('th',  text= re.compile('Manufacturer')).find_next('td').text.strip()
            except:
                try:
                    table_body=soup.find('div',id="detailBulletsWrapper_feature_div")
                    Manufacturer = table_body.find('span', text= re.compile('^Manufacturer')).find_next('span').text.strip()
                except:
                    Manufacturer = "Unavailable"
            return(Manufacturer)
    
        def Model():
            try:
                table_body=soup.find('table',id="productDetails_techSpec_section_1")
                Model = table_body.find('th',  text= re.compile('Model|model')).find_next('td').text.strip()
            except:
                try:
                    table_body=soup.find('div',id="detailBulletsWrapper_feature_div")
                    Model = table_body.find('span', text= re.compile('Model|model')).find_next('span').text.strip()
                except:
                    Model = "Unavailable"
            return(Model)
        
        def Best_Seller_Rank():
            try:
                table_body_extra = soup.find('table', id = "productDetails_detailBullets_sections1")
                Best_Sellers_Rank = table_body_extra.find('th',  text= re.compile('Best Sellers Rank')).find_next('td').text.strip()
            except:
                try:
                    table_body=soup.find('div',id="detailBulletsWrapper_feature_div")
                    Best_Sellers = table_body.find('span', text= re.compile('Best Sellers')).find_parent('span')#.text.strip()
                    unwanted = Best_Sellers.find('span')
                    unwanted.extract()
                    Best_Sellers_Rank = Best_Sellers.text.strip()
                except:
                    try:
                        table_body=soup.find('div',id="detailBulletsWrapper_feature_div")
                        Best_Sellers_Rank = table_body.find('span', text= re.compile('Best Sellers')).find_next('span').text.strip()
                    except:
                        Best_Sellers_Rank = "Unavailable"
            return(Best_Sellers_Rank)
           
    
        asin, title = Asin_Title()
        price = Price() 
        merchant = Merchant()
        rating = Rating()
        review = Review_count()
        available, condition = Availability_Condition()
        manufacturer = Manufacturer()
        model_no = Model()
        best_seller_rank = Best_Seller_Rank()
        buy_box = "Yes"
        #print(asin, title, price, merchant, rating, review, available, manufacturer, model_no, best_seller_rank, buy_box, condition)        
        #print(model_file)
        product = {
                'ASIN_File': asin_file,
                'Model_File' : model_file,
                'Supplier_File' :supplier_file,
                'ASIN Product' : asin,
                'Product Name' : title,
                'Merchant Info': merchant,
                'Price' : price,
                'Buy_Box': buy_box,
                'Ratings' : rating,
                'Reviews' : review,
                'In Stock': available,
                'Manufacturer': manufacturer,
                'Model No': model_no,
                'Best Sellers Rank': best_seller_rank,
                'Condition': condition            
                }
    
        return(product, asin, title, manufacturer, model_no)
            
    def getCompetitors(url, u, m,s, asin, product_name, manufacturer, model):
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        comp = []
        dict2={}
        try:
            element = WebDriverWait(driver, 5).until(
             EC.presence_of_element_located((By.XPATH, '//*[@id="aod-filter-string"]'))
             )
            element.click()
            #filter = driver.find_element_by_xpath('//*[@id="aod-filter-string"]')
            #filter.click()
            element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="aod-filter-list"]/div[7]/div/div/span')))
            driver.execute_script("arguments[0].click();", element)
            divTag = soup.find_all("div", {"id": "aod-offer"})
            #print(divTag)
            for tag in divTag:
                price_tag = tag.find_all("span", {"class": "a-offscreen"})
                merchant_name = tag.find_all("a", {"class":"a-size-small a-link-normal"})
                #ntag = driver.find_element_by_xpath('//*[@id="aod-offer-soldBy"]/div/div/div[2]/a')
                review_tag = tag.find_all("div", {"id":"aod-offer-seller-rating"})
                
                condition_tag = tag.find_all("div", {"id":"aod-offer-heading"})
                
                def c_price(price_tag):
                    for tag in price_tag:
                        if tag.text:
                            p = tag.text
                            p= p.replace("\n", "").replace("&nbsp", "")
                        elif tag.text == "":
                            p = "Unavailable"
                    return(p)
                def c_merchant(merchant_name):
                    for tag in merchant_name:
                        if tag.text:
                            n = tag.text
                            n=n.replace("\n", "")
                        elif tag.text == "":
                            n = "Unavailable"  
                    return(n)
                def c_review(review_tag):
                    for tag in review_tag:
                        if tag.text:
                            r = tag.text
                            r = r.replace("\n", "")
                        elif tag.text == "":
                            r = "Unavailable"
                    return (r)
                def c_condition(condition_tag):
                    for tag in condition_tag:
                        if tag.text:
                            o = tag.text
                            o = o.replace("\n", "")
                        elif tag.text == "":
                            o = "Unavailable"
                    return (o)
                dict2['ASIN_File'] = u
                dict2['Model_File'] = m
                dict2['Supplier_File'] = s
                dict2['ASIN Product'] = asin
                dict2['Product Name'] = product_name
                dict2['Merchant Info'] = c_merchant(merchant_name)
                dict2['Price'] = c_price(price_tag)
                dict2['Buy_Box'] = "No"
                dict2['Ratings'] = 'Unavailable'
                dict2['Reviews'] = c_review(review_tag)
                dict2['In Stock'] = 'Yes'
                dict2['Manufacturer'] = manufacturer
                dict2['Model No'] = model
                dict2['Best Sellers Rank'] = 'Unavailable'
                dict2['Condition'] = c_condition(condition_tag)
                comp.append(dict(dict2))
        except :
            divTag = soup.find_all("div", {"id": "aod-offer"})
    
            for tag in divTag:
                price_tag = tag.find_all("span", {"class": "a-offscreen"})
                merchant_name = tag.find_all("a", {"class":"a-size-small a-link-normal"})
                #ntag = driver.find_element_by_xpath('//*[@id="aod-offer-soldBy"]/div/div/div[2]/a')
                review_tag = tag.find_all("div", {"id":"aod-offer-seller-rating"})
                
                condition_tag = tag.find_all("div", {"id":"aod-offer-heading"})
                def c_price(price_tag):
                    for tag in price_tag:
                        if tag.text:
                            p = tag.text
                            p= p.replace("\n", "")
                        elif tag.text == "":
                            p = "Unavailable"
                    return(p)
                def c_merchant(merchant_name):
                    for tag in merchant_name:
                        if tag.text:
                            n = tag.text
                            n=n.replace("\n", "")
                        elif tag.text == "":
                            n = "Unavailable"  
                    return(n)
                def c_review(review_tag):
                    for tag in review_tag:
                        if tag.text:
                            r = tag.text
                            r = r.replace("\n", "")
                        elif tag.text == "":
                            r = "Unavailable"
                    return (r)
                def c_condition(condition_tag):
                    for tag in condition_tag:
                        if tag.text:
                            o = tag.text
                            o = o.replace("\n", "")
                        elif tag.text == "":
                            o = "Unavailable"
                    return (o)
                dict2['ASIN_File'] = u
                dict2['Model_File'] = m
                dict2['Supplier_File'] = s
                dict2['ASIN Product'] = asin
                dict2['Product Name'] = product_name
                dict2['Merchant Info'] = c_merchant(merchant_name)
                dict2['Price'] = c_price(price_tag)
                dict2['Buy_Box'] = "No"
                dict2['Ratings'] = 'Unavailable'
                dict2['Reviews'] = c_review(review_tag)
                dict2['In Stock'] = 'Yes'
                dict2['Manufacturer'] = manufacturer
                dict2['Model No'] = model
                dict2['Best Sellers Rank'] = 'Unavailable'
                dict2['Condition'] = c_condition(condition_tag)
                comp.append(dict(dict2))
        #dict2 = {}
        #print(comp)
        # return(data)
        return (comp)
    
    competitor_prices = []
    cp = []
    l = []
    i = 0
    for i in range(len(urls)):
        u = urls[i]
        m = model[i]
        s = supplier[i]
        product_info, asin_no, name, manufacturer, model_c = getData("https://www.amazon.ca/dp/"+u,u,m,s) 
        competitor_prices.append(product_info)
        asin_code = asin_no
        product_name = name
        manufactured_by = manufacturer
        model_code = model_c
        
        cp.append(getCompetitors("https://www.amazon.ca/dp/"+u+"/ref=olp_aod_redir#aod",u,m,s, asin_code,product_name, manufactured_by, model_code))
        li = [item for sublist in cp for item in sublist]
        l.append(competitor_prices+li)
        competitor_prices = []
        cp = []
        i = i + 1
        
    # print(competitor_prices)
    # print(len(competitor_prices))
    # l = [item for sublist in competitor_prices for item in sublist]
    l = [item for sublist in l for item in sublist]
    #print(l)
    pricesdf = pd.DataFrame(l)
    #r = pricesdf.to_excel('result.xlsx')
    return (pricesdf)


@app.route('/')
def form():
    return """
        <html>
            <body>
                <h1>Enter file with data to scrape</h1>

                <form action="/transform" method="post" enctype="multipart/form-data">
                    <input type="file" name="data_file" />
                    <input type="submit" />
                </form>
            </body>
        </html>
    """
@app.route('/transform', methods=["POST"])
def transform_view():
    f = request.files['data_file']
    if not f:
        return "No file"

    result = transform(f)
    #result = transform(csv_input)
    result = result.to_csv()
    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=result.csv"
    return (response)
