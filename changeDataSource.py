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
from __future__ import print_function
from __future__ import absolute_import
from builtins import range
from builtins import object
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtXml import *
from PyQt5.QtWidgets import *
from qgis.core import *
# Initialize Qt resources from file resources.py
from . import resources_rc
# Import the code for the dialog
from .changeDataSource_dialog import changeDataSourceDialog,dataSourceBrowser
from .setdatasource import setDataSource
from qgis.gui import QgsMessageBar
import os.path


class changeDataSource(object):
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
        self.changeDSActionVector = QAction(QIcon(os.path.join(self.plugin_dir,"icon.png")), u"Change vector datasource", self.iface )
        self.changeDSActionRaster = QAction(QIcon(os.path.join(self.plugin_dir,"icon.png")), u"Change raster datasource", self.iface )
        self.iface.addCustomActionForLayerType(self.changeDSActionVector,"", QgsMapLayer.VectorLayer,True)
        self.iface.addCustomActionForLayerType(self.changeDSActionRaster,"", QgsMapLayer.RasterLayer,True)
        self.changeDSTool = setDataSource(self, )
        self.browserDialog = dataSourceBrowser()

        self.badLayersHandler = myBadLayerHandler(self)
        s = QSettings()
        handleBadLayersSetting = s.value("changeDataSource/handleBadLayers", defaultValue =  "undef")
        if handleBadLayersSetting == "undef":
            self.handleBadLayers = None
            self.dlg.handleBadLayersCheckbox.setChecked(False)
            s.setValue("changeDataSource/handleBadLayers","false")
        elif handleBadLayersSetting == "true":
            self.handleBadLayers = True
            self.dlg.handleBadLayersCheckbox.setChecked(True)
        elif handleBadLayersSetting == "false":
            self.handleBadLayers = None
            self.dlg.handleBadLayersCheckbox.setChecked(False)
        #if self.handleBadLayers:
        #    QgsProject.instance().setBadLayerHandler(self.badLayersHandler)
        self.connectSignals()
        self.session  = 0

    def connectSignals(self):
        self.changeDSActionVector.triggered.connect(self.changeLayerDS)
        self.changeDSActionRaster.triggered.connect(self.changeLayerDS)
        self.dlg.replaceButton.clicked.connect(self.replaceDS)
        self.dlg.layerTable.verticalHeader().sectionClicked.connect(self.activateSelection)
        self.dlg.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(lambda: self.buttonBoxHub("Reset"))
        self.dlg.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(lambda: self.buttonBoxHub("Apply"))
        self.dlg.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(lambda: self.buttonBoxHub("Cancel"))
        self.dlg.reconcileButton.clicked.connect(self.reconcileUnhandled)
        self.dlg.closedDialog.connect(self.removeServiceLayers)
        self.dlg.handleBadLayersCheckbox.stateChanged.connect(self.handleBadLayerOption)
        self.iface.initializationCompleted.connect(self.initHandleBadLayers)
        self.iface.projectRead.connect(self.recoverUnhandledLayers)
        self.iface.newProjectCreated.connect(self.updateSession)
        #self.initHandleBadLayers()

    def setEmbeddedLayer(self,layer):
        root = QgsProject.instance().layerTreeRoot()
        layerNode = root.findLayer(layer.id())
        layerNode.setCustomProperty("embedded","")

    def handleBadLayerOption(self):
        s = QSettings()
        if self.dlg.handleBadLayersCheckbox.isChecked():
            self.handleBadLayers = True
            s.setValue("changeDataSource/handleBadLayers","true")
            msg = "Next projects Bad Layers (layers not found)\nwill be handled by changeDataSource Plugin\n\nQGis restart is needed."
        else:
            self.handleBadLayers = None
            s.setValue("changeDataSource/handleBadLayers","false")
            msg = "Next projects Bad Layers (layers not found)\nwill be handled by default Handler\n\nQGis restart is needed."
        reply = QMessageBox.question(None,"HANDLE BAD LAYERS",msg, QMessageBox.Ok)
        #self.initHandleBadLayers()

    def initHandleBadLayers(self):
        '''
        get control of bad layer handling
        '''
        if self.handleBadLayers:
            QgsProject.instance().setBadLayerHandler(self.badLayersHandler)
            try:
                QgsProject.instance().writeProject.connect(self.backupUnhandledLayers)
            except:
                pass
        else:
            try:
                QgsProject.instance().writeProject.disconnect(self.backupUnhandledLayers)
            except:
                pass


    def updateSession(self):
        self.session  += 1

    def recoverUnhandledLayers(self):
        '''
        reload unhandled layers as dum layers
        '''
        if self.handleBadLayers and self.badLayersHandler.getUnhandledLayers():
            root = QgsProject.instance().layerTreeRoot()
            unhandledGroup = root.addGroup("unhandled layers")
            #unhandledGroupIndex = self.iface.legendInterface().addGroup("unhandled_layers",True,0)
            for key,data in self.badLayersHandler.badLayersProps.items():
                if data["type"] == "vector":
                    if data["geometry"] == "Point":
                        layerGeometry = "MultiPoint"
                    elif data["geometry"] == "Line":
                        layerGeometry = "MultiLineString"
                    elif data["geometry"] == "Polygon":
                        layerGeometry = "MultiPolygon"
                    unhandledLayer = QgsVectorLayer(layerGeometry+"?crs="+data["authid"], data["layername"], "memory")
                elif data["type"] == "raster":
                    unhandledLayer = QgsRasterLayer(os.path.join(os.path.dirname(__file__),"unhandled.tif"), data["layername"], "gdal")
                else:
                    return
                self.badLayersHandler.badLayersProps[key]["tempid"] = unhandledLayer.id()
                '''
                assign original style to unhandled layers
                '''
                context = QgsReadWriteContext()
                XMLDocument = QDomDocument("style")
                XMLMapLayers = XMLDocument.createElement("maplayers")
                XMLMapLayer = XMLDocument.createElement("maplayer")
                unhandledLayer.writeLayerXml(XMLMapLayer, XMLDocument, context)
                unhandledRendererDom = XMLMapLayer.namedItem("renderer-v2")
                validRendererDom = data["layerDom"].namedItem("renderer-v2").cloneNode()
                XMLMapLayer.replaceChild(validRendererDom,unhandledRendererDom)
                XMLMapLayers.appendChild(XMLMapLayer)
                XMLDocument.appendChild(XMLMapLayers)
                unhandledLayer.readLayerXml(XMLMapLayer, context)
                #unhandledLayer.reload()
                QgsMapLayerRegistry.instance().addMapLayer(unhandledLayer,False)
                unhandledGroup.addLayer(unhandledLayer)


            #print self.badLayersHandler.getUnhandledLayers()
        else:
            self.updateSession()

        #open dialog if clicked open on bad layers dialog
        if self.badLayersHandler.checkOpenDialogOnRecover():
            self.populateLayerTable(onlyUnhandled=True)
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.reconcileButton.show()


    def backupUnhandledLayers(self,projectDom):
        '''
        remove unhandled_layers group and child layers
        re-insert backupped unhandled layers in projectlayers
        '''

        if self.badLayersHandler.getUnhandledLayers():
            #remove unhandled layers group from legend
            legendNode = projectDom.namedItem("legend")
            legendGroups = projectDom.elementsByTagName("legendgroup")
            for item in range(0,legendGroups.count()):
                group = legendGroups.item(item)
                #print group.attributes().namedItem("name").nodeValue()
                if group.attributes().namedItem("name").nodeValue() == "unhandled layers":
                    group.parentNode().removeChild(group)

            #remove unhandled layers group from layer-tree-group
            layertreeNode = projectDom.namedItem("layer-tree-group")
            layertreeGroups = projectDom.elementsByTagName("layer-tree-group")
            for item in range(0,layertreeGroups.count()):
                group = layertreeGroups.item(item)
                #print group.attributes().namedItem("name").nodeValue()
                if group.attributes().namedItem("name").nodeValue() == "unhandled layers":
                    group.parentNode().removeChild(group)

            #remove unhandled layers group from maplayers
            projectlayersNode = projectDom.namedItem("projectlayers")
            projectlayers = projectlayersNode.toElement().elementsByTagName("maplayer")
            projectlayers = projectDom.elementsByTagName("maplayer")
            for item in range(0,projectlayers.count()):
                maplayer = projectlayers.item(item)
                maplayerId = maplayer.namedItem("id").firstChild().nodeValue()
                if maplayerId in list(self.badLayersHandler.badLayersProps.keys()):
                    maplayer.parentNode().removeChild(maplayer)

            #add bad Layers DOM to projectlayers
            qgisElement = projectDom.namedItem("qgis")
            XMLUnhandledLayers = projectDom.createElement("projectlayers")
            legendGroups = projectDom.elementsByTagName("legendgroup")
            for key,data in self.badLayersHandler.badLayersProps.items():
                QgsMapLayerRegistry.instance().removeMapLayer(key)
                unhandledDom = data["layerDom"].cloneNode().toElement()
                XMLUnhandledLayers.appendChild(unhandledDom)
            qgisElement.appendChild(XMLUnhandledLayers)

            '''
            qgisElement = projectDom.namedItem("qgis")
            XMLUnhandledLayers = projectDom.createElement("unhandledlayers")
            for key,data in self.badLayersHandler.unhandledLayers.iteritems():
                print key
                QgsMapLayerRegistry.instance().removeMapLayer(key)
                unhandledDom = data["layerDom"].cloneNode().toElement()
                unhandledDom.setTagName("unhandledlayer")
                XMLUnhandledLayers.appendChild(unhandledDom)
            qgisElement.appendChild(XMLUnhandledLayers)
            '''

    def activateSelection(self,idx):
        indexes = []
        for selectionRange in self.dlg.layerTable.selectedRanges():
            indexes.extend(list(range(selectionRange.topRow(), selectionRange.bottomRow()+1)))
        if indexes != []:
            self.dlg.onlySelectedCheck.setChecked(True)
        else:
            self.dlg.onlySelectedCheck.setChecked(False)

    def changeLayerDS(self):
        self.dlg.hide()
        self.changeDSTool.openDataSourceDialog(self.iface.layerTreeView().currentLayer(), self.badLayersHandler)

    def unload(self):
        """
        Disconnects from signals. Removes the plugin menu item and icon from QGIS GUI.
        """
        self.iface.removeCustomActionForLayerType(self.changeDSActionVector)
        self.iface.removeCustomActionForLayerType(self.changeDSActionRaster)
        self.iface.initializationCompleted.disconnect(self.initHandleBadLayers)
        self.iface.projectRead.disconnect(self.recoverUnhandledLayers)
        try:
            QgsProject.instance().writeProject.disconnect(self.backupUnhandledLayers)
        except:
            pass

        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&changeDataSource'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def populateLayerTable(self, onlyUnhandled = None):
        '''
        method to write layer info in layer table
        '''
        self.changeDSTool.populateComboBox(self.dlg.datasourceCombo,[""]+list(self.changeDSTool.vectorDSList.keys())+list(self.changeDSTool.rasterDSList.keys()))
        self.dlg.layerTable.clear()
        for row in range(self.dlg.layerTable.rowCount()):
            self.dlg.layerTable.removeRow(row)
        self.dlg.layerTable.setRowCount(0)
        self.dlg.layerTable.setColumnCount(5)
        self.dlg.layerTable.setHorizontalHeaderItem(0,QTableWidgetItem("ID"))
        self.dlg.layerTable.setHorizontalHeaderItem(1,QTableWidgetItem("Layer Name"))
        self.dlg.layerTable.setHorizontalHeaderItem(2,QTableWidgetItem("Type"))
        self.dlg.layerTable.setHorizontalHeaderItem(3,QTableWidgetItem("Data source"))
        self.dlg.layerTable.setHorizontalHeaderItem(4,QTableWidgetItem(""))

        layersPropLayerDef = "Point?crs=epsg:3857&field=layerid:string(200)&field=layername:string(200)&field=layertype:string(20)&field=geometrytype:string(20)&field=provider:string(20)&field=datasource:string(250)&field=authid:string(20)"
        self.layersPropLayer = QgsVectorLayer(layersPropLayerDef,"layerTable","memory")
        dummyFeatures = []

        self.dlg.layerTable.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        self.dlg.layerTable.horizontalHeader().setClickable(False)

        self.dlg.layerTable.hideColumn(0)
        self.dlg.layerTable.hideColumn(5)
        self.dlg.layerTable.hideColumn(6)
        lr = QgsMapLayerRegistry.instance()

        for layer in lr.mapLayers().values():
            if layer.type() == QgsMapLayer.VectorLayer or layer.type() == QgsMapLayer.RasterLayer:
                provider = None
                if self.badLayersHandler.getActualLayersIds() and layer.id() in self.badLayersHandler.getActualLayersIds():
                    provider = self.badLayersHandler.getUnhandledLayerFromActualId(layer.id())["provider"]
                    source = self.badLayersHandler.getUnhandledLayerFromActualId(layer.id())["datasource"]
                    source = QgsProject.instance().readPath(source)
                    cellStyle = "QLineEdit{background: rgb(190,170,160);font: italic;}"
                else:
                    if not onlyUnhandled:
                        provider = layer.dataProvider().name()
                        source = layer.source()
                        cellStyle = ""
                if provider:
                    lastRow = self.dlg.layerTable.rowCount()
                    self.dlg.layerTable.insertRow(lastRow)
                    self.dlg.layerTable.setCellWidget(lastRow,0,self.getLabelWidget(layer.id(),0,style = cellStyle))
                    self.dlg.layerTable.setCellWidget(lastRow,1,self.getLabelWidget(layer.name(),1,style = cellStyle))
                    self.dlg.layerTable.setCellWidget(lastRow,2,self.getLabelWidget(provider,2,style = cellStyle))
                    self.dlg.layerTable.setCellWidget(lastRow,3,self.getLabelWidget(source,3,style = cellStyle))
                    self.dlg.layerTable.setCellWidget(lastRow,4,self.getButtonWidget(lastRow))

                    layerDummyFeature = QgsFeature(self.layersPropLayer.pendingFields())
                    if layer.type() == QgsMapLayer.VectorLayer:
                        type = "vector"
                        enumGeometryTypes =('Point','Line','Polygon','UnknownGeometry','NoGeometry')
                        geometry = enumGeometryTypes[layer.geometryType()]
                    else:
                        type = "raster"
                        geometry = ""
                    dummyGeometry = QgsGeometry.fromPoint(self.iface.mapCanvas().center())
                    layerDummyFeature.setGeometry(dummyGeometry)
                    layerDummyFeature.setAttributes([layer.id(), layer.name(), type, geometry, provider, source, layer.crs().authid()])
                    dummyFeatures.append(layerDummyFeature)

        self.layersPropLayer.dataProvider().addFeatures(dummyFeatures)
        QgsMapLayerRegistry.instance().addMapLayer(self.layersPropLayer)
        core.QgsProject.instance().layerTreeRoot().findLayer(self.layersPropLayer.id()).setItemVisibilityChecked(False)
        self.dlg.mFieldExpressionWidget.setLayer(self.layersPropLayer)
        self.dlg.layerTable.resizeColumnToContents(1)
        self.dlg.layerTable.horizontalHeader().setResizeMode(2,QHeaderView.ResizeToContents)
        self.dlg.layerTable.setColumnWidth(4,30)
        self.dlg.layerTable.setShowGrid(False)
        self.dlg.layerTable.horizontalHeader().setResizeMode(3,QHeaderView.Stretch) # was QHeaderView.Stretch

    def getButtonWidget(self,row):
        edit = QPushButton("...",parent = self.dlg.layerTable)
        edit.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
        edit.clicked.connect(lambda: self.browseAction(row))
        return edit

    def browseAction(self,row):
        '''
        method to open qgis browser dialog to get new datasource/provider
        '''
        layerId = self.dlg.layerTable.cellWidget(row,0).text()
        layerName = self.dlg.layerTable.cellWidget(row,1).text()
        newType,newProvider,newDatasource = dataSourceBrowser.uri(title = layerName)
        #check if databrowser return a incompatible layer type
        rowLayer = QgsMapLayerRegistry.instance().mapLayer(layerId)
        enumLayerTypes = ("vector","raster","plugin")
        if newType and enumLayerTypes[rowLayer.type()] != newType:
            self.iface.messageBar().pushMessage("Error", "Layer type mismatch %s/%s" % (enumLayerTypes[rowLayer.type()], newType), level=QgsMessageBar.CRITICAL, duration=4)
            return None
        if newDatasource:
            self.dlg.layerTable.cellWidget(row,3).setText(newDatasource)
        if newProvider:
            self.dlg.layerTable.cellWidget(row,2).setText(newProvider)

    def getLabelWidget(self,txt,column, style = None):
        '''
        method that returns a preformatted qlineedit widget
        '''
        edit = QLineEdit(parent = self.dlg.layerTable)
        idealWidth = QApplication.instance().fontMetrics().width(txt)
        edit.setMinimumWidth(idealWidth)
        if column == 2:
            edit.setMaximumWidth(60)
        edit.setText(txt)
        edit.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Ignored)
        if style:
            edit.setStyleSheet(style)
        else:
            edit.setStyleSheet("QLineEdit{background: rgba(0,190,0, 0%);}")
        edit.column = column
        edit.changed = None
        if column == 1:
                edit.setReadOnly(True)
        else:
            edit.textChanged.connect(lambda: self.highlightCell(edit,"QLineEdit{background: yellow;}"))
        edit.setCursorPosition(0)
        return edit

    def highlightCell(self,cell,newStyle):
        cell.setStyleSheet(newStyle)
        cell.changed = True

    def replaceDS(self):
        '''
        method to replace the datasource string accordind to find/replace string or to expression result if valid
        '''
        self.replaceList=[]
        indexes = []
        #build replace list
        if self.dlg.onlySelectedCheck.isChecked():
            for selectionRange in self.dlg.layerTable.selectedRanges():
                indexes.extend(list(range(selectionRange.topRow(), selectionRange.bottomRow()+1)))
            for row in indexes:
                self.replaceList.append(QgsMapLayerRegistry.instance().mapLayer(self.dlg.layerTable.cellWidget(row,0).text()))
        else:
            for row in range(0,self.dlg.layerTable.rowCount()):
                indexes.append(row)
                self.replaceList.append(QgsMapLayerRegistry.instance().mapLayer(self.dlg.layerTable.cellWidget(row,0).text()))
        for row in indexes:
            layerId = self.dlg.layerTable.cellWidget(row,0)
            cell = self.dlg.layerTable.cellWidget(row,3)
            orig = cell.text()
            if self.dlg.mFieldExpressionWidget.isValidExpression():
                exp = QgsExpression(self.dlg.mFieldExpressionWidget.currentText())
                exp.prepare(self.layersPropLayer.pendingFields())
                cell.setText(exp.evaluate(next(self.layersPropLayer.getFeatures(QgsFeatureRequest(row+1)))))
            else:
                cell.setText(cell.text().replace(self.dlg.findEdit.text(),self.dlg.replaceEdit.text()))
            if self.dlg.datasourceCombo.currentText() != "":
                self.dlg.layerTable.cellWidget(row,2).setText(self.dlg.datasourceCombo.currentText())

    def applyDSChanges(self, reconcileUnhandled = False):
        '''
        method to scan table row and apply the provider/datasource strings if changed
        '''

        for row in range(0,self.dlg.layerTable.rowCount()):
            rowProviderCell = self.dlg.layerTable.cellWidget(row,2)
            rowDatasourceCell = self.dlg.layerTable.cellWidget(row,3)
            rowLayerID = self.dlg.layerTable.cellWidget(row,0).text()
            rowLayerName = self.dlg.layerTable.cellWidget(row,1).text()
            rowProvider = rowProviderCell.text()
            rowDatasource = rowDatasourceCell.text()
            rowLayer = QgsMapLayerRegistry.instance().mapLayer(rowLayerID)
            if reconcileUnhandled and self.badLayersHandler.isUnhandled(rowLayerID):
                rowProviderChanging = True
                rowDatasourceChanging = True
            else:
                rowProviderChanging = rowProviderCell.changed
                rowDatasourceChanging = rowDatasourceCell.changed

            if rowProviderChanging or rowDatasourceChanging:
                # fix_print_with_import
                print(("ROWS",rowLayer,rowProvider,rowDatasource))
                if self.changeDSTool.applyDataSource(rowLayer,rowProvider,rowDatasource):
                    resultStyle = "QLineEdit{background: green;}"
                    if self.badLayersHandler.isUnhandled(rowLayerID):
                        # fix_print_with_import
                        print(self.badLayersHandler.getActualLayersIds())
                        self.badLayersHandler.removeUnhandledLayer(rowLayer.id())
                        if not self.badLayersHandler.getUnhandledLayers():
                            self.removeServiceLayers()
                else:
                    resultStyle = "QLineEdit{background: red;}"
                if rowProviderChanging:
                    rowProviderCell.setStyleSheet(resultStyle)
                if rowDatasourceChanging:
                    rowDatasourceCell.setStyleSheet(resultStyle)

    def removeServiceLayers(self):
        '''
        method to remove service properties layer, used for expression changes
        and unhandled layers group if empty
        '''
        # fix_print_with_import
        print("removing")
        try:
            QgsMapLayerRegistry.instance().removeMapLayer(self.layersPropLayer.id())
        except:
            pass
        #remove unhandled layers group if present
        unhandledGroup = QgsProject.instance().layerTreeRoot().findGroup("unhandled layers")
        # fix_print_with_import
        print(unhandledGroup)
        if unhandledGroup:
            # fix_print_with_import
            print(unhandledGroup.children())
            if not unhandledGroup.children():
                unhandledGroup.parent().removeChildNode(unhandledGroup)


    def buttonBoxHub(self,kod):
        '''
        method to handle button box clicking
        '''
        # fix_print_with_import
        print(kod)
        if kod == "Reset":
            # fix_print_with_import
            print("reset")
            self.removeServiceLayers()
            self.populateLayerTable()
        elif kod == "Cancel":
            self.removeServiceLayers()
            self.dlg.hide()
        elif kod == "Apply":
            self.applyDSChanges()

    def reconcileUnhandled(self):
        self.applyDSChanges(reconcileUnhandled = True)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        if not self.dlg.isVisible():
            self.populateLayerTable()

            if self.badLayersHandler.getUnhandledLayers():
                self.dlg.reconcileButton.show()
            else:
                self.dlg.reconcileButton.hide()

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
        else:
            self.dlg.raise_()


