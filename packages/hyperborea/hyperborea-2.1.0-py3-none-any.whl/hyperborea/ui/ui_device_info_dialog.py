# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'device_info_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.5.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QPlainTextEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_DeviceInfoDialog(object):
    def setupUi(self, DeviceInfoDialog):
        if not DeviceInfoDialog.objectName():
            DeviceInfoDialog.setObjectName(u"DeviceInfoDialog")
        DeviceInfoDialog.resize(736, 548)
        self.verticalLayout = QVBoxLayout(DeviceInfoDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.plainTextEdit = QPlainTextEdit(DeviceInfoDialog)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.plainTextEdit.setReadOnly(True)

        self.verticalLayout.addWidget(self.plainTextEdit)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.saveButton = QPushButton(DeviceInfoDialog)
        self.saveButton.setObjectName(u"saveButton")

        self.horizontalLayout.addWidget(self.saveButton)

        self.buttonBox = QDialogButtonBox(DeviceInfoDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.horizontalLayout.addWidget(self.buttonBox)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(DeviceInfoDialog)
        self.buttonBox.accepted.connect(DeviceInfoDialog.accept)
        self.buttonBox.rejected.connect(DeviceInfoDialog.reject)

        QMetaObject.connectSlotsByName(DeviceInfoDialog)
    # setupUi

    def retranslateUi(self, DeviceInfoDialog):
        DeviceInfoDialog.setWindowTitle(QCoreApplication.translate("DeviceInfoDialog", u"Device Information", None))
        self.saveButton.setText(QCoreApplication.translate("DeviceInfoDialog", u"Save As...", None))
    # retranslateUi

