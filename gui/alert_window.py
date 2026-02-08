from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLabel, QHeaderView, QPushButton,
                             QDialog, QFormLayout, QDoubleSpinBox, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

class ThresholdEditDialog(QDialog):
    """阈值编辑对话框"""
    def __init__(self, stock, parent=None):
        super().__init__(parent)
        self.stock = stock
        self.setWindowTitle(f"编辑阈值 - {stock.code} {stock.name}")
        self.resize(400, 350)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # 价格阈值
        self.upper_price_sb = QDoubleSpinBox()
        self.upper_price_sb.setRange(0, 999999)
        self.upper_price_sb.setDecimals(2)
        self.upper_price_sb.setValue(stock.upper_price if stock.upper_price is not None else 0)
        
        self.lower_price_sb = QDoubleSpinBox()
        self.lower_price_sb.setRange(0, 999999)
        self.lower_price_sb.setDecimals(2)
        self.lower_price_sb.setValue(stock.lower_price if stock.lower_price is not None else 0)
        
        # 涨跌幅阈值
        self.upper_pct_sb = QDoubleSpinBox()
        self.upper_pct_sb.setRange(-100, 100)
        self.upper_pct_sb.setDecimals(2)
        self.upper_pct_sb.setValue(stock.upper_pct if stock.upper_pct is not None else 0)
        
        self.lower_pct_sb = QDoubleSpinBox()
        self.lower_pct_sb.setRange(-100, 100)
        self.lower_pct_sb.setDecimals(2)
        self.lower_pct_sb.setValue(stock.lower_pct if stock.lower_pct is not None else 0)
        
        form.addRow("价格上限:", self.upper_price_sb)
        form.addRow("价格下限:", self.lower_price_sb)
        form.addRow("涨幅上限(%):", self.upper_pct_sb)
        form.addRow("跌幅下限(%):", self.lower_pct_sb)
        
        layout.addLayout(form)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                     QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_thresholds(self):
        """获取用户设置的阈值"""
        return {
            'upper_price': self.upper_price_sb.value() if self.upper_price_sb.value() > 0 else None,
            'lower_price': self.lower_price_sb.value() if self.lower_price_sb.value() > 0 else None,
            'upper_pct': self.upper_pct_sb.value() if self.upper_pct_sb.value() != 0 else None,
            'lower_pct': self.lower_pct_sb.value() if self.lower_pct_sb.value() != 0 else None
        }

class AlertWindow(QWidget):
    # 定义信号，用于通知主窗口刷新
    data_changed = pyqtSignal()
    
    def __init__(self, engine=None):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("股票预警窗口")
        self.resize(800, 400)
        
        layout = QVBoxLayout()
        self.label = QLabel("以下股票已触发阈值：")
        layout.addWidget(self.label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["代码", "名称", "当前价", "预警原因", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def edit_threshold(self, stock):
        """编辑股票阈值"""
        if not self.engine:
            return
        
        dialog = ThresholdEditDialog(stock, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            thresholds = dialog.get_thresholds()
            stock.set_thresholds(
                upper_price=thresholds['upper_price'],
                lower_price=thresholds['lower_price'],
                upper_pct=thresholds['upper_pct'],
                lower_pct=thresholds['lower_pct']
            )
            self.engine.save_config()
            self.data_changed.emit()  # 发射信号通知主窗口刷新
    
    def delete_stock(self, code):
        """删除股票"""
        if not self.engine:
            return
        
        self.engine.remove_stock(code)
        self.engine.save_config()
        self.data_changed.emit()  # 发射信号通知主窗口刷新

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
            
            self.table.setItem(row, 0, code_item)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, price_item)
            self.table.setItem(row, 3, reason_item)
            
            # 添加操作按钮
            button_widget = QWidget()
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(5, 2, 5, 2)
            
            edit_btn = QPushButton("编辑阈值")
            edit_btn.clicked.connect(lambda checked, s=stock: self.edit_threshold(s))
            edit_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, c=stock.code: self.delete_stock(c))
            delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")
            
            button_layout.addWidget(edit_btn)
            button_layout.addWidget(delete_btn)
            button_widget.setLayout(button_layout)
            
            self.table.setCellWidget(row, 4, button_widget)
        
        if len(alerting_stocks) > 0:
            self.show()
        else:
            self.hide()
