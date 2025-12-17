import greenhub as gh
import pandas as pd
import json
from sklearn.linear_model import LinearRegression
import numpy as np

"""
This is a filled-out example of how a `run` function can be implemented. 
It uses the very simple linear regression model that was created in `train_model.ipynb`. 

The model created is a "end of Season" model, which is executed only once a year in june, 
only using climate data from may for predicting the yield. Therefore the passed month is not used, 
cause Greenhub.ai already knows to only execute the model once in June, thanks to the model upload process form.

More:
- greenhub:  https://greenhub.ai
- docs:  https://docs.greenhub.ai
"""

def run(year: int, month: int):
    # -- Initialize GreenHub SDK --
    gh.initialize("[GREENHUB_API_KEY]")  # todo - add greenhub api key

    # -- Fetch and setup feature vector --
    # get climate data for MISSOURI from 2010 to 2020
    climate_data = gh.get_climate_data(
        country='US',
        start_year=year,
        spatial_resolution='state',
        time_resolution='monthly'
    )
    # we only consider data for MISSOURI and May
    climate_data = climate_data[climate_data['State'] == 'MISSOURI']
    climate_data = climate_data[(climate_data['Month'] == 5)]
    X = climate_data[[
        'Mean Min Temperature [K]',
        'Mean Max Temperature [K]',
        'Mean Temperature [K]',
        'Total Precipitation [mm]',
        'Temperature*Precipitation',
        'Temperature^2',
        'Precipitation^2',
        'Min Precipitation [mm]',
        'Max Precipitation [mm]',
        'Mean Precipitation [mm]'
    ]].to_numpy()
    # special: if the data contains NaN values the model does not work -> we return None instead
    if np.isnan(X).any():
        return pd.DataFrame({
            "state": ['MISSOURI'],
            "predictedYield": [None]
        })

    # -- Load model --
    # load model parameters from json
    with open("./model.json", "r") as f:
        model_params = json.load(f)
    # create model
    model = LinearRegression()
    model.coef_ = np.array(model_params["coef"])
    model.intercept_ = np.array(model_params["intercept"])

    # -- Run model --
    y_pred = model.predict(X)
    prediction = None
    if y_pred.shape == (1, 1):
        prediction = y_pred[0, 0]

    # -- Format to expected GreenHub output --
    output = pd.DataFrame({
        "state": ['MISSOURI'],
        "predictedYield": [prediction]
    })

    return output
