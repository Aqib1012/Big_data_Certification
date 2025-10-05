# utils.py
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

def load_data(path):
    df = pd.read_csv(path)
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    # Parse date
    if 'date' in df.columns:
        try:
            df['date'] = pd.to_datetime(df['date'])
        except Exception:
            # try dayfirst
            df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    # Ensure numeric columns exist
    if 'win_by_runs' in df.columns:
        df['win_by_runs'] = pd.to_numeric(df['win_by_runs'], errors='coerce')
    if 'win_by_wickets' in df.columns:
        df['win_by_wickets'] = pd.to_numeric(df['win_by_wickets'], errors='coerce')
    return df

def filter_data(df, date_from=None, date_to=None, seasons=None, team=None, venue=None):
    out = df.copy()
    if date_from is not None:
        out = out[out['date'] >= pd.to_datetime(date_from)]
    if date_to is not None:
        out = out[out['date'] <= pd.to_datetime(date_to)]
    if seasons:
        out = out[out['season'].isin(seasons)]
    if team:
        out = out[(out.get('team1') == team) | (out.get('team2') == team)]
    if venue:
        out = out[out['venue'] == venue]
    return out

def make_matches_per_year_fig(df):
    fig, ax = plt.subplots()
    if 'date' in df.columns and df['date'].notna().any():
        by_year = df.groupby(df['date'].dt.year).size()
        ax.plot(by_year.index, by_year.values, marker='o')
        ax.set_title('Matches per Year')
        ax.set_xlabel('Year')
        ax.set_ylabel('Matches')
    else:
        ax.text(0.5, 0.5, 'No date data available', ha='center', va='center')
        ax.set_axis_off()
    fig.tight_layout()
    return fig

def make_total_runs_hist_fig(df):
    # Dataset may not contain innings totals; we use win_by_runs as a proxy for runs differences.
    fig, ax = plt.subplots()
    if 'win_by_runs' in df.columns and df['win_by_runs'].dropna().shape[0] > 0:
        ax.hist(df['win_by_runs'].dropna(), bins=20)
        ax.set_title('Distribution of Win-by-Runs (proxy for runs)')
        ax.set_xlabel('Runs')
        ax.set_ylabel('Count')
    else:
        ax.text(0.5, 0.5, 'No runs-related numeric data available', ha='center', va='center')
        ax.set_axis_off()
    fig.tight_layout()
    return fig

def fig_to_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf
