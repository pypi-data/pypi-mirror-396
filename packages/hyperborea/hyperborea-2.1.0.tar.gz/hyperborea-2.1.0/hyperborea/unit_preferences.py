from dataclasses import dataclass
import math
from typing import TypedDict

from PySide6 import QtCore, QtWidgets

import asphodel

from .preferences import read_bool_setting, write_bool_setting
from .ui.ui_unit_preferences_widget import Ui_UnitPreferencesWidget


class UnitType(TypedDict):
    unit_type: int
    setting_name: str
    scale: float
    offset: float
    unit_strings: tuple[str, str, str]


class UnitButtonType(TypedDict):
    group: QtWidgets.QButtonGroup
    metric: QtWidgets.QRadioButton
    us: QtWidgets.QRadioButton
    alt: tuple[QtWidgets.QRadioButton, str] | None


# NOTE: code can only display one alternate unit per unit type in the dialog
alternate_units: list[UnitType] = [
    {"unit_type": asphodel.UnitType.WATT,
     "setting_name": "UseHorsepower",
     "scale": 1 / 746.0,
     "offset": 0.0,
     "unit_strings": ("HP", "HP", "HP")},
    {"unit_type": asphodel.UnitType.M_PER_S2,
     "setting_name": "UseGForce",
     "scale": 1 / 9.80665,
     "offset": 0.0,
     "unit_strings": ("g", "g", "<b>g</b>")},
    {"unit_type": asphodel.UnitType.HZ,
     "setting_name": "UseCPM",
     "scale": 60.0,
     "offset": 0.0,
     "unit_strings": ("CPM", "CPM", "CPM")},
    {"unit_type": asphodel.UnitType.METER,
     "setting_name": "UseInch",
     "scale": 39.3700787401575,
     "offset": 0.0,
     "unit_strings": ("in", "in", "in")},
    {"unit_type": asphodel.UnitType.GRAM,
     "setting_name": "UseOunce",
     "scale": 0.035273961949580414,
     "offset": 0.0,
     "unit_strings": ("oz", "oz", "oz")},
    {"unit_type": asphodel.UnitType.M3_PER_S,
     "setting_name": "UseGPM",
     "scale": 15850.323141489,
     "offset": 0.0,
     "unit_strings": ("gal/min", "gal/min", "gal/min")},
    {"unit_type": asphodel.UnitType.NEWTON_METER,
     "setting_name": "UseLbfIn",
     "scale": 8.850745780434613,
     "offset": 0.0,
     "unit_strings": ("lbf*in", b"lbf\xe2\x8b\x85in".decode("utf-8"),
                      "lbf&#8901;in")},
]


@dataclass
class UnitOption:
    unit_formatter: asphodel.UnitFormatter
    metric: bool  # formatter created when metric=True
    non_metric: bool  # formatter created (or equal to) when metric=False
    alt_setting_name: str | None  # only used when UseMixed=True
    base_str: str  # utf-8 base unit without any SI prefix
    metric_scale: float | None  # factor to get to formatter's SI prefix
    metric_relation: str | None  # None if it's a metric converter
    setting_name: str  # name used for this unit when stored in settings


