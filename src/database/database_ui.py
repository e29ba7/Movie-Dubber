from PyQt6.QtCore import QRect
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtWidgets import QTableView, QAbstractItemView, QLabel

from database import data_jaboody
from utils import Button, DialogWindow


class Ui_Database(DialogWindow):
    def __init__(self):
        super().__init__('database.ico', 'Movie Dub Database', 638, 770)
        self.data : list = []
        '''Database load'''
        self.load_database()
        '''SQLite Table Model'''
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
        self.load_button = Button('Load', self)
        self.load_button.setGeometry(QRect(256, 737, 71, 21))
        self.load_button.setDefault(True)
        self.load_button.clicked.connect(self.load_data)
        '''Cancel button'''
        self.cancel_button = Button('Cancel', self)
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
        self.accept()

    '''Cancel loading from database and close window'''
    def cancel_load(self):
        self.db.close()
        self.close()

    '''Generate database and load into memory'''
    def load_database(self):
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(":memory:")
        self.db.open()
        self.db.transaction()
        self.db.exec("""
            CREATE TABLE dubs (
            Movie VARCHAR(250) NOT NULL,
            Year VARCHAR(250) NOT NULL,
            Length VARCHAR(250),
            Delay VARCHAR(250) DEFAULT 0,
            Attenuation VARCHAR(250) DEFAULT 0.0,
            Volume VARCHAR(250) DEFAULT 0,
            PRIMARY KEY (Movie, Year))"""
            )
        self.db.commit()
        for dic in data_jaboody.Movies:
            self.db.transaction()
            self.db.exec(r'''
                INSERT OR IGNORE INTO dubs VALUES(
                "{}", {}, "{}", "{}", "{}", "{}")'''
                .format(
                    dic['Movie'],
                    dic['Year'],
                    dic['Length'],
                    dic['Delay'],
                    dic['Attenuation'],
                    dic['Volume']
                    )
                )
            self.db.commit()
