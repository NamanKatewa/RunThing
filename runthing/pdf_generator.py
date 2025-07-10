from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import datetime # Added import

from .database import connect_db, get_monthly_summary
from .stats import get_total_distance, get_total_time, get_average_pace, get_best_efforts
from .utils import convert_to_display_date

def generate_run_report_pdf(filename="run_report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("RunThing - Running Report", styles['h1']))
    story.append(Spacer(1, 0.2 * 100))

    # Overall Statistics
    story.append(Paragraph("Overall Statistics", styles['h2']))
    total_distance = get_total_distance()
    total_time_seconds = get_total_time()
    average_pace = get_average_pace()

    if total_distance == 0:
        story.append(Paragraph("No runs logged yet to generate statistics.", styles['Normal']))
    else:
        hours = total_time_seconds // 3600
        minutes = (total_time_seconds % 3600) // 60
        seconds = total_time_seconds % 60
        total_time_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

        stats_data = [
            ["Metric", "Value"],
            ["Total Distance", f"{total_distance:.2f} km"],
            ["Total Time", total_time_str],
            ["Average Pace", f"{average_pace:.2f} min/km"],
        ]
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(stats_table)

    story.append(Spacer(1, 0.4 * 100))

    # Monthly Summary
    story.append(Paragraph("Monthly Summary", styles['h2']))
    monthly_summary = get_monthly_summary()
    if not monthly_summary:
        story.append(Paragraph("No monthly data available.", styles['Normal']))
    else:
        monthly_data = [["Month", "Total Distance (km)", "Total Time"]]
        for month_data in monthly_summary:
            month_name = datetime.datetime.strptime(month_data['month'], '%Y-%m').strftime('%B %Y')
            month_total_time_seconds = month_data['total_time']
            month_hours = month_total_time_seconds // 3600
            month_minutes = (month_total_time_seconds % 3600) // 60
            month_seconds = month_total_time_seconds % 60
            month_time_str = f"{month_hours:02d}h {month_minutes:02d}m {month_seconds:02d}s"
            monthly_data.append([
                month_name,
                f"{month_data['total_distance']:.2f}",
                month_time_str
            ])
        monthly_table = Table(monthly_data)
        monthly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(monthly_table)

    story.append(Spacer(1, 0.4 * 100))

    # Best Efforts
    story.append(Paragraph("Best Efforts (Fastest Pace)", styles['h2']))
    best_efforts = get_best_efforts()
    if not best_efforts:
        story.append(Paragraph("No best efforts recorded yet.", styles['Normal']))
    else:
        best_effort_data = [["Distance (km)", "Time", "Pace (min/km)", "Date"]]
        for distance, run in best_efforts.items():
            total_seconds = run['time']
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            if hours > 0:
                time_str = f"{hours:02d}:" + time_str
            best_effort_data.append([
                f"{distance:.1f}",
                time_str,
                f"{run['pace']:.2f}",
                convert_to_display_date(run['date'])
            ])
        best_effort_table = Table(best_effort_data)
        best_effort_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(best_effort_table)

    story.append(Spacer(1, 0.4 * 100))

    # All Runs
    story.append(Paragraph("All Logged Runs", styles['h2']))
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, distance, time, pace, notes FROM runs ORDER BY date DESC")
    runs = cursor.fetchall()
    conn.close()

    if not runs:
        story.append(Paragraph("No runs logged yet.", styles['Normal']))
    else:
        run_data = [["Date", "Distance (km)", "Time", "Pace (min/km)", "Notes"]]
        for run in runs:
            total_seconds = run['time']
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            if hours > 0:
                time_str = f"{hours:02d}:" + time_str
            
            run_data.append([
                convert_to_display_date(run['date']),
                f"{run['distance']:.2f}",
                time_str,
                f"{run['pace']:.2f}",
                run['notes'] if run['notes'] else ""
            ])
        
        run_table = Table(run_data)
        run_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(run_table)

    doc.build(story)
    return filename