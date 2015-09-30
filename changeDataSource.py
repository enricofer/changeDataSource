# -*- coding: utf-8 -*-
"""
/***************************************************************************
 changeDataSource
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from changeDataSource_dialog import changeDataSourceDialog
from setdatasource import setDataSource
import os.path


class changeDataSource:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'changeDataSource_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = changeDataSourceDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&changeDataSource')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'changeDataSource')
        self.toolbar.setObjectName(u'changeDataSource')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('changeDataSource', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.join(self.plugin_dir,"icon.png")
        self.add_action(
            icon_path,
            text=self.tr(u'changeDataSource'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.changeDSActionVector = QAction(QIcon(os.path.join(self.plugin_dir,"icon.png")), u"Change vector datasource", self.iface.legendInterface() )
        self.changeDSActionRaster = QAction(QIcon(os.path.join(self.plugin_dir,"icon.png")), u"Change raster datasource", self.iface.legendInterface() )
        self.iface.legendInterface().addLegendLayerAction(self.changeDSActionVector,"","01", QgsMapLayer.VectorLayer,True)
        self.iface.legendInterface().addLegendLayerAction(self.changeDSActionRaster,"","02", QgsMapLayer.RasterLayer,True)
        self.changeDSTool = setDataSource(self.iface)
        self.connectSignals()


    def connectSignals(self):
        self.changeDSActionVector.triggered.connect(self.changeLayerDS)
        self.changeDSActionRaster.triggered.connect(self.changeLayerDS)
        self.dlg.replaceButton.clicked.connect(self.replaceDS)
        self.dlg.layerTable.verticalHeader().sectionClicked.connect(self.activateSelection)
        self.dlg.buttonBox.clicked.connect(self.buttonBoxHub)


    def activateSelection(self,idx):
        indexes = []
        for selectionRange in self.dlg.layerTable.selectedRanges():
            indexes.extend(range(selectionRange.topRow(), selectionRange.bottomRow()+1))
        print indexes
        if indexes != []:
            self.dlg.onlySelectedCheck.setChecked(True)
        else:
            self.dlg.onlySelectedCheck.setChecked(False)

    def changeLayerDS(self):
        print self.iface.legendInterface().currentLayer()
        self.changeDSTool.changeDataSource(self.iface.legendInterface().currentLayer())
        
    def unload(self):
        self.iface.legendInterface().removeLegendLayerAction(self.changeDSActionVector)
        self.iface.legendInterface().removeLegendLayerAction(self.changeDSActionRaster)
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&changeDataSource'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def populateLayerTable(self):
        self.changeDSTool.populateComboBox(self.dlg.datasourceCombo,[""]+self.changeDSTool.vectorDSList.keys()+self.changeDSTool.rasterDSList.keys())
        self.dlg.layerTable.clear()
        for row in range(self.dlg.layerTable.rowCount()):
            self.dlg.layerTable.removeRow(row)
        self.dlg.layerTable.setRowCount(0)
        self.dlg.layerTable.setColumnCount(4)
        self.dlg.layerTable.setHorizontalHeaderItem(0,QTableWidgetItem("ID"))
        self.dlg.layerTable.setHorizontalHeaderItem(1,QTableWidgetItem("Layer Name"))
        self.dlg.layerTable.setHorizontalHeaderItem(2,QTableWidgetItem("Type"))
        self.dlg.layerTable.setHorizontalHeaderItem(3,QTableWidgetItem("Data source"))
        self.dlg.layerTable.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.dlg.layerTable.horizontalHeader().setClickable(False)

        self.dlg.layerTable.hideColumn(0)
        lr = QgsMapLayerRegistry.instance()
        #self.dlg.layerTable.setRowCount(lr.count())
        for lid in lr.mapLayers():
            layer = lr.mapLayer( lid )
            if layer.type() == QgsMapLayer.VectorLayer or layer.type() == QgsMapLayer.RasterLayer:
                lastRow = self.dlg.layerTable.rowCount()
                self.dlg.layerTable.insertRow(lastRow)
                #lastRow += 1
                self.dlg.layerTable.setCellWidget(lastRow,0,self.getLabelWidget(layer.id(),0))
                self.dlg.layerTable.setCellWidget(lastRow,1,self.getLabelWidget(layer.name(),1))
                self.dlg.layerTable.setCellWidget(lastRow,2,self.getLabelWidget(layer.dataProvider().name(),2))
                self.dlg.layerTable.setCellWidget(lastRow,3,self.getLabelWidget(layer.source(),3))
        self.dlg.layerTable.resizeColumnsToContents()
        self.dlg.layerTable.horizontalHeader().setStretchLastSection(True)

    def getLabelWidget(self,txt,column):
        edit = QLineEdit(parent = self.dlg.layerTable)
        edit.setMinimumWidth(QApplication.instance().fontMetrics().width(txt)+5)
        edit.setText(txt)
        edit.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
        edit.setStyleSheet("QLineEdit{background: rgba(0,190,0, 0%);}")
        edit.column = column
        edit.changed = None
        if column == 1:
            	edit.setReadOnly(True)
        else:
            edit.textChanged.connect(lambda: self.highlightCell(edit,"QLineEdit{background: yellow;}"))
        return edit

    def highlightCell(self,cell,newStyle):
        cell.setStyleSheet(newStyle)
        cell.changed = True

    def replaceDS(self):
        self.replaceList=[]
        indexes = []
        #build replace list
        if self.dlg.onlySelectedCheck.isChecked():
            for selectionRange in self.dlg.layerTable.selectedRanges():
                indexes.extend(range(selectionRange.topRow(), selectionRange.bottomRow()+1))
            for row in indexes:
                self.replaceList.append(QgsMapLayerRegistry.instance().mapLayer(self.dlg.layerTable.cellWidget(row,0).text()))
        else:
            for row in range(0,self.dlg.layerTable.rowCount()):
                indexes.append(row)
                self.replaceList.append(QgsMapLayerRegistry.instance().mapLayer(self.dlg.layerTable.cellWidget(row,0).text()))
        print indexes
        for row in indexes:
            cell = self.dlg.layerTable.cellWidget(row,3)
            orig = cell.text()
            cell.setText(cell.text().replace(self.dlg.findEdit.text(),self.dlg.replaceEdit.text()))
            if self.dlg.datasourceCombo.currentText() != "":
                self.dlg.layerTable.cellWidget(row,2).setText(self.dlg.datasourceCombo.currentText())

    def applyDSChanges(self):
        for row in range(0,self.dlg.layerTable.rowCount()):
            DSTypeCell = self.dlg.layerTable.cellWidget(row,2)
            DSStringCell = self.dlg.layerTable.cellWidget(row,3)
            if DSTypeCell.changed or DSStringCell.changed:
                rowLayer = QgsMapLayerRegistry.instance().mapLayer(self.dlg.layerTable.cellWidget(row,0).text())
                rowDStype = rowLayer.dataProvider().name()
                rowDSstring = rowLayer.source()
                if DSTypeCell.changed:
                    rowDStype = DSTypeCell.text()
                if DSStringCell.changed:
                    rowDSstring = DSStringCell.text()
                if self.changeDSTool.applyDataSource(rowLayer,rowDStype,rowDSstring):
                    resultStyle = "QLineEdit{background: green;}"
                else:
                    resultStyle = "QLineEdit{background: red;}"
                if DSTypeCell.changed:
                    DSTypeCell.setStyleSheet(resultStyle)
                if DSStringCell.changed:
                    DSStringCell.setStyleSheet(resultStyle)


    def buttonBoxHub(self,button):
        if button.text() == "Reset":
            self.populateLayerTable()
        elif button.text() == "Apply":
            self.applyDSChanges()
        else:
            self.dlg.hide()

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.populateLayerTable()
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
