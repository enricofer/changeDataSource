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
from changeDataSource_dialog import dataSourceBrowser

from qgis.gui import QgsManageConnectionsDialog, QgsMessageBar
import os.path


class setDataSource(QtGui.QDialog, Ui_changeDataSourceDialog):

    def __init__(self,parent):
        QtGui.QDialog.__init__(self)
        self.parent = parent
        self.iface = parent.iface
        self.canvas = self.iface.mapCanvas()
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.changeDataSourceAction)
        self.buttonBox.rejected.connect(self.cancelDialog)
        self.selectDatasourceCombo.activated.connect(self.selectDS)
        self.openBrowser.clicked.connect(self.openFileBrowser)
        self.rasterDSList = {"wms":"Web Map Service (WMS)","gdal":"Raster images (GDAL)"}
        self.vectorDSList = {"ogr":"Vector layers (OGR)","delimitedtext": "Delimited Text", "gpx":" GPS eXchange Format", "postgres": "Postgis database layer","spatialite": "Spatialite database layer","oracle": "Oracle spatial database layer","mysql": "Mysql spatial database layer"}
        self.browsable=("ogr","gdal")

    def openFileBrowser(self):
        '''
        method used to open datasource browser dialog to get new provider/uri for the single layer
        '''
        type,provider,fileName = dataSourceBrowser.uri()
        enumLayerTypes = ("vector","raster","plugin")
        if type and enumLayerTypes[self.layer.type()] != type:
            self.iface.messageBar().pushMessage("Error", "Layer type mismatch: %s/%s" % (enumLayerTypes[self.layer.type()],type), level=QgsMessageBar.CRITICAL, duration=4)
        else:
            if fileName:
                self.lineEdit.setPlainText(fileName)
            if provider:
                allSources = [self.selectDatasourceCombo.itemText(i) for i in range(self.selectDatasourceCombo.count())]
                if type in allSources:
                    self.selectDatasourceCombo.setCurrentIndex(allSources.index(provider))
                else:
                    self.selectDatasourceCombo.addItem(provider)
                    self.selectDatasourceCombo.setCurrentIndex(self.selectDatasourceCombo.count()-1)

    def selectDS(self,i):
        '''
        method to catch datasource combo edits. No longer used. Stay here for future uses.
        '''
        pass

    def openDataSourceDialog(self,layer):
        '''
        method to prep and show single datasource edit dialog
        '''
        self.layer = layer
        self.setWindowTitle(layer.name())
        #if layer is unhandled get unhandled parameters
        if self.parent.badLayersHandler.getActualLayersIds() and self.layer.id() in self.parent.badLayersHandler.getActualLayersIds():

            provider = self.parent.badLayersHandler.getUnhandledLayerFromActualId(self.layer.id())["provider"]
            source = self.parent.badLayersHandler.getUnhandledLayerFromActualId(self.layer.id())["datasource"]
            self.label.setText("unhandled URI:")
        else:
            provider = self.layer.dataProvider().name()
            source = self.layer.source()
            self.label.setText("URI:")

        if provider == "ogr" or provider == "gdal":
            source = QgsProject.instance().readPath(source)

        if layer.type() == QgsMapLayer.VectorLayer:
            self.populateComboBox(self.selectDatasourceCombo,self.vectorDSList.keys(),predef = provider)
        else:
            self.populateComboBox(self.selectDatasourceCombo,self.rasterDSList.keys(),predef = provider)
        self.lineEdit.setPlainText(source)
        #self.selectDS(self.selectDatasourceCombo.currentIndex())
        #print source
        self.show()
        self.raise_()
        self.activateWindow()

    def cancelDialog(self):
        '''
        landing method clicking cancel in button box
        '''
        self.hide()

    def exrecoverJoins(self, oldLayer, newLayer):
        '''
        convenience method to rebuild joins if lost
        '''
        for layer in self.iface.legendInterface().layers():
            if layer.type() == QgsMapLayer.VectorLayer:
                for joinDef in layer.vectorJoins():
                    if joinDef.joinLayerId == oldLayer.id():
                        newJoinDef = joinDef
                        newJoinDef.joinLayerId = newLayer.id()
                        layer.removeJoin(oldLayer.id())
                        layer.addJoin(newJoinDef)

    def changeDataSourceAction(self):
        '''
        landing method clicking apply in button box
        '''
        self.applyDataSource(self.layer,self.selectDatasourceCombo.currentText().lower().replace(' ',''),self.lineEdit.toPlainText())
        #make a def procedure of this ....
        layerIsUnhandled = self.parent.badLayersHandler.getActualLayersIds() and self.layer.id() in self.parent.badLayersHandler.getActualLayersIds()
        if layerIsUnhandled:
            print self.parent.badLayersHandler.getActualLayersIds()
            self.parent.badLayersHandler.removeUnhandledLayer(self.layer.id())
            if not self.parent.badLayersHandler.getUnhandledLayers():
                self.parent.removeServiceLayers()


    def applyDataSource(self,applyLayer,newProvider,newDatasource):
        '''
        method to verify applying datasource/provider before definitive change to avoid qgis crashes
        '''
        self.hide()
        # new layer import
        if applyLayer.type() == QgsMapLayer.VectorLayer:
            probeLayer = QgsVectorLayer(newDatasource,"probe", newProvider)
        else:
            probeLayer = QgsRasterLayer(newDatasource,"probe", newProvider)
        if not probeLayer.isValid():
            self.iface.messageBar().pushMessage("Error", "New data source is not valid: "+newProvider+"|"+newDatasource, level=QgsMessageBar.CRITICAL, duration=4)
            return None
        if applyLayer.type() == QgsMapLayer.VectorLayer and probeLayer.geometryType() != applyLayer.geometryType():
            self.iface.messageBar().pushMessage("Error", "Geometry type mismatch", level=QgsMessageBar.CRITICAL, duration=4)
            return None
        #if URI is a local path transform it to absolute path
        #if newProvider == "ogr" or newProvider == "gdal" :
        #    try:
        #        newDatasource = os.path.relpath(probeLayer.source(),QgsProject.instance().readPath("./")).replace('\\','/')
        #    except:
        #        newDatasource = probeLayer.source()
        #else:
        #
        newDatasource = probeLayer.source()
        self.setDataSource(applyLayer, newProvider, newDatasource)
        return True

    def setDataSource(self, layer, newProvider, newDatasource):
        '''
        Method to write the new datasource to a raster Layer
        '''
        if "setDataSource" in dir(layer):
            qgisVersionOk = True
        else:
            qgisVersionOk = False
        # read layer definition
        print qgisVersionOk
        #if qgisVersionOk and layer.type() == QgsMapLayer.VectorLayer:
            # try to use ad-hoc method if possible
            #layer.setDataSource(newDatasource,layer.name(),newProvider)
        #else:
        XMLDocument = QDomDocument("style")
        XMLMapLayers = XMLDocument.createElement("maplayers")
        XMLMapLayer = XMLDocument.createElement("maplayer")
        layer.writeLayerXML(XMLMapLayer,XMLDocument)
        # apply layer definition
        XMLMapLayer.firstChildElement("datasource").firstChild().setNodeValue(newDatasource)
        XMLMapLayer.firstChildElement("provider").firstChild().setNodeValue(newProvider)
        if self.parent.badLayersHandler.getActualLayersIds() and layer.id() in self.parent.badLayersHandler.getActualLayersIds():
            #if layer is unhandled, rendered dom definition is replaced with the old one
            unhandledDom = self.parent.badLayersHandler.getUnhandledLayerFromActualId(layer.id())["layerDom"]
            unhandledRenderer = unhandledDom.namedItem("renderer-v2").cloneNode()
            if XMLMapLayer.replaceChild(unhandledRenderer,XMLMapLayer.namedItem("renderer-v2")).isNull():
                print "unhandled layer invalid renderer"
        XMLMapLayers.appendChild(XMLMapLayer)
        XMLDocument.appendChild(XMLMapLayers)
        layer.readLayerXML(XMLMapLayer)
        layer.reload()

        if self.parent.badLayersHandler.getActualLayersIds() and layer.id() in self.parent.badLayersHandler.getActualLayersIds():
            #find original location of the layer
            storedGroupName = self.parent.badLayersHandler.getUnhandledLayerFromActualId(layer.id())["legendgroup"]
            if storedGroupName != "":
                originalGroup = QgsProject.instance().layerTreeRoot().findGroup(storedGroupName)
                if not originalGroup:
                    originalGroup = QgsProject.instance().layerTreeRoot()
            else:
                originalGroup = QgsProject.instance().layerTreeRoot()
            #moving the layer to the original location
            print "GRUPPO:",storedGroupName
            layerMoving = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
            originalGroup.insertChildNode(0,layerMoving.clone())
            layerMoving.parent().removeChildNode(layerMoving)
            originalGroup.setExpanded (True)
            #remove layer from unhandled layers
            self.parent.badLayersHandler.removeUnhandledLayer(self.parent.badLayersHandler.getIdFromActualId(layer.id()))

        self.iface.actionDraw().trigger()
        self.iface.mapCanvas().refresh()
        self.iface.legendInterface().refreshLayerSymbology(layer)

    def populateComboBox(self,combo,list,dataPayload = None,predef = None,sort = None):
        '''
        procedure to fill specified combobox with provided list
        '''
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