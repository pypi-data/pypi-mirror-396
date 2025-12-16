from bec_widgets.utils.bec_widget import BECWidget
from qtpy.QtWidgets import QWidget

from bec_testing_plugin.bec_widgets.widgets.ExampleWidgetPlugin.ExampleWidgetPlugin_ui import (
    Ui_examplewidgetplugin,
)


class Examplewidgetplugin(BECWidget, QWidget, Ui_examplewidgetplugin):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.setupUi(self)


if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = Examplewidgetplugin()
    widget.show()
    sys.exit(app.exec())
