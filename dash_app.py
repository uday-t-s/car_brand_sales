# dash_app.py
import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import base64
import io

# -------------------------------
# Setup
# -------------------------------
app = dash.Dash(__name__)
app.title = "Car Data Dashboard 🚗"

# Theme Colors
BG_COLOR = "#0d0f12"
CARD_COLOR = "#161b22"
LIGHT_BLACK = "#2a2f38"
TEXT_COLOR = "#f5f5f5"
ACCENT = "#00ffff"

# -------------------------------
# CSS Styling (Updated for Visible Dropdown)
# -------------------------------
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background: #0d0f12;
                font-family: 'Inter', sans-serif;
            }
            /* Dropdown control */
            .Select-control {
                background-color: #161b22 !important;
                border: 1px solid #00ffff80 !important;
                border-radius: 10px !important;
                transition: all 0.3s ease-in-out !important;
                color: #ffffff !important;
            }

            /* When hovered or active (clicked) */
            .Select-control:hover,
            .Select--single.is-focused > .Select-control,
            .Select.is-focused > .Select-control {
                background-color: #2a2f38 !important;  /* Light black */
                border: 1px solid #00ffff !important;
                box-shadow: 0 0 10px rgba(0,255,255,0.4);
            }

            /* Dropdown menu styling */
            .Select-menu-outer {
                background-color: #2a2f38 !important; /* Light black dropdown background */
                border: 1px solid #00ffff70 !important;
                color: #ffffff !important;
                z-index: 9999 !important;
            }

            /* Dropdown options */
            .Select-option {
                background-color: #2a2f38 !important;
                color: #f5f5f5 !important;
                font-size: 15px !important;
            }

            /* Hovered option */
            .Select-option.is-focused {
                background-color: #00ffff33 !important;
                color: #ffffff !important;
            }

            /* Selected option */
            .Select-option.is-selected {
                background-color: #00ffff55 !important;
                color: #000000 !important;
                font-weight: 600 !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# -------------------------------
# Data Cleaning
# -------------------------------
def preprocess_data(df: pd.DataFrame):
    df_cleaned = df.copy()
    df_cleaned.drop_duplicates(inplace=True)
    df_cleaned.dropna(inplace=True)
    numeric_cols = df_cleaned.select_dtypes(include=["float64", "int64"]).columns
    for col in numeric_cols:
        q_low, q_high = df_cleaned[col].quantile(0.01), df_cleaned[col].quantile(0.99)
        df_cleaned = df_cleaned[(df_cleaned[col] >= q_low) & (df_cleaned[col] <= q_high)]
    return df_cleaned

# -------------------------------
# Layout
# -------------------------------
app.layout = html.Div(
    style={"backgroundColor": BG_COLOR, "minHeight": "100vh", "padding": "25px"},
    children=[
        html.H1(
            "🚗 Car Data Visualization Dashboard",
            style={"textAlign": "center", "color": ACCENT, "fontWeight": "700", "fontSize": "2.4rem"},
        ),
        html.P(
            "Upload your car dataset, clean it automatically, and visualize it interactively.",
            style={"textAlign": "center", "color": "#aaa", "marginBottom": "40px"},
        ),

        # Upload Section
        html.Div(
            [
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["📂 Drag & Drop or ", html.A("Select a CSV File", style={"color": ACCENT})]),
                    style={
                        "width": "60%",
                        "height": "80px",
                        "lineHeight": "80px",
                        "borderWidth": "2px",
                        "borderStyle": "dashed",
                        "borderRadius": "15px",
                        "textAlign": "center",
                        "margin": "auto",
                        "backgroundColor": CARD_COLOR,
                        "color": TEXT_COLOR,
                        "fontSize": "18px",
                        "transition": "0.3s",
                        "boxShadow": "0 0 10px rgba(0,255,255,0.3)",
                    },
                    multiple=False,
                ),
                html.Div(id="file-info", style={"textAlign": "center", "marginTop": "15px", "color": ACCENT}),
            ]
        ),

        html.Br(),

        # Dashboard layout
        html.Div(
            [
                html.Div(
                    [
                        html.H3("🎛 Dashboard Controls", style={"color": ACCENT}),
                        html.P("Customize your chart view:", style={"color": "#aaa"}),

                        html.Label("Chart Type:", style={"color": TEXT_COLOR}),
                        dcc.Dropdown(
                            id="chart-type",
                            options=[
                                {"label": "Bar Chart", "value": "bar"},
                                {"label": "Box Plot", "value": "box"},
                                {"label": "Scatter Plot", "value": "scatter"},
                                {"label": "Pie Chart", "value": "pie"},
                            ],
                            value="bar",
                            clearable=False,
                        ),
                        html.Br(),

                        html.Label("X-axis:", style={"color": TEXT_COLOR}),
                        dcc.Dropdown(id="x-axis", placeholder="Select column for X-axis"),
                        html.Br(),

                        html.Label("Y-axis:", style={"color": TEXT_COLOR}),
                        dcc.Dropdown(id="y-axis", placeholder="Select column for Y-axis"),
                        html.Br(),
                    ],
                    style={
                        "width": "25%",
                        "backgroundColor": CARD_COLOR,
                        "padding": "25px",
                        "borderRadius": "20px",
                        "float": "right",
                        "boxShadow": "0 0 20px rgba(0,255,255,0.15)",
                        "color": TEXT_COLOR,
                    },
                ),
                html.Div(
                    id="graph-display",
                    style={
                        "width": "70%",
                        "float": "left",
                        "backgroundColor": CARD_COLOR,
                        "padding": "20px",
                        "borderRadius": "20px",
                        "boxShadow": "0 0 25px rgba(0,255,255,0.1)",
                        "minHeight": "550px",
                    },
                ),
            ],
            style={"display": "flex", "justifyContent": "space-between", "gap": "2%"},
        ),
    ],
)

