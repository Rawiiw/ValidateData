from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import pandas as pd

def create_pdf_report(df, matches):
    pdf_file_name = "Reports/report.pdf"
    doc = SimpleDocTemplate(pdf_file_name, pagesize=letter)
    elements = []

    df_table_data = [list(df.columns)] + df.values.tolist()
    df_table = Table(df_table_data)
    df_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                  ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                  ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                  ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                  ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                  ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                  ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    if len(matches) % 2 == 0:  # Check if matches list has an even number of elements
        matches_table_data = [['ID', 'Satellite name', 'Satellite value', 'Satellite Datetime', 'Ground value', 'Ground Datetime']]
        for idx in range(0, len(matches), 2):
            match = matches[idx]
            if idx + 1 < len(matches):  # Ensure index doesn't exceed list length
                match_next = matches[idx + 1]
                matches_table_data.append([idx // 2 + 1,
                                           match.get('source', '').split(' - ')[1],
                                           match.get('value', ''),
                                           match.get('datetime', ''),
                                           match_next.get('value', ''),
                                           match_next.get('datetime', '')])

        matches_table = Table(matches_table_data)
        matches_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                           ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                           ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                           ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(matches_table)
    else:
        print("Matches list does not have an even number of elements. Cannot create PDF report.")

    doc.build(elements)
    print(f"PDF отчет сохранен в {pdf_file_name}")
