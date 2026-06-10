# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'browsedatasource.ui'
# Hand-updated for Qt5/Qt6 dual compatibility (qualified enums).

from qgis.PyQt import QtCore, QtWidgets


class Ui_dataSourceBrowser(object):
    def setupUi(self, dataSourceBrowser):
        dataSourceBrowser.setObjectName("dataSourceBrowser")
        dataSourceBrowser.resize(400, 444)
        self.buttonBox = QtWidgets.QDialogButtonBox(dataSourceBrowser)
        self.buttonBox.setGeometry(QtCore.QRect(50, 400, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.dataSourceTree = QtWidgets.QTreeView(dataSourceBrowser)
        self.dataSourceTree.setGeometry(QtCore.QRect(10, 11, 381, 381))
        self.dataSourceTree.setObjectName("dataSourceTree")

        self.retranslateUi(dataSourceBrowser)
        self.buttonBox.accepted.connect(dataSourceBrowser.accept)
        self.buttonBox.rejected.connect(dataSourceBrowser.reject)

    def retranslateUi(self, dataSourceBrowser):
        dataSourceBrowser.setWindowTitle(
            QtCore.QCoreApplication.translate("dataSourceBrowser", "Dialog")
        )
