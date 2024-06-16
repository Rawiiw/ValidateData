import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from rsme_mbe import calculate_rmse_mbe

def create_pdf_report(df, matches, satellite_name, start_date, end_date, coordinates, time_interval_minutes=None,
                      satellite_product=None, time_of_day=None):
    # Prompt user if they want to save the report
    save_report = input("Хотите сохранить отчёт? (да/нет) ").strip().lower()
    if save_report != 'да':
        print("Report generation canceled.")
        return

    # Create Reports and Graphics directories if they do not exist
    if not os.path.exists('Reports'):
        os.makedirs('Reports')
    if not os.path.exists('Graphics'):
        os.makedirs('Graphics')

    # Generate a timestamped filename for the PDF report
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_file_name = f"Reports/{satellite_name}_report_{start_date}_{end_date}_{current_time}.pdf"

    # Setup the PDF document
    doc = SimpleDocTemplate(pdf_file_name, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Add title and introductory information
    elements.append(Paragraph(f"Report from data {satellite_name}", styles['Title']))
    elements.append(Spacer(1, 12))

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

    # Add DataFrame content to the PDF
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

    # Add the matches table
    matches_table_data = [
        ['ID', 'Satellite Name', 'Satellite Value', 'Satellite Datetime', 'Ground Value', 'Ground Datetime']]
    for idx in range(0, len(matches), 2):
        if idx + 1 < len(matches):
            match_sat = matches[idx]
            match_gnd = matches[idx + 1]
            matches_table_data.append([
                idx // 2 + 1,
                match_sat.get('source', '').split(' - ')[1] if 'source' in match_sat and ' - ' in match_sat[
                    'source'] else 'N/A',
                match_sat.get('value', 'N/A'),
                match_sat.get('datetime', 'N/A'),
                match_gnd.get('value', 'N/A'),
                match_gnd.get('datetime', 'N/A')
            ])

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

    # Calculate RMSE and MBE
    rmse, mbe = calculate_rmse_mbe(matches)
    elements.append(Paragraph(f"RMSE: {rmse}", styles['Normal']))
    elements.append(Paragraph(f"MBE: {mbe}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Create and save the plot only if the satellite is not Landsat
    if satellite_name.lower() != 'landsat':
        fig, ax = plt.subplots(figsize=(10, 6))
        satellite_values = [float(matches[i]['value']) for i in range(0, len(matches), 2)]
        ground_values = [float(matches[i + 1]['value']) for i in range(0, len(matches), 2)]
        dates = [matches[i]['datetime'] for i in range(0, len(matches), 2)]

        ax.plot(dates, satellite_values, label='Satellite', marker='o', linestyle='-', color='red')
        ax.plot(dates, ground_values, label='Ground', marker='o', linestyle='-', color='blue')
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.set_title(f'{satellite_name} vs Ground Values')
        ax.legend()
        ax.grid(True)
        plt.xticks(rotation=45)

        plot_file_name = f"Graphics/{satellite_name}_plot_{current_time}.png"
        plt.savefig(plot_file_name)
        plt.close(fig)

        # Add plot to the PDF
        elements.append(Image(plot_file_name, width=640, height=480))
        elements.append(Spacer(1, 12))

    # Save the PDF report
    doc.build(elements)
    print(f"PDF report saved to {pdf_file_name}")




