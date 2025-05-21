
# general imports
import sys
from PyQt5.QtWidgets import QApplication

# app imports
from src.application import Midnight

if __name__ == "__main__":

    app = QApplication(sys.argv)
    midnight = Midnight()
    midnight.show()
    sys.exit(app.exec_())
#endif