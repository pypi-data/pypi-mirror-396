import json
import threading
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

import websocket

def check_chart(chart: pd.DataFrame):
    if not ("timestamp" in chart.columns and "close" in chart.columns):
        raise ValueError("Chart Dataframe must contain 'timestamp' and 'close' coloumns!")
    
def calcRSI(avg_gain, avg_loss):
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

class Settings:
    def __init__(self, timespan: int = 1000, default_money: float = 10000.0, buy_amount: float = 100.0, sell_amount: float = 100.0, start_asset: float = 0.0):
        self.timespan = timespan
        self.default_money = default_money
        self.buy_amount = buy_amount
        self.sell_amount = sell_amount
        self.start_asset = start_asset
    
    def set_timespan(self, timespan: int):
        self.timespan = timespan
    
    def set_default_money(self, default_money: float):
        self.default_money = default_money
    
    def set_buy_amount(self, buy_amount: float):
        self.buy_amount = buy_amount
    
    def set_sell_amount(self, sell_amount: float):
        self.sell_amount = sell_amount
    
    def set_start_asset(self, start_asset: float):
        self.start_asset = start_asset
    
    def get_timespan(self) -> int:
        return self.timespan
    
    def get_default_money(self) -> float:
        return self.default_money
    
    def get_buy_amount(self) -> float:
        return self.buy_amount
    
    def get_sell_amount(self) -> float:
        return self.sell_amount
    
    def get_start_asset(self) -> float:
        return self.start_asset


class ChartManager:
    def __init__(self, data: pd.DataFrame = None, settings: Settings = None):
        if data is not None:
            check_chart(data)
            self.df = data
        else:
            self.df = None
        
        self.settings = settings

    def set_chart_data(self, data: pd.DataFrame):
        check_chart(data)
        self.df = data
    
    def set_chart_settings(self, settings: Settings):
        self.settings = settings

    def get_chart_data(self):
        if self.settings:
            timespan = self.settings.timespan
            length = self.df.shape[0]
            random_indx = random.randrange(timespan, length - timespan - 1)
            df = self.df.iloc[random_indx:random_indx+timespan].copy()
            MACD_line = (df["close"].ewm(span=12, adjust=False).mean() - df["close"].ewm(span=26, adjust=False).mean())
            MACD_sign = MACD_line.ewm(span=9, adjust=False).mean()
            MACD_line_hist = MACD_line - MACD_sign
            df["change"] = df["close"].diff()
            df["gain"]=df["change"].clip(lower=0)
            df["loss"]=-df["change"].clip(upper=0)
            df["avggain"]=df["gain"].rolling(12).mean()
            df["avgloss"]=df["loss"].rolling(12).mean()
            df["RSI"]=df.apply(lambda r: calcRSI(r['avggain'], r["avgloss"]), axis=1)
            df["MACD"] = MACD_line
            df["MACD_SIGN"] = MACD_sign
            df["MACD_HIST"] = MACD_line_hist
            df["EMA25"] =  df["close"].ewm(span=25, adjust=False).mean()
            df["EMA50"] =  df["close"].ewm(span=50, adjust=False).mean()
            df["EMA100"] = df["close"].ewm(span=100, adjust=False).mean()
            df["EMA150"] = df["close"].ewm(span=150, adjust=False).mean()
            df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()
            df["EMA400"] = df["close"].ewm(span=400, adjust=False).mean()
            return df
        else:
            raise ValueError("Settings must be applied to the chartmanager!")

