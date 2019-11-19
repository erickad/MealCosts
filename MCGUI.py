#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'MealCostsGUI.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
"""
Classes and functions to create a user interface for MealCosts.py
using PyQt5.
"""

import MealCosts #Structures and functions to hold ingredients and recipes
import os #File/directory read/write
from PyQt5 import QtCore, QtGui, QtWidgets #GUI

class dictTableModel(QtCore.QAbstractTableModel):
    """
    A custom table model to contain ingredients of both recipes
    and ingredients.
    """
    def __init__(self, data, mType=True, parent=None):
        """
        Creates a model with the data of either type given.
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__data = data
        self.column_count = 2
        self.row_count = len(self.__data)
        self.modelType = mType
        self.num = 0

    def rowCount(self, parent=None):
        """
        Returns row count.
        """
        return self.row_count

    def columnCount(self, parent=None):
        """
        Returns column count.
        """
        return self.column_count

    def headerData(self, section, orientation, role):
        """
        Sets headerData for either type.
        """
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            if self.modelType:
                return ("Ingredient", "Cost per/kg/l")[section]
            else:
                return ("Ingredient", "Amount per/kg/l")[section]
        else:
            return "{}".format(section)

    def setType(self, mType):
        """
        Sets type of model as a boolean.
        """
        self.modelType = mType

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        Manipulates data using Qt model<->view fashion.
        """
        if (index.isValid() and role == QtCore.Qt.EditRole):
            row = index.row()
            column = index.column()
            if column == 0:
                if value in [i for i,p in self.__data]:
                    return False
                self.__data[row][0] = value
            elif column == 1:
                self.__data[row][1] = float(value)
            self.dataChanged.emit(index,index)
            return True
        return False

    def flags(self, index):
        """
        Returns flags of model.
        """
        return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsSelectable

    def data(self, index, role= QtCore.Qt.DisplayRole):
        """
        Method for Qt to access data.
        """
        if not index.isValid():
            return QtCore.QVariant()
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return self.__data[row][0]
            if column == 1:
                return self.__data[row][1]
        else:
            return QtCore.QVariant()

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        """
        Method for Qt to recognize row insert and insert values with
        user input dialog and subsequent default values.
        """
        self.beginInsertRows(parent,position,position+max(rows-1,0))
        for i in range(rows):
            win = insertRowWindow(self.__data)
            n,v,b = win.getItemAndValue()
            if b:
                self.__data.insert(position,[n,v])
            else:
                while "Ing-%s"%self.num in [x for x,y in self.__data]:
                    self.num += 1
                self.__data.insert(position,["Ing-%s"%self.num,0.0])

        self.row_count += rows
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        """
        Method for Qt to recognize row deletion
        """
        self.beginRemoveRows(parent,position,position+max(rows-1,0))
        for i in range(rows):
            del self.__data[position]
        self.row_count -= rows
        self.endRemoveRows()
        return True


class insertRowWindow(QtWidgets.QDialog):
    """
    A QDialog window to get user input on data to enter in row.
    """
    def __init__(self, data, parent=None):
        super(insertRowWindow, self).__init__(parent)
        self.setWindowTitle("Add item")
        self.modelData = data
        vLayout = QtWidgets.QVBoxLayout(self)
        hLayout1 = QtWidgets.QHBoxLayout()
        self.labelN = QtWidgets.QLabel("Name:",self)
        self.labelN.setAlignment(QtCore.Qt.AlignRight)
        hLayout1.addWidget(self.labelN)
        self.name = QtWidgets.QLineEdit(self)
        self.name.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[^()]+")))
        hLayout1.addWidget(self.name)
        vLayout.addLayout(hLayout1)
        hLayout2 = QtWidgets.QHBoxLayout()
        self.labelV = QtWidgets.QLabel("Amount:",self)
        self.labelV.setAlignment(QtCore.Qt.AlignRight)
        hLayout2.addWidget(self.labelV)
        self.value = QtWidgets.QDoubleSpinBox(self)
        self.value.setMaximum(1000.0)
        self.value.setDecimals(4)
        hLayout2.addWidget(self.value)
        vLayout.addLayout(hLayout2)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        vLayout.addWidget(buttons)

    def done(self, r):
        """
        Checks if data is valid before returning.
        """
        if QtWidgets.QDialog.Accepted == r:
            txt = self.name.text()
            if txt and (not txt.isspace()) and (txt not in
                [n for n,v in self.modelData]):
                QtWidgets.QDialog.done(self,r)
                return
            else:
                msg = QtWidgets.QMessageBox()
                if len(txt) == 0:
                    msg.setText("Name must be filled")
                elif txt.isspace():
                    msg.setText("Name must be filled")
                else:
                    msg.setText("%s \nalready present, please choose another." % txt)

                msg.exec()
                return
        else:
            QtWidgets.QDialog.done(self,r)
            return

    def getItemAndValue(self,parent=None):
        """
        Returns the results of the dialog.
        """
        result = self.exec_()
        return (self.name.text(), self.value.value(),
            result == QtWidgets.QDialog.Accepted)

