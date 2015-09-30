# -*- coding: utf-8 -*-
"""
/***************************************************************************
 changeDataSource
                                 A QGIS plugin
 right click on layer tree to change layer datasource
                             -------------------
        begin                : 2015-09-29
        copyright            : (C) 2015 by enrico ferreguti
        email                : enricofer@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load changeDataSource class from file changeDataSource.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .changeDataSource import changeDataSource
    return changeDataSource(iface)
