from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
import pandas as pd

from rsme_mbe import calculate_rmse_mbe

def create_pdf_report(df, matches, satellite_name, start_date, end_date, coordinates, time_interval_minutes=None, satellite_product=None, time_of_day=None):
    # Создаем папку Reports, если она не существует
    if not os.path.exists('Reports'):
        os.makedirs('Reports')

    # Создаем папку Graphics, если она не существует
    if not os.path.exists('Graphics'):
        os.makedirs('Graphics')

    # Формируем имя файла на основе текущего времени, названия спутника и дат начала и конца
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_file_name = f"Reports/{satellite_name}_report_{start_date}_{end_date}_{current_time}.pdf"

    doc = SimpleDocTemplate(pdf_file_name, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Добавляем заголовок
    elements.append(Paragraph(f"Report from data {satellite_name}", styles['Title']))
    elements.append(Spacer(1, 12))

    # Добавляем информацию о временном промежутке, координатах и типе спутника
    satellite_info = f"Satellite: {satellite_name.capitalize()}"
    if satellite_product:
        satellite_info += f"\nType: {satellite_product.capitalize()}"
    if time_of_day:
        satellite_info += f"\nTime of Day: {time_of_day.capitalize()}"
    if time_interval_minutes:
        satellite_info += f"\nTime Interval: {time_interval_minutes} minutes"
    satellite_info += f"\nCoordinates: {coordinates}"
    satellite_info += f"\nDate Range: {start_date} to {end_date}"
    elements.append(Paragraph(satellite_info, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Разделяем столбцы DataFrame на группы по столбцам и добавляем каждую группу на новую строку
    columns = list(df.columns)
    for i in range(0, len(columns), 7):
        subset = columns[i:i + 7]
        df_table_data = [subset] + df[subset].values.tolist()
        df_table = Table(df_table_data)
        df_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(df_table)
        elements.append(Spacer(1, 12))

    # Добавляем таблицу с совпадениями
    if len(matches) % 2 == 0:
        matches_table_data = [['ID', 'Satellite name', 'Satellite value', 'Satellite Datetime', 'Ground value', 'Ground Datetime']]
        for idx in range(0, len(matches), 2):
            match = matches[idx]
            if idx + 1 < len(matches):
                match_next = matches[idx + 1]
                matches_table_data.append([idx // 2 + 1,
                                           match.get('source', '').split(' - ')[1],
                                           match.get('value', ''),
                                           match.get('datetime', ''),
                                           match_next.get('value', ''),
                                           match_next.get('datetime', '')])

        matches_table = Table(matches_table_data)
        matches_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(matches_table)
        elements.append(Spacer(1, 12))
    else:
        print("Matches list does not have an even number of elements. Cannot create PDF report.")

    # Вычисляем RMSE и MBE
    rmse, mbe = calculate_rmse_mbe(matches)
    elements.append(Paragraph(f"RMSE: {rmse}", styles['Normal']))
    elements.append(Paragraph(f"MBE: {mbe}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Создаем и сохраняем графики
    fig, ax = plt.subplots()
    satellite_values = [float(matches[i]['value']) for i in range(0, len(matches), 2)]
    ground_values = [float(matches[i + 1]['value']) for i in range(0, len(matches), 2)]
    dates = [matches[i]['datetime'] for i in range(0, len(matches), 2)]

    # Поворачиваем даты на 45 градусов
    plt.xticks(rotation=45)

    ax.plot(dates, satellite_values, label='Satellite')
    ax.plot(dates, ground_values, label='Ground')
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.set_title(f'{satellite_name} vs Ground Values')
    ax.legend()
    plot_file_name = f"Graphics/{satellite_name}_plot_{current_time}.png"
    plt.savefig(plot_file_name)
    plt.close(fig)

    # Включаем графики в отчет
    elements.append(Image(plot_file_name, width=640, height=480))
    elements.append(Spacer(1, 12))

    # Подтверждение сохранения отчета
    save_report = input("Хотите ли вы сохранить отчет? (да/нет): ").lower()
    if save_report == "да":
        doc.build(elements)
        print(f"PDF отчет сохранен в {pdf_file_name}")
    else:
        print("Отчет не был сохранен.")