import sys
from app.gui import VeoStudioWindow
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = VeoStudioWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
