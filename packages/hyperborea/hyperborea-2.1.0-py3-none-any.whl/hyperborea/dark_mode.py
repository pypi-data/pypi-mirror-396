from PySide6 import QtCore, QtGui, QtWidgets


original_palette: QtGui.QPalette | None = None
current_setting: bool | None = None


def set_style(app: QtWidgets.QApplication, dark_mode: bool = True) -> None:
    global current_setting
    if current_setting == dark_mode:
        return
    current_setting = dark_mode

    app.setStyle("Fusion")

    global original_palette
    if original_palette is None:
        original_palette = app.palette()

    # Now use a palette to switch to dark colors:
    if dark_mode:
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ColorRole.Window,
                         QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ColorRole.WindowText,
                         QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.Base,
                         QtGui.QColor(25, 25, 25))
        palette.setColor(QtGui.QPalette.ColorRole.AlternateBase,
                         QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase,
                         QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipText,
                         QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.Text,
                         QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.PlaceholderText,
                         QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.Button,
                         QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText,
                         QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.BrightText,
                         QtCore.Qt.GlobalColor.red)
        palette.setColor(QtGui.QPalette.ColorRole.Link,
                         QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.ColorRole.Highlight,
                         QtGui.QColor(31, 97, 163))
        palette.setColor(QtGui.QPalette.ColorRole.HighlightedText,
                         QtCore.Qt.GlobalColor.white)

        palette.setColor(QtGui.QPalette.ColorGroup.Disabled,
                         QtGui.QPalette.ColorRole.WindowText,
                         QtCore.Qt.GlobalColor.darkGray)
        palette.setColor(QtGui.QPalette.ColorGroup.Disabled,
                         QtGui.QPalette.ColorRole.Text,
                         QtCore.Qt.GlobalColor.darkGray)
        palette.setColor(QtGui.QPalette.ColorGroup.Disabled,
                         QtGui.QPalette.ColorRole.ButtonText,
                         QtCore.Qt.GlobalColor.darkGray)
        palette.setColor(QtGui.QPalette.ColorGroup.Disabled,
                         QtGui.QPalette.ColorRole.Light,
                         QtCore.Qt.GlobalColor.black)

        app.setPalette(palette)
    else:
        app.setPalette(original_palette)
