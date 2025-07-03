import plotly.graph_objects as go

def plot_chart(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='lime',
        decreasing_line_color='red'
    )])
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        title="BTC/USDT Candlestick (1h)"
    )
    return fig
