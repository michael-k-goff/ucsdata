# This code populates the database.
# Acquire an api key from the EIA here: https://www.eia.gov/opendata/qb.php
# Create a separate file 'api_key.py' with one line as follows: api_key = "<api key acquired above>"

import requests
import sqlite3
import pandas as pd
import api_key # API key can be freely obtained from the EIA.

year_range = [1960,2021] # The first year, followed by one more than the last year

conn = sqlite3.connect("eia.db")
cur = conn.cursor()

# Same as the two letter postal codes
state_codes = {
    "Alabama":"AL",
    "Alaska":"AK",
    "Arizona":"AZ",
    "Arkansas":"AR",
    "California":"CA",
    "Colorado":"CO",
    "Connecticut":"CT",
    "Delaware":"DE",
    "District of Columbia":"DC",
    "Florida":"FL",
    "Georgia":"GA",
    "Hawaii":"HI",
    "Idaho":"ID",
    "Illinois":"IL",
    "Indiania":"IN",
    "Iowa":"IA",
    "Kansas":"KS",
    "Kentucky":"KY",
    "Louisiana":"LA",
    "Maine":"ME",
    "Maryland":"MD",
    "Massachusetts":"MA",
    "Michigan":"MI",
    "Minnesota":"MN",
    "Mississippi":"MS",
    "Missouri":"MO",
    "Montana":"MT",
    "Nebraska":"NE",
    "Nevada":"NV",
    "New Hampshire":"NH",
    "New Jersey":"NJ",
    "New Mexico":"NM",
    "New York":"NY",
    "North Carolina":"NC",
    "North Dakota":"ND",
    "Ohio":"OH",
    "Oklahoma":"OK",
    "Oregon":"OR",
    "Pennsylvania":"PA",
    "Rhode Island":"RI",
    "South Carolina":"SC",
    "South Dakota":"SD",
    "Tennessee":"TN",
    "Texas":"TX",
    "United States":"US",
    "Utah":"UT",
    "Vermont":"VT",
    "Virginia":"VA",
    "Washington":"WA",
    "West Virginia":"WV",
    "Wisconsin":"WI",
    "Wyoming":"WY"
}    

# Read a series from the EIA and store it in a table.
def add_state_data(state, dataset, table):
    series_name = "SEDS."+dataset+"."+state_codes[state]+".A"
    series_data = requests.get("http://api.eia.gov/series/?api_key="+api_key.api_key+"&series_id="+series_name)
    series_data = series_data.json()["series"][0]["data"]
    for i in range(len(series_data)):
        cur.execute("INSERT OR IGNORE INTO "+table+" (State, Year, Value) VALUES ('"+state+"',"+series_data[i][0]+", "+str(series_data[i][1])+");")
    conn.commit()
    
# Add some zeros, when they are needed for calculations.
def add_state_zero(state,table):
    series_data = [[str(year),"0"] for year in range(year_range[0],year_range[1])]
    for i in range(len(series_data)):
        cur.execute("INSERT OR IGNORE INTO "+table+" (State, Year, Value) VALUES ('"+state+"',"+series_data[i][0]+", "+str(series_data[i][1])+");")
    conn.commit()
    
# Add data in one table that is the quotient of two other data sets
def add_quotient_data(numerator, denominator, table):
    cur.execute("INSERT OR IGNORE INTO "+table+"(State, Year, Value) \
        SELECT "+numerator+".State, "+numerator+".Year, "+numerator+".Value / "+denominator+".Value as Value \
        FROM (\
            SELECT * FROM "+numerator+" \
        ) electricity \
        JOIN ( \
            SELECT * FROM "+denominator+" \
        ) energy \
        ON "+numerator+".State = "+denominator+".State AND "+numerator+".Year = "+denominator+".Year; \
    ")
    
######################################
######### Top Level Functions
######################################

def make_single_table(table):
    cur.execute("CREATE TABLE IF NOT EXISTS "+table+"( \
        State VARCHAR(32) NOT NULL, \
        Year int, \
        Value FLOAT, \
        UNIQUE (State, Year) \
    );")
    
def create_tables():
    make_single_table("electricity")
    make_single_table("energy")
    make_single_table("end_use_energy")
    make_single_table("electrification")
    make_single_table("electricity_price")
    make_single_table("energy_price")
    make_single_table("energy_price_share")
    make_single_table("gdp")
    make_single_table("population")
    make_single_table("gdp_per_capita")
    make_single_table("electricity_imports")
    make_single_table("residential_energy")
    make_single_table("residential_electricity")
    make_single_table("residential_electrification")
    make_single_table("commercial_energy")
    make_single_table("commercial_electricity")
    make_single_table("commercial_electrification")
    make_single_table("industrial_energy")
    make_single_table("industrial_electricity")
    make_single_table("industrial_electrification")
    make_single_table("transportation_energy")
    make_single_table("transportation_electricity")
    make_single_table("transportation_electrification")
    make_single_table("electric_energy")
    make_single_table("electric_electricity")
    make_single_table("electric_electrification")
    make_single_table("transportation_share")
    make_single_table("industrial_share")
    make_single_table("commercial_share")
    make_single_table("residential_share")
    make_single_table("electric_share")
    
def build_tables():
    for state in state_codes:
        print(state) # Included to track progress
        add_state_data(state,"TEEIB","electric_energy")
        add_state_zero(state,"electric_electricity")
        add_state_data(state,"TETXB","end_use_energy") # Very similar to energy
        add_state_data(state,"ELISP","electricity_imports")
        add_state_data(state,"GDPRX","gdp")
        add_state_data(state,"TPOPP","population")
        add_state_data(state,"ESTCD","electricity_price") # Average electricity price across all sectors
        add_state_data(state,"TETCD","energy_price") # Total average energy price
        add_state_data(state,"ESTCB","electricity")
        add_state_data(state,"TETCB","energy")
        add_state_data(state,"TEACB","transportation_energy")
        add_state_data(state,"ESACB","transportation_electricity")
        add_state_data(state,"TEICB","industrial_energy")
        add_state_data(state,"ESICB","industrial_electricity")
        add_state_data(state,"TECCB","commercial_energy")
        add_state_data(state,"ESCCB","commercial_electricity")
        add_state_data(state,"TERCB","residential_energy")
        add_state_data(state,"ESRCB","residential_electricity")

    # Rate of electrification as percent of total energy
    add_quotient_data("electricity", "energy", "electrification")
    # Electricity price as share of energy price
    add_quotient_data("electricity_price", "energy_price", "electricity_price_share")
    add_quotient_data("gdp", "population", "gdp_per_capita")
    add_quotient_data("residential_electricity", "residential_energy", "residential_electrification")
    add_quotient_data("commercial_electricity", "commercial_energy", "commercial_electrification")
    add_quotient_data("industrial_electricity", "industrial_energy", "industrial_electrification")
    add_quotient_data("transportation_electricity", "transportation_energy", "transportation_electrification")
    add_quotient_data("electric_electricity", "electric_energy", "electric_electrification") # Should all be zeroes
    add_quotient_data("transportation_energy", "energy", "transportation_share")
    add_quotient_data("industrial_energy", "energy", "industrial_share")
    add_quotient_data("commercial_energy", "energy", "commercial_share")
    add_quotient_data("residential_energy", "energy", "residential_share")
    add_quotient_data("electric_energy", "energy", "electric_share")
            
    conn.commit()
    
create_tables()
build_tables()
