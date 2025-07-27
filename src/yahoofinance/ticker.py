import yfinance as yf
from misc import lst

class Tickers(yf.Ticker):
  def __init__(self,**kw):
    self.symbol=symbol
    super().__init__(**kw)
    # self.data=yf.Ticker(symbol)


class Ticker(yf.Ticker):
  key_first=lst("symbol shortName")
  def __init__(self,symbol):
    self.symbol=symbol
    super().__init__(symbol)
    # self.data=yf.Ticker(symbol)

  "Yahoo finance logic"
  def get_data(ticker):
    return yf.Ticker(ticker)
  def get_recomendations(ticker):
    return yf.Ticker(ticker).ana       
  def __repr__(self):
    # return str(self.data.info)
    return "<Ticker: {symbol} {shortName}>".format(**self.info)
  def news(self):
    for x in self.news:
        # print(x)
        try: tn=sort_by(x["content"]["thumbnail"]["resolutions"],"width")[0]["url"]
        except: tn=""
        display( w.HBox([w.HTML(f'<img src="{tn}" width="80px"/><div>{x["content"]["pubDate"]}</h2>'),
                w.HTML('''
        <a href="{url}" target="_blank">{title}</a>: 
        <small>{summary}</small>
        '''.format(**x['content'],url=x['content']['canonicalUrl']['url']))]) # clickThroughUrl
        )
    def chart_analysts():
        pass