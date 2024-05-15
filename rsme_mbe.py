import numpy as np

def calculate_rmse_mbe(matches):
    satellite_values = []
    ground_values = []

    idx = 0
    while idx < len(matches):
        satellite_value = float(matches[idx]['value'])
        ground_value = float(matches[idx + 1]['value'])

        satellite_values.append(satellite_value)
        ground_values.append(ground_value)

        idx += 2

    rmse = np.sqrt(np.mean((np.array(satellite_values) - np.array(ground_values))**2))
    mbe = np.mean(np.array(satellite_values) - np.array(ground_values))

    return rmse, mbe
