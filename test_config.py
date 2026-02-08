"""
测试配置保存和加载功能
"""
from monitor_engine import MonitorEngine
import os

def test_save_and_load():
    print("=== 测试配置保存和加载 ===\n")
    
    # 创建测试引擎
    engine = MonitorEngine("test_config.json")
    
    # 添加股票并设置阈值
    print("1. 添加股票...")
    engine.add_stock("600000")
    engine.add_stock("000001")
    
    stock1 = engine.stocks["600000"]
    stock1.name = "浦发银行"
    stock1.upper_price = 12.0
    stock1.lower_price = 9.0
    stock1.upper_pct = 5.0
    stock1.lower_pct = -5.0
    stock1.upper_volume = 1000000
    
    stock2 = engine.stocks["000001"]
    stock2.name = "平安银行"
    stock2.upper_price = 13.0
    stock2.lower_pct = -3.0
    
    print(f"   添加了 {len(engine.stocks)} 只股票")
    
    # 保存配置
    print("\n2. 保存配置...")
    if engine.save_config():
        print("   ✓ 配置保存成功")
    
    # 清空当前配置
    print("\n3. 清空内存配置...")
    engine.stocks.clear()
    print(f"   当前股票数量: {len(engine.stocks)}")
    
    # 加载配置
    print("\n4. 从文件加载配置...")
    if engine.load_config():
        print("   ✓ 配置加载成功")
    
    # 验证加载结果
    print("\n5. 验证加载的数据:")
    for code, stock in engine.stocks.items():
        print(f"\n   股票代码: {stock.code}")
        print(f"   股票名称: {stock.name}")
        print(f"   价格上限: {stock.upper_price}")
        print(f"   价格下限: {stock.lower_price}")
        print(f"   涨幅上限: {stock.upper_pct}%")
        print(f"   跌幅下限: {stock.lower_pct}%")
        print(f"   成交量上限: {stock.upper_volume}")
    
    # 清理测试文件
    print("\n6. 清理测试文件...")
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
        print("   ✓ 测试文件已删除")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_save_and_load()
