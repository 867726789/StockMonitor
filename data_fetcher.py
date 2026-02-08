import pandas as pd
import time
import random
import requests
import re
from typing import List, Dict, Optional

# AkShare 作为可选依赖，如果导入失败也不影响程序运行
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("警告: AkShare 未安装或导入失败，将使用腾讯/新浪接口。")

class DataFetcher:
    """
    数据获取模块，负责从 AkShare 获取股票实时行情数据。
    支持多源备份（AkShare EM接口 -> 腾讯财经 -> 新浪财经）。
    """
    
    @staticmethod
    def get_realtime_quotes(stock_codes: List[str]) -> List[Dict]:
        """
        获取指定股票代码列表的实时行情数据。
        优先使用针对性强的“指定代码”接口，避免获取全量数据。
        """
        if not stock_codes:
            return []
            
        # 尝试 1: 腾讯财经接口 (最推荐：支持指定代码，速度极快且稳定)
        results = DataFetcher._get_from_tencent(stock_codes)
        if results and len(results) >= len(stock_codes) * 0.8:
            return results

        # 尝试 2: 新浪财经接口 (备份：同样支持指定代码)
        print("尝试 [接口 2] 新浪财经备份...")
        results = DataFetcher._get_from_sina(stock_codes)
        if results and len(results) >= len(stock_codes) * 0.8:
            return results

        # 尝试 3: AkShare 东方财富接口 (最终兜底：虽然是全量获取，但在前两个接口都挂掉时作为保障)
        if AKSHARE_AVAILABLE:
            print("尝试 [接口 3] AkShare EM 兜底...")
            try:
                df = ak.stock_zh_a_spot_em()
                if df is not None and not df.empty:
                    mask = df['代码'].isin(stock_codes)
                    filtered_df = df[mask].copy()
                    results = []
                    for _, row in filtered_df.iterrows():
                        results.append({
                            'code': str(row['代码']),
                            'name': str(row['名称']),
                            'price': float(row['最新价']) if pd.notnull(row['最新价']) else 0.0,
                            'pct_change': float(row['涨跌幅']) if pd.notnull(row['涨跌幅']) else 0.0,
                            'volume': float(row['成交量']) if pd.notnull(row['成交量']) else 0.0,
                            'high': float(row['最高']) if pd.notnull(row['最高']) else 0.0,
                            'low': float(row['最低']) if pd.notnull(row['最低']) else 0.0,
                            'amount': float(row['成交额']) if pd.notnull(row['成交额']) else 0.0
                        })
                    return results
            except Exception as e:
                print(f"AkShare 接口失败: {e}")
        
        print("所有接口获取失败，请检查网络或股票代码是否正确。")
        return []

    @staticmethod
    def _get_from_tencent(stock_codes: List[str]) -> List[Dict]:
        """从腾讯财经接口获取数据"""
        results = []
        formatted_codes = [f"sh{c}" if c.startswith(('6', '9')) else f"sz{c}" for c in stock_codes]
        url = f"http://qt.gtimg.cn/q={','.join(formatted_codes)}"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                lines = response.text.split(';')
                for line in lines:
                    parts = line.split('~')
                    if len(parts) > 40:
                        results.append({
                            'code': parts[2],
                            'name': parts[1],
                            'price': float(parts[3]),
                            'pct_change': float(parts[32]),
                            'volume': float(parts[6]),
                            'high': float(parts[33]),
                            'low': float(parts[34]),
                            'amount': float(parts[37]) * 10000 
                        })
            return results
        except Exception as e:
            print(f"腾讯接口获取失败: {e}")
        return []

    @staticmethod
    def _get_from_sina(stock_codes: List[str]) -> List[Dict]:
        """从新浪财经接口获取数据"""
        results = []
        formatted_codes = [f"sh{c}" if c.startswith(('6', '9')) else f"sz{c}" for c in stock_codes]
        url = f"http://hq.sinajs.cn/list={','.join(formatted_codes)}"
        headers = {'Referer': 'http://finance.sina.com.cn'} # 新浪接口需要 Referer
        try:
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                lines = response.text.split('\n')
                for i, line in enumerate(lines):
                    if '="' not in line: continue
                    data_str = line.split('="')[1].split('",')[0]
                    parts = data_str.split(',')
                    if len(parts) >= 30:
                        code = stock_codes[i]
                        price = float(parts[3])
                        pre_close = float(parts[2])
                        pct_change = round((price - pre_close) / pre_close * 100, 2) if pre_close != 0 else 0
                        results.append({
                            'code': code,
                            'name': parts[0],
                            'price': price,
                            'pct_change': pct_change,
                            'volume': float(parts[8]) / 100, # 新浪成交量单位是股，转为手
                            'high': float(parts[4]),
                            'low': float(parts[5]),
                            'amount': float(parts[9])
                        })
            return results
        except Exception as e:
            print(f"新浪接口获取失败: {e}")
        return []

if __name__ == "__main__":
    # 测试代码
    fetcher = DataFetcher()
    test_codes = ['600000', '000001']
    data = fetcher.get_realtime_quotes(test_codes)
    print(data)
