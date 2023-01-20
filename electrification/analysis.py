# Analysis

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import sqlite3
from statsmodels.tsa.stattools import grangercausalitytests
import statsmodels.api as sm
conn = sqlite3.connect("eia.db")
cur = conn.cursor()

# Test whether the electricity/energy price ratio Granger causes electrification rates in the US.
def granger_causality():
    maxlag = 15 # Maximum number of years to test for a lag

    df = pd.read_sql_query("SELECT electrification.State, electrification.Year, electrification.Value AS Elec, electricity_price_share.Value as ElecPriceShare \
        FROM electrification JOIN electricity_price_share ON electrification.Year = electricity_price_share.Year AND electrification.State = electricity_price_share.State \
        WHERE electrification.State = 'United States';",conn)

    test_result = grangercausalitytests(df[["ElecPriceShare", "Elec"]].diff().dropna(), maxlag=maxlag, verbose=False)
    min_result = min( [test_result[i][0]["ssr_chi2test"][1] for i in range(1,maxlag+1)] )
    for i in range(maxlag):
        print( test_result[i+1][0]["ssr_chi2test"][1] )
    print(min_result)
    
# Regression of electrification in terms of electricity/price ratio across states.
def price_elec_regression():
    df = pd.read_sql_query("SELECT electrification.State as State, electrification.Value AS Elec, electricity_price_share.Value AS ElecPriceShare \
        FROM electrification JOIN electricity_price_share \
        ON electrification.Year = electricity_price_share.Year AND electrification.State = electricity_price_share.State \
        WHERE electrification.Year = '2019' AND electrification.State != 'United States';",conn)
    X = df["ElecPriceShare"].to_numpy().reshape(-1,1)
    y = df["Elec"].to_numpy().reshape(-1,1)
    reg = LinearRegression().fit(X, y)
    predicted = reg.predict(X)
    
    X = sm.add_constant(X)
    mod = sm.OLS(y,X)
    fii = mod.fit()
    print(fii.summary2())

# Regression of electrification in terms of GDP per capita across states.
def gdp_elec_regression():
    df = pd.read_sql_query("SELECT electrification.State as State, electrification.Value AS Elec, gdp_per_capita.Value AS GDPCap \
        FROM electrification JOIN gdp_per_capita \
        ON electrification.Year = gdp_per_capita.Year AND electrification.State = gdp_per_capita.State \
        WHERE electrification.Year = '2019' AND electrification.State != 'United States' AND electrification.State != 'District of Columbia';",conn)
    X = df["GDPCap"].to_numpy().reshape(-1,1)
    y = df["Elec"].to_numpy().reshape(-1,1)
    reg = LinearRegression().fit(X, y)
    predicted = reg.predict(X)
    
    X = sm.add_constant(X)
    mod = sm.OLS(y,X)
    fii = mod.fit()
    print(fii.summary2())
        
# Regression of electrification in terms of the growth in total energy consumption from 2009 to 2019 across states.
def energy_elec_regression():
    df = pd.read_sql_query("SELECT electrification.State as State, electrification.Value AS Elec, energy.Value AS Energy \
        FROM electrification JOIN energy \
        ON electrification.Year = energy.Year AND electrification.State = energy.State \
        WHERE electrification.Year = '2019' AND electrification.State != 'United States';",conn)
    df2009 = pd.read_sql_query("SELECT electrification.State as State, electrification.Value AS Elec, energy.Value AS Energy \
        FROM electrification JOIN energy \
        ON electrification.State = energy.State \
        WHERE electrification.Year = '2019' AND energy.Year = '2009' AND electrification.State != 'United States';",conn)
    df["EnergyDiff"] = (df["Energy"] - df2009["Energy"])/df2009["Energy"]
    X = df["EnergyDiff"].to_numpy().reshape(-1,1)
    y = df["Elec"].to_numpy().reshape(-1,1)
    reg = LinearRegression().fit(X, y)
    predicted = reg.predict(X)
    
    X = sm.add_constant(X)
    mod = sm.OLS(y,X)
    fii = mod.fit()
    print(fii.summary2())
    
def regression(regressor, dependent):
    df = pd.read_sql_query("SELECT "+dependent"+.State as State, "+dependent+".Value AS Dependent, "+predictor+".Value AS Predictor \
        FROM "+dependent+" JOIN "+predictor+" \
        ON "+dependent+".Year = "+predictor+".Year AND "+dependent+".State = "+predictor+".State \
        WHERE "+dependent+".Year = '2019' AND "+dependent+".State != 'United States';",conn)
    X = df["Predictor"].to_numpy().reshape(-1,1)
    y = df["Dependent"].to_numpy().reshape(-1,1)
    reg = LinearRegression().fit(X, y)
    predicted = reg.predict(X)
    
    X = sm.add_constant(X)
    mod = sm.OLS(y,X)
    fii = mod.fit()
    print(fii.summary2())
    