def get_unit_options(unit_type: int, minimum: float, maximum: float,
                     resolution: float) -> list[UnitOption]:
    metric_formatter = asphodel.create_unit_formatter(
        unit_type, minimum, maximum, resolution, use_metric=True)
    us_formatter = asphodel.create_unit_formatter(
        unit_type, minimum, maximum, resolution, use_metric=False)

    # figure out if the metric formatter follows SI rules
    metric_scale = None
    base_str = metric_formatter.unit_utf8
    if metric_formatter.conversion_offset == 0.0:
        uf_1000x = asphodel.create_unit_formatter(
            unit_type, minimum * 1000.0, maximum * 1000.0, resolution,
            use_metric=True)
        ratio = (metric_formatter.conversion_scale /
                 uf_1000x.conversion_scale)
        if math.isclose(1000.0, ratio):
            # it's an SI unit formatter
            metric_scale = 1.0 / metric_formatter.conversion_scale

            # find the base string
            uf_base = asphodel.create_unit_formatter(
                unit_type, 1.0, 1.0, 1.0, use_metric=True)
            base_str = uf_base.unit_utf8

    unit_options = [UnitOption(
        unit_formatter=metric_formatter,
        metric=True,
        non_metric=(metric_formatter == us_formatter),
        alt_setting_name=None,
        base_str=base_str,
        metric_scale=metric_scale,
        metric_relation=None,
        setting_name="Metric")]

    if metric_formatter != us_formatter:
        metric_relation = asphodel.format_value_utf8(
            unit_type, 0.0, 1 / us_formatter.conversion_scale, use_metric=True)
        unit_options.append(UnitOption(
            unit_formatter=us_formatter,
            metric=False,
            non_metric=True,
            alt_setting_name=None,
            base_str=us_formatter.unit_utf8,
            metric_scale=None,
            metric_relation=metric_relation,
            setting_name="US"))

    # see if there's an alternate type
    for alternate_unit in alternate_units:
        if unit_type == alternate_unit['unit_type']:
            alt_formatter = asphodel.create_custom_unit_formatter(
                alternate_unit["scale"], alternate_unit["offset"],
                resolution, *alternate_unit["unit_strings"])
            metric_relation = asphodel.format_value_utf8(
                unit_type, 0.0, 1 / alternate_unit['scale'], use_metric=True)
            unit_options.append(UnitOption(
                unit_formatter=alt_formatter,
                metric=False,
                non_metric=False,
                alt_setting_name=alternate_unit['setting_name'],
                base_str=alt_formatter.unit_utf8,
                metric_scale=None,
                metric_relation=metric_relation,
                setting_name=alternate_unit['setting_name']))
    return unit_options


def get_si_unit_options(unit_type: int, minimum: float, maximum: float,
                        resolution: float) -> list[UnitOption]:
    """
    NOTE: this function assumes that the unit_type is actually an SI unit.
    """
    uf_base = asphodel.create_unit_formatter(
        unit_type, 1.0, 1.0, 1.0, use_metric=True)
    base_str = uf_base.unit_utf8

    if unit_type == asphodel.UnitType.SECOND:
        exponents = [0, -3, -6, -9]
    elif unit_type == asphodel.UnitType.HZ:
        exponents = [9, 6, 3, 0]
    elif (unit_type == asphodel.UnitType.GRAM or
          unit_type == asphodel.UnitType.GRAM_PER_S):
        exponents = [3, 0, -3, -6]
    elif unit_type == asphodel.UnitType.METER:
        exponents = [3, 0, -3, -6, -9]
    else:
        exponents = [6, 3, 0, -3, -6, -9]

    unit_options: list[UnitOption] = []
    for exponent in exponents:
        scaling_factor = 10**exponent

        # scale min and max by 10 to avoid floating point issues
        unit_formatter = asphodel.create_unit_formatter(
            unit_type, 10*scaling_factor, -10*scaling_factor,
            resolution, use_metric=True)

        unit_options.append(UnitOption(
            unit_formatter=unit_formatter,
            metric=True,
            non_metric=False,
            alt_setting_name=None,
            base_str=base_str,
            metric_scale=scaling_factor,
            metric_relation=None,
            setting_name=f"Metric{exponent}"))

    return unit_options


def get_default_option(settings: QtCore.QSettings, unit_type: int,
                       unit_options: list[UnitOption]) -> UnitOption:
    use_mixed = read_bool_setting(settings, "UseMixed", False)
    if use_mixed:
        for unit_option in unit_options:
            setting_name = unit_option.alt_setting_name
            if setting_name:
                if read_bool_setting(settings, setting_name, False):
                    return unit_option

        use_metric_overall = read_bool_setting(settings, "UseMetric", True)
        setting_name = "UseMetricType{}".format(unit_type)
        use_metric = read_bool_setting(
            settings, setting_name, use_metric_overall)
    else:
        use_metric = read_bool_setting(settings, "UseMetric", True)

    for unit_option in unit_options:
        if use_metric:
            if unit_option.metric:
                return unit_option
        else:
            if unit_option.non_metric:
                return unit_option

    # shouldn't get here with a valid set of unit options
    raise ValueError("No valid unit options")


