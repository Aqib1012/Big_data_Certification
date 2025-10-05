# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from fpdf import FPDF
from utils import load_data, filter_data, make_matches_per_year_fig, make_total_runs_hist_fig, fig_to_bytes
import os
from groq import Groq

# Streamlit page setup
st.set_page_config(page_title="ODI Matches PDF Report", layout="wide")

# --------------------------- #
# Summary Helper Function
# --------------------------- #
def create_summary(df):
    total_matches = len(df)
    winners = df['winner'].dropna()
    top_team = winners.value_counts().idxmax() if len(winners) > 0 else "N/A"
    most_player_of_match = df['player_of_match'].dropna()
    top_player = most_player_of_match.value_counts().idxmax() if len(most_player_of_match) > 0 else "N/A"
    avg_win_by_runs = int(df['win_by_runs'].dropna().mean()) if df['win_by_runs'].dropna().shape[0] > 0 else 0
    avg_win_by_wickets = float(df['win_by_wickets'].dropna().mean()) if df['win_by_wickets'].dropna().shape[0] > 0 else 0.0

    return {
        "Total matches": total_matches,
        "Top winning team": top_team,
        "Top player (Player of match)": top_player,
        "Average win by runs": avg_win_by_runs,
        "Average win by wickets": round(avg_win_by_wickets, 2)
    }

# --------------------------- #
# PDF Report Class
# --------------------------- #
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'ODI Matches Report', ln=True, align='C')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --------------------------- #
# PDF Builder Function (fixed for BytesIO)
# --------------------------- #
def build_pdf(title, filters_text, summary_dict, fig_bytes_list):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 20, title, ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(4)
    pdf.cell(0, 8, f'Report Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
    pdf.ln(4)
    pdf.multi_cell(0, 8, f'Filters applied: {filters_text}')
    pdf.ln(6)

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, 'Summary', ln=True)
    pdf.ln(2)
    pdf.set_font('Arial', '', 12)
    if isinstance(summary_dict, dict):
        for k, v in summary_dict.items():
            pdf.cell(0, 8, f'{k}: {v}', ln=True)
    else:
        pdf.multi_cell(0, 8, summary_dict)  # if it's AI text summary
    pdf.ln(4)

    # Add charts
    for b in fig_bytes_list:
        pdf.add_page()
        try:
            pdf.image(b, x=15, y=30, w=180)
        except Exception:
            import tempfile
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.write(b.getbuffer() if hasattr(b, "getbuffer") else b)
            tmp.flush()
            tmp.close()
            pdf.image(tmp.name, x=15, y=30, w=180)

    # Output PDF as BytesIO for Streamlit
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)

# --------------------------- #
# Main Streamlit App
# --------------------------- #
def main():
    st.title("🏏 ODI Matches — PDF Report Generator")

    # Load dataset
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
    filtered = filter_data(
        df,
        date_from=pd.to_datetime(date_range[0]),
        date_to=pd.to_datetime(date_range[1]),
        seasons=selected_seasons,
        team=selected_team if selected_team != "All" else None,
        venue=selected_venue if selected_venue != "All" else None
    )

    st.subheader("Filtered Matches")
    st.write(f"Showing **{len(filtered)}** matches")
    st.dataframe(filtered[['date', 'team1', 'team2', 'winner', 'venue', 'player_of_match']].sort_values('date', ascending=False).reset_index(drop=True).head(200))

    # KPIs
    st.subheader("Key metrics")
    summary = create_summary(filtered)
    cols = st.columns(5)
    for i, (k, v) in enumerate(summary.items()):
        cols[i].metric(k, v)

    # Charts
    st.subheader("Charts")
    col1, col2 = st.columns(2)
    fig1 = make_matches_per_year_fig(filtered)
    col1.pyplot(fig1)
    fig2 = make_total_runs_hist_fig(filtered)
    col2.pyplot(fig2)

    # --------------------------- #
    # Generate PDF from filtered data
    # --------------------------- #
    st.markdown("---")
    st.subheader("Generate PDF Report from Filters")
    report_title = st.text_input("Report title", value="ODI Matches Report")
    filters_text = f"Date: {date_range[0]} to {date_range[1]}; Seasons: {', '.join(map(str, selected_seasons))}; Team: {selected_team}; Venue: {selected_venue}"

    if st.button("Generate & Download PDF"):
        figs_bytes = [fig_to_bytes(fig1), fig_to_bytes(fig2)]
        pdf_file = build_pdf(report_title, filters_text, summary, figs_bytes)
        st.download_button("📄 Download PDF", data=pdf_file, file_name="odi_matches_report.pdf", mime="application/pdf")

    # --------------------------- #
    # Groq AI Assistant for Team/Year PDF
    # --------------------------- #
    st.markdown("---")
    st.subheader("🤖 AI Team/Year PDF Generator")
    team_input = st.text_input("Enter Team (for AI summary)", key="team_input")
    year_input = st.text_input("Enter Year (for AI summary)", key="year_input")

    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        client = Groq(api_key=groq_api_key)
    else:
        st.warning("⚠️ Groq API key not found.")
        return

    if st.button("Generate AI Team/Year PDF"):
        if not team_input or not year_input:
            st.warning("Please enter both Team and Year.")
        else:
            df['date'] = pd.to_datetime(df['date'])
            filtered_ai = df[
                ((df['team1'] == team_input) | (df['team2'] == team_input)) &
                (df['date'].dt.year == int(year_input))
            ]

            if filtered_ai.empty:
                st.warning("No matches found for this team/year.")
            else:
                # Charts
                fig1_ai = make_matches_per_year_fig(filtered_ai)
                fig2_ai = make_total_runs_hist_fig(filtered_ai)
                figs_bytes_ai = [fig_to_bytes(fig1_ai), fig_to_bytes(fig2_ai)]

                # Ask AI for summary
                with st.spinner("Generating AI summary..."):
                    prompt = f"Summarize ODI matches for {team_input} in {year_input} with top players, winners, and scores."
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a cricket analyst."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    summary_text = response.choices[0].message.content

                # Build PDF
                filters_text_ai = f"Team: {team_input}; Year: {year_input}"
                pdf_file_ai = build_pdf(f"{team_input} ODI Stats {year_input}", filters_text_ai, summary_text, figs_bytes_ai)

                st.success("AI PDF Generated ✅")
                st.download_button("📄 Download AI PDF", data=pdf_file_ai, file_name=f"{team_input}_ODI_{year_input}_report.pdf", mime="application/pdf")
                st.subheader("AI Summary")
                st.write(summary_text)

    # --------------------------- #
    # Groq AI Assistant for Q&A
    # --------------------------- #
    st.markdown("---")
    st.subheader("🤖 Ask AI about ODI Matches")
    user_question = st.text_input("Ask any question about ODI matches or this dataset:", key="qna_input")

    if groq_api_key:
        client = Groq(api_key=groq_api_key)
        if st.button("Ask AI Question"):
            if user_question.strip():
                with st.spinner("Thinking..."):
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a cricket data analyst. Answer based on ODI cricket facts."},
                            {"role": "user", "content": user_question}
                        ]
                    )
                    answer = response.choices[0].message.content
                    st.success("**AI Answer:**")
                    st.write(answer)
            else:
                st.warning("Please enter a question.")

if __name__ == "__main__":
    main()
