import plotly.graph_objects as go

def plot_chart(df, pattern_info=None, sl=None, tp=None):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='lime',
        decreasing_line_color='red',
        name="Price"
    )])

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        title="BTC/USDT Candlestick (1h)",
        hovermode='x unified',
        margin=dict(l=40, r=40, t=60, b=40)
    )

    if pattern_info:
        name = pattern_info['name']
        confidence = pattern_info['confidence']
        entry = pattern_info['entry']
        last_date = df.index[-1]

        shapes = []
        annotations = []

        # Entry line
        shapes.append(dict(
            type="line",
            xref="paper",
            x0=0,
            x1=1,
            y0=entry,
            y1=entry,
            line=dict(color="cyan", width=2, dash="dash"),
            name="Entry Line"
        ))
        annotations.append(dict(
            x=last_date,
            y=entry,
            xref="x",
            yref="y",
            text=f"Entry: {entry:.2f}",
            showarrow=True,
            arrowhead=3,
            ax=40,
            ay=-30,
            font=dict(color="cyan")
        ))

        # SL line
        if sl:
            shapes.append(dict(
                type="line",
                xref="paper",
                x0=0,
                x1=1,
                y0=sl,
                y1=sl,
                line=dict(color="red", width=2, dash="dot"),
                name="Stop Loss"
            ))
            annotations.append(dict(
                x=last_date,
                y=sl,
                xref="x",
                yref="y",
                text=f"Stop Loss: {sl:.2f}",
                showarrow=True,
                arrowhead=3,
                ax=40,
                ay=30,
                font=dict(color="red")
            ))

        # TP line
        if tp:
            shapes.append(dict(
                type="line",
                xref="paper",
                x0=0,
                x1=1,
                y0=tp,
                y1=tp,
                line=dict(color="green", width=2, dash="dot"),
                name="Take Profit"
            ))
            annotations.append(dict(
                x=last_date,
                y=tp,
                xref="x",
                yref="y",
                text=f"Take Profit: {tp:.2f}",
                showarrow=True,
                arrowhead=3,
                ax=40,
                ay=-30,
                font=dict(color="green")
            ))

        # Pattern key points markers
        for point_name, (idx, price) in pattern_info.get("key_points", {}).items():
            # Place markers/arrows for key points
            annotations.append(dict(
                x=idx,
                y=price,
                xref="x",
                yref="y",
                text=point_name,
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
                font=dict(color="yellow", size=12),
                bgcolor="rgba(0,0,0,0.5)",
                bordercolor="yellow",
                borderwidth=1,
                borderpad=2,
                align="center"
            ))

            # Optional: add circle markers
            fig.add_trace(go.Scatter(
                x=[idx],
                y=[price],
                mode='markers',
                marker=dict(size=10, color='yellow', symbol='circle-open'),
                showlegend=False,
                hoverinfo='skip'
            ))

        # Pattern title
        annotations.append(dict(
            x=0.5,
            y=1.05,
            xref='paper',
            yref='paper',
            text=f"Pattern: {name} ({confidence}%)",
            showarrow=False,
            font=dict(size=18, color="yellow"),
            align="center"
        ))

        fig.update_layout(shapes=shapes, annotations=annotations)

    return fig
