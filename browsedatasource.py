# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\DEMO\Dropbox\dev\changeDataSource\browsedatasource.ui'
#
# Created: Wed Nov 04 23:39:53 2015
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from builtins import object
from qgis.PyQt import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_dataSourceBrowser(object):
    def setupUi(self, dataSourceBrowser):
        dataSourceBrowser.setObjectName(_fromUtf8("dataSourceBrowser"))
        dataSourceBrowser.resize(400, 444)
        self.buttonBox = QtWidgets.QDialogButtonBox(dataSourceBrowser)
        self.buttonBox.setGeometry(QtCore.QRect(50, 400, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.dataSourceTree = QtWidgets.QTreeView(dataSourceBrowser)
        self.dataSourceTree.setGeometry(QtCore.QRect(10, 11, 381, 381))
        self.dataSourceTree.setObjectName(_fromUtf8("dataSourceTree"))

        self.retranslateUi(dataSourceBrowser)
        self.buttonBox.accepted.connect(dataSourceBrowser.accept)
        self.buttonBox.rejected.connect(dataSourceBrowser.reject)

    def retranslateUi(self, dataSourceBrowser):
        dataSourceBrowser.setWindowTitle(_translate("dataSourceBrowser", "Dialog", None))

