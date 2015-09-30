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

from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtXml import *
from ui_changeDSDialog import Ui_changeDataSourceDialog
from qgis.gui import QgsManageConnectionsDialog, QgsMessageBar
import os.path
# create the dialog for zoom to point


class setDataSource(QtGui.QDialog, Ui_changeDataSourceDialog):

    def __init__(self,iface):
        QtGui.QDialog.__init__(self)
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.changeDataSourceAction)
        self.buttonBox.rejected.connect(self.cancelDialog)
        self.selectDatasourceCombo.activated.connect(self.selectDS)
        #self.selectDatasourceCombo.hide()
        self.openBrowser.clicked.connect(self.openFileBrowser)
        self.rasterDSList = {"wms":"Web Map Service (WMS)","gdal":"Raster images (GDAL)"}
        self.vectorDSList = {"ogr":"Vector layers (OGR)","delimited text": "Delimited Text", "gpx":" GPS eXchange Format", "postgres": "Postgis database layer","spatialite": "Spatialite database layer","oracle": "Oracle spatial database layer","mysql": "Mysql spatial database layer"}
        self.browsable=("ogr","gdal")

    def openFileBrowser(self):
        exts = "All files (*.*);;ESRI shapefiles (*.shp);; Geojson (*.geojson);;Keyhole markup language (*.kml *.kmz)"
        fileName = QtGui.QFileDialog.getOpenFileName(None,"select OGR vector file", os.path.dirname(self.layer.source()), exts)
        if fileName:
            self.lineEdit.setPlainText(fileName)

    def selectDS(self,i):
        print "changed combo",i
        if self.selectDatasourceCombo.itemText(i) in self.browsable:
        #if self.selectDatasourceCombo.currentIndex()==0:
            self.openBrowser.setEnabled(True)
        else:
            self.openBrowser.setDisabled(True)

    def changeDataSource(self,layer):
        self.layer = layer
        if layer.type() == QgsMapLayer.VectorLayer:
            self.populateComboBox(self.selectDatasourceCombo,self.vectorDSList.keys(),predef=self.layer.dataProvider().name())
        else:
            self.populateComboBox(self.selectDatasourceCombo,self.rasterDSList.keys(),predef=self.layer.dataProvider().name())
        self.lineEdit.setPlainText(self.layer.source())
        self.selectDS(0)
        print self.layer.dataProvider().name()
        self.show()

    def cancelDialog(self):
        self.hide()

    def recoverJoins(self, oldLayer, newLayer):
        for layer in self.iface.legendInterface().layers():
            if layer.type() == QgsMapLayer.VectorLayer:
                for joinDef in layer.vectorJoins():
                    if joinDef.joinLayerId == oldLayer.id():
                        newJoinDef = joinDef
                        newJoinDef.joinLayerId = newLayer.id()
                        layer.removeJoin(oldLayer.id())
                        layer.addJoin(newJoinDef)

    def changeDataSourceAction(self):
        self.applyDataSource(self.layer,self.selectDatasourceCombo.currentText().lower().replace(' ',''),self.lineEdit.toPlainText())

    def applyDataSource(self,applyLayer,newDatasourceType,newDatasource):
        self.hide()
        # read layer definition
        XMLDocument = QDomDocument("style")
        XMLMapLayers = QDomElement()
        XMLMapLayers = XMLDocument.createElement("maplayers")
        XMLMapLayer = QDomElement()
        XMLMapLayer = XMLDocument.createElement("maplayer")
        applyLayer.writeLayerXML(XMLMapLayer,XMLDocument)
        self.iface.setActiveLayer(applyLayer)
        # new layer import
        nlayer = QgsVectorLayer(newDatasource,"probe", newDatasourceType)
        if not nlayer.isValid():
            self.iface.messageBar().pushMessage("Error", "New data source is not valid: "+newDatasourceType+"|"+newDatasource, level=QgsMessageBar.CRITICAL, duration=4)
            return None
        if nlayer == QgsMapLayer.VectorLayer and nlayer.geometryType() != self.layer.geometryType():
            self.iface.messageBar().pushMessage("Error", "Geometry type mismatch", level=QgsMessageBar.CRITICAL, duration=4)
            return None
        print applyLayer.dataProvider().name()
        # modify DOM element with new layer reference
        print nlayer.source()
        #print os.path.relpath(nlayer.source(),QgsProject.instance().readPath("./")).replace('\\','/')
        if newDatasourceType == "ogr" or newDatasourceType == "gdal" :
            try:
                newDatasource = os.path.relpath(nlayer.source(),QgsProject.instance().readPath("./")).replace('\\','/')
            except:
                newDatasource = nlayer.source()
        else:
            newDatasource = nlayer.source()
        print newDatasource
        self.setDataSource(applyLayer,newDatasource,newDatasourceType)
        return True

    def setDataSource(self,layer,newUri,newDatasourceType):
        '''
        Method to apply a new datasource to a vector Layer
        '''
        #newDS, newUri = self.splitSource(newSourceUri)
        #newDatasourceType = newDS or layer.dataProvider().name()
        # read layer definition
        XMLDocument = QDomDocument("style")
        XMLMapLayers = QDomElement()
        XMLMapLayers = XMLDocument.createElement("maplayers")
        XMLMapLayer = QDomElement()
        XMLMapLayer = XMLDocument.createElement("maplayer")
        layer.writeLayerXML(XMLMapLayer,XMLDocument)
        # apply layer definition
        XMLMapLayer.firstChildElement("datasource").firstChild().setNodeValue(newUri)
        XMLMapLayer.firstChildElement("provider").firstChild().setNodeValue(newDatasourceType)
        XMLMapLayers.appendChild(XMLMapLayer)
        XMLDocument.appendChild(XMLMapLayers)
        layer.readLayerXML(XMLMapLayer)
        layer.reload()
        self.iface.actionDraw().trigger()
        self.iface.mapCanvas().refresh()
        self.iface.legendInterface().refreshLayerSymbology(layer)

    def populateComboBox(self,combo,list,dataPayload = None,predef = None,sort = None):
        #procedure to fill specified combobox with provided list
        combo.blockSignals (True)
        combo.clear()
        model=QStandardItemModel(combo)
        predefInList = None
        for elem in list:
            try:
                item = QStandardItem(unicode(elem))
            except TypeError:
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
                combo.insertItem(0,predef)
                combo.setCurrentIndex(0)
        combo.blockSignals (False)