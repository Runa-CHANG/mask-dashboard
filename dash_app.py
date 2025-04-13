# dash_app.py
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Output, Input
import plotly.express as px
from stats_manager import get_history_dataframe, get_aggregated_stats

app = Dash(__name__)
server = app.server  # for gunicorn

def card(title, content):
    return html.Div([
        html.H4(title, style={'margin-bottom': '10px'}),
        content
    ], style={
        'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.1)',
        'padding': '20px',
        'border-radius': '8px',
        'backgroundColor': 'white',
        'margin': '10px',
        'flex': '1'
    })

app.layout = html.Div([
    html.H1("即時口罩統計 Dashboard", style={'textAlign': 'center'}),

    html.Div([
        card("口罩配戴比例（圓餅圖）", dcc.Graph(id='live-pie')),
        card("各類別累積人數（長條圖）", dcc.Graph(id='live-bar')),
        card("人數統計表", html.Div(id='summary-table')),
        card("辨識歷史紀錄", dash_table.DataTable(
            id='history-table',
            columns=[
                {'name': 'timestamp', 'id': 'timestamp'},
                {'name': 'label', 'id': 'label'}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center'},
            page_size=10
        ))
    ], style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'justifyContent': 'space-between',
    }),

    dcc.Interval(id='interval', interval=1000, n_intervals=0)
], style={'padding': '20px', 'backgroundColor': '#F5F7FA'})


@app.callback(
    [Output('live-pie', 'figure'),
     Output('live-bar', 'figure'),
     Output('history-table', 'data'),
     Output('summary-table', 'children')],
    [Input('interval', 'n_intervals')]
)
def update_graph(n):
    stats = get_aggregated_stats()
    labels = ['沒戴口罩', '有戴口罩', '未遮鼻', '掛下巴']
    keys = ['Without_Mask', 'With_Mask', 'Incorrectly_Worn_Mask', 'Partially_Worn_Mask']
    values = [stats.get(k, 0) for k in keys]

    pie = px.pie(
        names=labels,
        values=values,
        title="口罩配戴比例",
        color=labels,
        color_discrete_map={
            '沒戴口罩': '#FF4C4C',
            '有戴口罩': '#4CAF50',
            '未遮鼻': '#FFD700',
            '掛下巴': '#FF00FF'
        },
    )
    pie.update_layout(
        transition={'duration': 1000, 'easing': 'elastic-out'},
        showlegend=True
    )

    bar = px.bar(
        x=labels,
        y=values,
        title="各類別累積人數",
        color=labels,
        color_discrete_map={
            '沒戴口罩': '#FF4C4C',
            '有戴口罩': '#4CAF50',
            '未遮鼻': '#FFD700',
            '掛下巴': '#FF00FF'
        }
    )
    bar.update_layout(
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        yaxis=dict(
            tickformat=',d',
            nticks=5,
            ticks='outside',
            showline=True,
            linecolor='black',
            mirror=True
        )
    )

    df = get_history_dataframe()
    summary_table = html.Table([
        html.Thead(html.Tr([html.Th("類別"), html.Th("人數")])),
        html.Tbody([
            html.Tr([html.Td("沒戴口罩"), html.Td(stats.get("Without_Mask", 0))]),
            html.Tr([html.Td("有戴口罩"), html.Td(stats.get("With_Mask", 0))]),
            html.Tr([html.Td("未遮鼻"), html.Td(stats.get("Incorrectly_Worn_Mask", 0))]),
            html.Tr([html.Td("掛下巴"), html.Td(stats.get("Partially_Worn_Mask", 0))]),
            html.Tr([
                html.Td("總人數", style={"fontWeight": "bold"}),
                html.Td(sum(values), style={"fontWeight": "bold"})
            ])
        ])
    ], style={'width': '100%', 'textAlign': 'center'})

    return pie, bar, df.to_dict('records'), summary_table


if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=10000)



