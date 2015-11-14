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
from PyQt4.QtXml import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from changeDataSource_dialog import changeDataSourceDialog,dataSourceBrowser
from setdatasource import setDataSource
from qgis.gui import QgsMessageBar
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
        self.dataBrowser = datasourceBrowser()

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
        self.changeDSTool = setDataSource(self)
        self.browserDialog = dataSourceBrowser()
        self.badLayersHandler = myBadLayerHandler(self)
        self.connectSignals()
        self.session  = 0

    def connectSignals(self):
        self.changeDSActionVector.triggered.connect(self.changeLayerDS)
        self.changeDSActionRaster.triggered.connect(self.changeLayerDS)
        self.dlg.replaceButton.clicked.connect(self.replaceDS)
        self.dlg.layerTable.verticalHeader().sectionClicked.connect(self.activateSelection)
        self.dlg.buttonBox.clicked.connect(self.buttonBoxHub)
        self.dlg.reconcileButton.clicked.connect(self.reconcileUnhandled)
        self.iface.initializationCompleted.connect(self.initHandleBadLayers)
        self.iface.projectRead.connect(self.recoverUnhandledLayers)
        self.iface.newProjectCreated.connect(self.updateSession)
        QgsProject.instance().setBadLayerHandler(self.badLayersHandler)
        QgsProject.instance().writeProject.connect(self.backupUnhandledLayers)

    def resetEmbeddedLayer(self):
        root = QgsProject.instance().layerTreeRoot()
        layerNode = root.findLayer(self.iface.legendInterface().currentLayer().id())
        layerNode.removeCustomProperty("embedded")
        layerNode.removeCustomProperty("embedded_project")

    def initHandleBadLayers(self):
        '''
        get control of bad layer handling
        '''
        self.badLayersHandler = myBadLayerHandler(self)
        try:
            QgsProject.instance().setBadLayerHandler(self.badLayersHandler)
            QgsProject.instance().writeProject.connect(self.backupUnhandledLayers)
        except:
            pass

    def updateSession(self):
        self.session  += 1

    def recoverUnhandledLayers(self):
        '''
        reload unhandled layers as dum layers
        '''
        if self.badLayersHandler.getUnhandledLayers():
            root = QgsProject.instance().layerTreeRoot()
            unhandledGroup = root.addGroup("unhandled layers")
            #unhandledGroupIndex = self.iface.legendInterface().addGroup("unhandled_layers",True,0)
            for key,data in self.badLayersHandler.unhandledLayers.iteritems():
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
                self.badLayersHandler.unhandledLayers[key]["tempid"] = unhandledLayer.id()
                '''
                assign original style to unhandled layers
                '''
                XMLDocument = QDomDocument("style")
                XMLDocumentControl = QDomDocument("style")
                XMLMapLayers = QDomElement()
                XMLMapLayers = XMLDocument.createElement("maplayers")
                XMLMapLayer = QDomElement()
                XMLMapLayer = XMLDocument.createElement("maplayer")
                unhandledLayer.writeLayerXML(XMLMapLayer,XMLDocument)
                unhandledRendererDom = XMLMapLayer.namedItem("renderer-v2")
                validRendererDom = data["layerDom"].namedItem("renderer-v2").cloneNode()
                XMLMapLayer.replaceChild(validRendererDom,unhandledRendererDom)
                XMLMapLayers.appendChild(XMLMapLayer)
                XMLDocument.appendChild(XMLMapLayers)
                unhandledLayer.readLayerXML(XMLMapLayer)
                #unhandledLayer.reload()
                QgsMapLayerRegistry.instance().addMapLayer(unhandledLayer,False)
                unhandledGroup.addLayer(unhandledLayer)


            #print self.badLayersHandler.getUnhandledLayers()
        else:
            self.updateSession()


    def backupUnhandledLayers(self,projectDom):
        '''
        remove unhandled_layers group and child layers
        re-insert backupped unhandled layers in projectlayers
        '''

        if self.badLayersHandler.getUnhandledLayers():
            legendNode = projectDom.namedItem("legend")
            #legendGroups = legendNode.toElement().elementsByTagName("legendgroup")
            legendGroups = projectDom.elementsByTagName("legendgroup")
            for item in range(0,legendGroups.count()):
                group = legendGroups.item(item)
                #print group.attributes().namedItem("name").nodeValue()
                if group.attributes().namedItem("name").nodeValue() == "unhandled layers":
                    group.parentNode().removeChild(group)
            layertreeNode = projectDom.namedItem("layer-tree-group")
            layertreeGroups = projectDom.elementsByTagName("layer-tree-group")
            for item in range(0,layertreeGroups.count()):
                group = layertreeGroups.item(item)
                #print group.attributes().namedItem("name").nodeValue()
                if group.attributes().namedItem("name").nodeValue() == "unhandled layers":
                    group.parentNode().removeChild(group)
            projectlayersNode = projectDom.namedItem("projectlayers")
            projectlayers = projectlayersNode.toElement().elementsByTagName("maplayer")
            projectlayers = projectDom.elementsByTagName("maplayer")
            for item in range(0,projectlayers.count()):
                maplayer = projectlayers.item(item)
                maplayerId = maplayer.namedItem("id").firstChild().nodeValue()
                if maplayerId in self.badLayersHandler.unhandledLayers.keys():
                    maplayer.parentNode().removeChild(maplayer)

            qgisElement = projectDom.namedItem("qgis")
            XMLUnhandledLayers = projectDom.createElement("projectlayers")
            for key,data in self.badLayersHandler.unhandledLayers.iteritems():
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
            indexes.extend(range(selectionRange.topRow(), selectionRange.bottomRow()+1))
        if indexes != []:
            self.dlg.onlySelectedCheck.setChecked(True)
        else:
            self.dlg.onlySelectedCheck.setChecked(False)

    def changeLayerDS(self):
        self.changeDSTool.changeDataSource(self.iface.legendInterface().currentLayer())
        
    def unload(self):
        """Disconnects from signals. Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.legendInterface().removeLegendLayerAction(self.changeDSActionVector)
        self.iface.legendInterface().removeLegendLayerAction(self.changeDSActionRaster)
        self.iface.initializationCompleted.disconnect(self.initHandleBadLayers)
        self.iface.projectRead.disconnect(self.recoverUnhandledLayers)
        QgsProject.instance().writeProject.disconnect(self.backupUnhandledLayers)

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
        self.dlg.layerTable.setColumnCount(5)
        self.dlg.layerTable.setHorizontalHeaderItem(0,QTableWidgetItem("ID"))
        self.dlg.layerTable.setHorizontalHeaderItem(1,QTableWidgetItem("Layer Name"))
        self.dlg.layerTable.setHorizontalHeaderItem(2,QTableWidgetItem("Type"))
        self.dlg.layerTable.setHorizontalHeaderItem(3,QTableWidgetItem("Data source"))
        self.dlg.layerTable.setHorizontalHeaderItem(4,QTableWidgetItem(""))
        #self.dlg.layerTable.setHorizontalHeaderItem(5,QTableWidgetItem(""))
        #self.dlg.layerTable.setHorizontalHeaderItem(6,QTableWidgetItem(""))

        layersPropLayerDef = "Point?crs=epsg:3857&field=layerid:string(200)&field=layername:string(200)&field=layertype:string(20)&field=geometrytype:string(20)&field=provider:string(20)&field=datasource:string(250)&field=authid:string(20)"
        self.layersPropLayer = QgsVectorLayer(layersPropLayerDef,"layerTable","memory")
        dummyFeatures = []

        self.dlg.layerTable.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        self.dlg.layerTable.horizontalHeader().setClickable(False)

        self.dlg.layerTable.hideColumn(0)
        self.dlg.layerTable.hideColumn(5)
        self.dlg.layerTable.hideColumn(6)
        lr = QgsMapLayerRegistry.instance()
        #self.dlg.layerTable.setRowCount(lr.count())
        if self.badLayersHandler.getUnhandledLayers():
            defaultLayerOrder = self.badLayersHandler.originalOrder
        else:
            defaultLayerOrder = []
            for layer in self.iface.legendInterface().layers():
                defaultLayerOrder.append(layer.id())
        #print defaultLayerOrder
        #for lid in lr.mapLayers():

        for lid in defaultLayerOrder:
            if lr.mapLayer( lid ):
                layer = lr.mapLayer( lid )
            else:
                layer = self.badLayersHandler.getUnhandledLayerFromBadId(lid)
            if layer.type() == QgsMapLayer.VectorLayer or layer.type() == QgsMapLayer.RasterLayer:
                lastRow = self.dlg.layerTable.rowCount()
                self.dlg.layerTable.insertRow(lastRow)
                #lastRow += 1
                if self.badLayersHandler.getActualLayersIds() and layer.id() in self.badLayersHandler.getActualLayersIds():
                    provider = self.badLayersHandler.getUnhandledLayerFromActualId(layer.id())["provider"]
                    source = self.badLayersHandler.getUnhandledLayerFromActualId(layer.id())["datasource"]
                    source = QgsProject.instance().readPath(source)
                    cellStyle = "QLineEdit{background: rgb(190,170,160);font: italic;}"
                    order = self.badLayersHandler.getUnhandledLayersOrder(layer.id())
                else:
                    provider = layer.dataProvider().name()
                    source = layer.source()
                    order = defaultLayerOrder.index(layer.id())
                    cellStyle = ""
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
                #orderWidget = QTableWidgetItem()
                #orderWidget.setData(Qt.EditRole,order)
                #self.dlg.layerTable.setItem(lastRow,5,orderWidget)
                #orderWidget.setData(Qt.EditRole,defaultLayerOrder[order])
                #self.dlg.layerTable.setItem(lastRow,6,orderWidget)
        #self.dlg.layerTable.sortItems(6)
        print dummyFeatures
        self.layersPropLayer.dataProvider().addFeatures(dummyFeatures)
        QgsMapLayerRegistry.instance().addMapLayer(self.layersPropLayer)
        self.iface.legendInterface().setLayerVisible(self.layersPropLayer, False)
        #dumNode = QgsProject.instance().layerTreeRoot().findLayer(layersPropLayer.id())
        #dumNode.parent().removeChildNode(dumNode)
        self.dlg.mFieldExpressionWidget.setLayer(self.layersPropLayer)
        self.dlg.layerTable.resizeColumnToContents(1)
        self.dlg.layerTable.horizontalHeader().setResizeMode(2,QHeaderView.ResizeToContents)
        self.dlg.layerTable.setColumnWidth(4,30)
        #print self.dlg.layerTable.minimumSizeHint().width(),self.dlg.layerTable.columnWidth(1),self.dlg.layerTable.columnWidth(2),self.dlg.layerTable.columnWidth(3),self.dlg.layerTable.columnWidth(4)
        self.dlg.layerTable.horizontalHeader().setResizeMode(3,QHeaderView.Stretch)

    def getButtonWidget(self,row):
        edit = QPushButton("...",parent = self.dlg.layerTable)
        edit.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
        edit.clicked.connect(lambda: self.browseDS(row))
        return edit

    def browseDS(self,row):
        newType,newProvider,newDatasource = dataSourceBrowser.uri()
        #check if databrowser return a incompatible layer type
        layerId = self.dlg.layerTable.cellWidget(row,0).text()
        rowLayer = QgsMapLayerRegistry.instance().mapLayer(layerId)
        enumLayerTypes = ("vector","raster","plugin")
        if enumLayerTypes[rowLayer.type()] != newType:
            self.iface.messageBar().pushMessage("Error", "Layer type mismatch %s/%s" % (enumLayerTypes[rowLayer.type()], newType), level=QgsMessageBar.CRITICAL, duration=4)
            return None
        if newDatasource:
            self.dlg.layerTable.cellWidget(row,3).setText(newDatasource)
        if newProvider:
            self.dlg.layerTable.cellWidget(row,2).setText(newProvider)

    def browseAction(self,row):
        print "BROWSE"
        cellType = self.dlg.layerTable.cellWidget(row,2)
        cellSource = self.dlg.layerTable.cellWidget(row,3)
        type,filename = self.dataBrowser.browse(cellType.text(),cellSource.text())
        #check if databrowse return a incompatible layer type
        layerId = self.dlg.layerTable.cellWidget(row,0).text()
        rowLayer = QgsMapLayerRegistry.instance().mapLayer(layerId)
        enumLayerTypes = ("vector","raster","plugin")
        #print enumLayerTypes[rowLayer.type()], type
        if enumLayerTypes[rowLayer.type()] != type:
            self.iface.messageBar().pushMessage("Error", "Layer type mismatch", level=QgsMessageBar.CRITICAL, duration=4)
            return None
        if type:
            if type != cellType.text():
                cellType.setText(type)
                self.highlightCell(cellType,"QLineEdit{background: yellow;}")
        if filename:
            if filename != cellSource.text():
                cellSource.setText(filename)
                self.highlightCell(cellSource,"QLineEdit{background: yellow;}")


    def getLabelWidget(self,txt,column, style = None):
        edit = QLineEdit(parent = self.dlg.layerTable)
        edit.setMinimumWidth(QApplication.instance().fontMetrics().width(txt))
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
        for row in indexes:
            layerId = self.dlg.layerTable.cellWidget(row,0)
            cell = self.dlg.layerTable.cellWidget(row,3)
            orig = cell.text()
            if self.dlg.mFieldExpressionWidget.isValidExpression():
                exp = QgsExpression(self.dlg.mFieldExpressionWidget.currentText())
                exp.prepare(self.layersPropLayer.pendingFields())
                cell.setText(exp.evaluate(self.layersPropLayer.getFeatures(QgsFeatureRequest(row+1)).next()))
            else:
                cell.setText(cell.text().replace(self.dlg.findEdit.text(),self.dlg.replaceEdit.text()))
            if self.dlg.datasourceCombo.currentText() != "":
                self.dlg.layerTable.cellWidget(row,2).setText(self.dlg.datasourceCombo.currentText())

    def applyDSChanges(self, reconcileUnhandled = False):

        for row in range(0,self.dlg.layerTable.rowCount()):
            rowProviderCell = self.dlg.layerTable.cellWidget(row,2)
            rowDatasourceCell = self.dlg.layerTable.cellWidget(row,3)
            rowLayerID = self.dlg.layerTable.cellWidget(row,0).text()
            rowLayerName = self.dlg.layerTable.cellWidget(row,1).text()
            rowProvider = rowProviderCell.text()
            rowDatasource = rowDatasourceCell.text()
            rowLayer = QgsMapLayerRegistry.instance().mapLayer(rowLayerID)
            layerIsUnhandled = self.badLayersHandler.getActualLayersIds() and rowLayer.id() in self.badLayersHandler.getActualLayersIds()
            if reconcileUnhandled and layerIsUnhandled:
                rowProviderChanging = True
                rowDatasourceChanging = True
            else:
                rowProviderChanging = rowProviderCell.changed
                rowDatasourceChanging = rowDatasourceCell.changed

            if rowProviderChanging or rowDatasourceChanging:
                if self.changeDSTool.applyDataSource(rowLayer,rowProvider,rowDatasource):
                    resultStyle = "QLineEdit{background: green;}"
                else:
                    resultStyle = "QLineEdit{background: red;}"
                if rowProviderChanging:
                    rowProviderCell.setStyleSheet(resultStyle)
                if rowDatasourceChanging:
                    rowDatasourceCell.setStyleSheet(resultStyle)



    def buttonBoxHub(self,button):
        QgsMapLayerRegistry.instance().removeMapLayer(self.layersPropLayer.id())
        if button.text() == "Reset":
            self.populateLayerTable()
        elif button.text() == "Apply":
            self.applyDSChanges()
        else:
            self.dlg.hide()

    def reconcileUnhandled(self):
        self.applyDSChanges(reconcileUnhandled = True)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
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

class browseLineEdit(QLineEdit):
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


class datasourceBrowser():
    def __init__(self):
        pass
    def browse(self,type,uri):
        if type == "ogr":
            exts = "All files (*.*);;ESRI shapefiles (*.shp);; Geojson (*.geojson);;Keyhole markup language (*.kml *.kmz)"
            return ("ogr",QFileDialog.getOpenFileName(None,"select OGR vector file", os.path.dirname(uri), exts))
        elif type == "gdal":
            exts = "All files (*.*);;JPG (*.jpg *.jpeg);; PNG (*.png);;TIFF (*.tif *.tiff)"
            return ("ogr",QFileDialog.getOpenFileName(None,"select GDAL raster file", os.path.dirname(uri), exts))


class myBadLayerHandler(QgsProjectBadLayerHandler):
    def __init__(self,parent):
        super(myBadLayerHandler, self).__init__()
        self.parent = parent
        self.badLayers = None
        self.unhandledLayers = None
        self.badProject = None
        self.badSession = None

    def removeUnhandledLayer(self,removeKey):
        if self.getUnhandledLayers() and removeKey in self.getUnhandledLayers():
            self.unhandledLayers.pop(removeKey,None)

    def getUnhandledLayers(self):
        if self.badSession == self.parent.session:
            return self.unhandledLayers
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
            for key,data in self.getUnhandledLayers().iteritems():
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
        id = self.getIdFromActualId(actualId)
        if id:
            return self.getUnhandledLayers()[id]
        else:
            None

    def handleBadLayers(self,layers,projectDom):
        self.badLayers = layers
        self.badSession = self.parent.session
        self.badProjectDom = projectDom
        self.unhandledLayers = {}
        self.originalOrder = []
        legendElements = projectDom.elementsByTagName("legendlayer")
        for legendItem in range(0,legendElements.count()):
            legendLayerId = legendElements.item(legendItem).firstChild().firstChild().attributes().namedItem("layerid").nodeValue()
            self.originalOrder.append(legendLayerId)
        self.badProject = QgsProject.instance().fileName ()
        unhandledMessage = "The following layers have not valid datasource:\n\n"
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
            self.unhandledLayers[id]= {"id":id,"layername":layername,"type":type,"geometry":geometry,"provider":provider,"datasource":datasource,"authid":authid,"legendgroup":legendgroup,"legendcount":legendcount,"layerDom":layer.cloneNode()}
            #print self.unhandledLayers[id]
        unhandledMessage += "\nThese layers are stored under unhandled layers group\nand can be restored assigning a valid datasource when available \nwith change datasouce legend contextual menu command\nor by changeDataSource plugin table\n"
        QMessageBox.warning(None,"changeDataSource plugin: Managing bad layers",unhandledMessage,QMessageBox.Ok)
        #self.parent.populateLayerTable()
        #self.parent.dlg.show()
        #self.parent.dlg.raise_()



