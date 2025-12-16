import logging
import os

from PySide6 import QtCore, QtGui, QtWidgets

from asphodel.device_info import DeviceInfo

from .ui.ui_device_info_dialog import Ui_DeviceInfoDialog

logger = logging.getLogger(__name__)


class DeviceInfoDialog(Ui_DeviceInfoDialog, QtWidgets.QDialog):
    def __init__(self, device_info: DeviceInfo,
                 parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        self.device_info = device_info

        self.setupUi(self)  # type: ignore

        self.plainTextEdit.setFont(QtGui.QFontDatabase.systemFont(
            QtGui.QFontDatabase.SystemFont.FixedFont))

        self.device_info_str = device_info.summary()
        self.plainTextEdit.setPlainText(self.device_info_str)

        self.saveButton.clicked.connect(self.save)

    def get_save_path(self) -> str | None:
        serial_number = self.device_info.serial_number
        default_name = f"{serial_number}.txt"

        # find the directory from settings
        settings = QtCore.QSettings()
        directory = settings.value("infoSaveDirectory")
        if not directory or not isinstance(directory, str):
            directory = None
        elif not os.path.isdir(directory):
            directory = None

        if not directory:
            directory = QtCore.QStandardPaths.writableLocation(
                QtCore.QStandardPaths.StandardLocation.DocumentsLocation)

        file_and_dir = os.path.join(directory, default_name)

        caption = self.tr("Save Device Information")
        file_filter = self.tr("Text Files (*.txt);;All Files (*.*)")
        val = QtWidgets.QFileDialog.getSaveFileName(
            self, caption, file_and_dir, file_filter)
        output_path = val[0]

        if output_path:
            # save the directory
            output_dir = os.path.dirname(output_path)
            settings.setValue("infoSaveDirectory", output_dir)
            return os.path.abspath(output_path)
        else:
            return None

    @QtCore.Slot()
    def save(self) -> None:
        path = self.get_save_path()
        if path:
            try:
                with open(path, "wt", encoding="utf-8") as f:
                    f.write(self.device_info_str)
                    f.write("\n")  # trailing newline
            except Exception:
                msg = f"Error writing file {path}."
                logger.exception(msg)
                QtWidgets.QMessageBox.critical(self, self.tr("Error"),
                                               self.tr(msg))
                return
