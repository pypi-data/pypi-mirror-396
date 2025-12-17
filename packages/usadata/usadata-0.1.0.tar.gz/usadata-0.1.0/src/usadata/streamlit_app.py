from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.express as px
import us
import importlib.resources as resources

from usadata import data


def load_data() -> pd.DataFrame:
    """Load the packaged final dataset."""
    data_path = resources.files(data) / "final_data_set.csv"
    return pd.read_csv(data_path)


def choropleth(final_data_set: pd.DataFrame) -> None:
    df = final_data_set.copy()
    df["States"] = df["States"].str.strip()

    def get_abbr(name):
        if name == "District of Columbia":
            return "DC"
        state = us.states.lookup(name)
        return state.abbr

    df["States"] = df["States"].apply(get_abbr)

    fig = px.choropleth(
        df,
        locations="States",
        locationmode="USA-states",
        color="Avg_PM25",
        scope="usa",
        color_continuous_scale=["green", "yellow", "orange", "red"],
        range_color=[df["Avg_PM25"].min(), df["Avg_PM25"].max()],
        labels={"Avg_PM25": "Avg PM2.5"},
    )

    st.subheader("Average PM2.5 by State")
    st.plotly_chart(fig, use_container_width=True)


def high_and_low(final_data_set: pd.DataFrame) -> None:
    df = final_data_set.copy()

    columns_to_summarize = [
        "Not_graduated",
        "HDI",
        "Health_Index",
        "Education_Index",
        "Income_Index",
        "Homeless_Ratio",
        "Unsheltered_Homeless",
        "Avg_PM25",
    ]

    summary = []

    for col in columns_to_summarize:
        summary.append(
            {
                "Variable": col,
                "Average ± SD": f"{df[col].mean():.2f} ± {df[col].std():.2f}",
                "Highest State": f"{df.loc[df[col].idxmax(), 'States']} ({df[col].max():.2f})",
                "Lowest State": f"{df.loc[df[col].idxmin(), 'States']} ({df[col].min():.2f})",
            }
        )

    st.header("Summary Statistics")
    st.dataframe(pd.DataFrame(summary), use_container_width=True)


def show_correlations(df: pd.DataFrame) -> None:
    st.header("Correlation Matrix")
    corr = df.corr(numeric_only=True)
    st.dataframe(corr.style.format("{:.2f}"))


def main() -> None:
    """Streamlit entry point (matches professor template)."""
    st.set_page_config(page_title="STAT 386 Project", layout="wide")
    st.title("Visualize Our Project")

    df = load_data()

    st.subheader("Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    choropleth(df)
    high_and_low(df)
    show_correlations(df)


if __name__ == "__main__":
    main()
