from typing import List, Dict, Optional
import time
import json
import os
import sys

class StockItem:
    def __init__(self, code: str, name: str = ""):
        self.code = code
        self.name = name
        self.price = 0.0
        self.pct_change = 0.0
        self.volume = 0.0
        self.high = 0.0
        self.low = 0.0
        self.amount = 0.0
        
        # 阈值设置 - 价格和涨跌幅
        self.upper_price = None
        self.lower_price = None
        self.upper_pct = None
        self.lower_pct = None
        
        # 阈值设置 - 其他字段
        self.upper_volume = None
        self.lower_volume = None
        self.upper_high = None
        self.lower_high = None
        self.upper_low = None
        self.lower_low = None
        self.upper_amount = None
        self.lower_amount = None
        
        # 预警状态
        self.is_alerting = False
        self.alert_reasons = []

    def update_data(self, data: Dict):
        self.name = data.get('name', self.name)
        self.price = data.get('price', 0.0)
        self.pct_change = data.get('pct_change', 0.0)
        self.volume = data.get('volume', 0.0)
        self.high = data.get('high', 0.0)
        self.low = data.get('low', 0.0)
        self.amount = data.get('amount', 0.0)
        self.check_alerts()

    def set_thresholds(self, upper_price=None, lower_price=None, upper_pct=None, lower_pct=None):
        self.upper_price = upper_price
        self.lower_price = lower_price
        self.upper_pct = upper_pct
        self.lower_pct = lower_pct
        self.check_alerts()

    def check_alerts(self):
        self.alert_reasons = []
        
        # 检查价格阈值
        if self.upper_price is not None and self.price >= self.upper_price:
            self.alert_reasons.append(f"价格突破上限: {self.price} >= {self.upper_price}")
        if self.lower_price is not None and self.price <= self.lower_price:
            self.alert_reasons.append(f"价格跌破下限: {self.price} <= {self.lower_price}")
        
        # 检查涨跌幅阈值
        if self.upper_pct is not None and self.pct_change >= self.upper_pct:
            self.alert_reasons.append(f"涨幅超过上限: {self.pct_change}% >= {self.upper_pct}%")
        if self.lower_pct is not None and self.pct_change <= self.lower_pct:
            self.alert_reasons.append(f"跌幅超过下限: {self.pct_change}% <= {self.lower_pct}%")
        
        # 检查成交量阈值
        if self.upper_volume is not None and self.volume >= self.upper_volume:
            self.alert_reasons.append(f"成交量超过上限: {self.volume} >= {self.upper_volume}")
        if self.lower_volume is not None and self.volume <= self.lower_volume:
            self.alert_reasons.append(f"成交量低于下限: {self.volume} <= {self.lower_volume}")
        
        # 检查最高价阈值
        if self.upper_high is not None and self.high >= self.upper_high:
            self.alert_reasons.append(f"最高价超过上限: {self.high} >= {self.upper_high}")
        if self.lower_high is not None and self.high <= self.lower_high:
            self.alert_reasons.append(f"最高价低于下限: {self.high} <= {self.lower_high}")
        
        # 检查最低价阈值
        if self.upper_low is not None and self.low >= self.upper_low:
            self.alert_reasons.append(f"最低价超过上限: {self.low} >= {self.upper_low}")
        if self.lower_low is not None and self.low <= self.lower_low:
            self.alert_reasons.append(f"最低价低于下限: {self.low} <= {self.lower_low}")
        
        # 检查成交额阈值
        if self.upper_amount is not None and self.amount >= self.upper_amount:
            self.alert_reasons.append(f"成交额超过上限: {self.amount} >= {self.upper_amount}")
        if self.lower_amount is not None and self.amount <= self.lower_amount:
            self.alert_reasons.append(f"成交额低于下限: {self.amount} <= {self.lower_amount}")
        
        self.is_alerting = len(self.alert_reasons) > 0

class MonitorEngine:
    def __init__(self, config_file: str = "stock_config.json"):
        self.stocks: Dict[str, StockItem] = {}
        # 确保配置文件保存在程序运行目录
        if not os.path.isabs(config_file):
            # 如果是相对路径，保存在程序所在目录
            if getattr(sys, 'frozen', False):
                # PyInstaller 打包后的 EXE
                app_dir = os.path.dirname(sys.executable)
            else:
                # 开发环境
                app_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_file = os.path.join(app_dir, config_file)
        else:
            self.config_file = config_file

    def add_stock(self, code: str):
        if code not in self.stocks:
            self.stocks[code] = StockItem(code)
            return True
        return False

    def remove_stock(self, code: str):
        if code in self.stocks:
            del self.stocks[code]
            return True
        return False

    def update_stocks_data(self, realtime_data: List[Dict]):
        for data in realtime_data:
            code = data['code']
            if code in self.stocks:
                self.stocks[code].update_data(data)

    def get_alerting_stocks(self) -> List[StockItem]:
        return [stock for stock in self.stocks.values() if stock.is_alerting]

    def get_all_stocks(self) -> List[StockItem]:
        return list(self.stocks.values())

    def save_config(self):
        """保存股票列表和阈值配置到本地文件"""
        config_data = {
            'stocks': []
        }
        
        for stock in self.stocks.values():
            stock_config = {
                'code': stock.code,
                'name': stock.name,
                'thresholds': {
                    'upper_price': stock.upper_price,
                    'lower_price': stock.lower_price,
                    'upper_pct': stock.upper_pct,
                    'lower_pct': stock.lower_pct,
                    'upper_volume': stock.upper_volume,
                    'lower_volume': stock.lower_volume,
                    'upper_high': stock.upper_high,
                    'lower_high': stock.lower_high,
                    'upper_low': stock.upper_low,
                    'lower_low': stock.lower_low,
                    'upper_amount': stock.upper_amount,
                    'lower_amount': stock.lower_amount
                }
            }
            config_data['stocks'].append(stock_config)
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def load_config(self):
        """从本地文件加载股票列表和阈值配置"""
        if not os.path.exists(self.config_file):
            print(f"配置文件 {self.config_file} 不存在，将使用空列表")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self.stocks.clear()
            for stock_config in config_data.get('stocks', []):
                code = stock_config['code']
                stock = StockItem(code, stock_config.get('name', ''))
                
                # 恢复阈值设置
                thresholds = stock_config.get('thresholds', {})
                stock.upper_price = thresholds.get('upper_price')
                stock.lower_price = thresholds.get('lower_price')
                stock.upper_pct = thresholds.get('upper_pct')
                stock.lower_pct = thresholds.get('lower_pct')
                stock.upper_volume = thresholds.get('upper_volume')
                stock.lower_volume = thresholds.get('lower_volume')
                stock.upper_high = thresholds.get('upper_high')
                stock.lower_high = thresholds.get('lower_high')
                stock.upper_low = thresholds.get('upper_low')
                stock.lower_low = thresholds.get('lower_low')
                stock.upper_amount = thresholds.get('upper_amount')
                stock.lower_amount = thresholds.get('lower_amount')
                
                self.stocks[code] = stock
            
            print(f"成功加载 {len(self.stocks)} 只股票配置")
            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False
