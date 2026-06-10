# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'changeDataSource_dialog_base.ui'
# Hand-updated for Qt5/Qt6 dual compatibility (qualified enums).

from qgis.PyQt import QtCore, QtWidgets
from qgis.gui import QgsFieldExpressionWidget


class Ui_changeDataSourceDialogBase(object):
    def setupUi(self, changeDataSourceDialogBase):
        changeDataSourceDialogBase.setObjectName("changeDataSourceDialogBase")
        changeDataSourceDialogBase.resize(1027, 461)
        self.verticalLayout = QtWidgets.QVBoxLayout(changeDataSourceDialogBase)
        self.verticalLayout.setObjectName("verticalLayout")
        self.layerTable = QtWidgets.QTableWidget(changeDataSourceDialogBase)
        self.layerTable.setAlternatingRowColors(True)
        self.layerTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.layerTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.layerTable.setGridStyle(QtCore.Qt.PenStyle.DotLine)
        self.layerTable.setObjectName("layerTable")
        self.layerTable.setColumnCount(0)
        self.layerTable.setRowCount(0)
        self.layerTable.horizontalHeader().setHighlightSections(False)
        self.layerTable.horizontalHeader().setSortIndicatorShown(True)
        self.layerTable.verticalHeader().setVisible(True)
        self.verticalLayout.addWidget(self.layerTable)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(changeDataSourceDialogBase)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.findEdit = QtWidgets.QLineEdit(changeDataSourceDialogBase)
        self.findEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.findEdit.setObjectName("findEdit")
        self.horizontalLayout.addWidget(self.findEdit)
        self.label_2 = QtWidgets.QLabel(changeDataSourceDialogBase)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.replaceEdit = QtWidgets.QLineEdit(changeDataSourceDialogBase)
        self.replaceEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.replaceEdit.setObjectName("replaceEdit")
        self.horizontalLayout.addWidget(self.replaceEdit)
        self.label_4 = QtWidgets.QLabel(changeDataSourceDialogBase)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.mFieldExpressionWidget = QgsFieldExpressionWidget(changeDataSourceDialogBase)
        self.mFieldExpressionWidget.setObjectName("mFieldExpressionWidget")
        self.horizontalLayout.addWidget(self.mFieldExpressionWidget)
        self.label_3 = QtWidgets.QLabel(changeDataSourceDialogBase)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.datasourceCombo = QtWidgets.QComboBox(changeDataSourceDialogBase)
        self.datasourceCombo.setObjectName("datasourceCombo")
        self.horizontalLayout.addWidget(self.datasourceCombo)
        self.onlySelectedCheck = QtWidgets.QCheckBox(changeDataSourceDialogBase)
        self.onlySelectedCheck.setObjectName("onlySelectedCheck")
        self.horizontalLayout.addWidget(self.onlySelectedCheck)
        self.replaceButton = QtWidgets.QPushButton(changeDataSourceDialogBase)
        self.replaceButton.setObjectName("replaceButton")
        self.horizontalLayout.addWidget(self.replaceButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.horizontalLayout_2.addItem(spacerItem)
        self.handleBadLayersCheckbox = QtWidgets.QCheckBox(changeDataSourceDialogBase)
        self.handleBadLayersCheckbox.setObjectName("handleBadLayersCheckbox")
        self.horizontalLayout_2.addWidget(self.handleBadLayersCheckbox)
        self.reconcileButton = QtWidgets.QPushButton(changeDataSourceDialogBase)
        self.reconcileButton.setObjectName("reconcileButton")
        self.horizontalLayout_2.addWidget(self.reconcileButton)
        self.buttonBox = QtWidgets.QDialogButtonBox(changeDataSourceDialogBase)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Apply
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Reset
        )
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(changeDataSourceDialogBase)
        self.buttonBox.accepted.connect(changeDataSourceDialogBase.accept)
        self.buttonBox.rejected.connect(changeDataSourceDialogBase.reject)

    def retranslateUi(self, changeDataSourceDialogBase):
        _translate = QtCore.QCoreApplication.translate
        changeDataSourceDialogBase.setWindowTitle(_translate("changeDataSourceDialogBase", "Change datasource"))
        self.layerTable.setSortingEnabled(True)
        self.label.setText(_translate("changeDataSourceDialogBase", "Find:"))
        self.label_2.setText(_translate("changeDataSourceDialogBase", "Replace:"))
        self.label_4.setText(_translate("changeDataSourceDialogBase", "expression"))
        self.label_3.setText(_translate("changeDataSourceDialogBase", "New datasource type:"))
        self.onlySelectedCheck.setText(_translate("changeDataSourceDialogBase", "Between selected rows"))
        self.replaceButton.setText(_translate("changeDataSourceDialogBase", "Replace"))
        self.handleBadLayersCheckbox.setText(_translate("changeDataSourceDialogBase", "Handle bad layers"))
        self.reconcileButton.setText(_translate("changeDataSourceDialogBase", "Reconcile unhandled"))