class newRecipeWindow(QtWidgets.QDialog):
    """
    QDialog window to get user input on data for new recipe.
    """
    def __init__(self, mList, parent=None):
        super(newRecipeWindow, self).__init__(parent)
        self.setWindowTitle("Add recipe")
        self.recipes = mList.recipes
        layout = QtWidgets.QVBoxLayout(self)
        self.labelN = QtWidgets.QLabel("Recipe name:",self)
        layout.addWidget(self.labelN)
        self.name = QtWidgets.QLineEdit(self)
        self.name.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[^()]+")))
        layout.addWidget(self.name)
        self.labelS = QtWidgets.QLabel("Servings:",self)
        layout.addWidget(self.labelS)
        self.value = QtWidgets.QSpinBox(self)
        self.value.setMinimum(1)
        layout.addWidget(self.value)
        self.labelI = QtWidgets.QLabel("Instructions:",self)
        layout.addWidget(self.labelI)
        self.instr = QtWidgets.QTextEdit()
        layout.addWidget(self.instr)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def done(self, r):
        """
        Checks if data is valid before returning.
        """
        if QtWidgets.QDialog.Accepted == r:
            txt = self.name.text()
            if txt and (not txt.isspace()) and (txt not in
                [rn.name for rn in self.recipes]):
                QtWidgets.QDialog.done(self,r)
                return
            else:
                msg = QtWidgets.QMessageBox()
                if len(txt) == 0:
                    msg.setText("Name must be filled")
                elif txt.isspace():
                    msg.setText("Name must be filled")
                else:
                    msg.setText("%s \nalready present, please choose another." % txt)

                msg.exec()
                return
        else:
            QtWidgets.QDialog.done(self,r)
            return

    def getItemAndValue(self,parent=None):
        """
        Returns the results of the dialog.
        """
        result = self.exec_()
        return (self.name.text(), self.value.value(), self.instr.toPlainText(),
            result == QtWidgets.QDialog.Accepted)

