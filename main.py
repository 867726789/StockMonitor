import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from data_fetcher import DataFetcher
from monitor_engine import MonitorEngine
from gui.main_window import MainWindow
from gui.alert_window import AlertWindow

def main():
    app = QApplication(sys.argv)
    
    fetcher = DataFetcher()
    engine = MonitorEngine()
    
    main_window = MainWindow(engine, fetcher)
    alert_window = AlertWindow()
    
    def refresh_data():
        stock_codes = [s.code for s in engine.get_all_stocks()]
        if stock_codes:
            data = fetcher.get_realtime_quotes(stock_codes)
            engine.update_stocks_data(data)
            main_window.refresh_table()
            
            alerting_stocks = engine.get_alerting_stocks()
            alert_window.update_alerts(alerting_stocks)

    # 设置定时器，每 5 秒刷新一次
    timer = QTimer()
    timer.timeout.connect(refresh_data)
    timer.start(5000)
    
    main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
