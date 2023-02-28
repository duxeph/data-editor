try:
    from PyQt5.QtWidgets import *
    from PyQt5.uic import loadUi
    from PyQt5.QtGui import QFontMetrics
except ImportError as e:
    with open(os.getcwd()+"/log.txt", "w") as file:
        file.write(os.popen(f"pip install -r {os.getcwd()}/requirements.txt").read())
    try:
        from PyQt5.QtWidgets import *
        from PyQt5.uic import loadUi
        from PyQt5.QtGui import QFontMetrics
    except ImportError as e:
        print("[EXCEPTION] Something has gone wrong. Please provide requirements.txt before running again.")
        sys.exit()

from pandas import read_csv
from json import dumps

import os
import sys

class windowTwo(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        loadUi(os.getcwd()+"/gui/script.ui", self)
        
        self.textEdit.setTabStopDistance(QFontMetrics(self.textEdit.font()).horizontalAdvance(' ') * 4)

class window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.mainPath = os.getcwd()
        loadUi(self.mainPath+"/gui/main.ui", self)

        self.initialized = False
        self.sep = ","
        self.openButton.clicked.connect(self.choosePath)
        self.sepLine.textChanged.connect(self.sepChanged)
        
        self.tableWidget.clicked.connect(self.cellClicked)

        self.filterButton.clicked.connect(self.filterApplying)
        self.columnEditButton.clicked.connect(self.columnEditor)
        self.columnCreationButton.clicked.connect(self.columnCreator)
        self.toolButton1.clicked.connect(self.help1)
        self.toolButton2.clicked.connect(self.help2)
        self.toolButton3.clicked.connect(self.help3)
        
        self.saveButton.clicked.connect(self.saveChanges)
        self.reloadDataButton.clicked.connect(self.reloadData)
        self.commandBoxButton.clicked.connect(self.openCommandBox)
    
    ####################################################################################### # back-side - deep
    def cellClicked(self, index):
        print('[INFO]', index, "clicked.")
    #######################################################################################
    def reloadData(self):
        self.data = read_csv(self.path, sep=self.sep)
        self.configureTable()
    def sepChanged(self):
        temp = self.sep
        self.sep = self.sepLine.text() if self.sepLine.text()!="" else self.sep
        if self.initialized:
            try:
                self.reloadData()
            except:
                self.sep = temp
                print("[EXCEPTION] Could not change seperator.")
    def choosePath(self):
        try:
            self.sep = self.sepLine.text()
            self.path = str(QFileDialog.getOpenFileName(self, "Select a file to open")[0])
            self.data = read_csv(self.path, sep=self.sep)
            self.configureTable()
            print(self.path)
            
            if not self.initialized:
                self.filterButton.setEnabled(True)
                self.columnEditButton.setEnabled(True)
                self.columnCreationButton.setEnabled(True)
                
                self.saveButton.setEnabled(True)
                self.reloadDataButton.setEnabled(True)
                self.commandBoxButton.setEnabled(True)
                
                self.initialized = True
        except:
            print("[EXCEPTION] A problem is occured during selectin of path. Please try again with a valid path.")
    #######################################################################################
    def help1(self):
        msg = "Enter as: column, operation, value\nAs column, you can enter either column name or index\nAvailable operations: <, >, <=, >=, ==\nExample: column_1,<,50"
        QMessageBox.about(self, "Filtering info", msg,)
    def help2(self):
        msg = "Enter as: type, index 1, index 2, operation, index 3\nAvailable types: iloc/loc (iloc for index, loc for column name(s))\nAvailable operations: [del]ete, [copy], [move]\nExample: iloc,0,2,move,-2\nNote: If you choose to use copy, columns between index 1 and 2 will be copied to index 3."
        QMessageBox.about(self, "Column edition info", msg,)
    def help3(self):
        msg = "Enter as: type, index 1, index 2, operation\nAvailable types: iloc/loc (iloc for index, loc for column name(s)\nAvailable operations: +, -, *, /, **(^), %\nExample: iloc,0,2,**\nNote: Assume you choose to use +, result will be the addition of the columns at index 1 and 2."
        QMessageBox.about(self, "Column creation info", msg,)
    ####################################################################################### # command box
    def openCommandBox(self):
        self.commandBox = windowTwo()
        self.commandBox.show()

        self.commandBox.applyButton.clicked.connect(self.applyCommand)
        self.commandBox.saveButton.clicked.connect(self.saveScript)
        self.commandBox.loadButton.clicked.connect(self.loadScript)

        self.commandBox.exitButton.clicked.connect(self.commandBox.close)
    def applyCommand(self):
        command = self.commandBox.textEdit.toPlainText().replace('\t', ' '*4)
        with open(self.mainPath+'\\script.py', 'w') as file:
            file.write(command)
        print("[LOG] Written...")

        import script
        from importlib import reload
        reload(script)
        self.data = script.main(self.data)
        print("[LOG] Loaded and applied...")

        os.remove(self.mainPath+'\\script.py')
        print("[LOG] Removed...")
        
        if len(self.data.shape) < 2:
            self.data = self.data.to_frame()
            print("[LOG] Completed.")
        self.configureTable()

        self.commandBox.close()
    def saveScript(self):
        command = self.commandBox.textEdit.toPlainText().replace('\t', ' '*4)

        """for i in range(100):
            if i == 0:
                name = self.mainPath+'\\scripts\\script.py'
            else:
                name = self.mainPath+f'\\scripts\\script ({i}).py'
            if not os.path.exists(self.mainPath+"\\scripts"):
                os.mkdir(self.mainPath+"\\scripts")
            if not os.path.isfile(name):
                with open(name, 'w') as file:
                    file.write(command)
                break"""
        path = QFileDialog.getSaveFileName(self, 'Save as..', os.getcwd())[0]
        if path=="":
            print("[EXCEPTION] Did not select any path. Aborting..")
        else:
            with open(path, 'w') as file:
                file.write(command)
    def loadScript(self):
        path = QFileDialog.getOpenFileName(self, 'Select a script..', os.getcwd())[0]
        if path=="":
            print("[EXCEPTION] Did not select any path. Aborting..")
        else:
            with open(path) as file:
                command = file.read()
            self.commandBox.textEdit.setText(command)
    ####################################################################################### # upper three
    def filterApplying(self):
        filter = self.filterText.text().split(',')
        try:
            col, op, var = filter[0], filter[1], filter[2]
        except:
            print("[EXCEPTION] Invalid input.")
            return

        try:
            var = float(var)
        except:
            print('[EXCEPTION] You have to give a numeric value for int type filtering operations.')
            return

        try:
            col = int(col)
            col = self.data.columns[col]
        except:
            col = col

        if op == '<':
            self.data = self.data[self.data[col]<var]
        elif op == '>':
            self.data = self.data[self.data[col]>var]
        elif op == '<=':
            self.data = self.data[self.data[col]<=var]
        elif op == '>=':
            self.data = self.data[self.data[col]>=var]
        elif op == '==':
            self.data = self.data[self.data[col]==var]
        else:
            print('[EXCEPTION] No operation has been found for the chosen operator and value.')
            return

        self.configureTable()

    def columnEditor(self):
        """
        iloc, index_1, index_2, del
                                copy, index_new
                                move, index_new
        loc, key_1, key_2, del
                           copy, key_new
                           move, key_new
        """
        try:
            editor = self.columnEditText.text().split(',')

            if len(editor) == 5:
                if editor[0] == 'iloc':
                    editor[1], editor[2], editor[4] = int(editor[1]), int(editor[2]), int(editor[4])
                    for i in [1, 2, 4]:
                        if editor[i] < 0:
                            editor[i] = self.data.shape[1] + editor[i]
                    if editor[4] > editor[2]:
                        editor[4] += editor[2] - editor[1]
                elif editor[0] == 'loc':
                    editor[1], editor[2], editor[4] = list(self.data.columns).index(editor[1]), list(self.data.columns).index(editor[2]), list(self.data.columns).index(editor[4])
            elif len(editor) == 4:
                if editor[0] == 'iloc':
                    editor[1], editor[2] = int(editor[1]), int(editor[2])
                    for i in [1, 2]:
                        if editor[i] < 0:
                            editor[i] = self.data.shape[1] + editor[i]
                elif editor[0] == 'loc':
                    editor[1], editor[2] = list(self.data.columns).index(editor[1]), list(self.data.columns).index(editor[2])

            if editor[3] == 'del':
                self.data = self.iloc_del_function(editor[1], editor[2])
            elif editor[3] == 'copy':
                self.data = self.iloc_copy_function(editor[1], editor[2], editor[4])
            elif editor[3] == 'move':
                self.data = self.iloc_copy_function(editor[1], editor[2], editor[4])
                self.data = self.iloc_del_function(editor[1], editor[2])

                cols = []
                for i in range(self.data.shape[1]):
                    column = self.data.columns[i]
                    if column.endswith('_copy'):
                        cols.append(column[:-5])
                    else:
                        cols.append(column)
                self.data.columns = cols
        except:
            print("[EXCEPTION] Invalid input.")

        self.configureTable()
    def iloc_del_function(self, index_1, index_2):
        editProcessData = self.data.drop(columns=self.data.columns[index_1:index_2 + 1]).copy()

        return editProcessData
    def iloc_copy_function(self, index_1, index_2, index_new):
        from pandas import DataFrame, concat
        editProcessData = DataFrame()
        editProcessData = concat([editProcessData, self.data.iloc[:, :index_new]], axis=1)
        editProcessData = concat([editProcessData, self.data.iloc[:, index_1:index_2 + 1]], axis=1)
        editProcessData = concat([editProcessData, self.data.iloc[:, index_new:]], axis=1)

        cols = []
        for i in range(editProcessData.shape[1]):
            if i in range(index_new, index_new + (index_2 - index_1 + 1)):
                cols.append(editProcessData.columns[i] + '_copy')
            else:
                cols.append(editProcessData.columns[i])
        editProcessData.columns = cols

        return editProcessData        

    def columnCreator(self):
        """
        iloc, index_1, index_2, operator
        loc, key_1, key_2, operator
        """
        try:
            editor = self.columnCreationText.text().split(',')

            if editor[0] == 'iloc':
                editor[1], editor[2] = int(editor[1]), int(editor[2])
                for i in [1, 2]:
                    if editor[i] < 0:
                        editor[i] = self.data.shape[1] + editor[i]
            elif editor[0] == 'loc':
                editor[1], editor[2] = list(self.data.columns).index(editor[1]), list(self.data.columns).index(editor[2])
            
            if editor[3] == '+':
                newColumn = self.data.iloc[:, editor[1]] + self.data.iloc[:, editor[2]]
            elif editor[3] == '-':
                newColumn = self.data.iloc[:, editor[1]] - self.data.iloc[:, editor[2]]
            elif editor[3] == '*':
                newColumn = self.data.iloc[:, editor[1]] * self.data.iloc[:, editor[2]]
            elif editor[3] == '/':
                newColumn = self.data.iloc[:, editor[1]] / self.data.iloc[:, editor[2]]
            elif editor[3] == '**':
                newColumn = self.data.iloc[:, editor[1]] ** self.data.iloc[:, editor[2]]
            elif editor[3] == '%':
                newColumn = self.data.iloc[:, editor[1]] % self.data.iloc[:, editor[2]]

            from pandas import concat
            self.data = concat([self.data, newColumn], axis=1)

            cols = list(self.data.columns)
            for i in range(100):
                if i == 0 and cols.count('created_column') == 0:
                    cols[-1] = 'created_column'
                    break
                elif cols.count(f'created_column_'+str(i)) == 0:
                    cols[-1] = f'created_column_'+str(i)
                    break
            self.data.columns = cols
        except:
            print("[EXCEPTION] Invalid input.")

        self.configureTable()
    ####################################################################################### # left bottom
    def saveChanges(self):
        path = self.mainPath+'\\save\\'
        name = self.path.split("/")[-1]
        if not self.overwriteBox.isChecked():
            for i in range(100):
                if i == 0:
                    dataName = name
                else:
                    dataName = f'{".".join(name.split(".")[:-1])} ({i}).{name.split(".")[-1]}'
                control = os.path.isfile(path + dataName)
                if not control:
                    self.data.to_csv(path + dataName, index = False)
                    break
                else:
                    continue
        else:
            self.data.to_csv(path + name, index = False)

        print('[INFO] Save process has been completed.')
    ####################################################################################### # back-side - middle
    def configureTable(self):
        self.configureProcess = 1
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(self.data.columns))
        self.tableWidget.setHorizontalHeaderLabels(list(self.data.columns))
        for row in self.data.values:
            self.addTableRow(self.tableWidget, row)
        self.configureProcess = 0

        for i in range(len(self.data.columns)):
            self.tableWidget.setColumnWidth(i, 100)
        # self.setFixedWidth(525 + 100 * len(self.data.columns))
    def addTableRow(self, table, row_data):
        row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
        col = 0
        for item in row_data:
            cell = QTableWidgetItem(str(item))
            self.tableWidget.setItem(row, col, cell)
            col += 1

app=QApplication(sys.argv)
win=window()
win.show()
app.exec_()