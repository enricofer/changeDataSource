# -*- coding: utf-8 -*-
"""
/***************************************************************************
 undoLayerChangesDialog
                                 A QGIS plugin
 undoLayerChanges
                             -------------------
        begin                : 2014-09-04
        copyright            : (C) 2014 by Enrico Ferreguti
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
from qgis.core import (
    Qgis,
    QgsDataProvider,
    QgsMapLayer,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
)
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel

from .ui_changeDSDialog import Ui_changeDataSourceDialog
from .changeDataSource_dialog import dataSourceBrowser


class setDataSource(QtWidgets.QDialog, Ui_changeDataSourceDialog):

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self)
        self.parent = parent
        self.iface = parent.iface
        self.canvas = self.iface.mapCanvas()
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.changeDataSourceAction)
        self.buttonBox.rejected.connect(self.cancelDialog)
        self.selectDatasourceCombo.activated.connect(self.selectDS)
        self.openBrowser.clicked.connect(self.openFileBrowser)
        self.rasterDSList = {
            "wms": "Web Map Service (WMS)",
            "wcs": "Web Coverage Service (WCS)",
            "gdal": "Raster images (GDAL)",
            "arcgismapserver": "ArcGIS Map Server",
            "xyz": "XYZ tiles",
        }
        self.vectorDSList = {
            "ogr": "Vector layers (OGR)",
            "delimitedtext": "Delimited Text",
            "gpx": "GPS eXchange Format",
            "postgres": "PostGIS database layer",
            "spatialite": "Spatialite database layer",
            "oracle": "Oracle spatial database layer",
            "mssql": "MS SQL Server database layer",
            "hana": "SAP HANA database layer",
            "db2": "DB2 spatial database layer",
            "mysql": "Mysql spatial database layer",
            "wfs": "Web Feature Service (WFS)",
            "arcgisfeatureserver": "ArcGIS Feature Server",
        }
        self.browsable = ("ogr", "gdal")

    def openFileBrowser(self):
        '''
        method used to open datasource browser dialog to get new provider/uri for the single layer
        '''
        layer_type, provider, fileName = dataSourceBrowser.uri()
        enumLayerTypes = ("vector", "raster", "plugin")
        if layer_type and enumLayerTypes[self.layer.type()] != layer_type:
            self.iface.messageBar().pushMessage(
                "Error",
                "Layer type mismatch: %s/%s" % (enumLayerTypes[self.layer.type()], layer_type),
                level=Qgis.MessageLevel.Critical,
                duration=4,
            )
        else:
            if fileName:
                self.lineEdit.setPlainText(fileName)
            if provider:
                allSources = [self.selectDatasourceCombo.itemText(i) for i in range(self.selectDatasourceCombo.count())]
                if provider in allSources:
                    self.selectDatasourceCombo.setCurrentIndex(allSources.index(provider))
                else:
                    self.selectDatasourceCombo.addItem(provider)
                    self.selectDatasourceCombo.setCurrentIndex(self.selectDatasourceCombo.count() - 1)

    def selectDS(self, i):
        '''
        method to catch datasource combo edits. No longer used. Stay here for future uses.
        '''
        pass

    def openDataSourceDialog(self, layer):
        '''
        method to prep and show single datasource edit dialog
        '''
        self.layer = layer
        self.setWindowTitle(layer.name())

        provider = self.layer.dataProvider().name()
        source = self.layer.source()
        self.label.setText("URI:")

        if provider == "ogr" or provider == "gdal":
            source = QgsProject.instance().readPath(source)

        if layer.type() == QgsMapLayer.VectorLayer:
            self.populateComboBox(self.selectDatasourceCombo, list(self.vectorDSList.keys()), predef=provider)
        else:
            self.populateComboBox(self.selectDatasourceCombo, list(self.rasterDSList.keys()), predef=provider)
        self.lineEdit.setPlainText(source)
        self.show()
        self.raise_()
        self.activateWindow()

    def cancelDialog(self):
        '''
        landing method clicking cancel in button box
        '''
        self.hide()

    def changeDataSourceAction(self):
        '''
        landing method clicking apply in button box
        '''
        self.applyDataSource(
            self.layer,
            self.selectDatasourceCombo.currentText().lower().replace(' ', ''),
            self.lineEdit.toPlainText(),
        )

    def applyDataSource(self, applyLayer, newProvider, newDatasource):
        '''
        method to verify applying datasource/provider before definitive change to avoid qgis crashes
        '''
        self.hide()
        if applyLayer.type() == QgsMapLayer.VectorLayer:
            probeLayer = QgsVectorLayer(newDatasource, "probe", newProvider)
        else:
            probeLayer = QgsRasterLayer(newDatasource, "probe", newProvider)
        if not probeLayer.isValid():
            self.iface.messageBar().pushMessage(
                "Error",
                "New data source is not valid: " + newProvider + "|" + newDatasource,
                level=Qgis.MessageLevel.Critical,
                duration=4,
            )
            return None

        if applyLayer.type() == QgsMapLayer.VectorLayer and probeLayer.geometryType() != applyLayer.geometryType():
            self.iface.messageBar().pushMessage(
                "Error",
                "Geometry type mismatch",
                level=Qgis.MessageLevel.Critical,
                duration=4,
            )
            return None

        newDatasource = probeLayer.source()
        self.setDataSource(applyLayer, newProvider, newDatasource)
        return True

    def setDataSource(self, layer, newProvider, newDatasource):
        '''
        Apply new datasource using the native QgsMapLayer.setDataSource API.

        Using the native method (QGIS >= 3.20) instead of XML patching preserves
        auxiliary storage (manual label positions, data-defined overrides) and
        emits dataSourceChanged, which lets the layer tree clear its warning /
        "temporary memory" indicators when the new source is valid.
        '''
        options = QgsDataProvider.ProviderOptions()
        options.transformContext = QgsProject.instance().transformContext()
        layer.setDataSource(newDatasource, layer.name(), newProvider, options)
        layer.reload()

        self.iface.mapCanvas().refresh()
        self.iface.layerTreeView().refreshLayerSymbology(layer.id())

    def populateComboBox(self, combo, items, dataPayload=None, predef=None, sort=None):
        '''
        procedure to fill specified combobox with provided list
        '''
        combo.blockSignals(True)
        combo.clear()
        model = QStandardItemModel(combo)
        predefInList = None
        for elem in items:
            item = QStandardItem(str(elem))
            model.appendRow(item)
            if elem == predef:
                predefInList = elem
        if sort:
            model.sort(0)
        combo.setModel(model)
        if predef:
            if predefInList:
                combo.setCurrentIndex(combo.findText(predefInList))
            else:
                combo.insertItem(0, predef)
                combo.setCurrentIndex(0)
        combo.blockSignals(False)
