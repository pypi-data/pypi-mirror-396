#!/usr/bin/env python3

from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QPushButton, QGridLayout, QLabel, QHBoxLayout, QVBoxLayout, \
    QDoubleSpinBox,  QDialog, QComboBox, QFileDialog, QMessageBox, QSizePolicy, QAbstractItemView, QTableWidgetSelectionRange, QLineEdit, QCheckBox, QTextEdit
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import pandas as pd
import time
from pyrotoolbox.parsers import parse
import os
import pyqtgraph as pg
import numpy as np
import datetime as dt


pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOption('useOpenGL', False)
pg.setConfigOption('antialias', False)


class FireResponse(QMainWindow):
    def __init__(self):
        super().__init__()
        self.new_range_start_point = None
        self.new_range_region = None
        self.df = None
        self.meta = None
        self.path = None
        self.fname = None

        self.active_response = None
        self.responses = []
        self.initUI()

    def initUI(self):
        w = QWidget(self)
        self.setCentralWidget(w)
        main_grid = QGridLayout(w)
        menu_hbox = QHBoxLayout()
        settings_hbox = QHBoxLayout()
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()
        main_grid.addLayout(menu_hbox, 0, 0, 1, 2)
        main_grid.addLayout(settings_hbox, 1, 0, 1, 2)
        main_grid.addLayout(left_col, 2, 0)
        main_grid.addLayout(right_col, 2, 1)

        ################################################################################################################
        # Menu
        ################################################################################################################
        open_btn = QPushButton('open pyroscience file')
        open_csv_btn = QPushButton('open csv file')
        self.trace_combo = QComboBox()
        self.trace_combo.setMinimumWidth(150)
        self.trace_combo.currentTextChanged.connect(self.on_trace_selected)
        selfclr_responses_btn = QPushButton('clear')
        selfclr_responses_btn.clicked.connect(self.clear)
        save_btn = QPushButton('save')
        save_btn.clicked.connect(self.save)
        load_btn = QPushButton('load')
        load_btn.clicked.connect(self.load)
        self.report_btn = QPushButton('create report')
        self.report_btn.clicked.connect(self.create_report)
        self.report_btn.setEnabled(False)
        menu_hbox.addWidget(open_btn)
        menu_hbox.addWidget(open_csv_btn)
        menu_hbox.addWidget(self.trace_combo)
        menu_hbox.addWidget(selfclr_responses_btn)
        menu_hbox.addStretch(1)
        menu_hbox.addWidget(self.report_btn)
        menu_hbox.addWidget(save_btn)
        menu_hbox.addWidget(load_btn)

        open_btn.clicked.connect(self.trigger_select_pyroscience_file)
        open_csv_btn.clicked.connect(self.trigger_select_csv_file)

        ################################################################################################################
        # Settings
        ################################################################################################################

        self.threshold_sb = QDoubleSpinBox()
        self.threshold_sb.setRange(0, 10)
        self.threshold_sb.setSingleStep(0.5)
        self.threshold_sb.setSuffix(' %')
        self.threshold_sb.setValue(2)
        self.threshold_sb.setDecimals(1)

        self.force_start_edit = QLineEdit()
        self.force_end_edit = QLineEdit()

        settings_hbox.addWidget(QLabel('Onset Threshold: '))
        settings_hbox.addWidget(self.threshold_sb)
        settings_hbox.addWidget(QLabel('Force start value: '))
        settings_hbox.addWidget(self.force_start_edit)
        settings_hbox.addWidget(QLabel('Force end value: '))
        settings_hbox.addWidget(self.force_end_edit)
        settings_hbox.addStretch(1)


        ################################################################################################################
        # Left Overview Column
        ################################################################################################################
        self.overview_plot = pg.PlotWidget(axisItems={'bottom': DateAxis(orientation='bottom')})
        self.overview_plot.scene().sigMouseClicked.connect(self.onClick)
        self.overview_plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.overview_plot.setEnabled(False)

        hbox = QHBoxLayout()
        self.clr_responses_btn = QPushButton('Clear')
        self.clr_responses_btn.clicked.connect(self.clear_responses)
        self.export_response_btn = QPushButton('Export')
        self.export_response_btn.clicked.connect(self.export_response_table)
        hbox.addWidget(self.clr_responses_btn)
        hbox.addWidget(self.export_response_btn)

        self.table = pg.TableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.itemSelectionChanged.connect(self.table_selection_changed)

        left_col.addWidget(self.overview_plot)
        left_col.addLayout(hbox)
        left_col.addWidget(self.table)

        ################################################################################################################
        # Right Single Response Column
        ################################################################################################################
        self.response_plot = pg.PlotWidget()
        self.response_plot.addLegend(labelTextSize='12pt')
        self.response_plot.plotItem.legend.anchor(itemPos=(1, 0.5), parentPos=(1,0.5), offset=(-10,0))
        self.response_plot.plotItem.setLabel('bottom', 'time [s]')
        self.response_plot.plotItem.setLabel('left', 'Signal')
        t_grid = QGridLayout()
        w = QLabel('Threshold:', alignment=Qt.AlignRight)
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        t_grid.addWidget(w, 0, 0)

        w = QLabel('Start Value:', alignment=Qt.AlignRight)
        w.setStyleSheet("QLabel { color: red; }")
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        t_grid.addWidget(w, 1, 0)

        w = QLabel('Force Start Value:', alignment=Qt.AlignRight)
        w.setStyleSheet("QLabel { color: red; }")
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        t_grid.addWidget(w, 2, 0)

        w = QLabel('End Value:', alignment=Qt.AlignRight)
        w.setStyleSheet("QLabel { color: red; }")
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        t_grid.addWidget(w, 3, 0)

        w = QLabel('Force End Value:', alignment=Qt.AlignRight)
        w.setStyleSheet("QLabel { color: red; }")
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        t_grid.addWidget(w, 4, 0)

        w = QLabel('t63:', alignment=Qt.AlignRight)
        w.setStyleSheet("QLabel { color: blue; }")
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        t_grid.addWidget(w, 5, 0)

        w = QLabel('t90:', alignment=Qt.AlignRight)
        w.setStyleSheet("QLabel { color: cyan; }")
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        t_grid.addWidget(w, 6, 0)

        w = QLabel('t95:', alignment=Qt.AlignRight)
        w.setStyleSheet("QLabel { color: magenta; }")
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        t_grid.addWidget(w, 7, 0)

        w = QLabel('t99:', alignment=Qt.AlignRight)
        w.setStyleSheet("QLabel { color: green; }")
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        t_grid.addWidget(w, 8, 0)

        self.response_view_threshold_edit = QDoubleSpinBox()
        self.response_view_threshold_edit.setRange(0, 10)
        self.response_view_threshold_edit.setSuffix(' %')
        self.response_view_threshold_edit.setDecimals(1)
        self.response_view_threshold_edit.setSingleStep(0.5)
        self.response_view_threshold_edit.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.response_view_threshold_edit.valueChanged.connect(self.change_threshold_for_active_response)
        self.start_value_label = QLabel('')
        self.start_value_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.response_view_force_start_edit = QLineEdit()
        self.response_view_force_start_edit.editingFinished.connect(self.change_force_start_value_for_active_response)
        self.end_value_label = QLabel('')
        self.end_value_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.response_view_force_end_edit = QLineEdit()
        self.response_view_force_end_edit.editingFinished.connect(self.change_force_end_value_for_active_response)
        self.t63_label = QLabel('')
        self.t63_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.t90_label = QLabel('')
        self.t90_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.t95_label = QLabel('')
        self.t95_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.t99_label = QLabel('')
        self.t99_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        t_grid.addWidget(self.response_view_threshold_edit, 0, 1)
        t_grid.addWidget(self.start_value_label, 1, 1)
        t_grid.addWidget(self.response_view_force_start_edit, 2, 1)
        t_grid.addWidget(self.end_value_label, 3, 1)
        t_grid.addWidget(self.response_view_force_end_edit, 4, 1)
        t_grid.addWidget(self.t63_label, 5, 1)
        t_grid.addWidget(self.t90_label, 6, 1)
        t_grid.addWidget(self.t95_label, 7, 1)
        t_grid.addWidget(self.t99_label, 8, 1)

        right_col.addWidget(self.response_plot)
        right_col.addLayout(t_grid)

    def trigger_select_pyroscience_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Select Channel-File', self.path, filter='Text files (*.txt)')[0]
        self.load_pyro_file(fname)

    def trigger_select_csv_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Select csv file', self.path,
                                            filter='Text files (*.txt *.csv);;All Files (*)')[0]
        self.load_csv_file(fname)

    def load_pyro_file(self, fname=None):
        if not fname:
            return
        self.clear()
        try:
            df, meta = parse(fname)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error while loading file: {fname}:\n{e}', QMessageBox.Ok)
            return
        self.df = df
        meta['file_type'] = 'workbench'
        self.meta = meta
        self.path, self.fname = os.path.split(fname)
        self.trace_combo.currentTextChanged.disconnect()
        for c in df.columns:
            if c in ('time_s', 'ambient_light', 'status', 'pressure'):
                continue
            self.trace_combo.addItem(c)
        self.trace_combo.setCurrentIndex(-1)
        self.trace_combo.currentTextChanged.connect(self.on_trace_selected)
        self.trace_combo.showPopup()

    def load_csv_file(self, fname=None):
        if not fname:
            return
        self.clear()
        try:
            df = pd.read_csv(fname, index_col=0, parse_dates=True)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error while loading file: {fname}: {e}', QMessageBox.Ok)
        self.df = df
        self.meta = {'file_type': 'csv'}
        self.path, self.fname = os.path.split(fname)
        self.trace_combo.currentTextChanged.disconnect()
        for c in df.columns:
            if c in (' dt (s)', 'Ambient Light (mV)', 'Status', 'Date', 'Time', 'Pressure (mbar)'):
                continue
            self.trace_combo.addItem(c)
        self.trace_combo.setCurrentIndex(-1)
        self.trace_combo.currentTextChanged.connect(self.on_trace_selected)

    def on_trace_selected(self, trace: str):
        if self.df is None:
            return
        self.trace_combo.setEnabled(False)
        self.overview_plot.plotItem.plot(self.df.index.astype(np.int64)/1e9, self.df[trace], pen=pg.mkPen(width=3))
        self.overview_plot.setEnabled(True)
        self.overview_plot.autoRange()

    def clear_responses(self):
        ret = QMessageBox.question(self, "Do you want to delete all marked responses?", "Continue and delete all responses?", QMessageBox.Ok | QMessageBox.Cancel)
        if ret == QMessageBox.Cancel:
            return
        for resp in self.responses[:]:
            self.delete_response(resp)

    def export_response_table(self, checked=False, fname=None):
        if fname is None:
            fname = QFileDialog.getSaveFileName(self, "Choose a filename", self.path)[0]
        if not fname:
            return
        if not fname.endswith('.csv') and not fname.endswith('.txt'):
            fname += '.csv'
        self.get_response_df().to_csv(fname)

    def onClick(self, event):
        if event.buttons() == Qt.RightButton:
            # check if aborting a range
            if self.new_range_start_point:
                self.new_range_start_point = None
                self.overview_plot.removeItem(self.tmp_region)
                self.tmp_region = None
                self.overview_plot.scene().sigMouseMoved.disconnect()
        elif event.buttons() == Qt.LeftButton:
            if not self.new_range_start_point:  # start a new range
                # check if a range is to be selected
                for i in self.overview_plot.scene().itemsNearEvent(event):
                    if isinstance(i, pg.LinearRegionItem):
                        for resp in self.responses:
                            if i == resp.region_item:
                                self.set_active_response(resp)
                        return
                mousePoint = self.overview_plot.plotItem.vb.mapSceneToView(event._scenePos)
                self.new_range_start_point = mousePoint.x()
                self.tmp_region = pg.LinearRegionItem((self.new_range_start_point, self.new_range_start_point))
                self.overview_plot.addItem(self.tmp_region)
                self.overview_plot.scene().sigMouseMoved.connect(self.on_mouse_moved)
            else:  # finalize a range
                self.add_new_response(self.tmp_region.getRegion())
                self.new_range_start_point = None
                if self.tmp_region:
                    self.overview_plot.removeItem(self.tmp_region)
                    self.tmp_region = None
                    self.overview_plot.scene().sigMouseMoved.disconnect()
        event.accept()

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Delete:
            if self.active_response:
                self.delete_response(self.active_response)
        elif a0.key() == Qt.Key_Escape:
            if self.active_response:
                self.set_active_response(None)

    def on_mouse_moved(self, point):
        mousePoint = self.overview_plot.plotItem.vb.mapSceneToView(point)
        self.tmp_region.setRegion((self.new_range_start_point, mousePoint.x()))

    def add_new_response(self, rng, threshold=None, force_start=None, force_end=None, force_onset=None):
        start, end = rng
        region_item = pg.LinearRegionItem((start, end))
        region_item.setMovable(False)
        self.overview_plot.addItem(region_item)
        if force_start is None:
            try:
                force_start = float(self.force_start_edit.text())
            except:
                force_start = None
        if force_end is None:
            try:
                force_end = float(self.force_end_edit.text())
            except:
                force_end = None
        if threshold is None:
            threshold = self.threshold_sb.value()
        resp = Response(start, end, threshold, self.df, self.trace_combo.currentText(),
                        region_item=region_item, force_start_value=force_start, force_end_value=force_end,
                        force_onset_ts=force_onset)
        self.responses.append(resp)
        self.on_responses_changed()
        self.set_active_response(resp)

    def set_active_response(self, response):
        if self.active_response:  # de-activate last response if there was one
            self.active_response.changed.disconnect()
            self.active_response.region_item.setBrush(pg.mkBrush((0, 0, 255, 50)))
            self.active_response.region_item.setMovable(False)
            self.active_response.region_item.update()
            self.active_response = None
            self.clear_response_view()
            self.table.itemSelectionChanged.disconnect()
            self.table.setRangeSelected(QTableWidgetSelectionRange(0, 0, self.table.rowCount()-1, self.table.columnCount()-1), False)
            self.table.itemSelectionChanged.connect(self.table_selection_changed)

        self.active_response = response
        if self.active_response:
            self.active_response.changed.connect(self.update_response_view)
            self.active_response.changed.connect(self.on_responses_changed)
            self.active_response.region_item.setBrush(pg.mkBrush((255, 8, 0, 50)))
            self.active_response.region_item.setMovable(True)
            self.active_response.region_item.update()
            self.update_response_view(response)

            self.table.itemSelectionChanged.disconnect()
            self.table.setRangeSelected(QTableWidgetSelectionRange(self.responses.index(response), 0, self.responses.index(response), self.table.columnCount()-1), True)
            self.table.itemSelectionChanged.connect(self.table_selection_changed)

    def change_threshold_for_active_response(self, value: float):
        if not self.active_response:
            return
        self.active_response.set_threshold(value)

    def change_force_start_value_for_active_response(self):
        if not self.active_response:
            return
        try:
            val = float(self.response_view_force_start_edit.text())
        except:
            val = None
        self.active_response.set_force_start(val)

    def change_force_end_value_for_active_response(self):
        if not self.active_response:
            return
        try:
            val = float(self.response_view_force_end_edit.text())
        except:
            val = None
        self.active_response.set_force_end(val)

    def update_response_view(self, response):
        self.plot_response(response, self.response_plot)
        self.response_view_threshold_edit.setValue(response.threshold)
        self.start_value_label.setText('{:.2f}'.format(response.from_value))
        self.end_value_label.setText('{:.2f}'.format(response.to_value))

    @staticmethod
    def plot_response(response, plot_widget: pg.PlotWidget):
        plot_widget.clear()
        plot_widget.plotItem.legend.clear()
        if response.cut_data.empty or response.onset_ts != response.onset_ts:  # check if onset_ts is not NaN
            return
        d = response.cut_data.copy()
        d.index = (d.index - response.onset_ts).total_seconds()
        plot_widget.plot(np.array(d.index), np.array(d), pen=pg.mkPen(width=3))
        onset_inf_line = pg.InfiniteLine(0, pen=pg.mkPen(width=3, color='k'), movable=True)
        onset_inf_line.sigPositionChangeFinished.connect(response.on_onset_line_moved)
        plot_widget.addItem(onset_inf_line)
        plot_widget.addItem(pg.InfiniteLine(response.t63, pen=pg.mkPen(width=3, color='b'), name='t63 = {:.2f}'.format(response.t63)))
        plot_widget.addItem(pg.InfiniteLine(response.t90, pen=pg.mkPen(width=3, color='c'), name='t90 = {:.2f}'.format(response.t90)))
        plot_widget.addItem(pg.InfiniteLine(response.t95, pen=pg.mkPen(width=3, color='m'), name='t95 = {:.2f}'.format(response.t95)))
        plot_widget.addItem(pg.InfiniteLine(response.t99, pen=pg.mkPen(width=3, color='g'), name='t99 = {:.2f}'.format(response.t99)))
        plot_widget.addItem(pg.InfiniteLine(response.from_value, 0, pen=pg.mkPen(width=3, color='r')))
        plot_widget.addItem(pg.InfiniteLine(response.to_value, 0, pen=pg.mkPen(width=3, color='r')))
        plot_widget.plotItem.legend.addItem(pg.PlotDataItem(pen=pg.mkPen(width=3, color='b')), name='t63 = {:.2f} s'.format(response.t63))
        plot_widget.plotItem.legend.addItem(pg.PlotDataItem(pen=pg.mkPen(width=3, color='c')), name='t90 = {:.2f} s'.format(response.t90))
        plot_widget.plotItem.legend.addItem(pg.PlotDataItem(pen=pg.mkPen(width=3, color='m')), name='t95 = {:.2f} s'.format(response.t95))
        plot_widget.plotItem.legend.addItem(pg.PlotDataItem(pen=pg.mkPen(width=3, color='g')), name='t99 = {:.2f} s'.format(response.t99))

    @staticmethod
    def plot_response_to_file(response, fname):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        if response.cut_data.empty or response.onset_ts != response.onset_ts:  # check if onset_ts is not NaN
            return
        d = response.cut_data.copy()
        d.index = (d.index - response.onset_ts).total_seconds()
        ax.plot(d.index, d.array)
        ax.axvline(0, color='k', linewidth=0.5)
        ax.axvline(response.t63, label='t$_{{63}}$ = {:.2f}'.format(response.t63), color='r')
        ax.axvline(response.t90, label='t$_{{90}}$ = {:.2f}'.format(response.t90), color='g')
        ax.axvline(response.t95, label='t$_{{95}}$ = {:.2f}'.format(response.t95), color='c')
        ax.axvline(response.t99, label='t$_{{99}}$ = {:.2f}'.format(response.t99), color='m')
        ax.axhline(response.from_value, color='k')
        ax.axhline(response.to_value, color='k')
        ax.set_xlabel('time [s]')
        ax.set_ylabel(response.trace)
        ax.legend()
        fig.tight_layout()
        fig.savefig(fname, format='png')


    def delete_response(self, response):
        self.responses.remove(response)
        self.overview_plot.removeItem(response.region_item)
        if response == self.active_response:
            self.set_active_response(None)
        self.on_responses_changed()

    def on_responses_changed(self):
        # sort responses by start time
        self.responses.sort(key=lambda x: x.start)
        self.table.clear()
        df = self.get_response_df()
        if not df.empty:
            self.table.setData(df.to_numpy())
            self.table.setHorizontalHeaderLabels(df.columns)
            self.clr_responses_btn.setEnabled(bool(self.responses))
            self.export_response_btn.setEnabled(bool(self.responses))
            self.report_btn.setEnabled(bool(self.responses))

    def table_selection_changed(self):
        ranges = self.table.selectedRanges()
        if ranges:
            self.set_active_response(self.responses[ranges[0].topRow()])

    def get_response_df(self) -> pd.DataFrame:
        df = pd.DataFrame(index=range(len(self.responses)))
        df['start'] = [dt.datetime.utcfromtimestamp(i.start).strftime('%Y-%m-%d %H:%M:%S') for i in self.responses]
        df['end'] = [dt.datetime.utcfromtimestamp(i.end).strftime('%Y-%m-%d %H:%M:%S') for i in self.responses]
        df['threshold [%]'] = [i.threshold for i in self.responses]
        df['Start Value'] = [i.from_value for i in self.responses]
        df['End Value'] = [i.to_value for i in self.responses]
        df['t63 [s]'] = [i.t63 for i in self.responses]
        df['t90 [s]'] = [i.t90 for i in self.responses]
        df['t95 [s]'] = [i.t95 for i in self.responses]
        df['t99 [s]'] = [i.t99 for i in self.responses]
        df['T [°C]'] = [i.temperature for i in self.responses]
        return df

    def clear(self):
        """ Clear everything """
        self.df = None
        self.meta = None
        self.path = None
        self.fname = None
        self.new_range_start_point = None
        self.new_range_region = None
        self.responses = []
        self.active_response = None

        self.overview_plot.clear()
        self.table.clear()
        self.clear_response_view()

        self.trace_combo.clear()
        self.trace_combo.setEnabled(True)
        self.overview_plot.setEnabled(False)

        self.threshold_sb.setValue(2)
        self.force_start_edit.setText('')
        self.force_end_edit.setText('')

    def clear_response_view(self):
        self.response_plot.clear()
        self.response_view_threshold_edit.setValue(0)
        self.start_value_label.setText('')
        self.end_value_label.setText('')
        self.t63_label.setText('')
        self.t90_label.setText('')
        self.t95_label.setText('')
        self.t99_label.setText('')

    def save(self):
        # create directory in same directory
        name = os.path.join(self.path, self.fname + ' - Responses')
        i = 1
        while os.path.exists(name):
            name = os.path.join(self.path, self.fname + ' - Responses{}'.format(i))
            i += 1
        os.mkdir(name)
        settings = {'fname': os.path.join('..', os.path.split(self.fname)[1]),
                    'trace': self.trace_combo.currentText(),
                    'responses': []}
        for resp in self.responses:
            settings['responses'].append([resp.start, resp.end, resp.force_start_value, resp.force_end_value,
                                          resp.force_onset_ts, resp.threshold])
            settings['file_type'] = self.meta['file_type']
        import json
        with open(os.path.join(name, 'settings.json'), 'w') as f:
            json.dump(settings, f)
        self.export_response_table(fname=os.path.join(name, 'responses.csv'))

        for i, resp in enumerate(self.responses):
            self.plot_response_to_file(resp, os.path.join(name, f'response{i:0>3}.png'))

    def load(self):
        settings_path = QFileDialog.getOpenFileName(self, 'Select a settings file',
                                                    filter='Settings-File (settings.json)')[0]
        if not settings_path:
            return
        import json
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        if settings['file_type'] == 'workbench':
            self.load_workbench_file(os.path.join(os.path.split(settings_path)[0], settings['fname']))
        elif settings['file_type'] == 'developer_tool':
            self.load_devtool_file(os.path.join(os.path.split(settings_path)[0], settings['fname']))
        elif settings['file_type'] == 'csv':
            self.load_csv_file(os.path.join(os.path.split(settings_path)[0], settings['fname']))
        elif settings['file_type'] == 'fireplate':
            self.load_fireplate_file(os.path.join(os.path.split(settings_path)[0], settings['fname']))
        else:
            QMessageBox.warning(self, 'Error', 'Unknown file type', QMessageBox.Ok)
            return
        self.trace_combo.setCurrentText(settings['trace'])
        for start, end, force_start, force_end, force_onset, threshold in settings['responses']:
            self.add_new_response((start, end), threshold, force_start, force_end, force_onset)

    def create_report(self):
        self.resp_report_dialog = ResponseReportDialog(self.df, self.meta, self.get_response_df(), self.responses,
                                                       self.path)
        self.resp_report_dialog.exec_()
        # use reportlab
        # open dialog window with inputs
        # additional metadata: operator, date measured, date evaluated, device-id, channel, mean temperature,
        #


