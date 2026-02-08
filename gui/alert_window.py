from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class AlertWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("股票预警窗口")
        self.resize(500, 300)
        
        layout = QVBoxLayout()
        self.label = QLabel("以下股票已触发阈值：")
        layout.addWidget(self.label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["代码", "名称", "当前价", "预警原因"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def update_alerts(self, alerting_stocks):
        self.table.setRowCount(0)
        for stock in alerting_stocks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            code_item = QTableWidgetItem(stock.code)
            name_item = QTableWidgetItem(stock.name)
            price_item = QTableWidgetItem(str(stock.price))
            reason_item = QTableWidgetItem("; ".join(stock.alert_reasons))
            
            # 标红显示
            for item in [code_item, name_item, price_item, reason_item]:
                item.setForeground(QColor("red"))
                self.table.setItem(row, [0, 1, 2, 3][[code_item, name_item, price_item, reason_item].index(item)], item)
        
        if len(alerting_stocks) > 0:
            self.show()
        else:
            self.hide()
