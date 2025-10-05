# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from fpdf import FPDF
from utils import load_data, filter_data, make_matches_per_year_fig, make_total_runs_hist_fig, fig_to_bytes

st.set_page_config(page_title="ODI Matches PDF Report", layout="wide")

def create_summary(df):
    total_matches = len(df)
    winners = df['winner'].dropna()
    top_team = winners.value_counts().idxmax() if len(winners)>0 else "N/A"
    most_player_of_match = df['player_of_match'].dropna()
    top_player = most_player_of_match.value_counts().idxmax() if len(most_player_of_match)>0 else "N/A"
    avg_win_by_runs = int(df['win_by_runs'].dropna().mean()) if df['win_by_runs'].dropna().shape[0] > 0 else 0
    avg_win_by_wickets = float(df['win_by_wickets'].dropna().mean()) if df['win_by_wickets'].dropna().shape[0] > 0 else 0.0

    return {
        "Total matches": total_matches,
        "Top winning team": top_team,
        "Top player (Player of match)": top_player,
        "Average win by runs": avg_win_by_runs,
        "Average win by wickets": round(avg_win_by_wickets, 2)
    }

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'ODI Matches Report', ln=True, align='C')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def build_pdf(title, filters_text, summary_dict, fig_bytes_list):
    pdf = PDFReport()
    # Title page
    pdf.add_page()
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 20, title, ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(4)
    pdf.cell(0, 8, f'Report Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
    pdf.ln(4)
    pdf.multi_cell(0, 8, f'Filters applied: {filters_text}')
    pdf.ln(6)

    # Summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, 'Summary', ln=True)
    pdf.ln(2)
    pdf.set_font('Arial', '', 12)
    for k, v in summary_dict.items():
        pdf.cell(0, 8, f'{k}: {v}', ln=True)
    pdf.ln(4)

    # Figures (each on its own page)
    for b in fig_bytes_list:
        pdf.add_page()
        # Put image centered and sized to width 180
        # FPDF accepts a filename or bytes buffer. We'll write bytes to a BytesIO and pass its name via temporary save.
        # However FPDF's image method can accept a file-like if pillow is available; to be safe, we'll write to temp file.
        try:
            # try to use in-memory (works with pillow-backed FPDF)
            pdf.image(b, x=15, y=30, w=180)
        except Exception:
            # fallback: write to temp file
            import tempfile
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.write(b.getbuffer() if hasattr(b, "getbuffer") else b)
            tmp.flush()
            tmp.close()
            pdf.image(tmp.name, x=15, y=30, w=180)

    out = BytesIO()
    pdf.output(out)
    out.seek(0)
    return out

def main():
    st.title("ODI Matches — PDF Report Generator")

    # Load data
    df = load_data('ODI_Match_info.csv')

    # Sidebar filters
    st.sidebar.header("Filters")
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input("Date range", [min_date, max_date])

    seasons = sorted(df['season'].dropna().unique().tolist())
    selected_seasons = st.sidebar.multiselect("Season(s)", options=seasons, default=seasons)

    teams = sorted(set(df['team1'].dropna().unique().tolist() + df['team2'].dropna().unique().tolist()))
    selected_team = st.sidebar.selectbox("Team (any side)", options=["All"] + teams)

    venue_list = sorted(df['venue'].dropna().unique().tolist()) if 'venue' in df.columns else []
    selected_venue = st.sidebar.selectbox("Venue", options=["All"] + venue_list)

    # Apply filters
    filtered = filter_data(df,
                           date_from=pd.to_datetime(date_range[0]),
                           date_to=pd.to_datetime(date_range[1]),
                           seasons=selected_seasons,
                           team=selected_team if selected_team!="All" else None,
                           venue=selected_venue if selected_venue!="All" else None)

    st.subheader("Filtered Matches")
    st.write(f"Showing **{len(filtered)}** matches")
    st.dataframe(filtered[['date','team1','team2','winner','venue','player_of_match']].sort_values('date', ascending=False).reset_index(drop=True).head(200))

    # KPIs
    st.subheader("Key metrics")
    summary = create_summary(filtered)
    cols = st.columns(5)
    for i,(k,v) in enumerate(summary.items()):
        cols[i].metric(k, v)

    # Charts
    st.subheader("Charts")
    col1, col2 = st.columns(2)
    fig1 = make_matches_per_year_fig(filtered)
    col1.pyplot(fig1)
    fig2 = make_total_runs_hist_fig(filtered)  # depends on win_by_runs as a proxy for runs in dataset; if not available, will show message
    col2.pyplot(fig2)

    # Generate PDF
    st.markdown("---")
    st.subheader("Generate PDF Report")
    report_title = st.text_input("Report title", value="ODI Matches Report")
    filters_text = f"Date: {date_range[0]} to {date_range[1]}; Seasons: {', '.join(map(str, selected_seasons))}; Team: {selected_team}; Venue: {selected_venue}"

    if st.button("Generate & Download PDF"):
        # Convert figs to bytes
        figs_bytes = [fig_to_bytes(fig1), fig_to_bytes(fig2)]
        pdf_file = build_pdf(report_title, filters_text, summary, figs_bytes)
        st.download_button("Download PDF", data=pdf_file, file_name="odi_matches_report.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
