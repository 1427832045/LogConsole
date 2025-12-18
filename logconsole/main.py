"""
LogConsole 主程序入口
"""
import sys
from PyQt5.QtWidgets import QApplication
from logconsole.ui.main_window import MainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("LogConsole")
    app.setOrganizationName("LogConsole Team")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
