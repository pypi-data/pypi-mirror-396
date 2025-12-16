# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'unit_preferences_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QRadioButton, QSizePolicy,
    QWidget)

class Ui_UnitPreferencesWidget(object):
    def setupUi(self, UnitPreferencesWidget):
        if not UnitPreferencesWidget.objectName():
            UnitPreferencesWidget.setObjectName(u"UnitPreferencesWidget")
        UnitPreferencesWidget.resize(207, 17)
        self.unitGridLayout = QGridLayout(UnitPreferencesWidget)
        self.unitGridLayout.setObjectName(u"unitGridLayout")
        self.unitGridLayout.setContentsMargins(0, 0, 0, 0)
        self.metricUnits = QRadioButton(UnitPreferencesWidget)
        self.metricUnits.setObjectName(u"metricUnits")
        font = QFont()
        font.setBold(True)
        self.metricUnits.setFont(font)

        self.unitGridLayout.addWidget(self.metricUnits, 0, 0, 1, 1)

        self.usUnits = QRadioButton(UnitPreferencesWidget)
        self.usUnits.setObjectName(u"usUnits")
        self.usUnits.setFont(font)

        self.unitGridLayout.addWidget(self.usUnits, 0, 1, 1, 1)

        self.mixedUnits = QRadioButton(UnitPreferencesWidget)
        self.mixedUnits.setObjectName(u"mixedUnits")
        self.mixedUnits.setFont(font)

        self.unitGridLayout.addWidget(self.mixedUnits, 0, 2, 1, 1)


        self.retranslateUi(UnitPreferencesWidget)

        QMetaObject.connectSlotsByName(UnitPreferencesWidget)
    # setupUi

    def retranslateUi(self, UnitPreferencesWidget):
        self.metricUnits.setText(QCoreApplication.translate("UnitPreferencesWidget", u"SI", None))
        self.usUnits.setText(QCoreApplication.translate("UnitPreferencesWidget", u"US Customary", None))
        self.mixedUnits.setText(QCoreApplication.translate("UnitPreferencesWidget", u"Mixed", None))
        pass
    # retranslateUi

