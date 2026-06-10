# -*- coding: utf-8 -*-
"""
/***************************************************************************
 changeDataSourceDialog
                                 A QGIS plugin
 right click on layer tree to change layer datasource
                             -------------------
        begin                : 2015-09-29
        git sha              : $Format:%H$
        copyright            : (C) 2015 by enrico ferreguti
        email                : enricofer@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsBrowserModel, QgsMimeDataUtils

from .changeDataSource_dialog_base import Ui_changeDataSourceDialogBase
from .browsedatasource import Ui_dataSourceBrowser


class changeDataSourceDialog(QtWidgets.QDialog, Ui_changeDataSourceDialogBase):

    closedDialog = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(changeDataSourceDialog, self).__init__(parent)
        self.setupUi(self)

    def closeEvent(self, evnt):
        self.closedDialog.emit()


class dataSourceBrowser(QtWidgets.QDialog, Ui_dataSourceBrowser):

    def __init__(self, parent=None):
        """Constructor."""
        super(dataSourceBrowser, self).__init__(parent)
        self.setupUi(self)
        self.browserModel = QgsBrowserModel()
        self.browserModel.initialize()
        self.dataSourceTree.setModel(self.browserModel)
        self.dataSourceTree.doubleClicked.connect(self.getUriFromBrowser)
        self.dataSourceTree.header().hide()
        self.hide()
        self.buttonBox.accepted.connect(self.acceptedAction)
        self.buttonBox.rejected.connect(self.rejectedAction)
        self.acceptedFlag = None
        self.result = (None, None, None)

    def getUriFromBrowser(self, index):
        uri_list = QgsMimeDataUtils.decodeUriList(self.browserModel.mimeData([index]))
        if not uri_list:
            self.result = (None, None, None)
            return
        try:
            self.result = (uri_list[0].layerType, uri_list[0].providerKey, uri_list[0].uri)
            self.close()
            self.acceptedFlag = True
        except (AttributeError, IndexError):
            self.result = (None, None, None)

    def acceptedAction(self):
        self.getUriFromBrowser(self.dataSourceTree.currentIndex())
        self.close()
        self.acceptedFlag = True

    def rejectedAction(self):
        self.close()
        self.acceptedFlag = None

    @staticmethod
    def uri(title=""):
        dialog = dataSourceBrowser()
        dialog.setWindowTitle(title)
        dialog.exec()
        dialog.show()
        if dialog.acceptedFlag:
            return dialog.result
        else:
            return (None, None, None)
