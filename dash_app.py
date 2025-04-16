# dash_app.py
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData
from sqlalchemy import inspect

# 建立資料表（如果不存在）
def create_table_if_not_exists(engine):
    metadata = MetaData()
    inspector = inspect(engine)

    if "mask_summary" not in inspector.get_table_names():
        mask_summary = Table(
            "mask_summary", metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("timestamp", DateTime),
            Column("With_Mask", Integer),
            Column("Without_Mask", Integer),
            Column("Incorrectly_Worn_Mask", Integer),
            Column("Partially_Worn_Mask", Integer),
            Column("Total", Integer),
            Column("start_time", DateTime),
            Column("end_time", DateTime),
        )
        metadata.create_all(engine)
        print("✅ Created table 'mask_summary'")
    else:
        print("✅ Table 'mask_summary' already exists")

# PostgreSQL 連線資訊 (Render 的環境變數)
DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL)

# 初始化 Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "口罩辨識歷史統計"
server = app.server

# 資料讀取函式
def fetch_data():
    query = "SELECT * FROM mask_summary WHERE timestamp IS NOT NULL ORDER BY timestamp DESC"
    return pd.read_sql(query, engine)

# 統計圖與卡片 layout
def layout_dashboard(df, selected_time):
    if df.empty:
        # 預設資料（全為 0）
        pie_fig = px.pie(
            names=["With_Mask", "Without_Mask", "Incorrectly_Worn_Mask", "Partially_Worn_Mask"],
            values=[0, 0, 0, 0],
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )

        bar_fig = px.bar(
            x=["With_Mask", "Without_Mask", "Incorrectly_Worn_Mask", "Partially_Worn_Mask"],
            y=[0, 0, 0, 0],
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

            dbc.Alert("⚠️ 尚無任何辨識資料，請先完成一次辨識", color="warning"),

            dbc.Row([
                dbc.Col([
                    html.Label("選擇辨識時間："),
                    dcc.Dropdown(
                        id='timestamp-dropdown',
                        options=[],
                        placeholder="無可選時間",
                        disabled=True
                    )
                ], width=6),
                dbc.Col([], width=6)
            ], className="my-3"),

            dbc.Row([
                dbc.Col([
                    html.H5("累計人數統計"),
                    html.Div([
                        dbc.Card([dbc.CardBody([html.H4("0"), html.P("總人數")])], color="primary", inverse=True),
                        dbc.Card([dbc.CardBody([html.H4("0"), html.P("戴口罩")])], color="success", inverse=True),
                        dbc.Card([dbc.CardBody([html.H4("0"), html.P("未戴口罩")])], color="danger", inverse=True),
                        dbc.Card([dbc.CardBody([html.H4("0"), html.P("佩戴錯誤")])], color="warning", inverse=True),
                        dbc.Card([dbc.CardBody([html.H4("0"), html.P("部分遮蓋")])], color="info", inverse=True),
                    ], className="d-flex gap-3 flex-wrap justify-content-around my-3")
                ])
            ]),

            dbc.Row([
                dbc.Col([dcc.Graph(figure=pie_fig)], md=6),
                dbc.Col([dcc.Graph(figure=bar_fig)], md=6),
            ])
        ])
    
    # ⬇️ 有資料的狀況（原本邏輯保留）
    row = df[df['timestamp'] == selected_time]
    if row.empty:
        return html.Div("⚠️ 無此時間點的資料")
    row = row.iloc[0]

    # 圖表同你原本的邏輯
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
                    options=[{"label": pd.to_datetime(t).strftime('%Y-%m-%d %H:%M:%S'), "value": t} for t in df['timestamp']],
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
                    dbc.Card([dbc.CardBody([html.H4(int(row['Total'])), html.P("總人數")])], color="primary", inverse=True),
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


# Dash layout 初始化
def serve_layout():
    df = fetch_data()
    if df.empty:
        return html.Div("🚫 無資料可顯示")
    default_time = df['timestamp'].iloc[0]
    return layout_dashboard(df, default_time)

app.layout = serve_layout

# Callback：下拉選單變更時更新內容
@app.callback(
    Output('page-content', 'children'),
    Input('timestamp-dropdown', 'value')
)
def update_dashboard(selected_time):
    df = fetch_data()
    if df.empty or not selected_time:
        return layout_dashboard(df, selected_time=None)
    return layout_dashboard(df, selected_time)

# CSV 下載路由
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

# Excel 下載路由
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


# 呼叫這個函式來建立表格（放在 app 開始之前）
create_table_if_not_exists(engine)

# Layout 容器
app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="page-content")
])

# 啟動 Dash App（Render 用 host="0.0.0.0"）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)
