import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from performance_tracker import PerformanceTracker

app = dash.Dash(__name__)

performance_tracker = PerformanceTracker()

app.layout = html.Div([
    html.H1('Trading Bot Dashboard'),
    dcc.Graph(id='equity-curve'),
    dcc.Graph(id='trade-history'),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds, update every 1 minute
        n_intervals=0
    )
])

@app.callback(Output('equity-curve', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_equity_curve(n):
    equity_data = performance_tracker.get_equity_curve()
    df = pd.DataFrame(equity_data, columns=['timestamp', 'equity'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['equity'], mode='lines', name='Equity'))
    fig.update_layout(title='Equity Curve', xaxis_title='Time', yaxis_title='Equity')
    return fig

@app.callback(Output('trade-history', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_trade_history(n):
    trade_history = performance_tracker.get_trade_history()
    df = pd.DataFrame(trade_history, columns=['timestamp', 'action', 'price', 'amount'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['price'], mode='markers',
                             marker=dict(size=8, color=df['action'].map({'BUY': 'green', 'SELL': 'red'})),
                             text=df['action'] + ': ' + df['amount'].astype(str),
                             name='Trades'))
    fig.update_layout(title='Trade History', xaxis_title='Time', yaxis_title='Price')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)