class Strategy:
    def __init__(self, name: str = "My strategy"):
        self.name = name
        self.strategy_buys: pd.DataFrame = pd.DataFrame(columns=["Timestamp", "Price"]) # NEED THE FORMAT: ["Timestamp", "PRICE"]
        self.strategy_sells: pd.DataFrame = pd.DataFrame(columns=["Timestamp", "Price"]) # NEED THE FORMAT: ["Timestamp", "PRICE"]
    
    def set_name(self, name: str):
        self.name = name
    
    def set_strategy_sells(self, sells: pd.DataFrame):
        sells = pd.DataFrame(sells, columns=["Timestamp", "Price"])
        if "Timestamp" in sells.columns and "Price" in sells.columns:
            self.strategy_sells = sells
        else:
            raise ValueError("Dataframe must contain 'Timestamp' and 'Price' columns!")
    def set_strategy_buys(self, buys: pd.DataFrame):
        buys = pd.DataFrame(buys, columns=["Timestamp", "Price"])
        if "Timestamp" in buys.columns and "Price" in buys.columns:
            self.strategy_buys = buys
        else:
            raise ValueError("Dataframe must contain 'Timestamp' and 'Price' columns!")
    
    def get_strategy_buys(self):
        return self.strategy_buys

    def get_strategy_sells(self):
        return self.strategy_sells

class Simulation:
    def __init__(self, chart: pd.DataFrame, settings: Settings, strategy: Strategy):
        self.chart = chart
        self.settings = settings
        self.strategy = strategy
    
    def simulate(self):
        if (self.chart is None or self.settings is None or self.strategy is None):
            raise ValueError("Chart, Settings and Strategy must be set!")
        
        balance = []
        df = self.chart
        money = self.settings.default_money
        assets = self.settings.start_asset
        buy_amount = self.settings.buy_amount
        sell_amount = self.settings.sell_amount
        sells: pd.DataFrame = self.strategy.get_strategy_sells()
        buys: pd.DataFrame = self.strategy.get_strategy_buys()
        buy_times = set(buys["Timestamp"])
        sell_times = set(sells["Timestamp"])
        for _, row in df.iterrows():
            ts=row["timestamp"]
            if ts in buy_times:
                if(money>=buy_amount*row["close"]):
                    assets += buy_amount
                    money -= buy_amount*row["close"]
            if ts in sell_times:
                if(assets>=sell_amount):
                    assets -= sell_amount
                    money += sell_amount*row["close"]

            balance.append({"balance": money+(assets*row["close"])})
        
        PORTFOLIO = pd.DataFrame(balance)
        return PORTFOLIO

    def graph(self, rsi: bool = False, ema: bool = False, rsi_over = [30, 70]):
        portfolio = self.simulate()
        plt.style.use("dark_background")
        chart_copy = self.chart.copy()
        chart_copy['timestamp'] = pd.to_datetime(chart_copy['timestamp'], unit='ms').astype('datetime64[s]')
        if rsi:
            _, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 5))
        else:
            _, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5))
        plt.subplots_adjust(hspace=0.5)
        
        ax1.set_title("Price Chart with Signals")
        ax1.axvline(x=chart_copy['timestamp'].iloc[-1], color="red", linestyle="-", linewidth=1)
        if(ema):
            ema25 = chart_copy["close"].ewm(span=25, adjust=False).mean()
            ema50 = chart_copy["close"].ewm(span=50, adjust=False).mean()
            ema100 = chart_copy["close"].ewm(span=100, adjust=False).mean()
            ema150 = chart_copy["close"].ewm(span=150, adjust=False).mean()
            ema200 = chart_copy["close"].ewm(span=200, adjust=False).mean()
            ema400 = chart_copy["close"].ewm(span=400, adjust=False).mean()
            ax1.plot(chart_copy["timestamp"], ema200, color="#d284ff78", linewidth=1.5, label="EMA200")
            ax1.plot(chart_copy["timestamp"], ema100, color="#a200ff65", linewidth=1.5, label="EMA100")
            ax1.plot(chart_copy["timestamp"], ema150, color="#ff00f264", linewidth=1.5, label="EMA150")
            ax1.plot(chart_copy["timestamp"], ema400, color="#c300ff63", linewidth=1.5, label="EMA400")
            ax1.plot(chart_copy["timestamp"], ema50, color="#ff009d64", linewidth=1.5, label="EMA50")
            ax1.plot(chart_copy["timestamp"], ema25, color="#a200ff63", linewidth=1.5, label="EMA25")
        ax1.plot(chart_copy["timestamp"],chart_copy["close"])
        
        
        BUY_SIGNAL=self.strategy.get_strategy_buys()
        SELL_SIGNAL=self.strategy.get_strategy_sells()
        BUY_SIGNAL['Timestamp'] = pd.to_datetime(BUY_SIGNAL['Timestamp'], unit='ms').astype('datetime64[s]')
        SELL_SIGNAL['Timestamp'] = pd.to_datetime(SELL_SIGNAL['Timestamp'], unit='ms').astype('datetime64[s]')
        ax1.scatter(BUY_SIGNAL["Timestamp"], BUY_SIGNAL["Price"] - 1, color="#00FF0073", s=50, marker="^", zorder=5)
        ax1.scatter(SELL_SIGNAL["Timestamp"], SELL_SIGNAL["Price"] + 1, color="#ff101065", s=50, marker="v", zorder=5)
        x2 =  chart_copy["timestamp"]
        y2 =  portfolio["balance"]
        ax2.plot(x2,y2,  color="blue")
        ax2.set_title("FINAL PnL: "+str(round((portfolio["balance"].iloc[-1])-self.settings.default_money, 2))+"$")
        ax2.axvline(x=chart_copy['timestamp'].iloc[-1], color="red", linestyle="-", linewidth=1)
        
        if(rsi):
            ax3.plot(x2,chart_copy["RSI"],  color="blue")
            ax3.set_title("RSI")
            ax3.axhline(y=rsi_over[0], color="green", linestyle="--", linewidth=1)
            ax3.axhline(y=rsi_over[1], color="red", linestyle="--", linewidth=1)
            ax3.axvline(x=chart_copy['timestamp'].iloc[-1], color="red", linestyle="-", linewidth=1)
        
        plt.show()

