"""this script grabs the latest version of the average fuel sales statistics and adds them to db"""
import warnings
#import datetime as dt
import pandas as pd
import openpyxl
from bs4 import BeautifulSoup
import requests


# this script grabs the latest version of the average fuel sales statistics
# and adds them to db

#create a df for each year
def split_years(dt):
    """takes a dataframe, and returns a list of dataframes one per year"""
    dt['year'] = dt['Date'].dt.year
    return [dt[dt['year'] == y] for y in dt['year'].unique()]


def extract_avg_fuel_sales():
    """Get the HTML data from the web page which will have the link to the excel file."""
    # note the excel file name changes each month
    orig_url = "https://www.gov.uk/government/statistics/average-road-fuel-sales-and-stock-levels"
    html = requests.get(orig_url).content

    # Instantiate a BeautifulSoup object based on the HTML data.
    soup = BeautifulSoup(html, "html.parser")
    url = None
    print(soup.title)
    tag = soup.select("a.govuk-link.gem-c-attachment__link", limit=1)

    if (
        "average road fuel sales" in tag[0].string
        and "https://assets.publishing.service.gov.uk/" in tag[0]["href"]
    ):
        print("this is the one")
        url = tag[0]["href"]
        # TODO else raise exception
    r = requests.get(url, allow_redirects=True)
    open("avg_fuel_sales.xlsx", "wb").write(r.content)


def transform_avg_fuel_sales(df):
    """transform excel file to something more interesting"""
    # we want all fuel types, so use rows which have the total, remove those that are specigic to petrol or diesel
    df2_total = df[df["Fuel Type"] == "Total"]
    df2_diesel = df[df["Fuel Type"] == "Diesel"]
    df2_petrol = df[df["Fuel Type"] == "Petrol"]
    # we are only interested in a couple of columns, so create a new df with just those
    df3 = pd.DataFrame(df2_total, columns=["Date", "United Kingdom"])
    # add some new columbs based on rolling averages.
    # fills in blanks, and set as int
    df3["7days"] = df3["United Kingdom"].rolling(7).mean().fillna(0).astype(int)
    df3["4week"] = df3["United Kingdom"].rolling(28).mean().fillna(0).astype(int)
    df3["1year"] = df3["United Kingdom"].rolling(365).mean().fillna(0).astype(int)
    # convert date to a datetime format
    df3["Date"] = pd.to_datetime(df3["Date"])
    df3 = df3[df3["Date"].dt.year != 2020]
    df3["year"] = df3["Date"].dt.year
    print(df3.head(10))
    print(df3.tail(10))
    #new df without the UK col, ie the orig data, too noisey
    df4 = df3.drop(['United Kingdom'],axis=1)


def main():
    """ETL avg fuel sales from gov.uk website"""
    # extract_avg_fuel_sales()
    # this stops a warning message being show
    #warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
    df = pd.read_excel(
        "avg_fuel_sales.xlsx", sheet_name=8, skiprows=6, header=1, usecols="A,C,Q"
    )
    transform_avg_fuel_sales(df)


if __name__ == "__main__":
    main()
