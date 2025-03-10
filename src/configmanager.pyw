from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox, QVBoxLayout, QWidget, QPushButton, QLineEdit
import sys
import configparser

class PluginConfig(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Streamutils config - plugins")
        self.setGeometry(100, 100, 250, 400)
        self.plugin_list = {}

        self.configfile = "res/my_configuration.ini"
        self.configpathedit = QLineEdit()
        self.configpathedit.returnPressed.connect(self.change_config)

        self.config = configparser.ConfigParser()
        self.config.read(self.configfile)
        
        self.layout = QVBoxLayout()

        self.savebutton = QPushButton(text=f"Save to {self.configfile}")
        self.savebutton.clicked.connect(self.save_configuration)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.layout.addWidget(self.savebutton)
        self.layout.addWidget(self.configpathedit)
        self.show_plugin_list()

    def reconfig(self, new_path):
        self.configfile = new_path
        del self.config
        self.config = configparser.ConfigParser()
        self.config.read(self.configfile)
        self.show_plugin_list()
    
    def show_plugin_list(self):
        for widget in self.plugin_list.values():
            widget.deleteLater()  # Remove the widget from the layout and memory

        self.plugin_list = {}
        for name, value in self.config["Plugins.enable"].items():
            print(name, value)
            box = QCheckBox(text=name)
            if value == "yes": box.setChecked(True)

            self.layout.addWidget(box)
            self.plugin_list[name] = box
    
    def save_configuration(self):
        for name, box in self.plugin_list.items():
            state = "yes" if box.isChecked() else "no"
            print(name, box, state)
            self.config["Plugins.enable"][name] = state

        with open(self.configfile, "w") as f:
            self.config.write(f)
    
    def change_config(self):
        self.old_config = self.configfile
        try:
            self.reconfig(self.configpathedit.text())
        except Exception:
            print("That config wasn't valid oh no")
            self.reconfig(self.old_config)

        self.savebutton.setText(f"Save to {self.configfile}")
        print("New config", self.configfile)

class OtherOptions(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Streamutils config - plugins")
        self.setGeometry(100, 100, 640, 480)

        self.configfile = "res/my_configuration.ini"
        self.configpathedit = QLineEdit()
        self.configpathedit.returnPressed.connect(self.change_config)

        self.config = configparser.ConfigParser()
        self.config.read(self.configfile)
        
        self.layout = QVBoxLayout()

        self.savebutton = QPushButton(text=f"Save to {self.configfile}")
        self.savebutton.clicked.connect(self.save_configuration)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.layout.addWidget(self.configpathedit)
        self.layout.addWidget(self.savebutton)

    def change_config(self):
        self.old_config = self.configfile
        try:
            self.reconfig(self.configpathedit.text())
        except Exception:
            print("That config wasn't valid oh no")
            self.reconfig(self.old_config)

        self.savebutton.setText(f"Save to {self.configfile}")
        print("New config", self.configfile)

    def save_configuration(self):
        for name, box in self.plugin_list.items():
            state = "yes" if box.isChecked() else "no"
            print(name, box, state)
            self.config["Plugins.enable"][name] = state

        with open(self.configfile, "w") as f:
            self.config.write(f)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PluginConfig()
    window.show()
    sys.exit(app.exec_())
