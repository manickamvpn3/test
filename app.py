import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table

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

# Load country info dataset
df_country_info = pd.read_csv("updated_IEA.csv")

# Load government fiscal measures dataset
df_fiscal = pd.read_csv("merged.csv")

# ------------------------------------------------------------
# 2. DASH APP
# ------------------------------------------------------------

app = Dash(__name__)
server = app.server
app.layout = html.Div(
    style={
        "maxWidth": "1400px",
        "margin": "20px auto",
        "padding": "0 20px",
        "fontFamily": "Arial, sans-serif"
    },
    children=[

        html.H2(
            "Country Emissions Dashboard",
            style={"marginBottom": "10px", "color": "#2c3e50"}
        ),

        dcc.Dropdown(
            id="country-dropdown",
            options=[
                {"label": c, "value": c}
                for c in sorted(df["iso3_country"].unique())
            ],
            value="CHN",
            clearable=False,
            style={"width": "300px", "marginBottom": "15px"}
        ),

        # ----------------------------------------------------
        # TOP ROW: COUNTRY INFO (RIGHT) + SECTOR CHART (LEFT)
        # ----------------------------------------------------
        html.Div(
            style={"display": "flex", "gap": "15px", "marginBottom": "15px"},
            children=[
                # LEFT: Sector share bar
                html.Div(
                    style={"flex": "1"},
                    children=[dcc.Graph(id="sector-share-bar", style={"height": "400px"})]
                ),
                
                # RIGHT: Country info table
                html.Div(
                    style={"flex": "1"},
                    children=[
                        html.Div(
                            style={
                                "padding": "15px",
                                "backgroundColor": "#f8f9fa",
                                "borderRadius": "5px",
                                "border": "1px solid #dee2e6",
                                "display": "flex",
                                "flexDirection": "column"
                            },
                            children=[
                                html.H4("Country Information", style={"marginTop": "0", "marginBottom": "10px", "color": "#2c3e50", "fontSize": "14px"}),
                                
                                # Clickable titles table
                                dash_table.DataTable(
                                    id="country-info-table",
                                    style_cell={
                                        "textAlign": "left",
                                        "padding": "8px",
                                        "fontFamily": "Arial, sans-serif",
                                        "fontSize": "13px",
                                        "cursor": "pointer",
                                        "whiteSpace": "normal",
                                        "height": "auto"
                                    },
                                    style_cell_conditional=[
                                        {
                                            "if": {"column_id": "title"},
                                            "maxWidth": "250px",
                                            "overflow": "hidden",
                                            "textOverflow": "ellipsis"
                                        },
                                        {
                                            "if": {"column_id": "status"},
                                            "width": "100px"
                                        }
                                    ],
                                    style_header={
                                        "backgroundColor": "#2c3e50",
                                        "color": "white",
                                        "fontWeight": "bold",
                                        "fontSize": "13px"
                                    },
                                    style_data={
                                        "backgroundColor": "white",
                                        "border": "1px solid #dee2e6",
                                        "whiteSpace": "normal",
                                        "height": "auto"
                                    },
                                    style_data_conditional=[
                                        {
                                            "if": {"state": "active"},
                                            "backgroundColor": "#e3f2fd",
                                            "border": "1px solid #2196f3"
                                        }
                                    ],
                                    style_table={
                                        "maxHeight": "180px",
                                        "overflowY": "auto",
                                        "overflowX": "auto"
                                    },
                                    page_action="none",
                                    tooltip_data=[],
                                    tooltip_duration=None
                                ),
                                
                                # Description display area
                                html.Div(
                                    id="description-display",
                                    style={
                                        "marginTop": "15px",
                                        "padding": "12px",
                                        "backgroundColor": "white",
                                        "borderRadius": "4px",
                                        "border": "1px solid #dee2e6",
                                        "flex": "1",
                                        "fontSize": "13px",
                                        "color": "#495057",
                                        "overflowY": "auto"
                                    }
                                )
                            ]
                        )
                    ]
                ),
            ]
        ),

        # ----------------------------------------------------
        # MIDDLE ROW: EMISSIONS TRENDS + FISCAL MEASURES
        # ----------------------------------------------------
        html.Div(
            style={"display": "flex", "gap": "15px", "marginTop": "15px"},
            children=[
                html.Div(
                    style={"flex": "1"},
                    children=[dcc.Graph(id="emissions-trends-absolute", style={"height": "400px"})]
                ),
                
                # Government Fiscal Measures
                html.Div(
                    style={"flex": "1"},
                    children=[
                        html.Div(
                            style={
                                "padding": "15px",
                                "backgroundColor": "#f8f9fa",
                                "borderRadius": "5px",
                                "border": "1px solid #dee2e6",
                                "display": "flex",
                                "flexDirection": "column"
                            },
                            children=[
                                html.H4("Government Fiscal Measures", style={"marginTop": "0", "marginBottom": "10px", "color": "#2c3e50", "fontSize": "14px"}),
                                
                                # Fiscal measures table
                                dash_table.DataTable(
                                    id="fiscal-measures-table",
                                    style_cell={
                                        "textAlign": "left",
                                        "padding": "8px",
                                        "fontFamily": "Arial, sans-serif",
                                        "fontSize": "13px",
                                        "cursor": "pointer",
                                        "whiteSpace": "normal",
                                        "height": "auto"
                                    },
                                    style_cell_conditional=[
                                        {
                                            "if": {"column_id": "matched_title"},
                                            "maxWidth": "250px",
                                            "overflow": "hidden",
                                            "textOverflow": "ellipsis"
                                        },
                                        {
                                            "if": {"column_id": "budget_commitment"},
                                            "width": "120px"
                                        }
                                    ],
                                    style_header={
                                        "backgroundColor": "#2c3e50",
                                        "color": "white",
                                        "fontWeight": "bold",
                                        "fontSize": "13px"
                                    },
                                    style_data={
                                        "backgroundColor": "white",
                                        "border": "1px solid #dee2e6",
                                        "whiteSpace": "normal",
                                        "height": "auto"
                                    },
                                    style_data_conditional=[
                                        {
                                            "if": {"state": "active"},
                                            "backgroundColor": "#e3f2fd",
                                            "border": "1px solid #2196f3"
                                        }
                                    ],
                                    style_table={
                                        "maxHeight": "180px",
                                        "overflowY": "auto",
                                        "overflowX": "auto"
                                    },
                                    page_action="none",
                                    tooltip_data=[],
                                    tooltip_duration=None
                                ),
                                
                                # Fiscal description display area
                                html.Div(
                                    id="fiscal-description-display",
                                    style={
                                        "marginTop": "15px",
                                        "padding": "12px",
                                        "backgroundColor": "white",
                                        "borderRadius": "4px",
                                        "border": "1px solid #dee2e6",
                                        "flex": "1",
                                        "fontSize": "13px",
                                        "color": "#495057",
                                        "overflowY": "auto"
                                    }
                                )
                            ]
                        )
                    ]
                ),
            ]
        ),

        # ----------------------------------------------------
        # BOTTOM ROW: EMISSIONS STRUCTURE (FULL WIDTH)
        # ----------------------------------------------------
        html.Div(
            style={"marginTop": "15px"},
            children=[dcc.Graph(id="emissions-structure-ordered", style={"height": "400px"})]
        )
    ]
)