def _get_settings_key(serial_number: str, channel_id: int, channel_name: str,
                      unit_type: int) -> str:
    return f"{serial_number}/Channel{channel_id}_{channel_name}_{unit_type}"


def get_default_channel_option(
        settings: QtCore.QSettings, serial_number: str, channel_id: int,
        channel_name: str, unit_type: int, unit_options: list[UnitOption],
        si_unit_options: list[UnitOption]) -> UnitOption:
    key = _get_settings_key(serial_number, channel_id, channel_name, unit_type)
    value = settings.value(key)

    if value:
        for unit_option in unit_options:
            if unit_option.setting_name == value:
                return unit_option

        for unit_option in si_unit_options:
            if unit_option.setting_name == value:
                return unit_option

    return get_default_option(settings, unit_type, unit_options)


def set_default_channel_option(
        settings: QtCore.QSettings, serial_number: str, channel_id: int,
        channel_name: str, unit_type: int, unit_options: list[UnitOption],
        unit_option: UnitOption) -> None:
    key = _get_settings_key(serial_number, channel_id, channel_name, unit_type)
    default_option = get_default_option(settings, unit_type, unit_options)
    if default_option != unit_option:
        settings.setValue(key, unit_option.setting_name)
    else:
        settings.remove(key)


def create_unit_formatter(settings: QtCore.QSettings, unit_type: int,
                          minimum: float, maximum: float, resolution: float)\
                              -> asphodel.UnitFormatter:
    unit_options = get_unit_options(unit_type, minimum, maximum, resolution)
    option = get_default_option(settings, unit_type, unit_options)
    return option.unit_formatter