class Ui_MainWindow(QtCore.QObject):
    """
    Main UI window created partially in QtDesigner and remainder in writing.
    """
    def setupUi(self, MainWindow):
        """
        Initial QtDesigner UI setup with various additions and edits.
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(551, 641)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 531, 611))
        self.tabWidget.setObjectName("tabWidget")

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.tab_2)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 521, 571))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton_6 = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout_4.addWidget(self.pushButton_6)
        self.pushButton_5 = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_4.addWidget(self.pushButton_5)
        self.spinBox_1 = QtWidgets.QSpinBox(self.verticalLayoutWidget_2)
        self.spinBox_1.setObjectName("spinBox_1")
        self.horizontalLayout_4.addWidget(self.spinBox_1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.tableView = QtWidgets.QTableView(self.verticalLayoutWidget_2)
        self.tableView.setObjectName("tableView")
        self.verticalLayout_3.addWidget(self.tableView)
        self.tabWidget.addTab(self.tab_2, "")

        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.tab)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 521, 571))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.comboBox = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout_5.addWidget(self.comboBox)

        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_5.addWidget(self.label_2)
        self.spinBox_3 = QtWidgets.QSpinBox(self.verticalLayoutWidget)
        self.spinBox_3.setObjectName("spinBox_3")
        self.horizontalLayout_5.addWidget(self.spinBox_3)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_6)

        self.pushButton_7 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_7.setObjectName("pushButton_7")
        self.horizontalLayout_5.addWidget(self.pushButton_7)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_3 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_3.addWidget(self.pushButton_3)
        self.pushButton_2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_3.addWidget(self.pushButton_2)
        self.spinBox_2 = QtWidgets.QSpinBox(self.verticalLayoutWidget)
        self.spinBox_2.setObjectName("spinBox_1")
        self.horizontalLayout_3.addWidget(self.spinBox_2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.tableView_2 = QtWidgets.QTableView(self.verticalLayoutWidget)
        self.tableView_2.setObjectName("tableView_2")
        self.verticalLayout_2.addWidget(self.tableView_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.lcd = QtWidgets.QLCDNumber(self.verticalLayoutWidget)
        self.lcd.setObjectName("lcd")
        self.horizontalLayout_2.addWidget(self.lcd)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.tabWidget.addTab(self.tab, "")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 591, 30))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.actionOpen_3 = QtWidgets.QAction(MainWindow)
        self.actionOpen_3.setObjectName("actionOpen_3")
        self.actionSave_3 = QtWidgets.QAction(MainWindow)
        self.actionSave_3.setObjectName("actionSave_3")
        self.actionNew_Recipe = QtWidgets.QAction(MainWindow)
        self.actionNew_Recipe.setObjectName("actionNew_Recipe")
        self.actionSave_Ingredients = QtWidgets.QAction(MainWindow)
        self.actionSave_Ingredients.setObjectName("actionSave_Ingredients")
        self.actionOpen_Recipe = QtWidgets.QAction(MainWindow)
        self.actionOpen_Recipe.setObjectName("actionOpen_Recipe")
        self.actionRemove_Recipe = QtWidgets.QAction(MainWindow)
        self.actionRemove_Recipe.setObjectName("actionRemove_Recipe")
        self.actionView = QtWidgets.QAction(MainWindow)
        self.actionView.setObjectName("actionView")
        self.menuFile.addAction(self.actionOpen_3)
        self.menuFile.addAction(self.actionSave_Ingredients)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen_Recipe)
        self.menuFile.addAction(self.actionSave_3)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionNew_Recipe)
        self.menuFile.addAction(self.actionRemove_Recipe)
        self.menubar.addAction(self.menuFile.menuAction())

        #Non-generated
        self.actionOpen_3.triggered.connect(self.openIngredients)
        self.actionSave_Ingredients.triggered.connect(self.saveIngredients)
        self.actionOpen_Recipe.triggered.connect(self.openRecipes)
        self.actionSave_3.triggered.connect(self.saveRecipes)
        self.actionNew_Recipe.triggered.connect(self.newRecipe)
        self.actionRemove_Recipe.triggered.connect(self.remRecipe)
        self.pushButton_7.clicked.connect(self.instrDialog)
        self.pushButton_6.clicked.connect(self.addIngredient)
        self.pushButton_5.clicked.connect(self.remIngredient)
        self.pushButton_3.clicked.connect(self.addToRecipe)
        self.pushButton_2.clicked.connect(self.remFromRecipe)
        self.pushButton.clicked.connect(self.calcRecipe)
        self.comboBox.activated.connect(self.viewRecipe)
        self.spinBox_3.valueChanged[int].connect(self.saveServ)

        #Variables
        self.mealList = MealCosts.MealList()
        self.recModels = {}
        self.model_I = None
        self.model_R = None
        self.model_R_Proxy = QtCore.QSortFilterProxyModel(self)
        self.model_R_Proxy.setSortCaseSensitivity(0)
        self.tableView_2.setModel(self.model_R_Proxy)
        self.dialog = None
        self.dLabel = None

        #Various
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableView_2.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.label_2.setAlignment(QtCore.Qt.AlignRight)
        self.spinBox_3.setMinimum(1)
        self.pushButton_6.setToolTip("Add an ingredient to ingredients")
        self.pushButton_5.setToolTip("Remove an ingredient from ingredients")
        self.pushButton_3.setToolTip("Add an ingredient to recipe")
        self.pushButton_2.setToolTip("Remove an ingredient from recipe")
        self.pushButton_7.setToolTip("Show and edit instructions")
        self.pushButton.setToolTip("Calculate recipe cost (0 if lacking ingredients)")
        self.spinBox_1.setToolTip("Number of item to add/remove")
        self.spinBox_2.setToolTip("Number of item to add/remove")
        self.spinBox_3.setToolTip("Set number of servings")
        self.comboBox.setToolTip("Recipe to view/edit")
        self.lcd.setToolTip("Cost of recipe (0 if lacking ingredients)")

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.openIngredients()
        self.openRecipes()

    def retranslateUi(self, MainWindow):
        """
        Sets the UI strings.
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Meal Costs"))
        self.pushButton_3.setText(_translate("MainWindow", "Add"))
        self.pushButton_2.setText(_translate("MainWindow", "Remove"))
        self.pushButton_7.setText(_translate("MainWindow", "Instructions"))
        self.pushButton.setText(_translate("MainWindow", "Calculate Recipe cost"))
        self.label_2.setText(_translate("MainWindow", "Servings:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Recipe"))
        self.pushButton_6.setText(_translate("MainWindow", "Add"))
        self.pushButton_5.setText(_translate("MainWindow", "Remove"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Ingredients"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpen_3.setText(_translate("MainWindow", "Load Ingredients"))
        self.actionSave_3.setText(_translate("MainWindow", "Save Recipes"))
        self.actionNew_Recipe.setText(_translate("MainWindow", "New Recipe"))
        self.actionSave_Ingredients.setText(_translate("MainWindow", "Save Ingredients"))
        self.actionOpen_Recipe.setText(_translate("MainWindow", "Load Recipes"))
        self.actionView.setText(_translate("MainWindow", "View"))
        self.actionRemove_Recipe.setText(_translate("MainWindow","Remove Recipe"))

#Non-generated
    def openIngredients(self):
        """
        Loads the ingredients using MealCosts and displays them in model.
        """
        self.mealList.readIngredients()
        ing = self.mealList.ingredients
        self.spinBox_1.setMaximum(len(ing))
        self.model_I = dictTableModel(ing)
        self.model_I_Proxy = QtCore.QSortFilterProxyModel(self)
        self.model_I_Proxy.setSortCaseSensitivity(0)
        self.model_I_Proxy.setSourceModel(self.model_I)
        self.tableView.setItemDelegate(ValidatedItemDelegate())
        self.tableView.setModel(self.model_I_Proxy)
        self.tableView.setSortingEnabled(True)
        self.model_I_Proxy.sort(-1, QtCore.Qt.AscendingOrder)

    def saveIngredients(self):
        """
        Saves current ingredients.
        """
        self.mealList.writeIngredients()

    def addIngredient(self):
        """
        Adds an ingredient to model and data.
        """
        if self.model_I is None:
            return False
        ind = self.spinBox_1.value()
        self.spinBox_1.setMaximum(self.spinBox_1.maximum()+1)
        self.model_I.insertRows(ind, 1)
        return True

    def remIngredient(self):
        """
        Removes an ingredient from model and data.
        """
        if self.model_I is not None:
            rows = self.model_I.row_count
            ind = self.spinBox_1.value()
            if rows != 0 and rows > ind:
                self.model_I.removeRows(ind,1)
                self.spinBox_1.setMaximum(max(self.spinBox_1.maximum()-1,0))
                return True
        return False

    def openRecipes(self):
        """
        Loads recipes using MealCosts and displays them in respective models.
        """
        self.mealList.readRecipes()
        self.comboBox.clear()
        for r in self.mealList.recipes:
            self.comboBox.addItem(r.name)
            self.recModels[r.name] = dictTableModel(r.contents, False)
        if self.comboBox.count() > 0:
            self.viewRecipe()

    def viewRecipe(self):
        """
        Sets the model for the recipe view and other initializations.
        """
        if len(self.mealList.recipes) < 1:
            self.model_R = None
            self.model_R_Proxy.setSourceModel(self.model_R)
            return False
        self.model_R = self.recModels[self.comboBox.currentText()]
        self.model_R_Proxy.setSourceModel(self.model_R)
        rec = self.mealList.getRecipe(self.comboBox.currentText())
        self.spinBox_3.setValue(rec.serv)
        rec.calcRecipeCost()
        self.lcd.display(rec.cost)
        self.spinBox_2.setMaximum(len(rec.contents))
        self.tableView_2.setItemDelegate(ValidatedItemDelegate())
        self.tableView_2.setSortingEnabled(True)
        self.model_R_Proxy.sort(-1, QtCore.Qt.AscendingOrder)
        return True

    def calcRecipe(self):
        """
        Calculates the recipe cost if possible, otherwise displays Lacking
        ingredints in a messagebox.
        """
        if len(self.mealList.recipes) < 1:
            return False
        rec = self.mealList.getRecipe(self.comboBox.currentText())
        lack = rec.calcRecipeCost()
        if len(lack) == 0:
            self.lcd.display(rec.cost)
        else:
            msg = QtWidgets.QMessageBox()
            ing = '\n'.join(lack)
            msg.setText("Lacking ingredients: \n%s" % ing)
            msg.exec()
            self.lcd.display(0)
        return True

    def addToRecipe(self):
        """
        Adds an ingredient to recipe model and data.
        """
        if self.model_R is None:
            return False
        ind = self.spinBox_2.value()
        self.spinBox_2.setMaximum(self.spinBox_2.maximum()+1)
        self.model_R.insertRows(ind, 1)
        return True

    def remFromRecipe(self):
        """
        Removes an ingredient from recipe model and data.
        """
        if self.model_R is not None:
            rows = self.model_R.row_count
            ind = self.spinBox_2.value()
            if rows != 0 and rows > ind:
                self.model_R.removeRows(ind,1)
                self.spinBox_2.setMaximum(max(self.spinBox_2.maximum()-1,0))
                return True
        return False

    def newRecipe(self):
        """
        Opens a dialog for user to input a new recipes data and adds it.
        """
        win = newRecipeWindow(self.mealList)
        n,v,i,b = win.getItemAndValue()
        if b:
            rec = MealCosts.Recipe(n,self.mealList,[],v,i)
            if self.mealList.addRecipe(rec):
                self.comboBox.addItem(rec.name)
                self.recModels[rec.name] = dictTableModel(rec.contents, False)
                self.viewRecipe()
                return True
        return False

    def saveRecipes(self):
        """
        Write recipes data to files.
        """
        self.mealList.writeRecipes()

    def remRecipe(self):
        """
        Removes a recipe from recipes using a dialog
        with a combobox of current recipes.
        """
        if len(self.mealList.recipes) < 1:
            return False
        rec, ok = QtWidgets.QInputDialog().getItem(self.centralwidget,
            "Recipe to remove","Recipe:",
            [r.name for r in self.mealList.recipes] , 0, False)
        if ok:
            if os.path.exists('./Recipes/%s.txt'%rec):
                os.remove('./Recipes/%s.txt'%rec)
            self.mealList.removeRecipe(rec)
            self.comboBox.removeItem(self.comboBox.findText(rec))
            del self.recModels[rec]
            self.viewRecipe()
            return True

    def instrDialog(self):
        """
        Opens a dialog to read and edit the current recipes instructions.
        """
        if len(self.mealList.recipes) == 0:
            return False
        rec = self.mealList.getRecipe(self.comboBox.currentText())
        if self.dialog is None:
            self.dialog = QtWidgets.QDialog(self.centralwidget)
            self.dialog.setMinimumSize(320,520)
            self.dText = QtWidgets.QTextEdit(self.dialog)
            self.dText.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
            self.dButton = QtWidgets.QPushButton(self.dialog)
            self.dButton.setText("Save")
            layout = QtWidgets.QGridLayout()
            layout.addWidget(self.dText)
            layout.addWidget(self.dButton)
            self.dialog.setLayout(layout)
            self.dButton.clicked.connect(self.saveInstr)
        self.dialog.setWindowTitle(rec.name)
        self.dText.setPlainText(rec.instr)
        self.dialog.show()
        return True

    def saveInstr(self):
        """
        Saves the current dialog recipe instructions.
        """
        rec = self.mealList.getRecipe(self.comboBox.currentText())
        if not rec is None:
            rec.instr = self.dText.toPlainText()
            self.dialog.accept()
            return True
        msg = QtWidgets.QMessageBox()
        msg.setText("Recipe no longer present.")
        msg.exec()
        self.dialog.reject()
        return False

    def saveServ(self):
        """
        Saves the current spinbox value to be number of serving for recipe.
        """
        if len(self.mealList.recipes) == 0:
            return False
        rec = self.mealList.getRecipe(self.comboBox.currentText())
        rec.serv = self.spinBox_3.value()
        return True

    def testing(self):
        """
        Prints current ingredients and recipes for testing/debugging purposes.
        """
        self.mealList.printIng()
        self.mealList.printRecipes()

class ValidatedItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    A custom delegator to ensure non-empty names and limit double decimals.
    """
    def createEditor(self, widget, option, index):
        if not index.isValid():
            return 0
        if index.column() == 0:
            editor = QtWidgets.QLineEdit(widget)
            validator = QtGui.QRegExpValidator(QtCore.QRegExp("[^()]+"), editor)
            editor.setValidator(validator)
            return editor
        if index.column() == 1:
            editor = QtWidgets.QLineEdit(widget)
            validator = QtGui.QRegExpValidator(
                QtCore.QRegExp("^\d+\.?\d?\d?\d?\d?$"), editor)
            editor.setValidator(validator)
            return editor
        return super(ValidatedItemDelegate, self).createEditor(widget,
            option, index)
#End Non-generated

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
