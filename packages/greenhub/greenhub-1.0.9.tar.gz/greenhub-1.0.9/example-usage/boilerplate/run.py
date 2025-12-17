import greenhub as gh
import pandas as pd


def run(year: int, month: int):
    
    # Initialize GreenHub SDK
    # TODO: You can find your API key in your Account dialog at the top right of the GreenHub page
    gh.initialize("YOUR_API_KEY")

    # Fetch and setup feature vector
    features = ...  # TODO

    # Load model
    model = ...  # TODO

    # Run model
    prediction = ...  # TODO

    # Format to expected GreenHub output
    output = ...  # TODO

    return output
