import pandas as pd
import openpyxl
from openpyxl import Workbook 
from openpyxl import load_workbook  
import warnings
from bs4 import BeautifulSoup
import requests

# this script grabs the latest version of the average fuel sales statistics
# and adds them to db

def extract_avg_fuel_sales():
    """Get the HTML data from the web page which will have the link to the excel file."""
    # 
    # note the excel file name changes each month
    orig_url = "https://www.gov.uk/government/statistics/average-road-fuel-sales-and-stock-levels"
    html = requests.get("https://www.gov.uk/government/statistics/average-road-fuel-sales-and-stock-levels").content

    # Instantiate a BeautifulSoup object based on the HTML data.
    soup = BeautifulSoup(html, "html.parser")
    url = None
    print (soup.title)
    tag = soup.select("a.govuk-link.gem-c-attachment__link", limit=1)

    if 'average road fuel sales' in tag[0].string and 'https://assets.publishing.service.gov.uk/' in tag[0]['href']:
        print ('this is the one') 
        url = tag[0]['href']
    r = requests.get(url, allow_redirects=True)
    open('avg_fuel_sales.xlsx', 'wb').write(r.content)

def transform_avg_fuel_sales(df):
    df2 = df[df['Fuel Type'] == "Diesel"] 


def main():
    """ETL avg fuel sales from gov.uk website"""
    #extract_avg_fuel_sales()
    # this stops a warning message being show
    warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
    df = pd.read_excel('avg_fuel_sales.xlsx', sheet_name=8, skiprows=6, header=1, usecols="A,C,Q")
    transform_avg_fuel_sales(df)
  
  
if __name__ == '__main__':
    main()