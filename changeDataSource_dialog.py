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

import os

from PyQt4 import QtGui, uic
from qgis.core import QgsBrowserModel,QgsMimeDataUtils
from changeDataSource_dialog_base import Ui_changeDataSourceDialogBase
from browsedatasource import Ui_dataSourceBrowser

class changeDataSourceDialog(QtGui.QDialog, Ui_changeDataSourceDialogBase):
    def __init__(self, parent=None):
        """Constructor."""
        super(changeDataSourceDialog, self).__init__(parent)
        #QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

class dataSourceBrowser(QtGui.QDialog, Ui_dataSourceBrowser):

    def __init__(self, parent=None):
        """Constructor."""
        super(dataSourceBrowser, self).__init__(parent)
        #QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.browserModel = QgsBrowserModel()
        self.dataSourceTree.setModel(self.browserModel)
        self.dataSourceTree.doubleClicked.connect(self.getUriFromBrowser)
        self.hide()
        self.buttonBox.accepted.connect(self.acceptedAction)
        self.buttonBox.rejected.connect(self.rejectedAction)
        self.acceptedFlag = None

    def getUriFromBrowser(self,index):
        uriItem = self.browserModel.dataItem(index)
        uri_list = QgsMimeDataUtils.decodeUriList(self.browserModel.mimeData([index]))
        try:
            #print uri_list[0].providerKey,uri_list[0].uri
            self.result =  (uri_list[0].providerKey,uri_list[0].uri)
            self.close()
            self.acceptedFlag = True
        except:
            #print "NO VALID URI"
            self.result = (None,None)

    def acceptedAction(self):
        self.getUriFromBrowser(self.dataSourceTree.currentIndex())
        self.close()
        self.acceptedFlag = True

    def rejectedAction(self):
        self.close()
        self.acceptedFlag = None

    @staticmethod
    def uri():
        dialog = dataSourceBrowser()
        result = dialog.exec_()
        dialog.show()
        if dialog.acceptedFlag:
            return (dialog.result)
        else:
            return (None,None)