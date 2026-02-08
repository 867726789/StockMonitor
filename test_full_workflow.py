"""
完整的端到端测试：模拟用户使用流程
"""
from monitor_engine import MonitorEngine
from data_fetcher import DataFetcher
import os
import time

def test_full_workflow():
    print("=== 股市监听系统 - 完整流程测试 ===\n")
    
    # 步骤 1: 创建引擎
    print("1. 初始化监控引擎...")
    engine = MonitorEngine("test_workflow_config.json")
    fetcher = DataFetcher()
    
    # 步骤 2: 添加股票
    print("\n2. 添加监控股票...")
    engine.add_stock("600000")
    engine.add_stock("000001")
    print(f"   已添加 {len(engine.stocks)} 只股票")
    
    # 步骤 3: 获取实时数据
    print("\n3. 获取实时行情数据...")
    stock_codes = [s.code for s in engine.get_all_stocks()]
    data = fetcher.get_realtime_quotes(stock_codes)
    if data:
        print(f"   成功获取 {len(data)} 只股票的数据")
        engine.update_stocks_data(data)
        for stock in engine.get_all_stocks():
            print(f"   - {stock.code} {stock.name}: ¥{stock.price} ({stock.pct_change}%)")
    
    # 步骤 4: 设置阈值
    print("\n4. 设置监控阈值...")
    stock1 = engine.stocks["600000"]
    stock1.upper_price = stock1.price + 0.5 if stock1.price > 0 else 12.0
    stock1.lower_price = stock1.price - 0.5 if stock1.price > 0 else 9.0
    print(f"   {stock1.code} 价格阈值: {stock1.lower_price} - {stock1.upper_price}")
    
    # 步骤 5: 保存配置
    print("\n5. 保存配置到本地...")
    if engine.save_config():
        print(f"   ✓ 配置已保存到: {engine.config_file}")
    
    # 步骤 6: 模拟程序重启
    print("\n6. 模拟程序重启，加载配置...")
    engine2 = MonitorEngine("test_workflow_config.json")
    if engine2.load_config():
        print(f"   ✓ 成功加载 {len(engine2.stocks)} 只股票")
        for stock in engine2.get_all_stocks():
            print(f"   - {stock.code} {stock.name}")
            if stock.upper_price:
                print(f"     价格阈值: {stock.lower_price} - {stock.upper_price}")
    
    # 步骤 7: 检查预警
    print("\n7. 检查预警状态...")
    engine2.update_stocks_data(data)
    alerting = engine2.get_alerting_stocks()
    if alerting:
        print(f"   ⚠ 发现 {len(alerting)} 只股票触发预警:")
        for stock in alerting:
            print(f"   - {stock.code}: {', '.join(stock.alert_reasons)}")
    else:
        print("   ✓ 暂无股票触发预警")
    
    # 清理
    print("\n8. 清理测试文件...")
    if os.path.exists("test_workflow_config.json"):
        os.remove("test_workflow_config.json")
        print("   ✓ 测试文件已删除")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_full_workflow()
