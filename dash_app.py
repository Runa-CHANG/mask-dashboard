import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

# PostgreSQL 連線資訊 (Render 提供的環境變數)
DB_URL = os.getenv("DATABASE_URL")  # e.g. postgres://user:pass@host:port/dbname
engine = create_engine(DB_URL)

# 初始化 Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "口罩辨識歷史統計"
server = app.server

# 讀取資料函式
def fetch_data():
    query = "SELECT * FROM mask_summary ORDER BY timestamp DESC"
    return pd.read_sql(query, engine)

def layout_dashboard(df, selected_time):
    row = df[df['timestamp'] == selected_time].iloc[0]
    
    pie_fig = px.pie(
        names=["With_Mask", "Without_Mask", "Incorrectly_Worn_Mask", "Partially_Worn_Mask"],
        values=[row['With_Mask'], row['Without_Mask'], row['Incorrectly_Worn_Mask'], row['Partially_Worn_Mask']],
        color_discrete_sequence=px.colors.sequential.RdBu,
        hole=0.4,
    )

    bar_fig = px.bar(
        x=["With_Mask", "Without_Mask", "Incorrectly_Worn_Mask", "Partially_Worn_Mask"],
        y=[row['With_Mask'], row['Without_Mask'], row['Incorrectly_Worn_Mask'], row['Partially_Worn_Mask']],
        color=["With_Mask", "Without_Mask", "Incorrectly_Worn_Mask", "Partially_Worn_Mask"],
        color_discrete_map={
            "With_Mask": "green",
            "Without_Mask": "red",
            "Incorrectly_Worn_Mask": "orange",
            "Partially_Worn_Mask": "purple",
        },
    )
    bar_fig.update_layout(yaxis_title="人數")

    return dbc.Container([
        html.H2("📊 歷史口罩辨識統計報告"),

        dbc.Row([
            dbc.Col([
                html.Label("選擇辨識時間："),
                dcc.Dropdown(
                    id='timestamp-dropdown',
                    options=[{"label": t, "value": t} for t in df['timestamp']],
                    value=selected_time,
                    clearable=False
                ),
            ], width=6),
            dbc.Col([
                html.A("下載 CSV", id='download-csv', href=f"/download/csv?timestamp={selected_time}", className="btn btn-outline-primary mx-1"),
                html.A("下載 Excel", id='download-excel', href=f"/download/excel?timestamp={selected_time}", className="btn btn-outline-success mx-1"),
            ], width=6, className="text-end")
        ], className="my-3"),

        dbc.Row([
            dbc.Col([
                html.H5("累計人數統計"),
                html.Div([
                    dbc.Card([dbc.CardBody([html.H4(int(row['Total']), className="card-title"), html.P("總人數")])], color="primary", inverse=True),
                    dbc.Card([dbc.CardBody([html.H4(int(row['With_Mask'])), html.P("戴口罩")])], color="success", inverse=True),
                    dbc.Card([dbc.CardBody([html.H4(int(row['Without_Mask'])), html.P("未戴口罩")])], color="danger", inverse=True),
                    dbc.Card([dbc.CardBody([html.H4(int(row['Incorrectly_Worn_Mask'])), html.P("佩戴錯誤")])], color="warning", inverse=True),
                    dbc.Card([dbc.CardBody([html.H4(int(row['Partially_Worn_Mask'])), html.P("部分遮蓋")])], color="info", inverse=True),
                ], className="d-flex gap-3 flex-wrap justify-content-around my-3")
            ])
        ]),

        dbc.Row([
            dbc.Col([dcc.Graph(figure=pie_fig)], md=6),
            dbc.Col([dcc.Graph(figure=bar_fig)], md=6),
        ])
    ])

# 主頁路由
@app.callback(
    Output('page-content', 'children'),
    Input('timestamp-dropdown', 'value')
)
def update_dashboard(selected_time):
    df = fetch_data()
    return layout_dashboard(df, selected_time)

# App Layout
@app.callback(Output('page-content', 'children'), Input('timestamp-dropdown', 'value'))
def update_dashboard(selected_time):
    df = fetch_data()
    return layout_dashboard(df, selected_time)

@app.server.route("/download/csv")
def download_csv():
    from flask import request, Response
    df = fetch_data()
    timestamp = request.args.get("timestamp")
    row = df[df['timestamp'] == timestamp]
    csv_data = row.to_csv(index=False)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=mask_summary_{timestamp}.csv"}
    )

@app.server.route("/download/excel")
def download_excel():
    from flask import request, Response
    import io
    df = fetch_data()
    timestamp = request.args.get("timestamp")
    row = df[df['timestamp'] == timestamp]
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        row.to_excel(writer, index=False)
    output.seek(0)
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-disposition": f"attachment; filename=mask_summary_{timestamp}.xlsx"}
    )

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="page-content")
])

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)


