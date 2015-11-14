# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\DEMO\Dropbox\dev\changeDataSource\changeDataSource_dialog_base.ui'
#
# Created: Sat Nov 14 15:11:22 2015
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_changeDataSourceDialogBase(object):
    def setupUi(self, changeDataSourceDialogBase):
        changeDataSourceDialogBase.setObjectName(_fromUtf8("changeDataSourceDialogBase"))
        changeDataSourceDialogBase.resize(1027, 461)
        self.verticalLayout = QtGui.QVBoxLayout(changeDataSourceDialogBase)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.layerTable = QtGui.QTableWidget(changeDataSourceDialogBase)
        self.layerTable.setAlternatingRowColors(True)
        self.layerTable.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.layerTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.layerTable.setGridStyle(QtCore.Qt.DotLine)
        self.layerTable.setObjectName(_fromUtf8("layerTable"))
        self.layerTable.setColumnCount(0)
        self.layerTable.setRowCount(0)
        self.layerTable.horizontalHeader().setHighlightSections(False)
        self.layerTable.horizontalHeader().setSortIndicatorShown(True)
        self.layerTable.verticalHeader().setVisible(True)
        self.verticalLayout.addWidget(self.layerTable)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(changeDataSourceDialogBase)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.findEdit = QtGui.QLineEdit(changeDataSourceDialogBase)
        self.findEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.findEdit.setObjectName(_fromUtf8("findEdit"))
        self.horizontalLayout.addWidget(self.findEdit)
        self.label_2 = QtGui.QLabel(changeDataSourceDialogBase)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.replaceEdit = QtGui.QLineEdit(changeDataSourceDialogBase)
        self.replaceEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.replaceEdit.setObjectName(_fromUtf8("replaceEdit"))
        self.horizontalLayout.addWidget(self.replaceEdit)
        self.label_4 = QtGui.QLabel(changeDataSourceDialogBase)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout.addWidget(self.label_4)
        self.mFieldExpressionWidget = QgsFieldExpressionWidget(changeDataSourceDialogBase)
        self.mFieldExpressionWidget.setObjectName(_fromUtf8("mFieldExpressionWidget"))
        self.horizontalLayout.addWidget(self.mFieldExpressionWidget)
        self.label_3 = QtGui.QLabel(changeDataSourceDialogBase)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.datasourceCombo = QtGui.QComboBox(changeDataSourceDialogBase)
        self.datasourceCombo.setObjectName(_fromUtf8("datasourceCombo"))
        self.horizontalLayout.addWidget(self.datasourceCombo)
        self.onlySelectedCheck = QtGui.QCheckBox(changeDataSourceDialogBase)
        self.onlySelectedCheck.setObjectName(_fromUtf8("onlySelectedCheck"))
        self.horizontalLayout.addWidget(self.onlySelectedCheck)
        self.replaceButton = QtGui.QPushButton(changeDataSourceDialogBase)
        self.replaceButton.setObjectName(_fromUtf8("replaceButton"))
        self.horizontalLayout.addWidget(self.replaceButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.reconcileButton = QtGui.QPushButton(changeDataSourceDialogBase)
        self.reconcileButton.setObjectName(_fromUtf8("reconcileButton"))
        self.horizontalLayout_2.addWidget(self.reconcileButton)
        self.buttonBox = QtGui.QDialogButtonBox(changeDataSourceDialogBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(changeDataSourceDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), changeDataSourceDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), changeDataSourceDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(changeDataSourceDialogBase)

    def retranslateUi(self, changeDataSourceDialogBase):
        changeDataSourceDialogBase.setWindowTitle(_translate("changeDataSourceDialogBase", "Change datasource globally", None))
        self.layerTable.setSortingEnabled(True)
        self.label.setText(_translate("changeDataSourceDialogBase", "Find:", None))
        self.label_2.setText(_translate("changeDataSourceDialogBase", "Replace:", None))
        self.label_4.setText(_translate("changeDataSourceDialogBase", "expression", None))
        self.label_3.setText(_translate("changeDataSourceDialogBase", "New datasource type:", None))
        self.onlySelectedCheck.setText(_translate("changeDataSourceDialogBase", "Between selected rows", None))
        self.replaceButton.setText(_translate("changeDataSourceDialogBase", "Replace", None))
        self.reconcileButton.setText(_translate("changeDataSourceDialogBase", "Reconcile unhandled", None))

from qgis.gui import QgsFieldExpressionWidget
