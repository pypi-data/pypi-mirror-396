from bec_widgets.utils.bec_widget import BECWidget
from qtpy.QtWidgets import QWidget


class Nouiwidgetplugin(BECWidget, QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)

if __name__ == "__main__":
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = Nouiwidgetplugin()
    widget.show()
    sys.exit(app.exec())