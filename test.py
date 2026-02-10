from bs4 import BeautifulSoup
import requests
from selenium import webdriver




def scrapping(url):
    soup=requests.get(url)
    