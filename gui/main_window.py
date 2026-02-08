from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QLabel, QHeaderView, QFormLayout, QDoubleSpinBox, 
                             QCheckBox, QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

class MainWindow(QMainWindow):
    def __init__(self, engine, fetcher):
        super().__init__()
        self.engine = engine
        self.fetcher = fetcher
        self.setWindowTitle("股市实时监听系统")
        self.resize(1200, 650)

        # 数据字段配置（中文名、字段key、是否默认显示）
        self.data_fields = {
            'price': {'name': '最新价', 'enabled': True},
            'pct_change': {'name': '涨跌幅(%)', 'enabled': True},
            'volume': {'name': '成交量(手)', 'enabled': False},
            'high': {'name': '最高价', 'enabled': False},
            'low': {'name': '最低价', 'enabled': False},
            'amount': {'name': '成交额(元)', 'enabled': False}
        }

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # 左侧列表区
        left_layout = QVBoxLayout()
        
        # 数据展示选择区
        display_group = QGroupBox("数据展示选择")
        display_layout = QHBoxLayout()
        self.field_checkboxes = {}
        for field_key, field_info in self.data_fields.items():
            cb = QCheckBox(field_info['name'])
            cb.setChecked(field_info['enabled'])
            cb.stateChanged.connect(self.on_field_selection_changed)
            self.field_checkboxes[field_key] = cb
            display_layout.addWidget(cb)
        display_group.setLayout(display_layout)
        left_layout.addWidget(display_group)
        
        # 添加股票
        add_layout = QHBoxLayout()
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("输入股票代码 (如 600000)")
        self.add_btn = QPushButton("添加监控")
        self.add_btn.clicked.connect(self.add_stock)
        add_layout.addWidget(self.code_input)
        add_layout.addWidget(self.add_btn)
        left_layout.addLayout(add_layout)

        # 股票表格
        self.table = QTableWidget()
        self.update_table_columns()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.table)
        
        main_layout.addLayout(left_layout, 2)

        # 右侧设置区
        right_layout = QVBoxLayout()
        
        # 使用滚动区域包裹阈值设置
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        scroll_layout.addWidget(QLabel("监控阈值设置"))
        
        # 动态生成阈值输入框
        self.threshold_widgets = {}
        self.threshold_form = QFormLayout()
        
        for field_key, field_info in self.data_fields.items():
            upper_sb = QDoubleSpinBox()
            upper_sb.setRange(0, 999999)
            upper_sb.setDecimals(2)
            lower_sb = QDoubleSpinBox()
            lower_sb.setRange(-999999, 999999)
            lower_sb.setDecimals(2)
            
            self.threshold_widgets[field_key] = {
                'upper': upper_sb,
                'lower': lower_sb,
                'upper_label': QLabel(f"{field_info['name']}上限:"),
                'lower_label': QLabel(f"{field_info['name']}下限:")
            }
            
            self.threshold_form.addRow(self.threshold_widgets[field_key]['upper_label'], upper_sb)
            self.threshold_form.addRow(self.threshold_widgets[field_key]['lower_label'], lower_sb)
        
        scroll_layout.addLayout(self.threshold_form)
        
        self.save_threshold_btn = QPushButton("保存阈值设置")
        self.save_threshold_btn.clicked.connect(self.save_thresholds)
        scroll_layout.addWidget(self.save_threshold_btn)
        
        self.remove_btn = QPushButton("移除选中股票")
        self.remove_btn.clicked.connect(self.remove_stock)
        self.remove_btn.setStyleSheet("background-color: #ff4d4d; color: white;")
        scroll_layout.addWidget(self.remove_btn)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        right_layout.addWidget(scroll_area)
        
        main_layout.addLayout(right_layout, 1)
        
        # 初始化时更新阈值控件可见性
        self.update_threshold_visibility()

    def on_field_selection_changed(self):
        """字段选择改变时更新表格和阈值设置"""
        self.update_table_columns()
        self.update_threshold_visibility()
        self.refresh_table()

    def update_table_columns(self):
        """根据勾选状态更新表格列"""
        headers = ["代码", "名称"]
        for field_key, checkbox in self.field_checkboxes.items():
            if checkbox.isChecked():
                headers.append(self.data_fields[field_key]['name'])
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

    def update_threshold_visibility(self):
        """根据勾选状态显示/隐藏对应的阈值设置"""
        for field_key, checkbox in self.field_checkboxes.items():
            visible = checkbox.isChecked()
            self.threshold_widgets[field_key]['upper'].setVisible(visible)
            self.threshold_widgets[field_key]['lower'].setVisible(visible)
            self.threshold_widgets[field_key]['upper_label'].setVisible(visible)
            self.threshold_widgets[field_key]['lower_label'].setVisible(visible)

    def add_stock(self):
        code = self.code_input.text().strip()
        if code:
            if self.engine.add_stock(code):
                self.refresh_table()
                self.code_input.clear()
                self.engine.save_config()  # 保存配置

    def remove_stock(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        code = self.table.item(selected_items[0].row(), 0).text()
        self.engine.remove_stock(code)
        self.refresh_table()
        self.engine.save_config()  # 保存配置

    def on_selection_changed(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        code = self.table.item(selected_items[0].row(), 0).text()
        stock = self.engine.stocks.get(code)
        if stock:
            # 加载当前股票的阈值设置
            self.threshold_widgets['price']['upper'].setValue(stock.upper_price if stock.upper_price is not None else 0)
            self.threshold_widgets['price']['lower'].setValue(stock.lower_price if stock.lower_price is not None else 0)
            self.threshold_widgets['pct_change']['upper'].setValue(stock.upper_pct if stock.upper_pct is not None else 0)
            self.threshold_widgets['pct_change']['lower'].setValue(stock.lower_pct if stock.lower_pct is not None else 0)
            
            # 其他字段阈值（如果 StockItem 支持）
            for field in ['volume', 'high', 'low', 'amount']:
                upper_attr = f'upper_{field}'
                lower_attr = f'lower_{field}'
                if hasattr(stock, upper_attr):
                    self.threshold_widgets[field]['upper'].setValue(getattr(stock, upper_attr) or 0)
                if hasattr(stock, lower_attr):
                    self.threshold_widgets[field]['lower'].setValue(getattr(stock, lower_attr) or 0)

    def save_thresholds(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        code = self.table.item(selected_items[0].row(), 0).text()
        stock = self.engine.stocks.get(code)
        if stock:
            # 保存价格和涨跌幅阈值
            up = self.threshold_widgets['price']['upper'].value()
            lp = self.threshold_widgets['price']['lower'].value()
            uct = self.threshold_widgets['pct_change']['upper'].value()
            lct = self.threshold_widgets['pct_change']['lower'].value()
            
            stock.set_thresholds(
                upper_price=up if up > 0 else None,
                lower_price=lp if lp > 0 else None,
                upper_pct=uct if uct != 0 else None,
                lower_pct=lct if lct != 0 else None
            )
            
            # 保存其他字段阈值（如果需要扩展）
            for field in ['volume', 'high', 'low', 'amount']:
                upper_val = self.threshold_widgets[field]['upper'].value()
                lower_val = self.threshold_widgets[field]['lower'].value()
                setattr(stock, f'upper_{field}', upper_val if upper_val > 0 else None)
                setattr(stock, f'lower_{field}', lower_val if lower_val != 0 else None)
            
            self.engine.save_config()  # 保存配置

    def refresh_table(self):
        stocks = self.engine.get_all_stocks()
        self.table.setRowCount(len(stocks))
        
        for i, stock in enumerate(stocks):
            col = 0
            # 代码和名称固定显示
            self.table.setItem(i, col, QTableWidgetItem(stock.code))
            col += 1
            self.table.setItem(i, col, QTableWidgetItem(stock.name))
            col += 1
            
            # 根据勾选状态显示其他字段
            for field_key, checkbox in self.field_checkboxes.items():
                if checkbox.isChecked():
                    value = getattr(stock, field_key, 0)
                    
                    # 特殊处理涨跌幅显示
                    if field_key == 'pct_change':
                        item = QTableWidgetItem(f"{value}%")
                        if value > 0:
                            item.setForeground(QColor("red"))
                        elif value < 0:
                            item.setForeground(QColor("green"))
                    else:
                        item = QTableWidgetItem(str(value))
                    
                    self.table.setItem(i, col, item)
                    col += 1
            
            # 如果触发预警，整行背景变色
            if stock.is_alerting:
                for j in range(self.table.columnCount()):
                    if self.table.item(i, j):
                        self.table.item(i, j).setBackground(QColor("#ffcccc"))