class browseLineEdit(QLineEdit):
    '''
    class to provide custom resizable lineedit
    '''
    buttonClicked = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(browseLineEdit, self).__init__(parent)

        self.button = QToolButton(self)
        self.button.setIcon(QIcon(os.path.join(os.path.dirname(__file__),"BrowseButton.png")))
        self.button.setStyleSheet('border: 0px; padding: 0px;')
        self.button.setCursor(Qt.ArrowCursor)
        self.button.clicked.connect(self.buttonClicked.emit)

        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        buttonSize = self.button.sizeHint()

        self.setStyleSheet('QLineEdit {padding-left: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth*2 + 2),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth*2 + 2))

    def resizeEvent(self, event):
        buttonSize = self.button.sizeHint()
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.button.move(self.rect().right() - frameWidth - buttonSize.width(),
                         (self.rect().bottom() - buttonSize.height() + 1)/2)
        super(browseLineEdit, self).resizeEvent(event)


class myBadLayerHandler(QgsProjectBadLayerHandler):
    '''
    class that inherits default QgsProjectBadLayerHandler to
    '''
    def __init__(self,parent):
        super(myBadLayerHandler, self).__init__()
        self.parent = parent
        self.badLayers = None
        self.badLayersProps = None
        self.badProject = None
        self.badSession = None
        self.openDialogOnRecover = None

    def removeUnhandledLayer(self,removeKey):
        if self.getUnhandledLayers() and removeKey in self.getUnhandledLayers():
            del self.badLayersProps[removeKey]

    def isUnhandled(self,layerid):
        if self.getUnhandledLayers():
            return layerid in self.getActualLayersIds()
        else:
            return None

    def getUnhandledLayers(self):
        if self.badSession == self.parent.session:
            return self.badLayersProps
        else:
            #print "badSESSION",self.badSession,"actualSESSION",self.parent.session
            return None

    def getUnhandledLayersOrder(self,unhandledId):
        badId = self.getIdFromActualId(unhandledId)
        return self.originalOrder.index(badId)

    def getUnhandledLayerFromBadId(self,badId):
        return QgsMapLayerRegistry.instance().mapLayer( self.getUnhandledLayers()[badId]["tempid"] )

    def getActualLayersIds(self):
        if self.getUnhandledLayers():
            actualLayersIds = {}
            for key,data in self.getUnhandledLayers().items():
                actualLayersIds[data["tempid"]] = key
            return actualLayersIds
        else:
            return None

    def getIdFromActualId(self,actualId):
        if self.getUnhandledLayers():
            try:
                return self.getActualLayersIds()[actualId]
            except:
                None
        else:
            None

    def getUnhandledLayerFromActualId(self,actualId):
        '''
        method to build original layer order: not used, leaved for future use.
        '''
        id = self.getIdFromActualId(actualId)
        if id:
            return self.getUnhandledLayers()[id]
        else:
            None

    def buildOriginalOrder(self):
        '''
        method to build original layer order: not used, leaved for future use.
        '''
        self.originalOrder = []
        legendElements = projectDom.elementsByTagName("legendlayer")
        for legendItem in range(0,legendElements.count()):
            legendLayerId = legendElements.item(legendItem).firstChild().firstChild().attributes().namedItem("layerid").nodeValue()
            if legendLayerId in self.badLayersProps:
                id = self.badLayersProps[legendLayerId]["tempid"]
            else:
                id = legendLayerId
            self.originalOrder.append(id)

    def checkOpenDialogOnRecover(self):
        '''
        method to return once the open dialog on recover option
        '''
        if self.openDialogOnRecover:
            return True
            self.openDialogOnRecover = None
        else:
            return None


    def handleBadLayers(self,layers,projectDom):
        '''
        method the overrides QgsProjectBadLayerHandler method to provide alternative bad layers handling
        bad layers = lost layers
        bad datasources: datasources of bad layers
        unhandled layers: actual bad layers alias
        unhandled datasources: datasources of the unhandled layers
        '''
        self.badLayers = layers
        self.badSession = self.parent.session
        self.badProjectDom = projectDom
        self.badLayersProps = {}
        #remember original layer order
        self.originalOrder = []
        legendElements = projectDom.elementsByTagName("legendlayer")
        for legendItem in range(0,legendElements.count()):
            legendLayerId = legendElements.item(legendItem).firstChild().firstChild().attributes().namedItem("layerid").nodeValue()
            self.originalOrder.append(legendLayerId)
        self.badProject = QgsProject.instance().fileName ()
        unhandledMessage = "The following layers have not valid datasource:\n\n"
        #scanning DOM to store lost layers properties
        for layer in layers:
            type = layer.attributes().namedItem("type").firstChild().nodeValue()
            geometry = layer.attributes().namedItem("geometry").firstChild().nodeValue()
            id = layer.namedItem("id").firstChild().nodeValue()
            provider = layer.namedItem("provider").firstChild().nodeValue()
            datasource = layer.namedItem("datasource").firstChild().nodeValue()
            layername = layer.namedItem("layername") .firstChild().nodeValue()
            unhandledMessage += layername+"\n"
            srsItem = layer.namedItem("srs")
            authid = srsItem.firstChild().namedItem("authid").firstChild().nodeValue()
            XMLDocument = QDomDocument("unhandled layers")
            XMLMapLayers = QDomElement()
            XMLMapLayers = XMLDocument.createElement("maplayers")
            newLayer = layer.cloneNode()
            XMLMapLayers.appendChild(newLayer.toElement())
            XMLDocument.appendChild(XMLMapLayers)
            count = 0
            legendgroup = None
            legendcount = None
            for legendItem in range(0,legendElements.count()):
                legendLayerId = legendElements.item(legendItem).firstChild().firstChild().attributes().namedItem("layerid").nodeValue()
                if legendLayerId == id:
                    legendgroup = legendElements.item(legendItem).parentNode().attributes().namedItem("name").nodeValue()
                    legendcount = count
                count += 1
            self.badLayersProps[id]= {"id":id,"layername":layername,"type":type,"geometry":geometry,"provider":provider,"datasource":datasource,"authid":authid,"legendgroup":legendgroup,"legendcount":legendcount,"layerDom":layer.cloneNode()}
            #print self.unhandledLayers[id]
        unhandledMessage += "\nThese layers are stored under unhandled layers group\nand can be restored assigning a valid datasource when available \nwith change datasouce legend contextual menu command\nor by changeDataSource plugin table\n"

        # open message box with bad layers warning
        mbox = QMessageBox(None)
        mbox.setText(unhandledMessage);
        mbox.setWindowTitle("changeDataSource plugin: Managing bad layers")
        myYesButton = mbox.addButton("Open plugin table", QMessageBox.YesRole);
        myNoButton = mbox.addButton("OK", QMessageBox.NoRole);
        mbox.setIcon(QMessageBox.Warning);
        mbox.exec_()
        if mbox.clickedButton() == myYesButton:
            self.openDialogOnRecover = True
        else:
            self.openDialogOnRecover = None

