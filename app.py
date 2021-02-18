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

app = Flask(__name__)



def transform(file):
    PATH = "C:\Program Files\chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    df = pd.read_csv(file) # can also index sheet by name or fetch all sheets
    urls = df['ASIN'].tolist()
    model = df['Model'].tolist()
    supplier = df['Supplier'].tolist()

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
    return response

    
def open_browser():
      webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == "__main__":
      Timer(1, open_browser).start();
      app.run(port=5000)
