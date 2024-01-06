import plotly
import plotly.graph_objects as go

def plot_candlestick_chart(data, trade_actions):
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Price')])
    for trade in trade_actions:
        color = 'green' if trade['action'] == 'buy' else 'red'
        fig.add_annotation(x=trade['date'], y=trade['price'], text=trade['action'].capitalize(), showarrow=True, arrowhead=1, arrowcolor=color, bgcolor=color)
    fig.update_layout(title='Price Chart with Trade Annotations', xaxis_title='Date', yaxis_title='Price in USD', template='plotly_dark')
    return fig