import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

df = pd.read_csv("country_inventory_global_co2e_100yr.csv")
countries = [
    "AGO","ARG","AUS","AUT","AZE","BHR","BGD","BRB","BEL","BRA","CAN","CHL",
    "CHN","COL","CRI","CYP","CZE","DNK","DOM","EGY","EST","FIN","FRA","DEU",
    "HKG","HUN","IND","IDN","IRL","ISR","ITA","JPN","KAZ","KEN","LVA","LTU",
    "LUX","MYS","MLT","MEX","MAR","NLD","NZL","NGA","NOR","OMN","PAN","PER",
    "PHL","POL","PRT","QAT","KOR","ROU","RUS","SAU","SRB","SGP","SVK","SVN",
    "ZAF","ESP","SWE","CHE","THA","TUR","ARE","GBR","USA","URY","ECU","SLV",
    "GHA","JAM","JOR","KWT","PAK","PRY","LKA","UKR","VNM","HRV","UGA","GRC","BGR"
]

df = df[df["iso3_country"].isin(countries)]

latest_year = df["year"].max()

# ------------------------------------------------------------
# 2. DASH APP
# ------------------------------------------------------------

app = Dash(__name__)
server = app.server
app.layout = html.Div(
    style={"maxWidth": "1200px", "margin": "auto"},
    children=[

        html.H2("Country Emissions Materiality Dashboard"),

        # ------------------------
        # Country dropdown
        # ------------------------
        dcc.Dropdown(
            id="country-dropdown",
            options=[
                {"label": c, "value": c}
                for c in sorted(df["iso3_country"].unique())
            ],
            value="CHN",
            clearable=False,
            style={"width": "300px"}
        ),

        html.Br(),

        # ------------------------
        # Chart 1: Sector shares
        # ------------------------
        dcc.Graph(id="sector-share-bar"),

        # ------------------------
        # Chart 2: Cumulative coverage
        # ------------------------
        dcc.Graph(id="cumulative-coverage"),

        # ------------------------
        # Chart 3: Emissions trends
        # ------------------------
        dcc.Graph(id="emissions-trends")
    ]
)

# ------------------------------------------------------------
# 3. CALLBACK
# ------------------------------------------------------------

@app.callback(
    Output("sector-share-bar", "figure"),
    Output("cumulative-coverage", "figure"),
    Output("emissions-trends", "figure"),
    Input("country-dropdown", "value")
)
def update_dashboard(country):

    # ------------------------
    # Filter data
    # ------------------------
    df_country = df[df["iso3_country"] == country]

    # ------------------------
    # Chart 1: Sector shares (latest year)
    # ------------------------
    df_latest = df_country[df_country["year"] == latest_year]

    sector_totals = (
        df_latest.groupby("sector", as_index=False)
                 .agg(emissions=("emissions", "sum"))
    )

    sector_totals["share"] = (
        sector_totals["emissions"] / sector_totals["emissions"].sum()
    )

    fig1 = px.bar(
        sector_totals.sort_values("share"),
        x="share",
        y="sector",
        orientation="h",
        labels={
            "share": "Share of national emissions",
            "sector": "Sector"
        },
        title=f"{country}: Emissions by Sector ({latest_year})"
    )

    fig1.update_xaxes(tickformat=".0%")

    # ------------------------
    # Chart 2: Cumulative coverage
    # ------------------------
    sector_sorted = sector_totals.sort_values(
        "share", ascending=False
    ).reset_index(drop=True)

    sector_sorted["cumulative_share"] = sector_sorted["share"].cumsum()
    sector_sorted["rank"] = sector_sorted.index + 1

    fig2 = px.line(
        sector_sorted,
        x="rank",
        y="cumulative_share",
        markers=True,
        labels={
            "rank": "Number of sectors (ranked)",
            "cumulative_share": "Cumulative share of emissions"
        },
        title=f"{country}: Cumulative Emissions Coverage"
    )

    fig2.update_yaxes(tickformat=".0%")
    fig2.update_xaxes(dtick=1)

    # ------------------------
    # Chart 3: Emissions trends (top 5 sectors)
    # ------------------------
    top_sectors = sector_sorted.head(5)["sector"].tolist()

    df_trends = df_country[df_country["sector"].isin(top_sectors)]

    trend_totals = (
        df_trends.groupby(["year", "sector"], as_index=False)
                 .agg(emissions=("emissions", "sum"))
    )

    fig3 = px.line(
        trend_totals,
        x="year",
        y="emissions",
        color="sector",
        labels={
            "year": "Year",
            "emissions": "Emissions",
            "sector": "Sector"
        },
        title=f"{country}: Emissions Trends (Top 5 Sectors)"
    )

    return fig1, fig2, fig3

# ------------------------------------------------------------
# 4. RUN APP
# ------------------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True, jupyter_mode='inline')
