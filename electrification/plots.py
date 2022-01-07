# Plots

###### Imports and set up

import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import matplotlib.ticker as mtick

conn = sqlite3.connect("eia.db")
cur = conn.cursor()

# List of state names in the database
states = cur.execute("SELECT DISTINCT State FROM electrification;")
state_names = []
for row in states:
    state_names.append(row[0])
    
###### Plots

def electrification_plot():
    ###### Set up data
    df = pd.read_sql_query("SELECT * FROM electrification WHERE State = 'United States';",conn)
    df["Value"] = 100*2.5*df["Value"] # Assuming a primary energy factor of 2.5. The factor of 100 is for percentages.

    ###### Electrification Plot
    fig = plt.figure(1, (7, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(df["Year"],df["Value"],color="#333333")

    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    plt.ylim(0,100)
    plt.ylabel("Electrification Rate")
    plt.title("Electrification in the United States")
    plt.savefig("us_elec100.svg")
    plt.clf()

def electrification_plot_states():
    ###### Set up data
    df = pd.read_sql_query("SELECT * FROM electrification WHERE State = 'United States';",conn)
    df["Value"] = 100*2.5*df["Value"] # Assuming a primary energy factor of 2.5. The factor of 100 is for percentages.

    ###### Electrification Plot
    fig = plt.figure(1, (7, 4))
    ax = fig.add_subplot(1, 1, 1)
    for i in range(len(state_names)):
        if state_names[i] != "United States":
            df = pd.read_sql_query("SELECT * FROM electrification WHERE State = '"+state_names[i]+"';",conn)
            df["Value"] = 100*2.5*df["Value"] # Assuming a primary energy factor of 2.5. The factor of 100 is for percentages.
            ax.plot(df["Year"],df["Value"], linewidth = 1, color="#333333",alpha=0.5)
    df = pd.read_sql_query("SELECT * FROM electrification WHERE State = 'United States';",conn)
    df["Value"] = 100*2.5*df["Value"] # Assuming a primary energy factor of 2.5. The factor of 100 is for percentages.
    ax.plot(df["Year"],df["Value"], linewidth = 5, color='black')

    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    plt.ylabel("Electrification Rate")
    plt.title("Electrification in the US and States")
    plt.savefig("us_elec_states.svg")
    plt.clf()

def price_plot():
    ###### Set up data for prices
    df = pd.read_sql_query("SELECT * FROM electricity_price_share WHERE State = 'United States';",conn)
    init_value = df["Value"][0]

    ###### Price Plot
    fig = plt.figure(1, (7, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(df["Year"],df["Value"],color="#333333")

    plt.title("United States Electricity-Energy Price Ratio")
    plt.savefig("us_elec_price.svg")
    plt.clf()

def price_electrification_by_state():
    df = pd.read_sql_query("SELECT electrification.State as State, electrification.Value AS Elec, electricity_price_share.Value AS ElecPriceShare \
        FROM electrification JOIN electricity_price_share \
        ON electrification.Year = electricity_price_share.Year AND electrification.State = electricity_price_share.State \
        WHERE electrification.Year = '2019' AND electrification.State != 'United States';",conn)
    fig = plt.figure(1, (7, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(250*df["Elec"],df["ElecPriceShare"],'bo',color="#333333")
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())

    plt.xlabel("Electrification")
    plt.ylabel("Electricity to Energy Price Ratio")
    plt.title("Electrification and Prices by State in 2019")
    plt.savefig("elec_elec_price_state.svg")
    plt.clf()
    
def elec_gdp():
    df = pd.read_sql_query("SELECT electrification.State as State, electrification.Value AS Elec, gdp_per_capita.Value AS GDPCap \
        FROM electrification JOIN gdp_per_capita \
        ON electrification.Year = gdp_per_capita.Year AND electrification.State = gdp_per_capita.State \
        WHERE electrification.Year = '2019' AND electrification.State != 'United States';",conn)
    
    fig = plt.figure(1, (7, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(df["Elec"],df["GDPCap"],'bo')

    plt.xlabel("Electrification")
    plt.ylabel("GDP Per Capita")
    plt.savefig("elec_gdp_capita.png")
    plt.clf()
    
def elec_transportation():
    df = pd.read_sql_query("SELECT electrification.State as State, electrification.Value AS Elec, transportation_share.Value AS TranspoShare \
        FROM electrification JOIN transportation_share \
        ON electrification.Year = transportation_share.Year AND electrification.State = transportation_share.State \
        WHERE electrification.Year = '2019' AND electrification.State != 'United States';",conn)
    
    fig = plt.figure(1, (7, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(df["Elec"],df["TranspoShare"],'bo')

    plt.xlabel("Electrification")
    plt.ylabel("Transportation Share")
    plt.savefig("elec_transpo.png")
    plt.clf()
    
def elec_industry():
    df = pd.read_sql_query("SELECT electrification.State as State, electrification.Value AS Elec, industrial_share.Value AS IndustryShare \
        FROM electrification JOIN industrial_share \
        ON electrification.Year = industrial_share.Year AND electrification.State = industrial_share.State \
        WHERE electrification.Year = '2019' AND electrification.State != 'United States';",conn)
    
    fig = plt.figure(1, (7, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(df["Elec"],df["IndustryShare"],'bo')

    plt.xlabel("Electrification")
    plt.ylabel("Industrial Share")
    plt.savefig("elec_industry.png")
    plt.clf()
    
def elec_residential():
    df = pd.read_sql_query("SELECT electrification.State as State, electrification.Value AS Elec, residential_share.Value AS ResShare \
        FROM electrification JOIN residential_share \
        ON electrification.Year = residential_share.Year AND electrification.State = residential_share.State \
        WHERE electrification.Year = '2019' AND electrification.State != 'United States';",conn)
    
    fig = plt.figure(1, (7, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(df["Elec"],df["ResShare"],'bo')

    plt.xlabel("Electrification")
    plt.ylabel("Residential Share")
    plt.savefig("elec_res.png")
    plt.clf()
    
def elec_commercial():
    df = pd.read_sql_query("SELECT electrification.State as State, electrification.Value AS Elec, commercial_share.Value AS CommShare \
        FROM electrification JOIN commercial_share \
        ON electrification.Year = commercial_share.Year AND electrification.State = commercial_share.State \
        WHERE electrification.Year = '2019' AND electrification.State != 'United States';",conn)
    
    fig = plt.figure(1, (7, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(df["Elec"],df["CommShare"],'bo')

    plt.xlabel("Electrification")
    plt.ylabel("Commercial Share")
    plt.savefig("elec_comm.png")
    plt.clf()
    
def elec_by_sector():
    df_elec = pd.read_sql_query("SELECT * FROM electrification WHERE State = 'United States';",conn)
    df_elec_res = pd.read_sql_query("SELECT * FROM residential_electrification WHERE State = 'United States';",conn)
    df_elec_comm = pd.read_sql_query("SELECT * FROM commercial_electrification WHERE State = 'United States';",conn)
    df_elec_ind = pd.read_sql_query("SELECT * FROM industrial_electrification WHERE State = 'United States';",conn)
    df_elec_transpo = pd.read_sql_query("SELECT * FROM transportation_electrification WHERE State = 'United States';",conn)
    
    fig = plt.figure(1, (7, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(df_elec_comm["Year"],100*2.5*df_elec_comm["Value"],label="Commercial",color="#333333",linewidth=1)
    ax.plot(df_elec_res["Year"],100*2.5*df_elec_res["Value"],label="Residential",color="#333333",linewidth=1)
    ax.plot(df_elec["Year"],100*2.5*df_elec["Value"],label="Overall",color="#333333",linewidth=2)
    ax.plot(df_elec_ind["Year"],100*2.5*df_elec_ind["Value"],label="Industrial",color="#333333",linewidth=1)
    ax.plot(df_elec_transpo["Year"],100*2.5*df_elec_transpo["Value"],label="Transpo.",color="#333333",linewidth=1)
    ax.text(1983,55,"Commercial")
    ax.text(1990,43,"Residential")
    ax.text(1990,29,"Overall")
    ax.text(1990,22,"Industrial")
    ax.text(1990,1.5,"Transportation")
    plt.ylabel("Electrification")
    #plt.legend()
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    
    plt.savefig("elec_by_sector.svg")
    plt.clf()    

electrification_plot()
electrification_plot_states()
price_plot()
price_electrification_by_state()
elec_gdp()
elec_transportation()
elec_industry()
elec_residential()
elec_commercial()
elec_by_sector()
