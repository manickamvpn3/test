import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# ------------------------------------------------------------
# 1. LOAD + FILTER DATA
# ------------------------------------------------------------
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
serever = app.server
app.layout = html.Div(
    style={"maxWidth": "1200px", "margin": "auto"},
    children=[

        html.H2("Country Emissions Dashboard"),

        dcc.Dropdown(
            id="country-dropdown",
            options=[
                {"label": c, "value": c}
                for c in sorted(df["iso3_country"].unique())
            ],
            value="CHN",
            clearable=False,
            style={"width": "300px", "marginBottom": "20px"}
        ),

        # ----------------------------------------------------
        # TOP ROW: TWO CHARTS SIDE BY SIDE
        # ----------------------------------------------------
        html.Div(
            style={"display": "flex", "gap": "20px"},
            children=[

                html.Div(
                    style={"flex": "1"},
                    children=[dcc.Graph(id="sector-share-bar")]
                ),

                html.Div(
                    style={"flex": "1"},
                    children=[dcc.Graph(id="emissions-trends-absolute")]
                ),
            ]
        ),

        # ----------------------------------------------------
        # BOTTOM ROW: FULL-WIDTH CHART
        # ----------------------------------------------------
        html.Div(
            style={"marginTop": "20px"},
            children=[dcc.Graph(id="emissions-structure-ordered")]
        )
    ]
)

# ------------------------------------------------------------
# 3. CALLBACK
# ------------------------------------------------------------

@app.callback(
    Output("sector-share-bar", "figure"),
    Output("emissions-trends-absolute", "figure"),
    Output("emissions-structure-ordered", "figure"),
    Input("country-dropdown", "value")
)
def update_dashboard(country):

    df_country = df[df["iso3_country"] == country]

    # ------------------------
    # Chart 1: Sector share bar
    # ------------------------
    df_latest = df_country[df_country["year"] == latest_year]

    sector_latest = (
        df_latest.groupby("sector", as_index=False)
                 .agg(emissions=("emissions", "sum"))
    )

    sector_latest["share"] = (
        sector_latest["emissions"] / sector_latest["emissions"].sum()
    )

    sector_latest = sector_latest.sort_values("share")

    fig1 = px.bar(
        sector_latest,
        x="share",
        y="sector",
        orientation="h",
        title=f"{country}: Emissions by Sector ({latest_year})",
        labels={"share": "Share of national emissions", "sector": "Sector"}
    )

    fig1.update_xaxes(tickformat=".0%")

    # ------------------------
    # Top sectors
    # ------------------------
    top_sectors = (
        sector_latest.sort_values("share", ascending=False)
                     .head(5)["sector"]
                     .tolist()
    )

    df_top = df_country[df_country["sector"].isin(top_sectors)]

    yearly_totals = (
        df_top.groupby(["year", "sector"], as_index=False)
              .agg(emissions=("emissions", "sum"))
    )

    # ------------------------
    # Chart 2: Absolute trends
    # ------------------------
    fig2 = px.line(
        yearly_totals,
        x="year",
        y="emissions",
        color="sector",
        title=f"{country}: Emissions Trends (Top 5 Sectors)",
        labels={"emissions": "Emissions", "year": "Year", "sector": "Sector"}
    )

    # ------------------------
    # Chart 3: Structure (ordered)
    # ------------------------
    yearly_totals["year_total"] = (
        yearly_totals.groupby("year")["emissions"].transform("sum")
    )

    yearly_totals["share"] = (
        yearly_totals["emissions"] / yearly_totals["year_total"]
    )

    sector_order = (
        sector_latest.sort_values("share", ascending=False)["sector"]
                     .tolist()
    )

    fig3 = px.area(
        yearly_totals,
        x="year",
        y="share",
        color="sector",
        groupnorm="fraction",
        category_orders={"sector": sector_order},
        title=f"{country}: Emissions Structure Over Time (Top 5 Sectors)",
        labels={"share": "Share of emissions", "year": "Year", "sector": "Sector"}
    )

    fig3.update_yaxes(tickformat=".0%")

    return fig1, fig2, fig3

# ------------------------------------------------------------
# 4. RUN APP
# ------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
