import logging

from PySide6 import QtCore, QtWidgets

import asphodel

from . import unit_preferences
from .ui.ui_unit_selection_dialog import Ui_UnitSelectionDialog

logger = logging.getLogger(__name__)


class UnitSelectionDialog(Ui_UnitSelectionDialog, QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        self.unit_info: dict[
            QtWidgets.QRadioButton,
            tuple[int, asphodel.UnitFormatter]] = {}

        self.setupUi(self)  # type: ignore

        self.add_radio_buttons()

        self.values_updated()

    def add_radio_buttons(self) -> None:
        self.button_group = QtWidgets.QButtonGroup(self)
        self.button_group.buttonClicked.connect(self.values_updated)

        for unit_type, unit_type_name in enumerate(asphodel.unit_type_names):
            row_count = self.unitGridLayout.rowCount()

            # create metric button
            metric_formatter = asphodel.create_unit_formatter(
                unit_type, 0.0, 0.0, 0.0, use_metric=True)
            metric_button = QtWidgets.QRadioButton(self)
            if unit_type_name == "UNIT_TYPE_NONE":
                metric_button.setText("None")
            else:
                metric_button.setText(metric_formatter.unit_utf8)
            self.button_group.addButton(metric_button)
            self.unit_info[metric_button] = (unit_type, metric_formatter)
            self.unitGridLayout.addWidget(metric_button, row_count, 0)

            # create us button
            us_formatter = asphodel.create_unit_formatter(
                unit_type, 0.0, 0.0, 0.0, use_metric=False)
            if metric_formatter != us_formatter:
                us_button = QtWidgets.QRadioButton(self)
                us_button.setText(us_formatter.unit_utf8)
                self.button_group.addButton(us_button)
                self.unit_info[us_button] = (unit_type, us_formatter)
                self.unitGridLayout.addWidget(us_button, row_count, 1)

            # see if there's an alternate type for this unit
            for alternate_unit in unit_preferences.alternate_units:
                if unit_type == alternate_unit['unit_type']:
                    alt_button = QtWidgets.QRadioButton(self)
                    alt_name = alternate_unit['unit_strings'][1]  # UTF-8
                    metric_relation = metric_formatter.format_utf8(
                        1 / alternate_unit['scale'])
                    alt_text = "{} ({})".format(alt_name, metric_relation)
                    alt_button.setText(alt_text)
                    self.button_group.addButton(alt_button)
                    self.unitGridLayout.addWidget(alt_button, row_count, 2)

                    f = asphodel.create_custom_unit_formatter(
                        alternate_unit["scale"], alternate_unit["offset"],
                        0.0, *alternate_unit["unit_strings"])
                    self.unit_info[alt_button] = (unit_type, f)
                    break

    def is_valid(self) -> bool:
        # this can be null according to the Qt docs, but it's not reflected in
        # the type hints in PySide6 6.9.2
        if self.button_group.checkedButton() is None:  # pyright: ignore
            return False

        return True

    def done(self, r: int) -> None:
        if r and not self.is_valid():
            return
        super().done(r)

    @QtCore.Slot()
    def values_updated(self) -> None:
        ok_button = self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok)
        if self.is_valid():
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

    def get_unit_info(self) -> tuple[int, asphodel.UnitFormatter] | None:
        button: QtWidgets.QRadioButton = \
            self.button_group.checkedButton()  # type: ignore
        if button in self.unit_info:
            return self.unit_info[button]
        return None
