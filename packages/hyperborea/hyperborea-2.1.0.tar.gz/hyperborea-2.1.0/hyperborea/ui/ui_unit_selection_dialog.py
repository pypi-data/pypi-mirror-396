# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'unit_selection_dialog.ui'
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
    QGridLayout, QLabel, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_UnitSelectionDialog(object):
    def setupUi(self, UnitSelectionDialog):
        if not UnitSelectionDialog.objectName():
            UnitSelectionDialog.setObjectName(u"UnitSelectionDialog")
        UnitSelectionDialog.resize(184, 68)
        self.verticalLayout = QVBoxLayout(UnitSelectionDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.unitGridLayout = QGridLayout()
        self.unitGridLayout.setObjectName(u"unitGridLayout")
        self.unitGridLayout.setHorizontalSpacing(20)
        self.unitGridLayout.setVerticalSpacing(1)
        self.metricLabel = QLabel(UnitSelectionDialog)
        self.metricLabel.setObjectName(u"metricLabel")
        font = QFont()
        font.setBold(True)
        self.metricLabel.setFont(font)

        self.unitGridLayout.addWidget(self.metricLabel, 0, 0, 1, 1)

        self.usLabel = QLabel(UnitSelectionDialog)
        self.usLabel.setObjectName(u"usLabel")
        self.usLabel.setFont(font)

        self.unitGridLayout.addWidget(self.usLabel, 0, 1, 1, 1)

        self.otherLabel = QLabel(UnitSelectionDialog)
        self.otherLabel.setObjectName(u"otherLabel")
        self.otherLabel.setFont(font)

        self.unitGridLayout.addWidget(self.otherLabel, 0, 2, 1, 1)


        self.verticalLayout.addLayout(self.unitGridLayout)

        self.verticalSpacer = QSpacerItem(20, 7, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(UnitSelectionDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(UnitSelectionDialog)
        self.buttonBox.accepted.connect(UnitSelectionDialog.accept)
        self.buttonBox.rejected.connect(UnitSelectionDialog.reject)

        QMetaObject.connectSlotsByName(UnitSelectionDialog)
    # setupUi

    def retranslateUi(self, UnitSelectionDialog):
        UnitSelectionDialog.setWindowTitle(QCoreApplication.translate("UnitSelectionDialog", u"Select Unit", None))
        self.metricLabel.setText(QCoreApplication.translate("UnitSelectionDialog", u"SI", None))
        self.usLabel.setText(QCoreApplication.translate("UnitSelectionDialog", u"US Customary", None))
        self.otherLabel.setText(QCoreApplication.translate("UnitSelectionDialog", u"Other", None))
    # retranslateUi

