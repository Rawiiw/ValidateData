import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.stats import linregress

def plot_data(satellite_name, matches, time_interval_minutes=None, satellite_product=None, time_of_day=None):
    if matches:
        # Создание фигуры с несколькими графиками
        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(12, 12), gridspec_kw={'hspace': 0.5})  # Увеличенное вертикальное расстояние между графиками

        # Первый график: наземные и спутниковые данные
        ax1 = axes[0]
        satellite_x = []  # Данные для спутниковых значений
        satellite_y = []

        ground_x = []  # Данные для наземных значений
        ground_y = []

        for match in matches:
            if match['source'].startswith('Satellite'):
                satellite_x.append(pd.to_datetime(match['datetime']))
                satellite_y.append(float(match['value']))
            else:
                ground_x.append(pd.to_datetime(match['datetime']))
                ground_y.append(float(match['value']))

        # Построение точек для спутниковых значений на первом графике
        ax1.plot(satellite_x, satellite_y, marker='o', linestyle='', color='red', label='Satellite')
        ax1.plot(ground_x, ground_y, marker='o', linestyle='', color='blue', label='Ground Measurement')
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Comparison of Ground Measurement with Satellites')
        ax1.grid(True)
        ax1.legend()

        # Формирование информации о спутнике и данных
        satellite_info = f'Satellite: {satellite_name.capitalize()}'
        if satellite_name.lower() == 'modis' and satellite_product and time_of_day:
            satellite_info += f'\nType: {satellite_product.capitalize()} {time_of_day.capitalize()}'
            satellite_info += f'\nTime Interval: {time_interval_minutes} minutes'

        # Добавляем информацию о спутнике на график
        ax1.text(0.05, 0.95, satellite_info, transform=ax1.transAxes,
                 verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

        # Второй график: облако рассеяния
        ax2 = axes[1]

        ax2.scatter(ground_y, satellite_y, color='green', alpha=0.5)
        ax2.axhline((max(satellite_y) + min(satellite_y)) / 2, color='black', linestyle='--')
        ax2.axvline((max(ground_y) + min(ground_y)) / 2, color='black', linestyle='--')

        # Добавляем диагональную ось
        ax2.plot([min(ground_y), max(ground_y)], [min(satellite_y), max(satellite_y)], color='gray', linestyle='--')

        # Вычисляем коэффициенты регрессии
        slope, intercept, r_value, p_value, std_err = linregress(ground_y, satellite_y)

        # Создаем уравнение регрессии в виде строки
        regression_eqn = f'Regression Line: y = {slope:.2f}x + {intercept:.2f}\nR-squared: {r_value ** 2:.2f}'

        # Добавляем уравнение регрессии на график
        ax2.text(0.5, 0.9, regression_eqn, horizontalalignment='center', verticalalignment='center',
                 transform=ax2.transAxes, fontsize=10, bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))

        ax2.set_xlabel('Ground Temperature (°C)')
        ax2.set_ylabel('Satellite Temperature (°C)')
        ax2.set_title('Scatter Plot of Ground vs. Satellite Temperature')
        ax2.grid(True)

        # Третий график: мода и тренд
        ax3 = axes[2]

        # Собираем все данные для определения моды
        all_temperatures = ground_y + satellite_y

        # Вычисляем моду для всех данных
        mode_all = pd.Series(all_temperatures).mode()[0]

        # Для всех данных
        ax3.plot(ground_x + satellite_x, [mode_all] * (len(ground_x) + len(satellite_x)), linestyle='--', color='black', label=f'Mode: {mode_all}')

        # Тренд
        trend_ground = np.polyfit(range(len(ground_y)), ground_y, 1)
        trend_satellite = np.polyfit(range(len(satellite_y)), satellite_y, 1)
        ax3.plot(ground_x, np.polyval(trend_ground, range(len(ground_y))), linestyle=':', color='blue', label='Ground Trend')
        ax3.plot(satellite_x, np.polyval(trend_satellite, range(len(satellite_y))), linestyle=':', color='red', label='Satellite Trend')

        ax3.set_ylabel('Temperature (°C)')
        ax3.set_title('Mode and Trend of Ground vs. Satellite Temperature')
        ax3.grid(True)
        ax3.legend()


        plt.show()


        save_plot = input("Хотите ли сохранить график? (да/нет): ").lower()
        if save_plot == "да":

            if not os.path.exists('Graphics'):
                os.makedirs('Graphics')
            current_time = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
            plt.savefig(f'Graphics/{satellite_name}_comparison_{satellite_product}_{time_of_day}_{time_interval_minutes}_{current_time}.png')
        elif save_plot == "нет":
            print("График не сохранен.")
        else:
            print("Некорректный ответ.")
    else:
        print("No matches found.")
