import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.stats import linregress


def plot_data(satellite_name, matches, time_interval_minutes=None, satellite_product=None, time_of_day=None):
    if matches:
        if satellite_name.lower() == 'landsat':
            fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 8), gridspec_kw={'hspace': 0.5})
        else:
            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(12, 12), gridspec_kw={'hspace': 0.5})

        # First plot: Ground vs Satellite data comparison
        ax1 = axes[0]
        satellite_x = []  # Satellite data
        satellite_y = []
        ground_x = []  # Ground measurement data
        ground_y = []

        for match in matches:
            if match['source'].startswith('Satellite'):
                satellite_x.append(pd.to_datetime(match['datetime']))
                satellite_y.append(float(match['value']))
            else:
                ground_x.append(pd.to_datetime(match['datetime']))
                ground_y.append(float(match['value']))

        min_len = min(len(satellite_x), len(ground_x), len(satellite_y), len(ground_y))
        satellite_x = satellite_x[:min_len]
        satellite_y = satellite_y[:min_len]
        ground_x = ground_x[:min_len]
        ground_y = ground_y[:min_len]

        ax1.plot(satellite_x, satellite_y, marker='o', linestyle='', color='red', label='Satellite')
        ax1.plot(ground_x, ground_y, marker='o', linestyle='', color='blue', label='Ground Measurement')
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Comparison of Ground Measurement with Satellites')
        ax1.grid(True)
        ax1.legend()

        satellite_info = f'Satellite: {satellite_name.capitalize()}'
        if satellite_name.lower() == 'modis' and satellite_product and time_of_day:
            satellite_info += f'\nType: {satellite_product.capitalize()} {time_of_day.capitalize()}'
            satellite_info += f'\nTime Interval: {time_interval_minutes} minutes'

        ax1.text(0.05, 0.95, satellite_info, transform=ax1.transAxes,
                 verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

        # Second plot: Scatter plot
        ax2 = axes[1]

        ax2.scatter(ground_y, satellite_y, color='green', alpha=0.5)
        ax2.axhline((max(satellite_y) + min(satellite_y)) / 2, color='black', linestyle='--')
        ax2.axvline((max(ground_y) + min(ground_y)) / 2, color='black', linestyle='--')
        ax2.plot([min(ground_y), max(ground_y)], [min(satellite_y), max(satellite_y)], color='gray', linestyle='--')

        slope, intercept, r_value, p_value, std_err = linregress(ground_y, satellite_y)
        regression_eqn = f'Regression Line: y = {slope:.2f}x + {intercept:.2f}\nR-squared: {r_value ** 2:.2f}'
        ax2.text(0.5, 0.9, regression_eqn, horizontalalignment='center', verticalalignment='center',
                 transform=ax2.transAxes, fontsize=10,
                 bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))

        ax2.set_xlabel('Ground Temperature (°C)')
        ax2.set_ylabel('Satellite Temperature (°C)')
        ax2.set_title('Scatter Plot of Ground vs. Satellite Temperature')
        ax2.grid(True)

        # Third plot: Mode and Trend (only for MODIS)
        if satellite_name.lower() != 'landsat':
            ax3 = axes[2]

            all_temperatures = ground_y + satellite_y
            mode_all = pd.Series(all_temperatures).mode()[0]

            ax3.plot(ground_x + satellite_x, [mode_all] * (len(ground_x) + len(satellite_x)), linestyle='--',
                     color='black', label=f'Mode: {mode_all}')

            trend_ground = np.polyfit(range(len(ground_y)), ground_y, 1)
            trend_satellite = np.polyfit(range(len(satellite_y)), satellite_y, 1)
            ax3.plot(ground_x, np.polyval(trend_ground, range(len(ground_y))), linestyle=':', color='blue',
                     label='Ground Trend')
            ax3.plot(satellite_x, np.polyval(trend_satellite, range(len(satellite_y))), linestyle=':', color='red',
                     label='Satellite Trend')

            ax3.set_ylabel('Temperature (°C)')
            ax3.set_title('Mode and Trend of Ground vs. Satellite Temperature')
            ax3.grid(True)
            ax3.legend()

        # Prompt user to save the plot
        save_plot = input("Хотите сохранить график? (да/нет): ").strip().lower()
        if save_plot == 'да':
            if not os.path.exists('Graphics'):
                os.makedirs('Graphics')
            current_time = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
            plt.savefig(
                f'Graphics/{satellite_name}_comparison_{satellite_product}_{time_of_day}_{time_interval_minutes}_{current_time}.png')
            print(
                f"Plot saved as Graphics/{satellite_name}_comparison_{satellite_product}_{time_of_day}_{time_interval_minutes}_{current_time}.png")

        plt.show()
        plt.close(fig)
    else:
        print("No matches found.")


