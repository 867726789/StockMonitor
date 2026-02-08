"""
测试新增的数据展示选择功能
"""
import sys
from PyQt6.QtWidgets import QApplication
from test_data_fetcher import TestDataFetcher
from monitor_engine import MonitorEngine, StockItem

# 测试 StockItem 是否有新增的字段
def test_stock_item():
    print("=== 测试 StockItem 数据字段 ===")
    stock = StockItem("600000", "测试股票")
    
    # 测试更新数据
    test_data = {
        'code': '600000',
        'name': '浦发银行',
        'price': 10.12,
        'pct_change': -1.08,
        'volume': 759256.0,
        'high': 10.27,
        'low': 10.06,
        'amount': 769320000.0
    }
    
    stock.update_data(test_data)
    
    print(f"代码: {stock.code}")
    print(f"名称: {stock.name}")
    print(f"价格: {stock.price}")
    print(f"涨跌幅: {stock.pct_change}")
    print(f"成交量: {stock.volume}")
    print(f"最高价: {stock.high}")
    print(f"最低价: {stock.low}")
    print(f"成交额: {stock.amount}")
    
    # 测试阈值设置
    print("\n=== 测试阈值设置 ===")
    stock.upper_volume = 800000
    stock.lower_amount = 700000000
    stock.check_alerts()
    
    print(f"是否触发预警: {stock.is_alerting}")
    print(f"预警原因: {stock.alert_reasons}")
    
    print("\n✓ StockItem 测试通过")

if __name__ == "__main__":
    test_stock_item()
    print("\n所有测试完成！")
