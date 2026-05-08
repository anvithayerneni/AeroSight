"""
AeroSight Professional Excel & CSV Business Report Generator
Uses openpyxl to generate styled executive workbooks with formulas, KPI cards, and embedded charts.
"""

import os

import openpyxl
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from warehouse.db import get_db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "reports", "output")

# Style Palette
NAVY_HEADER = "1B365D"
SKY_ACCENT = "0072CE"
LIGHT_GRAY = "F4F6F9"
BORDER_GRAY = "D1D5DB"
WHITE = "FFFFFF"

def style_header_cell(cell, text, fill_hex=NAVY_HEADER):
    cell.value = text
    cell.font = Font(name="Calibri", size=11, bold=True, color=WHITE)
    cell.fill = PatternFill(start_color=fill_hex, end_color=fill_hex, fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

def style_kpi_card(ws, start_row, start_col, title, value, unit=""):
    # Title
    t_cell = ws.cell(row=start_row, column=start_col, value=title)
    t_cell.font = Font(name="Calibri", size=9, bold=True, color="555555")
    t_cell.fill = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")
    t_cell.alignment = Alignment(horizontal="center")
    
    # Value
    v_cell = ws.cell(row=start_row + 1, column=start_col, value=f"{value} {unit}".strip())
    v_cell.font = Font(name="Calibri", size=16, bold=True, color=SKY_ACCENT)
    v_cell.fill = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")
    v_cell.alignment = Alignment(horizontal="center", vertical="center")

def autofit_columns(ws):
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

class ReportGenerator:
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.db = get_db()

    def generate_monthly_operations_report(self) -> str:
        """Generates the Monthly Network Operations & Punctuality Executive Report."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Monthly Operations"

        # Title Banner
        ws.merge_cells("A1:G1")
        title_cell = ws["A1"]
        title_cell.value = "AEROSIGHT AIRLINE OPERATIONS — MONTHLY EXECUTIVE REPORT"
        title_cell.font = Font(name="Calibri", size=14, bold=True, color=WHITE)
        title_cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 35

        # Query Monthly Summary
        query = """
        SELECT 
            d.year,
            d.month,
            d.month_name,
            COUNT(f.flight_id) AS total_flights,
            SUM(CASE WHEN f.cancelled = 0 THEN 1 ELSE 0 END) AS operated_flights,
            SUM(f.cancelled) AS cancelled_flights,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 2) AS avg_dep_delay,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.arr_delay END), 2) AS avg_arr_delay,
            ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS on_time_arrival_pct
        FROM fact_flights f
        LEFT JOIN dim_date d ON f.date_key = d.date_key
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month;
        """
        df = self.db.query_df(query)

        # Overall Totals for KPI Cards
        total_flt = int(df["total_flights"].sum())
        avg_arr = round(float(df["avg_arr_delay"].mean()), 1)
        avg_otp = round(float(df["on_time_arrival_pct"].mean()), 1)
        
        style_kpi_card(ws, 3, 2, "TOTAL FLIGHTS", f"{total_flt:,}")
        style_kpi_card(ws, 3, 4, "SYSTEM AVG DELAY", f"{avg_arr}", "min")
        style_kpi_card(ws, 3, 6, "ON-TIME ARRIVAL (OTP-15)", f"{avg_otp}", "%")
        ws.row_dimensions[3].height = 18
        ws.row_dimensions[4].height = 28

        # Data Table Headers
        headers = ["Year", "Month", "Total Flights", "Operated", "Cancelled", "Avg Dep Delay (min)", "Avg Arr Delay (min)", "OTP-15 (%)"]
        start_row = 7
        for col_idx, h in enumerate(headers, start=1):
            style_header_cell(ws.cell(row=start_row, column=col_idx), h)
        ws.row_dimensions[start_row].height = 24

        # Populate Rows
        thin_border = Border(
            left=Side(style='thin', color=BORDER_GRAY),
            right=Side(style='thin', color=BORDER_GRAY),
            top=Side(style='thin', color=BORDER_GRAY),
            bottom=Side(style='thin', color=BORDER_GRAY)
        )

        for r_idx, row in df.iterrows():
            curr_row = start_row + 1 + r_idx
            ws.cell(row=curr_row, column=1, value=int(row["year"]))
            ws.cell(row=curr_row, column=2, value=str(row["month_name"]))
            ws.cell(row=curr_row, column=3, value=int(row["total_flights"]))
            ws.cell(row=curr_row, column=4, value=int(row["operated_flights"]))
            ws.cell(row=curr_row, column=5, value=int(row["cancelled_flights"]))
            ws.cell(row=curr_row, column=6, value=float(row["avg_dep_delay"]))
            ws.cell(row=curr_row, column=7, value=float(row["avg_arr_delay"]))
            ws.cell(row=curr_row, column=8, value=float(row["on_time_arrival_pct"]))
            
            for c in range(1, 9):
                cell = ws.cell(row=curr_row, column=c)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="right" if c >= 3 else "center")

        # Summary Formula Row
        sum_row = start_row + len(df) + 1
        ws.cell(row=sum_row, column=2, value="Total / Average:").font = Font(bold=True)
        ws.cell(row=sum_row, column=3, value=f"=SUM(C{start_row+1}:C{sum_row-1})").font = Font(bold=True)
        ws.cell(row=sum_row, column=4, value=f"=SUM(D{start_row+1}:D{sum_row-1})").font = Font(bold=True)
        ws.cell(row=sum_row, column=5, value=f"=SUM(E{start_row+1}:E{sum_row-1})").font = Font(bold=True)
        ws.cell(row=sum_row, column=7, value=f"=AVERAGE(G{start_row+1}:G{sum_row-1})").font = Font(bold=True)
        ws.cell(row=sum_row, column=8, value=f"=AVERAGE(H{start_row+1}:H{sum_row-1})").font = Font(bold=True)

        autofit_columns(ws)

        out_path = os.path.join(self.output_dir, "monthly_operations_report.xlsx")
        wb.save(out_path)
        df.to_csv(os.path.join(self.output_dir, "monthly_operations_report.csv"), index=False)
        print(f"✅ Generated {out_path}")
        return out_path

    def generate_airport_performance_report(self) -> str:
        """Generates the Airport Congestion & Hub Performance Report with charts."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Airport Performance"

        # Title
        ws.merge_cells("A1:H1")
        title_cell = ws["A1"]
        title_cell.value = "AEROSIGHT — AIRPORT CONGESTION & PUNCTUALITY AUDIT REPORT"
        title_cell.font = Font(name="Calibri", size=14, bold=True, color=WHITE)
        title_cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 35

        query = """
        SELECT 
            f.origin_airport_key AS iata,
            ap.name AS airport_name,
            ap.city,
            ap.state,
            ap.hub,
            COUNT(f.flight_id) AS departures,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.taxi_out END), 1) AS avg_taxi_out_min,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 1) AS avg_dep_delay_min,
            ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.dep_delay >= 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS delayed_dep_pct,
            ROUND((SUM(f.cancelled)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS cancellation_rate_pct
        FROM fact_flights f
        LEFT JOIN dim_airport ap ON f.origin_airport_key = ap.iata
        GROUP BY f.origin_airport_key, ap.name, ap.city, ap.state, ap.hub
        ORDER BY departures DESC;
        """
        df = self.db.query_df(query)

        headers = ["IATA", "Airport Name", "City", "State", "Hub Tier", "Departures", "Avg Taxi Out (min)", "Avg Dep Delay (min)", "Delayed Flights (%)", "Cancellation (%)"]
        start_row = 3
        for col_idx, h in enumerate(headers, start=1):
            style_header_cell(ws.cell(row=start_row, column=col_idx), h)
        ws.row_dimensions[start_row].height = 24

        thin_border = Border(
            left=Side(style='thin', color=BORDER_GRAY), right=Side(style='thin', color=BORDER_GRAY),
            top=Side(style='thin', color=BORDER_GRAY), bottom=Side(style='thin', color=BORDER_GRAY)
        )

        for r_idx, row in df.iterrows():
            curr_row = start_row + 1 + r_idx
            ws.cell(row=curr_row, column=1, value=str(row["iata"]))
            ws.cell(row=curr_row, column=2, value=str(row["airport_name"]))
            ws.cell(row=curr_row, column=3, value=str(row["city"]))
            ws.cell(row=curr_row, column=4, value=str(row["state"]))
            ws.cell(row=curr_row, column=5, value=str(row["hub"]))
            ws.cell(row=curr_row, column=6, value=int(row["departures"]))
            ws.cell(row=curr_row, column=7, value=float(row["avg_taxi_out_min"]))
            ws.cell(row=curr_row, column=8, value=float(row["avg_dep_delay_min"]))
            ws.cell(row=curr_row, column=9, value=float(row["delayed_dep_pct"]))
            ws.cell(row=curr_row, column=10, value=float(row["cancellation_rate_pct"]))
            
            for c in range(1, 11):
                cell = ws.cell(row=curr_row, column=c)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="right" if c >= 6 else "left")

        # Embed Bar Chart for Top 10 Airport Traffic
        chart = BarChart()
        chart.type = "col"
        chart.style = 10
        chart.title = "Top Hub Airport Flight Volume"
        chart.y_axis.title = "Departures"
        chart.x_axis.title = "Airport"

        data_ref = Reference(ws, min_col=6, min_row=start_row, max_row=start_row + 10)
        cats_ref = Reference(ws, min_col=1, min_row=start_row + 1, max_row=start_row + 10)
        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats_ref)
        chart.width = 16
        chart.height = 10
        ws.add_chart(chart, f"L{start_row}")

        autofit_columns(ws)

        out_path = os.path.join(self.output_dir, "airport_performance_report.xlsx")
        wb.save(out_path)
        df.to_csv(os.path.join(self.output_dir, "airport_performance_report.csv"), index=False)
        print(f"✅ Generated {out_path}")
        return out_path

    def generate_airline_performance_report(self) -> str:
        """Generates the Carrier Reliability & Delay Root Cause Report."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Airline Reliability"

        # Title
        ws.merge_cells("A1:I1")
        title_cell = ws["A1"]
        title_cell.value = "AEROSIGHT — AIRLINE CARRIER RELIABILITY & ON-TIME RANKINGS"
        title_cell.font = Font(name="Calibri", size=14, bold=True, color=WHITE)
        title_cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 35

        query = """
        SELECT 
            f.carrier_key AS carrier_code,
            a.airline_name,
            a.fleet_size,
            a.primary_hub,
            COUNT(f.flight_id) AS total_flights,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.dep_delay END), 2) AS avg_dep_delay,
            ROUND(AVG(CASE WHEN f.cancelled = 0 THEN f.arr_delay END), 2) AS avg_arr_delay,
            ROUND((SUM(CASE WHEN f.cancelled = 0 AND f.arr_delay < 15 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS otp15_pct,
            ROUND((SUM(CASE WHEN f.cancelled = 0 THEN 1 ELSE 0 END)::DOUBLE / COUNT(f.flight_id)) * 100, 2) AS completion_rate_pct
        FROM fact_flights f
        LEFT JOIN dim_airline a ON f.carrier_key = a.carrier_code
        GROUP BY f.carrier_key, a.airline_name, a.fleet_size, a.primary_hub
        ORDER BY total_flights DESC;
        """
        df = self.db.query_df(query)

        headers = ["Carrier Code", "Airline Name", "Fleet Size", "Primary Hub", "Total Flights", "Avg Dep Delay (min)", "Avg Arr Delay (min)", "OTP-15 (%)", "Completion Rate (%)"]
        start_row = 3
        for col_idx, h in enumerate(headers, start=1):
            style_header_cell(ws.cell(row=start_row, column=col_idx), h)
        ws.row_dimensions[start_row].height = 24

        thin_border = Border(
            left=Side(style='thin', color=BORDER_GRAY), right=Side(style='thin', color=BORDER_GRAY),
            top=Side(style='thin', color=BORDER_GRAY), bottom=Side(style='thin', color=BORDER_GRAY)
        )

        for r_idx, row in df.iterrows():
            curr_row = start_row + 1 + r_idx
            ws.cell(row=curr_row, column=1, value=str(row["carrier_code"]))
            ws.cell(row=curr_row, column=2, value=str(row["airline_name"]))
            ws.cell(row=curr_row, column=3, value=int(row["fleet_size"]))
            ws.cell(row=curr_row, column=4, value=str(row["primary_hub"]))
            ws.cell(row=curr_row, column=5, value=int(row["total_flights"]))
            ws.cell(row=curr_row, column=6, value=float(row["avg_dep_delay"]))
            ws.cell(row=curr_row, column=7, value=float(row["avg_arr_delay"]))
            ws.cell(row=curr_row, column=8, value=float(row["otp15_pct"]))
            ws.cell(row=curr_row, column=9, value=float(row["completion_rate_pct"]))
            
            for c in range(1, 10):
                cell = ws.cell(row=curr_row, column=c)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="right" if c in [3, 5, 6, 7, 8, 9] else "center")

        autofit_columns(ws)

        out_path = os.path.join(self.output_dir, "airline_performance_report.xlsx")
        wb.save(out_path)
        df.to_csv(os.path.join(self.output_dir, "airline_performance_report.csv"), index=False)
        print(f"✅ Generated {out_path}")
        return out_path

    def generate_all_reports(self):
        self.generate_monthly_operations_report()
        self.generate_airport_performance_report()
        self.generate_airline_performance_report()

if __name__ == "__main__":
    gen = ReportGenerator()
    gen.generate_all_reports()