# Decompose variance in electrification into variance between secctors and variance within sectors.
def decomposition():
    df_elecrification = pd.read_sql_query("SELECT * FROM electrification WHERE Year = '2019' AND State != 'United States';",conn)
    df_shares = [
        pd.read_sql_query("SELECT * FROM residential_share WHERE Year = '2019' and State != 'United States';",conn),
        pd.read_sql_query("SELECT * FROM commercial_share WHERE Year = '2019' and State != 'United States';",conn),
        pd.read_sql_query("SELECT * FROM industrial_share WHERE Year = '2019' and State != 'United States';",conn),
        pd.read_sql_query("SELECT * FROM transportation_share WHERE Year = '2019' and State != 'United States';",conn)
    ]
    df_elec = [
        pd.read_sql_query("SELECT * FROM residential_electricity WHERE Year = '2019' and State != 'United States';",conn),
        pd.read_sql_query("SELECT * FROM commercial_electricity WHERE Year = '2019' AND State != 'United States';",conn),
        pd.read_sql_query("SELECT * FROM industrial_electricity WHERE Year = '2019' and State != 'United States';",conn),
        pd.read_sql_query("SELECT * FROM transportation_electricity WHERE Year = '2019' and State != 'United States';",conn)
    ]
    df_energy = [
        pd.read_sql_query("SELECT * FROM residential_energy WHERE Year = '2019' and State != 'United States';",conn),
        pd.read_sql_query("SELECT * FROM commercial_energy WHERE Year = '2019' and State != 'United States';",conn),
        pd.read_sql_query("SELECT * FROM industrial_energy WHERE Year = '2019' and State != 'United States';",conn),
        pd.read_sql_query("SELECT * FROM transportation_energy WHERE Year = '2019' and State != 'United States';",conn)
    ]
    df_shares_us = [
        pd.read_sql_query("SELECT * FROM residential_share WHERE Year = '2019' and State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM commercial_share WHERE Year = '2019' and State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM industrial_share WHERE Year = '2019' and State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM transportation_share WHERE Year = '2019' and State = 'United States';",conn)
    ]
    df_elec_us = [
        pd.read_sql_query("SELECT * FROM residential_electricity WHERE Year = '2019' and State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM commercial_electricity WHERE Year = '2019' AND State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM industrial_electricity WHERE Year = '2019' and State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM transportation_electricity WHERE Year = '2019' and State = 'United States';",conn)
    ]
    df_energy_us = [
        pd.read_sql_query("SELECT * FROM residential_energy WHERE Year = '2019' and State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM commercial_energy WHERE Year = '2019' and State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM industrial_energy WHERE Year = '2019' and State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM transportation_energy WHERE Year = '2019' and State = 'United States';",conn)
    ]
    # Another way of calculating electrification
    df_elec_constant_shares = sum([df_shares_us[i]["Value"][0]*df_elec[i]["Value"]/df_energy[i]["Value"] for i in range(4)])
    elec_constant_shares = np.var(df_elec_constant_shares) # 0.0005997759446552342
    df_elec_constant_rate = sum([df_shares[i]["Value"]*df_elec_us[i]["Value"][0]/df_energy_us[i]["Value"][0] for i in range(4)])
    elec_constant_rate = np.var(df_elec_constant_rate) # 0.00031628128005427774
    elec_overall = np.var(df_elecrification["Value"]) # 0.0008719045137182862
    print("Variance due to varying electrification rates within sectors: "+str( (elec_constant_shares+(elec_overall-elec_constant_rate)) / 2.0 / elec_overall) )
    
def decomposition_time():
    df_electrification = pd.read_sql_query("SELECT * FROM electrification WHERE State = 'United States';",conn)
    df_shares_us = [
        pd.read_sql_query("SELECT * FROM residential_share WHERE State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM commercial_share WHERE State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM industrial_share WHERE State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM transportation_share WHERE State = 'United States';",conn)
    ]
    df_elec_us = [
        pd.read_sql_query("SELECT * FROM residential_electricity WHERE State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM commercial_electricity WHERE State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM industrial_electricity WHERE State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM transportation_electricity WHERE State = 'United States';",conn)
    ]
    df_energy_us = [
        pd.read_sql_query("SELECT * FROM residential_energy WHERE State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM commercial_energy WHERE State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM industrial_energy WHERE State = 'United States';",conn),
        pd.read_sql_query("SELECT * FROM transportation_energy WHERE State = 'United States';",conn)
    ]
    in_sector_diff = []
    for i in range(1960,2019): # Do range(1960,2019) for the full version
        index = i-1960
        in_sector_difference1 = sum([df_shares_us[i]["Value"][index]*df_elec_us[i]["Value"][index+1]/df_energy_us[i]["Value"][index+1] for i in range(4)]) - \
                                sum([df_shares_us[i]["Value"][index]*df_elec_us[i]["Value"][index]/df_energy_us[i]["Value"][index] for i in range(4)])
        in_sector_difference2 = sum([df_shares_us[i]["Value"][index+1]*df_elec_us[i]["Value"][index+1]/df_energy_us[i]["Value"][index+1] for i in range(4)]) - \
                                sum([df_shares_us[i]["Value"][index+1]*df_elec_us[i]["Value"][index]/df_energy_us[i]["Value"][index] for i in range(4)])
        in_sector_diff.append( (in_sector_difference1+in_sector_difference2)/ 2.0 / (df_electrification["Value"][1] - df_electrification["Value"][0]) )
    print(sum(in_sector_diff)/len(in_sector_diff))

price_elec_regression()
gdp_elec_regression()
decomposition()
decomposition_time()