# -------------------------------
# Callbacks
# -------------------------------
@app.callback(
    [Output("file-info", "children"), Output("x-axis", "options"), Output("y-axis", "options")],
    [Input("upload-data", "contents")],
    [State("upload-data", "filename")],
)
def update_dropdowns(contents, filename):
    if contents is None:
        return "", [], []
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    df_cleaned = preprocess_data(df)
    numeric_cols = df_cleaned.select_dtypes(include=["float64", "int64"]).columns.tolist()
    categorical_cols = df_cleaned.select_dtypes(include=["object", "category"]).columns.tolist()
    info = f"✅ Uploaded: {filename} | Cleaned Rows: {df_cleaned.shape[0]}"
    return info, [{"label": c, "value": c} for c in categorical_cols + numeric_cols], [{"label": c, "value": c} for c in numeric_cols]

@app.callback(
    Output("graph-display", "children"),
    [Input("upload-data", "contents"), Input("x-axis", "value"), Input("y-axis", "value"), Input("chart-type", "value")],
)
def update_graph(contents, x_col, y_col, chart_type):
    if contents is None or x_col is None:
        return html.P("📊 Upload data and select fields to generate charts.",
                      style={"textAlign": "center", "color": "#888", "fontSize": "1.1rem"})
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    df_cleaned = preprocess_data(df)
    if chart_type == "bar":
        fig = px.bar(df_cleaned, x=x_col, y=y_col, color=x_col, title=f"{y_col} by {x_col}")
    elif chart_type == "box":
        fig = px.box(df_cleaned, x=x_col, y=y_col, color=x_col, title=f"Distribution of {y_col} by {x_col}")
    elif chart_type == "scatter":
        fig = px.scatter(df_cleaned, x=x_col, y=y_col, color=x_col, title=f"{y_col} vs {x_col}")
    elif chart_type == "pie":
        fig = px.pie(df_cleaned, names=x_col, title=f"Distribution of {x_col}")
    fig.update_layout(
        template="plotly_dark",
        height=550,
        paper_bgcolor=CARD_COLOR,
        plot_bgcolor=CARD_COLOR,
        font_color=TEXT_COLOR,
        title_font=dict(size=22, color=ACCENT),
        hoverlabel=dict(bgcolor=ACCENT, font_color="#000", font_size=14),
    )
    return dcc.Graph(figure=fig, style={"height": "550px", "borderRadius": "15px"})

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8050)
