from PyQt6.QtCore import QRect
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtWidgets import QTableView, QAbstractItemView, QPushButton, QLabel

from database import dics2db
from library import DialogWindow


class Ui_Database(DialogWindow):
    def __init__(self):
        super().__init__('database.ico', 'Movie Dub Database', 638, 770)
        dics2db.DictionaryToDatabase()
        self.data : list = []
        '''Database load'''
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName("database.db")
        self.db.open()
        self.model = QSqlTableModel()
        self.model.setTable('dubs')
        self.model.select()
        '''SQLite Table Viewer'''
        self.table = QTableView(self)
        self.table.setGeometry(QRect(10, 28, 620, 699))
        self.table.setModel(self.model)
        self.table.setCornerButtonEnabled(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.doubleClicked.connect(self.load_data)
        self.table.show()
        '''Load button'''
        self.load_button = QPushButton(self)
        self.load_button.setText('Load')
        self.load_button.setGeometry(QRect(256, 737, 71, 21))
        self.load_button.clicked.connect(self.load_data)
        '''Cancel button'''
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.setGeometry(QRect(333, 737, 71, 21))
        self.cancel_button.clicked.connect(self.cancel_load)
        '''Execute'''
        self.exec()

    #################
    #|  FUNCTIONS  |#
    #################

    '''Get selected row data and close window'''
    def load_data(self):
        for row in self.table.selectedIndexes():
            self.data.append(row.data())
        Ui_Database.accept(self)

    '''Cancel loading from database and close window'''
    def cancel_load(self):
        self.db.close()
        self.close()
