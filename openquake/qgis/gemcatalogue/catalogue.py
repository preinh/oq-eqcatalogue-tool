# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EqCatalogue
                                 A QGIS plugin
 earthquake catalogue tool
                              -------------------
        begin                : 2013-02-20
        copyright            : (C) 2013 by GEM Foundation
        email                : devops@openquake.org
 ***************************************************************************/

# Copyright (c) 2010-2013, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.
"""

import uuid
import os
import httplib
import tempfile
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py, used for side-effects
import resources_rc
# Import the code for the dialog
from openquake.qgis.gemcatalogue.dock import Dock
from openquake.qgis.gemcatalogue.importer_dialog import ImporterDialog
from openquake.qgis.gemcatalogue.download_exposure import \
    ExposureDownloader, ExposureDownloadError
from openquake.qgis.gemcatalogue.platform_settings \
    import PlatformSettingsDialog

from eqcatalogue import CatalogueDatabase, filtering
from eqcatalogue.importers import V1, Iaspei, store_events


FMT_MAP = {ImporterDialog.ISF_PATTERN: V1,
           ImporterDialog.IASPEI_PATTERN: Iaspei}


class EqCatalogue:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = QFileInfo(
            QgsApplication.qgisUserDbFilePath()
        ).path() + "/python/plugins/eqcatalogue"
        # initialize locale
        localePath = ""
        locale = str(QSettings().value("locale/userLocale"))[0:2]
        self.dockIsVisible = True

        if QFileInfo(self.plugin_dir).exists():
            localePath = (self.plugin_dir + "/i18n/eqcatalogue_" +
                          locale + ".qm")

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dock = Dock(self.iface, gemcatalogue=self)
        self.catalogue_db = None
        self.data_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'data'))

    def initGui(self):
        # Create action that will start plugin configuration
        self.show_catalogue_action = QAction(
            QIcon(":/plugins/eqcatalogue/icon.png"),
            u"Eqcatalogue Toggle Dock", self.iface.mainWindow())
        self.show_catalogue_action.setCheckable(True)
        self.show_catalogue_action.setChecked(self.dockIsVisible)

        self.import_action = QAction(
            QIcon(":/plugins/eqcatalogue/icon.png"),
            u"Import catalogue file in db", self.iface.mainWindow())

        self.get_platform_settings = QAction(
            QIcon(":/plugins/eqcatalogue/icon.png"),
            u"Settings for the GEM platform", self.iface.mainWindow())

        # connect the action to the run method
        QObject.connect(self.dock, SIGNAL("visibilityChanged(bool)"),
                        self.update_toggle_status)
        QObject.connect(self.show_catalogue_action, SIGNAL("triggered()"),
                        self.toggle_dock)
        self.import_action.triggered.connect(self.show_import_dialog)
        self.get_platform_settings.triggered.connect(self.platform_settings)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.show_catalogue_action)
        self.iface.addPluginToMenu(u"&eqcatalogue", self.show_catalogue_action)
        self.iface.addPluginToMenu(u"&eqcatalogue", self.import_action)
        self.iface.addPluginToMenu(u"&eqcatalogue", self.get_platform_settings)

        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)

        # display world map
        QObject.connect(self.iface, SIGNAL('initializationCompleted()'),
                        self.load_countries)

    def unload(self):
        # Remove the plugin menu item and icon
        self.dock.close()
        self.iface.removeToolBarIcon(self.show_catalogue_action)
        self.iface.removePluginMenu(
            u"&eqcatalogue", self.show_catalogue_action)
        self.iface.removePluginMenu(u"&eqcatalogue", self.import_action)
        self.iface.removePluginMenu(
            u"&eqcatalogue", self.get_platform_settings)

    def toggle_dock(self):
        # show the dock
        self.dockIsVisible = not self.dockIsVisible
        self.dock.setVisible(self.dockIsVisible)

    def update_toggle_status(self, status):
        self.dockIsVisible = status
        self.show_catalogue_action.setChecked(status)

    def update_catalogue_db(self, db_filename):
        self.catalogue_db = CatalogueDatabase(filename=db_filename)
        agencies = list(self.catalogue_db.get_agencies())
        mscales = list(self.catalogue_db.get_measure_scales())
        dates = self.catalogue_db.get_dates()
        self.dock.set_agencies(agencies)
        self.dock.set_magnitude_scales(mscales)
        self.dock.set_dates(dates)

    def create_db(self, catalogue_filename, fmt, db_filename):
        cat_db = CatalogueDatabase(filename=db_filename)
        parser = FMT_MAP[fmt]
        self.dock.enableBusyCursor()
        try:
            with open(catalogue_filename, 'rb') as cat_file:
                store_events(parser, cat_file, cat_db)
            self.dock.update_selectDbComboBox(db_filename)
        finally:
            self.dock.disableBusyCursor()
        return cat_db

    def show_import_dialog(self):
        self.import_dialog = ImporterDialog(self.iface)
        if self.import_dialog.exec_():
            self.create_db(self.import_dialog.import_file_path,
                           str(self.import_dialog.fmt),
                           self.import_dialog.save_file_path)

    def platform_settings(self):
        dialog = PlatformSettingsDialog(self.iface)
        dialog.exec_()

    def show_exposure(self, hostname, username, password):
        self.dock.enableBusyCursor()
        try:
            crs = self.iface.mapCanvas().mapRenderer().destinationCrs()
            xform = QgsCoordinateTransform(
                crs, QgsCoordinateReferenceSystem(4326))
            extent = xform.transform(self.dock.selectedExtent())
            lon_min, lon_max = extent.xMinimum(), extent.xMaximum()
            lat_min, lat_max = extent.yMinimum(), extent.yMaximum()

            # download data
            ed = ExposureDownloader(hostname)
            ed.login(username, password)
            try:
                fname = ed.download(lat_min, lon_min, lat_max, lon_max)
            except ExposureDownloadError as e:
                self.dock.disableBusyCursor()
                QMessageBox.warning(
                    self.dock, 'Exposure Download Error', str(e))
                return
            # don't remove the file, otherwise there will concurrency problems
            uri = 'file://%s?delimiter=%s&xField=%s&yField=%s&crs=epsg:4326&' \
                'skipLines=25&trimFields=yes' % (fname, ',', 'lon', 'lat')
            vlayer = QgsVectorLayer(uri, 'exposure_export', 'delimitedtext')
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        finally:
            self.dock.disableBusyCursor()

    def update_map(self, agencies_selected, mscales_selected, mag_range,
                   date_range, selected_extent):
        filter_agency = filtering.WithAgencies(
            [str(x) for x in agencies_selected])
        filter_mscales = filtering.WithMagnitudeScales(
            [str(x) for x in mscales_selected])
        filter_mvalues = filtering.C(magnitude__gt=mag_range.low_value,
                                     magnitude__lt=mag_range.high_value)
        filter_dvalues = filtering.C(time__between=date_range)

        results = filter_agency & filter_mscales & filter_mvalues\
            & filter_dvalues

        if selected_extent is not None:
            filter_pvalues = filtering.WithinPolygon(
                selected_extent.asWktPolygon())
            results = results & filter_pvalues

        self.create_layer(results)

    def create_layer(self, data):
        dock = self.dock
        date_range = ':'.join([
            str(dock.timeRangeWidget.get_from_pydatetime().year),
            str(dock.timeRangeWidget.get_to_pydatetime().year)
        ])
        mag_range = ':'.join([str(dock.mag_range.lowValue()),
                              str(dock.mag_range.highValue())])
        agencies = ','.join(map(str, dock.agenciesWidget.get_selected_items()))
        mscales = ','.join(map(str, dock.magnitudesWidget.get_selected_items()))

        display_name = 'Events-%s-%s-%s-%s' % (
            date_range, mag_range, mscales, agencies)

        uri = 'Point?crs=epsg:4326&index=yes&uuid=%s' % uuid.uuid4()
        vlayer = QgsVectorLayer(uri, display_name, 'memory')
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)

        provider = vlayer.dataProvider()
        vlayer.startEditing()
        provider.addAttributes([
            QgsField('agency', QVariant.String),
            QgsField('event_name', QVariant.String),
            QgsField('event_measure', QVariant.String),
        ])
        features = []
        for i, row in enumerate(data):
            x, y = row.position_as_tuple()
            feat = QgsFeature()
            geom = QgsGeometry.fromPoint(QgsPoint(x, y))
            feat.setGeometry(geom)
            feat.setAttributes([str(row.agency),
                                row.event_name,
                                str(row)])
            features.append(feat)
        provider.addFeatures(features)
        vlayer.commitChanges()
        vlayer.updateExtents()
        self.iface.mapCanvas().setExtent(vlayer.extent())
        vlayer.triggerRepaint()

    def load_countries(self):
        display_name = 'Population density'
        uri = os.path.join(self.data_dir, 'Countries.shp')
        vlayer = QgsVectorLayer(uri, display_name, 'ogr')
        QgsMapLayerRegistry.instance().addMapLayers([vlayer])