class ResponseReportDialog(QDialog):
    def __init__(self, data, meta, response_table, responses, default_path=None, parent=None):
        super().__init__(parent=parent)
        self.data = data
        self.default_path = default_path
        self.meta = meta
        self.response_table = response_table
        self.responses = responses
        self.initUI()

    def initUI(self):
        grid = QGridLayout(self)
        self.sensor_name_edit = QLineEdit()
        self.sensor_type_combo = QComboBox()
        self.sensor_type_combo.addItems(['OXSP5', 'AquaOx', 'AquaOx-HS', 'PK5', 'PK6', 'PK65', 'PK7', 'PK8'])
        self.sensor_type_combo.setEditable(True)
        self.sensor_type_combo.setCurrentIndex(-1)
        self.sensor_format_combo = QComboBox()
        self.sensor_format_combo.addItems(['5mm Spot', 'SC', 'CAP', 'FLOW'])
        self.sensor_format_combo.setEditable(True)
        self.sensor_format_combo.setCurrentIndex(-1)
        self.experiment_name = QLineEdit()
        self.experiment_name.setText(self.meta.get('experiment_name', 'no name'))
        self.experiment_description = QTextEdit()
        self.experiment_description.setText(self.meta.get('experiment_description', 'no description'))
        self.operator_edit = QLineEdit()
        self.date_measured_edit = QLineEdit()
        self.date_measured_edit.setText(self.data.index[0].strftime('%Y-%m-%d'))
        self.date_evaluated_edit = QLineEdit()
        self.date_evaluated_edit.setText(dt.datetime.now().strftime('%Y-%m-%d'))
        self.device_id_edit = QLineEdit()
        self.device_id_edit.setText(self.meta.get('device_serial', 'unknown serial'))
        self.channel_edit = QLineEdit()
        self.channel_edit.setText(str(self.meta.get('Channel', 'unknown channel')))
        self.sampling_interval_edit = QLineEdit()
        self.sampling_interval_edit.setText('{:.1f} s'.format((self.data.index[-1] - self.data.index[0]).total_seconds()/len(self.data)))
        self.add_plots_cb = QCheckBox('add plots')
        self.add_plots_cb.setChecked(True)

        create_btn = QPushButton('Create Report')
        create_btn.clicked.connect(self.create_report)

        grid.addWidget(QLabel('Sensor Name:'), 0, 0)
        grid.addWidget(self.sensor_name_edit, 0, 1)
        grid.addWidget(QLabel('Sensor Typ:'), 1, 0)
        grid.addWidget(self.sensor_type_combo, 1, 1)
        grid.addWidget(QLabel('Sensor Format:'), 2, 0)
        grid.addWidget(self.sensor_format_combo, 2, 1)
        grid.addWidget(QLabel('Experiment Name:'), 3, 0)
        grid.addWidget(self.experiment_name, 3, 1)
        grid.addWidget(QLabel('Experiment Beschreibung:'), 4, 0)
        grid.addWidget(self.experiment_description, 4, 1)
        grid.addWidget(QLabel('Operator: '), 5, 0)
        grid.addWidget(self.operator_edit, 5, 1)
        grid.addWidget(QLabel('Gemessen am:'), 6, 0)
        grid.addWidget(self.date_measured_edit, 6, 1)
        grid.addWidget(QLabel('Ausgewertet am:'), 7, 0)
        grid.addWidget(self.date_evaluated_edit, 7, 1)
        grid.addWidget(QLabel('Device-id:'), 8, 0)
        grid.addWidget(self.device_id_edit, 8, 1)
        grid.addWidget(QLabel('Channel:'), 9, 0)
        grid.addWidget(self.channel_edit, 9, 1)
        grid.addWidget(QLabel('Sampling Interval:'), 10, 0)
        grid.addWidget(self.sampling_interval_edit, 10, 1)
        grid.addWidget(self.add_plots_cb, 11, 0, 1, 2)
        grid.addWidget(create_btn, 12, 0, 1, 2)

    def create_report(self):
        fname = QFileDialog.getSaveFileName(self, "Choose a filename for the report", self.default_path)[0]
        if not fname:
            return
        if not fname.endswith('.pdf'):
            fname += '.pdf'

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.pdfgen import canvas
        from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak, Table, ListItem, TableStyle, Image
        import reportlab.lib.colors as colors

        # Definieren der Styles
        style = getSampleStyleSheet()

        def dataframe_to_table(df):
            l = []
            l.append([''] + list(df.columns))
            for i, row in df.iterrows():
                l.append([str(i)] + list(row))
            return Table(l, repeatRows=1)

        class FooterCanvas(canvas.Canvas):

            def __init__(self, *args, **kwargs):
                canvas.Canvas.__init__(self, *args, **kwargs)
                self.pages = []

            def showPage(self):
                self.pages.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                page_count = len(self.pages)
                for page in self.pages:
                    self.__dict__.update(page)
                    self.draw_canvas(page_count)
                    canvas.Canvas.showPage(self)
                canvas.Canvas.save(self)

            def draw_canvas(self, page_count):
                page = "Page %s of %s" % (self._pageNumber, page_count)
                #name = "{}".format(df['Standard'][0])
                x = 128
                self.saveState()
                self.setStrokeColorRGB(0, 0, 0)
                self.setLineWidth(0.5)
                self.line(66, 78, A4[0] - 66, 78)
                self.setFont('Helvetica', 10)
                #self.drawString(80, 65, name)
                self.drawString(A4[0] - x, 65, page)
                self.restoreState()

        # Anlegen einer Liste, welche den Seiteninhalt enthält
        story = []
        # Generieren von Inhalt
        story.append(Paragraph('Response Time Messung', style['Title']))
        #story.append(Paragraph('Ergebnisse', style['Heading3']))

        table = Table([['Sensor:', self.sensor_name_edit.text()],
                       ['Typ:', self.sensor_type_combo.currentText()],
                       ['Format:', self.sensor_format_combo.currentText()],
                       ['Experiment:', self.experiment_name.text()],
                       ['Beschreibung:', self.experiment_description.toPlainText().strip()],
                       ['Durchgeführt am:', self.date_measured_edit.text()],
                       ['Ausgewertet am:', self.date_evaluated_edit.text()],
                       ['Gerät:', '{} Ch. {}'.format(self.device_id_edit.text(), self.channel_edit.text()) ],
                       ['Messinterval:', self.sampling_interval_edit.text()],
                       ])
        table.hAlign = 'LEFT'
        story.append(table)

        story.append(Paragraph('Ergebnisse', style['Heading3']))
        t = self.response_table.copy().iloc[:, 3:]
        if len(t) > 1:
            t.loc['mean'] = t.mean()
        table = dataframe_to_table(t.round(3))
        table.hAlign = 'LEFT'
        table.setStyle(TableStyle([('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.black)]))
        table.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, 0), 1, colors.black)]))
        if len(t) > 1:
            table.setStyle(TableStyle([('LINEABOVE', (0, -1), (-1, -1), 1, colors.black)]))
        table.setStyle(TableStyle([('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.black)]))
        story.append(table)

        story.append(Paragraph('Einstellungen', style['Heading3']))
        if self.meta:
            table = Table([[k, str(v)] for k, v in self.meta['settings'].items()])
            table.hAlign = 'LEFT'
            story.append(table)
        else:
            story.append(Paragraph('unknown'))

        story.append(Paragraph('Kalibration', style['Heading3']))
        if self.meta:
            table = Table([[k, str(v)] for k, v in self.meta['calibration'].items()])
            table.hAlign = 'LEFT'
            story.append(table)
        else:
            story.append(Paragraph('unknown'))

        from io import BytesIO
        if self.add_plots_cb.isChecked():
            for resp in self.responses:
                img = BytesIO()
                FireResponse.plot_response_to_file(resp, img)
                img.seek(0)
                #img = BytesIO(img.data())
                story.append(Image(img, width=0.6 * A4[0], height=480 / 640 * 0.6 * A4[0]))

        # Anlegen des PDFs
        pdf = SimpleDocTemplate(fname, pagesize=A4)
        pdf.build(story, canvasmaker=FooterCanvas)
        self.close()


class Response(QObject):
    changed = pyqtSignal(object)

    def __init__(self, start, end, threshold, data: pd.DataFrame, trace: str, region_item: pg.LinearRegionItem,
                 force_start_value=None, force_end_value=None, force_onset_ts=None):
        super().__init__()
        self.data = data
        self.trace = trace
        self.threshold = threshold
        self.start = start
        self.end = end
        self.force_start_value = force_start_value
        self.force_end_value = force_end_value
        self.force_onset_ts = force_onset_ts
        self.from_value = np.nan
        self.to_value = np.nan
        self.onset_ts = np.nan
        self.t63_ts = np.nan
        self.t63 = np.nan
        self.t90_ts = np.nan
        self.t90 = np.nan
        self.t95_ts = np.nan
        self.t95 = np.nan
        self.t99_ts = np.nan
        self.t99 = np.nan
        self.temperature = np.nan
        self.region_item = region_item
        region_item.sigRegionChangeFinished.connect(self.on_region_changed)

        self.evaluate_response_times()

    @property
    def cut_data(self):
        return self.data.loc[dt.datetime.utcfromtimestamp(self.start).strftime('%Y-%m-%d %H:%M:%S.%f'): dt.datetime.utcfromtimestamp(self.end).strftime('%Y-%m-%d %H:%M:%S.%f'), self.trace]


    def set_threshold(self, value: float):
        self.threshold = value
        self.force_onset_ts = False
        self.evaluate_response_times()
        self.changed.emit(self)

    def set_force_start(self, value):
        self.force_start_value = value
        self.evaluate_response_times()
        self.changed.emit(self)

    def set_force_end(self, value):
        self.force_end_value = value
        self.evaluate_response_times()
        self.changed.emit(self)

    def evaluate_response_times(self):
        # cut data
        d = self.cut_data
        if self.force_start_value is not None:
            self.from_value = start = self.force_start_value
        else:
            self.from_value = start = d.iloc[:5].mean()
        if self.force_end_value is not None:
            self.to_value = end = self.force_end_value
        else:
            self.to_value = end = d.iloc[-5:].mean()
        timestamps = []
        for threshold in [start + thres / 100 * (end - start) for thres in [self.threshold, 63, 90, 95, 99]]:
            for i in range(len(d.index) - 1):
                if (end > start and d.iloc[i + 1] > threshold) or (start > end and d.iloc[i + 1] < threshold):
                    timestamps.append(d.index[i])
                    break
                elif i + 2 == len(d.index):
                    timestamps.append(np.nan)
        self.onset_ts, self.t63_ts, self.t90_ts, self.t95_ts, self.t99_ts = timestamps
        if self.force_onset_ts:
            self.onset_ts = self.force_onset_ts
        self.t63 = (self.t63_ts - self.onset_ts).total_seconds()
        self.t90 = (self.t90_ts - self.onset_ts).total_seconds()
        self.t95 = (self.t95_ts - self.onset_ts).total_seconds()
        self.t99 = (self.t99_ts - self.onset_ts).total_seconds()
        try:
            self.temperature = self.data['Sample Temp. (°C)'][dt.datetime.utcfromtimestamp(self.start): dt.datetime.utcfromtimestamp(self.end)].mean()
        except KeyError:
            self.temperature = np.nan

    def on_region_changed(self, region: pg.LinearRegionItem):
        self.start, self.end = region.getRegion()
        self.evaluate_response_times()
        self.changed.emit(self)

    def on_onset_line_moved(self, line):
        self.force_onset_ts = self.onset_ts + pd.Timedelta(seconds=line.value())
        self.evaluate_response_times()
        self.changed.emit(self)




class DateAxis(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        """ Copied from the internet

        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.autoSIPrefix = False

    def tickStrings(self, values, scale, spacing):
        strns = []
        try:
            rng_min = self.getViewBox().viewRange()[0][0]
            rng_max = self.getViewBox().viewRange()[0][1]
            rng = rng_max - rng_min
        except ValueError:
            rng_min = 0
            rng_max = 0
            rng = 0
        #if rng < 120:
        #    return pg.AxisItem.tickStrings(self, values, scale, spacing)
        if rng < 3600*24:  # < 1 day
            string = '%H:%M:%S'
            label = '%b %d'
        elif rng >= 3600*24 and rng < 3600*24*30:  # > 1 day, < 1 month
            string = '%d. %b %H:%M'
            label = '%b, %Y'
        elif rng >= 3600*24*30 and rng < 3600*24*30*24:  # > 1 month, < 2 years
            string = '%b %d'
            label = '%Y'
        elif rng >=3600*24*30*24:  # > 2 years
            string = '%b, %Y'
            label = ''
        for x in values:
            try:
                strns.append(dt.datetime.utcfromtimestamp(x).strftime(string))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        try:
            l = time.strftime(label, time.gmtime(rng_min))
            if time.strftime(label, time.gmtime(rng_max)) != time.strftime(label, time.gmtime(rng_min)):
                l += ' - ' + time.strftime(label, time.gmtime(rng_max))
        except ValueError:
            l = ''
        self.setLabel(text=l, units='', unitPrefix='')
        return strns

    def tickSpacing(self, minVal, maxVal, size):
        """Return values describing the desired spacing and offset of ticks.

        This method is called whenever the axis needs to be redrawn and is a
        good method to override in subclasses that require control over tick locations.

        The return value must be a list of tuples, one for each set of ticks::

            [
                (major tick spacing, offset),
                (minor tick spacing, offset),
                (sub-minor tick spacing, offset),
                ...
            ]
        """

        dif = abs(maxVal - minVal)
        if dif == 0:
            return []

        ## decide optimal minor tick spacing in pixels (this is just aesthetics)
        optimalTickCount = max(2., np.log(size))

        ## optimal minor tick spacing
        optimalSpacing = dif / optimalTickCount

        intervals = [1, 5, 10, 30, 60, 300, 600, 1800, 3600, 3*3600, 6*3600, 12*3600, 24*3600, 24*3600]
        i = 0
        while intervals[i] <= optimalSpacing:
            i += 1
            if len(intervals) - 1 == i:
                intervals.append(intervals[-1]*2)

        return (intervals[i+1], 0), (intervals[i], 0)


def main():
    import sys
    app = QApplication(sys.argv)
    gui = FireResponse()
    gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


