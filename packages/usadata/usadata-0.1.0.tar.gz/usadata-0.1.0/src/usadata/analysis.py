import pandas as pd
from scipy.stats import ttest_ind
import statsmodels.api as sm
from itertools import combinations
from .cleaning import USdata  # provide backwards-compatible access to USdata


def t_test(factor1, factor2, variable, data):
    """Perform a t-test between two groups defined by factor1 and factor2 on the specified variable."""
    """Input: Dataframe"""
    group1 = data[data[factor1] == factor2[0]][variable].dropna()
    group2 = data[data[factor1] == factor2[1]][variable].dropna()
    
    t_stat, p_value = ttest_ind(group1, group2, equal_var=False)
    return t_stat, p_value




def TTests(dataFrame):
    """Conduct t-tests for various variables across North/South and East/West regions."""
    test_outputs = []

    state_regionNS = {
    # Southern States
    'Alabama': 'South', 'Arkansas': 'South', 'Florida': 'South', 'Georgia': 'South',
    'Kentucky': 'South', 'Louisiana': 'South', 'Mississippi': 'South',
    'North Carolina': 'South', 'Oklahoma': 'South', 'South Carolina': 'South',
    'Tennessee': 'South', 'Texas': 'South', 'Virginia': 'South', 'West Virginia': 'South',
    'Delaware': 'South', 'Maryland': 'South', 'District of Columbia': 'South',

    # Northern States
    'Connecticut': 'North', 'Maine': 'North', 'Massachusetts': 'North', 
    'New Hampshire': 'North', 'Rhode Island': 'North', 'Vermont': 'North',
    'New Jersey': 'North', 'New York': 'North', 'Pennsylvania': 'North', 
    'Ohio': 'North', 'Michigan': 'North', 'Indiana': 'North',
    'Illinois': 'North', 'Iowa': 'North', 'Minnesota': 'North', 'Wisconsin': 'North',
    'North Dakota': 'North', 'South Dakota': 'North', 'Nebraska': 'North',
    'Kansas': 'North', 'Missouri': 'North', 'Montana': 'North', 'Wyoming': 'North',
    'Colorado': 'North', 'Idaho': 'North', 'Washington': 'North', 'Oregon': 'North'
}

    # Apply mapping
    dataFrame['RegionNS'] = dataFrame['States'].map(state_regionNS)

    state_regionEW = {
    # East
    'Maine': 'East', 'New Hampshire': 'East', 'Vermont': 'East',
    'Massachusetts': 'East', 'Rhode Island': 'East', 'Connecticut': 'East',
    'New York': 'East', 'New Jersey': 'East', 'Pennsylvania': 'East',
    'Delaware': 'East', 'Maryland': 'East', 'District of Columbia': 'East',
    'Virginia': 'East', 'West Virginia': 'East', 'North Carolina': 'East',
    'South Carolina': 'East', 'Georgia': 'East', 'Florida': 'East',
    'Alabama': 'East', 'Mississippi': 'East', 'Tennessee': 'East',
    'Kentucky': 'East', 'Ohio': 'East', 'Michigan': 'East', 'Indiana': 'East',
    'Illinois': 'East', 'Wisconsin': 'East', 'Minnesota': 'East',
    'Iowa': 'East', 'Missouri': 'East', 'Arkansas': 'East', 'Louisiana': 'East',

    # West
    'Texas': 'West', 'Oklahoma': 'West', 'Kansas': 'West', 'Nebraska': 'West',
    'South Dakota': 'West', 'North Dakota': 'West', 'Montana': 'West',
    'Wyoming': 'West', 'Colorado': 'West', 'New Mexico': 'West',
    'Arizona': 'West', 'Utah': 'West', 'Idaho': 'West', 
    'Washington': 'West', 'Oregon': 'West', 'California': 'West',
    'Nevada': 'West', 'Hawaii': 'West', 'Alaska': 'West'
}

    # Apply mapping
    dataFrame['RegionEW'] = dataFrame['States'].map(state_regionEW)   

    # T-tests
    for region_type, regions in [('RegionNS', ['North', 'South']), ('RegionEW', ['East', 'West'])]:
        for variable in ['Avg_PM25', 'Health_Index', 'Education_Index', 'Income_Index', 'Homeless_Ratio']:
            t_stat, p_value = t_test(region_type, regions, variable, dataFrame)
            test_outputs.append((region_type, variable, t_stat, p_value))

    for res in test_outputs:
        print(f"Region Type: {res[0]}, Variable: {res[1]}, t-statistic: {res[2]:.4f}, p-value: {res[3]:.4f}")


# use pm25 as response for regression analysis
# create function to do regression analysis
# 1. do a Best subset Regression to select variables
# 2. output regression summary table

def regression_analysis(dataFrame, response_var):
    """Perform regression analysis using statsmodels."""
    """Input: Dataframe and response variable name as string"""
    # predictor variables are the features in the dataFrame except the response variable
    y = dataFrame[response_var]
    if not pd.api.types.is_numeric_dtype(y):
        raise ValueError(f"Response variable '{response_var}' must be numeric.")
    # Define potential predictor variables

    predictors = dataFrame.columns.tolist()
    predictors.remove(response_var)

    predictors = dataFrame[predictors].select_dtypes(include=['number']).columns.tolist()

    best_aic = float('inf')
    best_model = None
    best_combination = None

    # Best subset selection
    for i in range(1, len(predictors) + 1):
        for combo in combinations(predictors, i):
            X = dataFrame[list(combo)]
            X = sm.add_constant(X)  # Add constant term
            y = dataFrame[response_var]

            model = sm.OLS(y, X).fit()
            if model.aic < best_aic:
                best_aic = model.aic
                best_model = model
                best_combination = combo

    print(f"Best model using predictors: {best_combination}")
    print(best_model.summary())
