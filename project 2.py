import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import streamlit as st

BASE_DIR = Path(r"C:\Users\santh\Documents\Python\data")
VOLATILITY_FILE = BASE_DIR / "stock_volatility_report.csv"
CUMULATIVE_FILE = BASE_DIR / "stock_cumulative_return_report.csv"
YEARLY_FILE = BASE_DIR / "yearly_returns_with_sector.csv"
CORRELATION_FILE = BASE_DIR / "stock_correlation_matrix.csv"
MONTHLY_FILE = BASE_DIR / "monthly_returns_report.csv"

@st.cache_data
def load_volatility():
    return pd.read_csv(VOLATILITY_FILE)

@st.cache_data
def load_cumulative():
    df = pd.read_csv(CUMULATIVE_FILE)
    df["date"] = pd.to_datetime(df["date"])
    return df

@st.cache_data
def load_yearly():
    return pd.read_csv(YEARLY_FILE)

@st.cache_data
def load_correlation():
    corr_df = pd.read_csv(CORRELATION_FILE, index_col=0)
    corr_df = corr_df.apply(pd.to_numeric, errors="coerce")
    corr_df.dropna(axis=0, how="all", inplace=True)
    corr_df.dropna(axis=1, how="all", inplace=True)
    return corr_df

@st.cache_data
def load_monthly():
    df = pd.read_csv(MONTHLY_FILE)
    df['Month'] = pd.to_datetime(df['Month'])
    return df

def plot_volatility():
    volatility_df = load_volatility()
    plot_vol = volatility_df.nlargest(10, "Volatility")
    fig, ax = plt.subplots(figsize=(20, 12))
    ax.bar(plot_vol["Symbol"], plot_vol["Volatility"], color="red")
    ax.set_title("Top 10 Most Volatile Stocks")
    ax.set_xlabel("Stock")
    ax.set_ylabel("Volatility")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    fig.tight_layout()
    st.pyplot(fig)

def plot_cumulative():
    cum_df = load_cumulative()
    top5_symbols = (
        cum_df.groupby("Symbol")["Cumulative_Return"]
              .last()
              .nlargest(5)
              .index
    )
    fig, ax = plt.subplots(figsize=(20, 12))
    for symbol in top5_symbols:
        data = cum_df[cum_df["Symbol"] == symbol]
        ax.plot(data["date"], data["Cumulative_Return"] * 100, label=symbol)
    ax.set_title("Top 5 Stocks – Cumulative Return Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return (%)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)
    fig.tight_layout()
    st.pyplot(fig)

def plot_sector_returns():
    df = load_yearly()
    sector_col = "sector"
    return_col = "YearlyReturn"   
    sector_avg = (
        df.groupby(sector_col)[return_col]
          .mean()
          .sort_values(ascending=False)
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["green" if x > 0 else "red" for x in sector_avg]
    ax.barh(sector_avg.index, sector_avg.values, color=colors)
    ax.set_title("Average Yearly Return by Sector")
    ax.set_xlabel("Return (%)")
    fig.tight_layout()
    st.pyplot(fig)

def plot_correlation():
    corr_df = load_correlation()
    fig, ax = plt.subplots(figsize=(12, 10))
    img = ax.imshow(corr_df.values, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar(img, fraction=0.046, pad=0.04, ax=ax)
    ax.set_xticks(range(len(corr_df.columns)))
    ax.set_xticklabels(corr_df.columns, rotation=90)
    ax.set_yticks(range(len(corr_df.index)))
    ax.set_yticklabels(corr_df.index)
    ax.set_title("Stock Price Correlation Matrix")
    fig.tight_layout()
    st.pyplot(fig)

def plot_monthly_returns():
    monthly_df = load_monthly()
    months = sorted(monthly_df['Month'].unique())[:12]
    fig, axes = plt.subplots(4, 3, figsize=(20, 24))
    axes = axes.flatten()
    
    for i, month in enumerate(months):
        month_data = monthly_df[monthly_df['Month'] == month]
        top = month_data.nlargest(5, 'Returns')
        bottom = month_data.nsmallest(5, 'Returns')
        combined = pd.concat([top, bottom]).sort_values('Returns', ascending=False)
        
        sns.barplot(data=combined, x='Returns', y='Symbol', ax=axes[i])
        
        for bar in axes[i].patches:
            val = bar.get_width()
            bar.set_color('#2ecc71' if val > 0 else '#e74c3c')
        
        axes[i].set_title(month.strftime('%B %Y'), fontweight='bold', fontsize=14)
        axes[i].set_xlabel('Return %')
        axes[i].set_ylabel('')
        axes[i].grid(axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    st.pyplot(fig)

st.title("Stock Analysis Dashboard")

col1, col2 = st.columns(2)
with col1:
    st.header("Top 10 Most Volatile Stocks")
    plot_volatility()
with col2:
    st.header("Top 5 Cumulative Returns")
    plot_cumulative()

st.header(" Sector Performance")
plot_sector_returns()

st.header("Stock Correlation Matrix")
plot_correlation()

st.header(" Monthly Top/Bottom 5 Returns (Last 12 Months)")
plot_monthly_returns()