class Session:
    def __init__(self, websocketURL: str, strategy=None):
        self.websocketURL = websocketURL
        self.strategy_function = strategy
        self.ws = None
        self.running = False
        self.thread = None
        
    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            if self.strategy_function:
                self.strategy_function(data)
        except Exception as e:
            print(f"Error on message: {e}")
    
    def _on_error(self, ws, error):
        print(f"WS Error: {error}")
    
    def _on_close(self, ws, close_code, close_msg):
        print("WS Closed")
        self.running = False
    
    def _on_open(self, ws):
        print(f"WS Connected: {self.websocketURL}")
        self.running = True
    
    def start(self):
        if self.running:
            print("Error: Session is already running")
            return
        
        def run_websocket():
            self.ws = websocket.WebSocketApp(
                self.websocketURL,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            self.ws.run_forever()
        self.thread = threading.Thread(target=run_websocket, daemon=True)
        self.thread.start()
        print("WS session started")
    
    def stop(self):
        if self.ws:
            self.ws.close()
            self.running = False
            print("WS Session stopped")
    
    def set_strategy(self, strategy_function):
        self.strategy_function = strategy_function
        
    def is_connected(self):
        return self.running

    def live_chart(self, df_getter, interval=1, max_p=1000, show_ema=True, show_rsi=False, rsi_levels=[30,70], timeframe='1tick'):
        plt.style.use("dark_background")
        if show_rsi:
            fig, (ax1,ax2) = plt.subplots(2,1,figsize=(12,8), gridspec_kw={'height_ratios': [3, 1]})
        else:
            fig, ax1 = plt.subplots(1,1,figsize=(12,6))
            ax2 = None
        plt.subplots_adjust(hspace=0.3)
        
        def make_timeframe(self, df: pd.DataFrame, timeframe):
            if timeframe == "1tick":
                return df
            
            timeframes = {
                '1m': '1min', '5m': '5min', '15m': '15min', '30m': '30min',
                '1h': '1H', '4h': '4H', '12h': '12H',
                '1D': '1D', '3D': '3D', '1W': '1W'
            }
            
            if timeframe not in timeframes:
                #print(f"Unknown timeframe: {timeframe}, using 1tick")
                return df

            freq = timeframes[timeframe]
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'], unit='ms')
            df_copy.set_index('timestamp', inplace=True)
            
            agg = {'close': 'last'}
            if 'signal' in df_copy.columns:
                agg['signal'] = 'last'
            
            new_orderd = df_copy.resample(freq).agg(agg).dropna()
            new_orderd.reset_index(inplace=True)
            
            
            return new_orderd
            
        
        def animate(frame):
            try:
                df = df_getter()
                
                if df is None or len(df) == 0:
                    return
                
                df = make_timeframe(self, df, timeframe=timeframe)
                if len(df) == 0:
                    return
                
                if len(df) > max_p:
                    df = df.iloc[-max_p:].copy()
                else:
                    df = df.copy()
                
                if df['timestamp'].dtype != 'datetime64[ns]':
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['close'] = pd.to_numeric(df['close'], errors='coerce')
                
                ax1.clear()
                if ax2:
                    ax2.clear()
                
                ax1.plot(df['timestamp'], df['close'], linewidth=2, label='Price')
                
                if show_ema and len(df) >= 25:
                    if len(df) >= 25:
                        ema25 = df['close'].ewm(span=25, adjust=False).mean()
                        ax1.plot(df['timestamp'], ema25, color='#a200ff63', linewidth=1.5, label='EMA25', alpha=0.7)
                    if len(df) >= 50:
                        ema50 = df['close'].ewm(span=50, adjust=False).mean()
                        ax1.plot(df['timestamp'], ema50, color='#ff009d64', linewidth=1.5, label='EMA50', alpha=0.7)
                    if len(df) >= 100:
                        ema100 = df['close'].ewm(span=100, adjust=False).mean()
                        ax1.plot(df['timestamp'], ema100, color='#a200ff65', linewidth=1.5, label='EMA100', alpha=0.7)
                    if len(df) >= 200:
                        ema200 = df['close'].ewm(span=200, adjust=False).mean()
                        ax1.plot(df['timestamp'], ema200, color='#d284ff78', linewidth=1.5, label='EMA200', alpha=0.7)
                
                ax1.set_title(f'Live Session ({len(df)} points) - {timeframe}')
                ax1.set_xlabel('Time')
                ax1.set_ylabel('Price')
                buy_signals = df[df['signal'] == 'buy']
                sell_signals = df[df['signal'] == 'sell']
                ax1.scatter(buy_signals['timestamp'], buy_signals['close'], color='#00FF0073', marker='^', s=50)
                ax1.scatter(sell_signals['timestamp'], sell_signals['close'], color='#ff101065', marker='v', s=50)
                ax1.legend(loc='upper left')
                ax1.grid(True, alpha=0.3)
                plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
                if show_rsi and ax2 and len(df) >= 14:
                    df_rsi = df.copy()
                    df_rsi['change'] = df_rsi['close'].diff()
                    df_rsi['gain'] = df_rsi['change'].clip(lower=0)
                    df_rsi['loss'] = -df_rsi['change'].clip(upper=0)
                    df_rsi['avggain'] = df_rsi['gain'].rolling(14).mean()
                    df_rsi['avgloss'] = df_rsi['loss'].rolling(14).mean()
                    df_rsi['RSI'] = df_rsi.apply(lambda r: calcRSI(r['avggain'], r['avgloss']), axis=1)
                    ax2.plot(df_rsi['timestamp'], df_rsi['RSI'], linewidth=2)
                    ax2.axhline(y=rsi_levels[0], color='green', linestyle='--', linewidth=1, alpha=0.7)
                    ax2.axhline(y=rsi_levels[1], color='red', linestyle='--', linewidth=1, alpha=0.7)
                    ax2.set_title('RSI', fontsize=12)
                    ax2.set_xlabel('Time')
                    ax2.set_ylabel('RSI')
                    ax2.set_ylim(0, 100)
                    ax2.grid(True, alpha=0.3)
                    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

            except Exception as e:
                print(f"Error updating: {e}")
        
        ani = animation.FuncAnimation(fig, animate, interval=int(interval), cache_frame_data=False)
        plt.tight_layout()
        
        try:
            plt.show()
        except KeyboardInterrupt:
            print("\n X Chart closed")
            self.stop()
            