class UnitPreferencesWidget(Ui_UnitPreferencesWidget, QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        self.settings = QtCore.QSettings()

        self.unit_buttons: dict[int, UnitButtonType] = {}

        self.setupUi(self)  # type: ignore

        self._create_unit_buttons()

        self.metricUnits.toggled.connect(self.toggled_metric)
        self.usUnits.toggled.connect(self.toggled_us)
        self.mixedUnits.toggled.connect(self.toggled_mixed)

        self.unitGridLayout.setColumnStretch(0, 1)
        self.unitGridLayout.setColumnStretch(1, 1)
        self.unitGridLayout.setColumnStretch(2, 1)

        self.read_settings()

    def _create_unit_buttons(self) -> None:
        for unit_type in range(len(asphodel.unit_type_names)):
            metric_formatter = asphodel.create_unit_formatter(
                unit_type, 0.0, 0.0, 0.0, use_metric=True)
            us_formatter = asphodel.create_unit_formatter(
                unit_type, 0.0, 0.0, 0.0, use_metric=False)

            # see if there's an alternate type for this button
            alt: tuple[QtWidgets.QRadioButton, str] | None = None
            for alternate_unit in alternate_units:
                if unit_type == alternate_unit['unit_type']:
                    alt_setting = alternate_unit['setting_name']
                    alt_button = QtWidgets.QRadioButton(self)
                    alt_name = alternate_unit['unit_strings'][1]  # UTF-8
                    metric_relation = metric_formatter.format_utf8(
                        1 / alternate_unit['scale'])
                    alt_text = "{} ({})".format(alt_name, metric_relation)
                    alt_button.setText(alt_text)
                    alt = (alt_button, alt_setting)
                    break

            button_dict: UnitButtonType
            if metric_formatter != us_formatter:
                # need two buttons
                row_count = self.unitGridLayout.rowCount()
                button_group = QtWidgets.QButtonGroup(self)

                metric_button = QtWidgets.QRadioButton(self)
                button_group.addButton(metric_button)
                metric_button.setText(metric_formatter.unit_utf8)
                self.unitGridLayout.addWidget(metric_button, row_count, 0)

                us_button = QtWidgets.QRadioButton(self)
                button_group.addButton(us_button)
                us_button.setText(us_formatter.unit_utf8)
                self.unitGridLayout.addWidget(us_button, row_count, 1)

                if alt:
                    button_group.addButton(alt[0])
                    self.unitGridLayout.addWidget(alt[0], row_count, 2)

                button_dict = {
                    "group": button_group,
                    "metric": metric_button,
                    "us": us_button,
                    "alt": alt,
                }
                self.unit_buttons[unit_type] = button_dict
            elif alt is not None:
                # need a combined metric/us button
                row_count = self.unitGridLayout.rowCount()
                button_group = QtWidgets.QButtonGroup(self)

                metric_us_button = QtWidgets.QRadioButton(self)
                button_group.addButton(metric_us_button)
                metric_us_button.setText(metric_formatter.unit_utf8)
                self.unitGridLayout.addWidget(metric_us_button, row_count, 0,
                                              1, 2)

                if alt:
                    button_group.addButton(alt[0])
                    self.unitGridLayout.addWidget(alt[0], row_count, 2)

                button_dict = {
                    "group": button_group,
                    "metric": metric_us_button,
                    "us": metric_us_button,
                    "alt": alt,
                }
                self.unit_buttons[unit_type] = button_dict
            else:
                pass  # only metric available: no button needed

    def read_settings(self) -> None:
        use_mixed = read_bool_setting(self.settings, "UseMixed", False)
        use_metric = read_bool_setting(self.settings, "UseMetric", True)

        if use_mixed:
            self.mixedUnits.setChecked(True)

            # load unit settings
            for unit_type, button_dict in self.unit_buttons.items():
                alt = button_dict["alt"]
                if alt is not None:
                    alt_button, alt_setting = alt
                    use_alt = read_bool_setting(
                        self.settings, alt_setting, False)
                    if use_alt:
                        alt_button.setChecked(True)
                else:
                    use_alt = False

                if not use_alt:
                    setting_name = "UseMetricType{}".format(unit_type)
                    type_metric = read_bool_setting(
                        self.settings, setting_name, use_metric)
                    if type_metric:
                        button_dict["metric"].setChecked(True)
                    else:
                        button_dict["us"].setChecked(True)
        else:
            if use_metric:
                self.metricUnits.setChecked(True)
            else:
                self.usUnits.setChecked(True)

    def write_settings(self) -> None:
        use_mixed = self.mixedUnits.isChecked()
        write_bool_setting(self.settings, "UseMixed", use_mixed)

        if use_mixed:
            for unit_type, button_dict in self.unit_buttons.items():
                alt = button_dict["alt"]
                if alt is not None:
                    alt_button, alt_setting = alt
                    use_alt = alt_button.isChecked()
                    write_bool_setting(self.settings, alt_setting, use_alt)
                else:
                    use_alt = False

                if not use_alt:
                    if button_dict["metric"] is not button_dict["us"]:
                        setting_name = "UseMetricType{}".format(unit_type)
                        type_metric = button_dict["metric"].isChecked()
                        write_bool_setting(self.settings, setting_name,
                                           type_metric)
        else:
            use_metric = self.metricUnits.isChecked()
            write_bool_setting(self.settings, "UseMetric", use_metric)

    @QtCore.Slot()
    def toggled_metric(self) -> None:
        if self.metricUnits.isChecked():
            for button_dict in self.unit_buttons.values():
                button_dict['metric'].setChecked(True)

                button_dict['metric'].setEnabled(False)
                button_dict['us'].setEnabled(False)
                if button_dict['alt'] is not None:
                    button_dict['alt'][0].setEnabled(False)

    @QtCore.Slot()
    def toggled_us(self) -> None:
        if self.usUnits.isChecked():
            for button_dict in self.unit_buttons.values():
                button_dict['us'].setChecked(True)

                button_dict['metric'].setEnabled(False)
                button_dict['us'].setEnabled(False)
                if button_dict['alt'] is not None:
                    button_dict['alt'][0].setEnabled(False)

    @QtCore.Slot()
    def toggled_mixed(self) -> None:
        if self.mixedUnits.isChecked():
            for button_dict in self.unit_buttons.values():
                button_dict['metric'].setEnabled(True)
                button_dict['us'].setEnabled(True)
                if button_dict['alt'] is not None:
                    button_dict['alt'][0].setEnabled(True)
