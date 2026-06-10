# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_changeDSDialog.ui'
# Hand-updated for Qt5/Qt6 dual compatibility (qualified enums).

from qgis.PyQt import QtCore, QtWidgets


class Ui_changeDataSourceDialog(object):
    def setupUi(self, changeDataSourceDialog):
        changeDataSourceDialog.setObjectName("changeDataSourceDialog")
        changeDataSourceDialog.resize(297, 305)
        self.verticalLayout = QtWidgets.QVBoxLayout(changeDataSourceDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(changeDataSourceDialog)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.selectDatasourceCombo = QtWidgets.QComboBox(changeDataSourceDialog)
        self.selectDatasourceCombo.setObjectName("selectDatasourceCombo")
        self.verticalLayout.addWidget(self.selectDatasourceCombo)
        self.label = QtWidgets.QLabel(changeDataSourceDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QPlainTextEdit(changeDataSourceDialog)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.openBrowser = QtWidgets.QPushButton(changeDataSourceDialog)
        self.openBrowser.setObjectName("openBrowser")
        self.verticalLayout.addWidget(self.openBrowser)
        self.buttonBox = QtWidgets.QDialogButtonBox(changeDataSourceDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(changeDataSourceDialog)
        QtCore.QMetaObject.connectSlotsByName(changeDataSourceDialog)

    def retranslateUi(self, changeDataSourceDialog):
        _translate = QtCore.QCoreApplication.translate
        changeDataSourceDialog.setWindowTitle(_translate("changeDataSourceDialog", "undoLayerChanges"))
        self.label_2.setText(_translate("changeDataSourceDialog", "Datasource Types"))
        self.label.setText(_translate("changeDataSourceDialog", "URI:"))
        self.openBrowser.setText(_translate("changeDataSourceDialog", "Browse"))
