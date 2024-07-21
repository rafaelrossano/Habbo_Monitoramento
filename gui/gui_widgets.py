from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtSvgWidgets import QSvgWidget

containerColor = "#474747"
class SearchWidget(QtWidgets.QFrame):
    def __init__(self, ui, parent, x, y, width, height, object_name, background_color, search_bar_width, items_type, results_tracker_text):
        super().__init__(parent)
        self.setGeometry(x, y, width, height)
        self.setObjectName(object_name)
        self.setStyleSheet(f'background-color: {background_color}')
        self.show()
        self.searchBar = QtWidgets.QLineEdit(self)
        self.searchBar.setObjectName("searchBar")
        searchBarSpace = search_bar_width + 10
        self.searchBar.setGeometry(10, int(height*0.2), search_bar_width, int(height*0.6))
        self.searchBar.setStyleSheet("background-color: #FFFFFF; color: #000000; padding-left: 3px;")
        ui.current_font.setPointSize(12)
        ui.current_font.setBold(False)
        self.searchBar.setFont(ui.current_font)
        self.searchBar.installEventFilter(ui)
        self.searchBar.setPlaceholderText("Buscar...")
        self.searchBar.show()

        searchNavUtilsY = int(self.size().height()/2 - 10)
        self.resultsTracker = QtWidgets.QLabel(self)
        self.resultsTracker.setObjectName("resultsTracker")
        self.resultsTracker.setText(results_tracker_text)
        self.resultsTracker.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.resultsTracker.setFixedSize(60, int(height*0.6))
        self.resultsTracker.move(searchBarSpace + 5, int(height/2 - self.resultsTracker.size().height()/2))

        self.backButton = QSvgWidget("gui/assets/images/up_arrow_disabled.svg", self)
        self.backButton.setObjectName("backButton")
        self.backButton.setGeometry(searchBarSpace + 60 + 10, searchNavUtilsY, 20, 20)
        self.backButton.mousePressEvent = lambda event: ui.highlight_selected_result(-1, items_type)
        self.backButton.show()

        self.nextButton = QSvgWidget("gui/assets/images/down_arrow_disabled.svg", self)
        self.nextButton.setObjectName("nextButton")
        self.nextButton.setGeometry(searchBarSpace + 5 + 60 + 5 + 20 + 5, searchNavUtilsY, 20, 20)
        self.nextButton.mousePressEvent = lambda event: ui.highlight_selected_result(1, items_type)
        self.nextButton.show()

        print("quantidade de elementos na lista:", len(self.findChildren(QSvgWidget)))
        for widget in self.findChildren(QSvgWidget):
            widget.setStyleSheet("background-color: " + background_color + ";")
            widget.setCursor(Qt.CursorShape.PointingHandCursor)
            widget.installEventFilter(ui)
            widget.enterEvent = lambda event, w=widget: w.setStyleSheet("border-radius: 5px; background-color: " + containerColor + ";")
            widget.leaveEvent = lambda event, w=widget: w.setStyleSheet("background-color: " + background_color + ";")