# ------------------------------------------------------------
# 3. CALLBACK
# ------------------------------------------------------------

@app.callback(
    Output("country-info-table", "data"),
    Output("country-info-table", "columns"),
    Output("country-info-table", "tooltip_data"),
    Output("description-display", "children"),
    Output("fiscal-measures-table", "data"),
    Output("fiscal-measures-table", "columns"),
    Output("fiscal-measures-table", "tooltip_data"),
    Output("fiscal-description-display", "children"),
    Output("sector-share-bar", "figure"),
    Output("emissions-trends-absolute", "figure"),
    Output("emissions-structure-ordered", "figure"),
    Input("country-dropdown", "value"),
    Input("country-info-table", "active_cell"),
    Input("fiscal-measures-table", "active_cell")
)
def update_dashboard(country, active_cell, fiscal_active_cell):

    # ------------------------
    # Country Info Table
    # ------------------------
    country_info = df_country_info[df_country_info["iso3"] == country]
    
    if not country_info.empty:
        table_data = country_info[["title", "status"]].to_dict("records")
        table_columns = [
            {"name": "Title", "id": "title"},
            {"name": "Status", "id": "status"}
        ]
        
        # Add tooltips for full title text
        tooltip_data = [
            {
                "title": {"value": row["title"], "type": "markdown"}
            }
            for _, row in country_info.iterrows()
        ]
        
        # Display description based on clicked row
        if active_cell and active_cell["row"] < len(country_info):
            row_idx = active_cell["row"]
            description = country_info.iloc[row_idx]["description"]
            description_display = html.Div([
                html.Strong("Description: ", style={"color": "#2c3e50"}),
                html.Span(description if pd.notna(description) else "No description available")
            ])
        else:
            description_display = html.Div(
                "Click on a row to view its description",
                style={"fontStyle": "italic", "color": "#6c757d"}
            )
    else:
        table_data = [{"title": "No data available", "status": "N/A"}]
        table_columns = [
            {"name": "Title", "id": "title"},
            {"name": "Status", "id": "status"}
        ]
        tooltip_data = []
        description_display = html.Div(
            "No information available for this country",
            style={"fontStyle": "italic", "color": "#6c757d"}
        )

    # ------------------------
    # Government Fiscal Measures Table
    # ------------------------
    fiscal_info = df_fiscal[df_fiscal["iso3"] == country]
    
    if not fiscal_info.empty:
        fiscal_table_data = fiscal_info[["matched_title", "budget_commitment"]].to_dict("records")
        fiscal_table_columns = [
            {"name": "Measure Title", "id": "matched_title"},
            {"name": "Budget Commitment", "id": "budget_commitment"}
        ]
        
        # Add tooltips for full title text
        fiscal_tooltip_data = [
            {
                "matched_title": {"value": row["matched_title"], "type": "markdown"}
            }
            for _, row in fiscal_info.iterrows()
        ]
        
        # Display description based on clicked row
        if fiscal_active_cell and fiscal_active_cell["row"] < len(fiscal_info):
            row_idx = fiscal_active_cell["row"]
            fiscal_description = fiscal_info.iloc[row_idx]["description"]
            fiscal_description_display = html.Div([
                html.Strong("Description: ", style={"color": "#2c3e50"}),
                html.Span(fiscal_description if pd.notna(fiscal_description) else "No description available")
            ])
        else:
            fiscal_description_display = html.Div(
                "Click on a row to view its description",
                style={"fontStyle": "italic", "color": "#6c757d"}
            )
    else:
        fiscal_table_data = [{"matched_title": "No fiscal measures available", "budget_commitment": "N/A"}]
        fiscal_table_columns = [
            {"name": "Measure Title", "id": "matched_title"},
            {"name": "Budget Commitment", "id": "budget_commitment"}
        ]
        fiscal_tooltip_data = []
        fiscal_description_display = html.Div(
            "No fiscal measures available for this country",
            style={"fontStyle": "italic", "color": "#6c757d"}
        )

    # ------------------------
    # Emissions Data
    # ------------------------
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
    fig1.update_layout(margin=dict(l=20, r=20, t=40, b=20), title_font_size=14)

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
    
    fig2.update_layout(margin=dict(l=20, r=20, t=40, b=20), title_font_size=14)

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
    fig3.update_layout(margin=dict(l=20, r=20, t=40, b=20), title_font_size=14)

    return table_data, table_columns, tooltip_data, description_display, fiscal_table_data, fiscal_table_columns, fiscal_tooltip_data, fiscal_description_display, fig1, fig2, fig3

# ------------------------------------------------------------
# 4. RUN APP
# ------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
