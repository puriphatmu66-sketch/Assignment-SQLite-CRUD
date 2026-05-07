import sys
import sqlite3
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

class DatabaseManager:
    def __init__(self, db_name="users.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL,
            year  TEXT,
            admin INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(sql)
        self.conn.commit()

    def add_user(self, name, year, admin):
        sql = "INSERT INTO users (name, year, admin) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (name, year, 1 if admin else 0))
        self.conn.commit()

    def get_all_users(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()

    def update_user(self, user_id, name, year, admin):
        sql = "UPDATE users SET name=?, year=?, admin=? WHERE id=?"
        self.cursor.execute(sql, (name, year, 1 if admin else 0, user_id))
        self.conn.commit()

    def delete_user(self, user_id):
        self.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("โปรแกรมทดสอบ - user.ui")
        self.resize(800, 600)

        self.db = DatabaseManager()
        self.selected_id = None

        self._build_ui()
        self._connect_signals()
        self.load_data()


    def _build_ui(self):
        from PySide6.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
            QTableWidget, QTableWidgetItem, QHeaderView,
            QLineEdit, QCheckBox, QPushButton, QLabel,
            QMenuBar, QMenu
        )

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "NAME", "YEAR", "Admin"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.tableWidget, stretch=1)

        input_widget = QWidget()
        grid = QGridLayout(input_widget)
        grid.setContentsMargins(0, 6, 0, 0)

        grid.addWidget(QLabel("Name"), 0, 0)
        self.lineEditName = QLineEdit()
        grid.addWidget(self.lineEditName, 0, 1)
        self.btnAdd = QPushButton("Add")
        self.btnAdd.setMinimumWidth(100)
        grid.addWidget(self.btnAdd, 0, 2)
        self.btnUpdate = QPushButton("Update")
        self.btnUpdate.setMinimumWidth(100)
        grid.addWidget(self.btnUpdate, 0, 3)

        grid.addWidget(QLabel("Year"), 1, 0)
        year_row = QHBoxLayout()
        self.lineEditYear = QLineEdit()
        self.lineEditYear.setMaximumWidth(160)
        year_row.addWidget(self.lineEditYear)
        self.checkBoxAdmin = QCheckBox("Admin")
        year_row.addWidget(self.checkBoxAdmin)
        year_row.addStretch()
        grid.addLayout(year_row, 1, 1)
        self.btnDel = QPushButton("Del")
        self.btnDel.setMinimumWidth(100)
        grid.addWidget(self.btnDel, 1, 2)

        main_layout.addWidget(input_widget)

        menubar = self.menuBar()
        menubar.addMenu("File")


    def _connect_signals(self):
        self.btnAdd.clicked.connect(self.create_data)
        self.btnUpdate.clicked.connect(self.update_data)
        self.btnDel.clicked.connect(self.delete_data)
        self.tableWidget.cellClicked.connect(self.select_data)

    def load_data(self):
        rows = self.db.get_all_users()
        self.tableWidget.setRowCount(0)
        for row_num, row_data in enumerate(rows):
            self.tableWidget.insertRow(row_num)
            for col_num, value in enumerate(row_data):
                if col_num == 3:          # คอลัมน์ Admin → แสดง Yes/No
                    display = "Yes" if value else "No"
                    item = QTableWidgetItem(display)
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row_num, col_num, item)

    def select_data(self, row):
        id_item   = self.tableWidget.item(row, 0)
        name_item = self.tableWidget.item(row, 1)
        year_item = self.tableWidget.item(row, 2)
        adm_item  = self.tableWidget.item(row, 3)

        if id_item:
            self.selected_id = id_item.text()
            self.lineEditName.setText(name_item.text() if name_item else "")
            self.lineEditYear.setText(year_item.text() if year_item else "")
            self.checkBoxAdmin.setChecked(
                adm_item.text() == "Yes" if adm_item else False
            )

    def create_data(self):
        name  = self.lineEditName.text().strip()
        year  = self.lineEditYear.text().strip()
        admin = self.checkBoxAdmin.isChecked()

        if not name:
            QMessageBox.warning(self, "Error", "กรุณากรอกชื่อ")
            return

        self.db.add_user(name, year, admin)
        self.load_data()
        self._clear_inputs()
        QMessageBox.information(self, "Success", "บันทึกข้อมูลเรียบร้อย!")

  
    def update_data(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Warning", "กรุณาเลือกรายการที่ต้องการแก้ไข")
            return

        name  = self.lineEditName.text().strip()
        year  = self.lineEditYear.text().strip()
        admin = self.checkBoxAdmin.isChecked()

        if not name:
            QMessageBox.warning(self, "Error", "กรุณากรอกชื่อ")
            return

        self.db.update_user(self.selected_id, name, year, admin)
        self.load_data()
        self._clear_inputs()
        QMessageBox.information(self, "Success", "แก้ไขข้อมูลเรียบร้อย!")

    def delete_data(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Warning", "กรุณาเลือกรายการที่ต้องการลบ")
            return

        confirm = QMessageBox.question(
            self, "Confirm", "ต้องการลบข้อมูลนี้ใช่หรือไม่?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.db.delete_user(self.selected_id)
            self.load_data()
            self._clear_inputs()

    def _clear_inputs(self):
        self.lineEditName.clear()
        self.lineEditYear.clear()
        self.checkBoxAdmin.setChecked(False)
        self.selected_id = None

    def closeEvent(self, event):
        self.db.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
