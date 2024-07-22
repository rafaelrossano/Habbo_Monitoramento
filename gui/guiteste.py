import random
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtSvgWidgets import QSvgWidget
from gui_widgets import SearchWidget
import socket
import threading
import sqlite3
from functools import partial
# from api.db_functions import read_table
# from api.config import *
from shared_variables import groups_members, groups_members_lock, groups_atts, groups_atts_lock
from gui_tools import read_table, commit_changes, run_client

groups = [("acesso_a_base", '#ff3333', '[DIC] Acesso à Base ®', '[DIC] Acesso à Base ®'),
          ("corpo_executivo", '#ededed', '[DIC] Corpo Executivo ®', '[DIC] Corpo Executivo ®'),
          ("corpo_executivo_superior", '#cfcfcf', '[DIC] Corpo Executivo Superior ®', '[DIC] Corpo Exec. Superior ®'),
          ("oficiais", '#fc5b5b', '[DIC] Oficiais ®', '[DIC] Oficiais ®'),
          ("oficiais_superiores", '#fbc900', '[DIC] Oficiais Superiores ®', '[DIC] Oficiais Sup. ®'),
          ("pracas", '#0acf02', '[DIC] Praças ®', '[DIC] Praças ®'),
        ]

def find_group_index(group):
    for i in range(len(groups)):
        if group == groups[i][0]:
            return i
        
date_displays = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

# groups_members = {}
groups_members_lock = threading.Lock()

# groups_atts = {}
group_atts_lock = threading.Lock()

windowWidth = 1130
windowHeight = 650

highlightedGroupThickness = 8

groupMembersWidth = 560
configsWidth = groupMembersWidth
configsHeight = 40
groupMembersHeight = windowHeight - configsHeight

navBarWidth = windowWidth // 10
groupsSize = navBarWidth
# groupsX = int(navBarWidth/2 - groupsSize/2)
groupsX = 0

attsX = navBarWidth + groupMembersWidth
attsY = 0
attsWidth = windowWidth - (navBarWidth + groupMembersWidth)
attsHeight = windowHeight - configsHeight

attContainerWidth = attsWidth
attContainerHeight = 100

centralX = 0
centralY = 0

random_colors = ["red", "yellow", "green", "blue", "purple", "orange", "pink", "brown", "cyan", "magenta", "teal", "lavender", "maroon", "navy", "olive", "lime", "beige", "crimson", "coral", "indigo", "gold", "silver", "violet", "turquoise", "tan", "plum", "salmon", "orchid", "khaki", "aquamarine", "chartreuse", "chocolate", "wheat", "azure", "lavender", "ivory", "gray", "black", "white"]

groupMembersContainerHeight = 80
defaultMargin = 15
fontcolor = "#FFFFFF"
backgroundColor = "#2e2e2e"
highlightedColor = "#7a7a7a"
containerColor = "#474747"
contrastColor = "#cfcfcf"
disabledColor = "#919191"
searchHighlightedColor = "#696969"
searchSelectedHighlightedColor = "#a87b13"

class GUI_MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(windowWidth, windowHeight)
        MainWindow.setFixedSize(windowWidth, windowHeight)
        MainWindow.setWindowIcon(QtGui.QIcon('gui/assets/images/CORE.png'))
        MainWindow.setStyleSheet("background-color:" + backgroundColor + ";")

        # Este widget basicamente é o widget-pai. Ele serve para ser parent de todos os principais containers
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("color: " + fontcolor + ";")

        self.current_members = []
        self.searched_members = []
        self.members_filter = ["user_name"]

        self.current_atts = []
        self.searched_atts = []
        self.atts_filter = ["attName"]
        # Grupos na barra de navegação
        self.groups = []

        self.current_font = QtGui.QFont()

        self.current_group = 'acesso_a_base'

        # Barra de navegação entre grupos
        self.navBar = QtWidgets.QFrame(self.centralwidget)
        self.navBar.setObjectName("navBar")
        self.navBar.setGeometry(QtCore.QRect(centralX, centralY, windowWidth // 10, windowHeight))
        self.navBar.setStyleSheet("background-color:" + backgroundColor + ";")


        # Linha que separa a navBar do conteúdo dos grupos [UNICAMENTE COSMÉTICA]
        self.lineNavContent = QtWidgets.QFrame(self.centralwidget)
        self.lineNavContent.setGeometry(QtCore.QRect(windowWidth // 10, centralY, 5, windowHeight))
        self.lineNavContent.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.lineNavContent.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.lineNavContent.setObjectName("line")

        # Marcador de qual grupo está selecionado para visualização
        self.selectedGroupHighlight = QtWidgets.QFrame(self.centralwidget)
        self.selectedGroupHighlight.setObjectName("selectedGroupHighlight")
        self.selectedGroupHighlight.setGeometry(QtCore.QRect(groupsX - highlightedGroupThickness,
                                                             windowHeight // 20 - highlightedGroupThickness,
                                                             groupsSize + highlightedGroupThickness * 2,
                                                             groupsSize + highlightedGroupThickness * 2))
        self.selectedGroupHighlight.setStyleSheet("background-color: " + highlightedColor + "; border-radius: 25px;")

        # Criação dos símbolos dos grupos na navbar
        # Depende da quantidade de grupos, se tiver até 6 não tem scroll, se tiver mais de 6, tem

        for i in range(len(groups)):
            self.group = QtWidgets.QLabel(self.navBar)
            self.group.setObjectName(groups[i][0])
            self.group.setGeometry(QtCore.QRect(0, 10 + navBarWidth*i, navBarWidth, navBarWidth))
            self.group.setPixmap(QtGui.QPixmap('gui/assets/images/' + groups[i][0] + '.png'))
            bgColor = backgroundColor if i > 0 else highlightedColor
            self.group.setStyleSheet(f"""
                QLabel {{
                    background-color: {bgColor};
                    padding: 15px;  
                }}
                QLabel:hover {{
                    padding: 10px;
                }}
            """)
            self.group.setScaledContents(True)
            self.group.mousePressEvent = lambda event, i=i, group=self.group: self.select_group(group, groups[i][0])
            self.group.show()

            self.groups.append(self.group)

        self.groupsScrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.groupsScrollArea.setObjectName("groupsScrollArea")
        self.style_scroll_bar(self.groupsScrollArea)
        # self.groupsScrollArea.update()
        self.groupsScrollArea.setGeometry(0, 0, navBarWidth, windowHeight)
        self.groupsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.groupsScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.groupsScrollArea.setWidgetResizable(True)
        self.groupsScrollArea.setWidget(self.navBar)

        # Aqui, é apenas setada a altura o scroll deverá cobrir
        required_height_for_gsa = 10 + len(self.groups) * (groupsSize) + 10
        self.navBar.setMinimumSize(navBarWidth, required_height_for_gsa)

        # Aba de configurações/filtros de exibição
        self.configsContainer = QtWidgets.QFrame(self.centralwidget)
        self.configsContainer.setObjectName("configsContainer")
        self.configsContainer.setGeometry(navBarWidth, centralY, configsWidth, configsHeight)
        self.configsContainer.setStyleSheet("#configsContainer { background-color: " + backgroundColor + "; border-right: 1px solid; border-left: 1px solid; border-color: " + contrastColor + "; }")
        self.configsContainer.show()

        self.show_admins = QtWidgets.QCheckBox()
        self.show_admins.setStyleSheet("border: none;")
        self.show_admins.setText("Mostrar admins")
        self.show_admins.setObjectName("show_admins")
        self.show_admins.mousePressEvent = lambda event: self.toggle_show_admins()
        self.show_admins.setChecked(True)
        self.show_admins.show()

        self.admins_first = QtWidgets.QCheckBox()
        self.admins_first.setStyleSheet("border: none;")
        self.admins_first.setText("Admins primeiro")
        self.admins_first.setObjectName("admins_first")
        self.admins_first.mousePressEvent = lambda event: self.toggle_admins_first()
        self.admins_first.setChecked(True)
        self.admins_first.show()

        self.load_group_members('acesso_a_base')  # Carrega as informações de um grupo qualquer 
        self.load_atts('acesso_a_base')
        # TODO : Decidir o grupo inicial (talvez passe a ser aquele mais genérico com os logs de todos os grupos cadastrados)

        self.attsTop = QtWidgets.QWidget(self.centralwidget)
        self.attsTop.setObjectName("attsTop")
        self.attsTop.setGeometry(attsX, attsY, attsWidth, configsHeight)
        self.attsTop.show()

        self.attsLabel = QtWidgets.QLabel("Atividade", self.attsTop)
        self.attsLabel.setObjectName("attsLabel")
        self.current_font.setPointSize(14)
        self.current_font.setBold(True)
        self.attsLabel.setFont(self.current_font)
        self.attsLabel.setFixedSize(115, configsHeight)
        # self.attsLabel.setSizePolicy(sizePolicy)
        self.attsLabel.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.attsLabel.move(10, 0)

        self.refreshButton = QSvgWidget("gui/assets/images/refresh_white.svg", self.attsTop)
        self.refreshButton.setObjectName("refreshButton")
        self.refreshButton.setFixedSize(20, 20)
        self.refreshButton.mousePressEvent = lambda event: self.refresh_screen(self.current_group)
        self.refreshButton.move(attsWidth - 30, int(configsHeight/2 - self.refreshButton.size().height()/2))        # self.refreshButton.mousePressEvent = lambda event: 
        self.refreshButton.show()

        rt_display = str(len(self.current_members)) if len(self.current_members) < 1000 else "999+"
        self.membersSearchWidget = SearchWidget(
            ui=self, 
            parent=self.configsContainer,
            x=15 + self.show_admins.size().width() + 15 + self.admins_first.size().width() + 10,
            y=0,
            width=260,
            height=configsHeight,
            object_name="membersSearchWidget",
            background_color=backgroundColor,
            search_bar_width=130,
            items_type="members",
            results_tracker_text="---",
        )
        self.membersSearchBar = self.membersSearchWidget.findChild(QtWidgets.QLineEdit, "searchBar")
        self.membersSearchBar.textChanged.connect(partial(self.search, "members"))

        rt_display = str(len(self.current_atts)) if len(self.current_atts) < 1000 else "999+"
        self.attsSearchWidget = SearchWidget(
            ui=self,
            parent=self.attsTop,
            x=self.attsLabel.size().width() + 10,
            y=0,
            width=250,
            height=configsHeight,
            object_name="attsSearchWidget",
            background_color=backgroundColor,
            search_bar_width=120,
            items_type="atts",
            results_tracker_text="---",
        )
        self.attsSearchBar = self.attsSearchWidget.findChild(QtWidgets.QLineEdit, "searchBar")
        self.attsSearchBar.textChanged.connect(partial(self.search, "atts"))

        self.membersFilterButton = QSvgWidget("gui/assets/images/filter_white.svg", self.configsContainer)
        self.membersFilterButton.setObjectName("membersFilterButton")
        self.membersFilterButton.setGeometry(
            15 + self.show_admins.size().width() + 15 + self.admins_first.size().width() + 10 + self.membersSearchWidget.size().width() + 10, 
            int(self.configsContainer.size().height()/2 - 10),
            20,
            20)
        self.membersFilterButton.mousePressEvent = lambda event: self.toggle_members_filter()
        self.membersFilterButton.show()

        self.membersFilterContainer = QtWidgets.QFrame(self.centralwidget)
        self.membersFilterContainer.setObjectName("membersFilterContainer")
        self.membersFilterContainer.setStyleSheet("#membersFilterContainer { border-width: 0 0 1px 1px; border-radius: 5px; border-style: solid; border-color: white; } position: fixed;")
        self.membersFilterContainer.setFixedSize(200, 150)
        self.membersFilterContainer.move(navBarWidth + groupMembersWidth - self.membersFilterContainer.size().width(), configsHeight)
        self.membersFilterContainer.hide()

        self.show_filters_label = QtWidgets.QLabel("Filtros de exibição", self.membersFilterContainer)
        self.show_filters_label.setObjectName("show_filters_label")
        self.show_filters_label.move(15, 10)

        self.search_filter_label = QtWidgets.QLabel("Filtros de pesquisa", self.membersFilterContainer)
        self.search_filter_label.setObjectName("search_filter_label")
        self.search_filter_label.move(15, 10 + (5+self.show_admins.size().height())*3)

        self.members_by_name_filter = QtWidgets.QCheckBox()
        self.members_by_name_filter.setStyleSheet("border: none;")
        self.members_by_name_filter.setText("Nickname")
        self.members_by_name_filter.setObjectName("members_by_name_filter")
        self.members_by_name_filter.mousePressEvent = lambda event: self.toggle_members_by_name_filter()
        self.members_by_name_filter.setChecked(True)
        self.members_by_name_filter.show()

        self.members_by_motto_filter = QtWidgets.QCheckBox()
        self.members_by_motto_filter.setStyleSheet("border: none;")
        self.members_by_motto_filter.setText("Missão")
        self.members_by_motto_filter.setObjectName("members_by_motto_filter")
        self.members_by_motto_filter.mousePressEvent = lambda event: self.toggle_members_by_motto_filter()
        self.members_by_motto_filter.setChecked(False)
        self.members_by_motto_filter.show()

        self.show_admins.setParent(self.membersFilterContainer)
        self.admins_first.setParent(self.membersFilterContainer)
        self.members_by_name_filter.setParent(self.membersFilterContainer)
        self.members_by_motto_filter.setParent(self.membersFilterContainer)

        self.show_admins.move(15 + 10, 10 + (5+self.show_admins.size().height())*1)
        self.admins_first.move(15 + 10 + 10, 10 + (5+self.show_admins.size().height())*2)
        self.members_by_name_filter.move(15 + 10, 10+ (5+self.show_admins.size().height())*4)
        self.members_by_motto_filter.move(15 + 10, 10 + (5+self.show_admins.size().height())*5)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)


    def toggle_members_filter(self):
        if self.membersFilterContainer.isVisible():
            self.membersFilterContainer.hide()
        else:
            self.membersFilterContainer.raise_()
            self.membersFilterContainer.show()

    def eventFilter(self, source, event):
        if hasattr(self, 'membersSearchWidget'):
            membersSearchBar = self.membersSearchWidget.findChild(QtWidgets.QLineEdit, 'searchBar')
        if hasattr(self, 'attsSearchWidget'):
            attsSearchBar = self.attsSearchWidget.findChild(QtWidgets.QLineEdit, 'searchBar')
        if (event.type() == QtCore.QEvent.Type.KeyPress):
            if (event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter):
                if source is membersSearchBar:
                    items_type = "members"
                if source is attsSearchBar:
                    items_type = "atts"

                if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                    self.highlight_selected_result(-1, items_type)
                else:
                    self.highlight_selected_result(1, items_type)

        return False
    
    def search(self, items_type):
        if items_type == "members":
            prompt = self.membersSearchBar.text()
            self.searched_members = match_nicknames(prompt, self.current_members, self.members_filter)
            self.highlight_results(self.searched_members)
            self.searched_highlighted_member_index = 0
            self.highlight_selected_result(0, "members")
            self.membersFilterContainer.raise_()
        if items_type == "atts":
            prompt = self.attsSearchBar.text()
            self.searched_atts = match_nicknames(prompt, self.current_atts, self.atts_filter)
            self.highlight_results(self.searched_atts)
            self.searched_highlighted_att_index = 0
            self.highlight_selected_result(0, "atts")

    # Função burocrática, deixa como tá
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("[DIC] SIENA", "[DIC] SIENA"))

    # Switch entre "Admins primeiro" ligado e desligado
    def toggle_admins_first(self):
        if not self.admins_first.isChecked():
            self.admins_first.setChecked(True)
        else:
            self.admins_first.setChecked(False)
        self.refresh_group_members(self.current_group)

    # Switch entre "Mostrar admins" ligado e desligado
    def toggle_show_admins(self):
        # Esta checkbox também controla a checkbox de "Admins primeiro", já que, se não há admins, ela perde o sentido
        if not self.show_admins.isChecked():
            self.show_admins.setChecked(True)
            self.admins_first.setEnabled(True)
            self.admins_first.setStyleSheet("color: " + fontcolor + "; border: none")  # Cor da fonte normal
        else:
            self.show_admins.setChecked(False)
            self.admins_first.setEnabled(False)
            self.admins_first.setStyleSheet("color: " + disabledColor + "; border: none")  # Cor da fonte desabilitada

        prompt = self.membersSearchBar.text()
        self.refresh_group_members(self.current_group)
        self.membersSearchBar.setText(prompt)

    def toggle_members_by_name_filter(self):
        if not self.members_by_name_filter.isChecked():
            self.members_by_name_filter.setChecked(True)
            if "user_name" not in self.members_filter:
                self.members_filter.append("user_name")
        else:
            self.members_by_name_filter.setChecked(False)
            if "user_name" in self.members_filter:
                self.members_filter.remove("user_name")
        self.search("members")

    def toggle_members_by_motto_filter(self):
        if not self.members_by_motto_filter.isChecked():
            self.members_by_motto_filter.setChecked(True)
            if "motto" not in self.members_filter:
                self.members_filter.append("motto")
        else:
            self.members_by_motto_filter.setChecked(False)
            if "motto" in self.members_filter:
                self.members_filter.remove("motto")
        self.search("members")

    def consult_list(self, group):
        # Consultando lista de membros do grupo
        with groups_members_lock:
            members_data = groups_members.get(group)

        if members_data is not None:
            if not self.show_admins.isChecked():
                members_data = [member for member in members_data if not (member['isAdmin'] == '1')]
                return members_data
            if self.admins_first.isChecked():
                members_data = sorted(members_data, key=lambda x: x['isAdmin'] == '1', reverse=True)
                return members_data

        return members_data

    # Carrega as informações do grupo selecionado (principal função da GUI)
    def load_group_members(self, group):
        self.current_members = []

        members_data = self.consult_list(group)
        if not hasattr(self, 'groupNameLabel'):
            self.groupNameLabel = QtWidgets. QLabel(self.configsContainer)
            self.groupNameLabel.setObjectName("groupNameLabel")
            self.groupNameLabel.setStyleSheet("background-color: red;")
            self.current_font.setPointSize(11)
            self.groupNameLabel.setFont(self.current_font)
            self.groupNameLabel.setFixedSize(260, configsHeight)
            self.groupNameLabel.move(10, int(configsHeight/2 - self.groupNameLabel.size().height()/2))
            self.groupNameLabel.show()

        self.groupNameLabel.setText(groups[find_group_index(self.current_group)][3] + "(" + str(len(members_data)) + ")")


        if hasattr(self, 'membersSearchWidget'):
            self.clear_search_bar(self.membersSearchWidget)

        if hasattr(self, 'groupMembersContainer'):
            for child in self.groupMembersContainer.findChildren(QtWidgets.QFrame, "memberContainer"):
                child.setParent(None)
                child.deleteLater()
        else:
            self.groupMembersContainer = QtWidgets.QWidget(self.centralwidget)
            self.groupMembersContainer.setObjectName("groupMembersContainer")
            self.groupMembersContainer.setGeometry(navBarWidth, configsHeight, groupMembersWidth, groupMembersHeight)
            self.groupMembersContainer.show()
            self.groupMembersContainer.setVisible(True)

        if members_data:
            self.groupMembersContainer.setMinimumSize(groupMembersWidth, len(members_data) * (groupMembersContainerHeight + defaultMargin))

            for i, member in enumerate(members_data):
                self.current_font.setPointSize(14)

                container = QtWidgets.QFrame(self.groupMembersContainer)
                container.setObjectName("memberContainer")
                container.setGeometry(0, 0 + (groupMembersContainerHeight + defaultMargin) * i, groupMembersWidth, 80)
                container.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed))
                container.setStyleSheet("background-color: " + containerColor + ";")
                container.show()

                user_image = QtWidgets.QLabel(container)
                user_image.setGeometry(QtCore.QRect(15, 5, 70, 70))
                user_image.setPixmap(QtGui.QPixmap('gui/assets/images/user_white.png'))
                user_image.setScaledContents(True)
                user_image.setObjectName("userImg" + str(i))
                user_image.show()

                user_name = QtWidgets.QLabel(container)
                user_name.setObjectName("user_name")
                user_name.move(groupMembersWidth // 5, 10)
                user_name.setFont(self.current_font)
                user_name.setText(member['nickname'])
                user_name.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                user_name.show()

                self.current_font.setPointSize(11)
                motto = QtWidgets.QLabel(container)
                motto.setObjectName("motto")
                motto.setGeometry(groupMembersWidth // 5, 40, groupMembersWidth, 30)
                motto.setFont(self.current_font)
                motto.setStyleSheet("color: #c7c7c7;")
                motto.setText(member['missao'])
                motto.show()

                if member['isAdmin'] == '1':
                    adm_crown_img = QtWidgets.QLabel(container)
                    adm_crown_img.setGeometry(QtCore.QRect(groupMembersWidth // 5 + user_name.size().width() + 10, 12, 20, 20))
                    adm_crown_img.setPixmap(QtGui.QPixmap('gui/assets/images/adm.png'))
                    adm_crown_img.setScaledContents(True)
                    adm_crown_img.setObjectName("admImg" + str(i))
                    adm_crown_img.show()

                self.current_members.append(container)

        if not hasattr(self, 'membersScrollArea'):
            self.membersScrollArea = QtWidgets.QScrollArea(self.centralwidget)
            self.membersScrollArea.setObjectName("membersScrollArea")
            self.style_scroll_bar(self.membersScrollArea)
            self.membersScrollArea.setGeometry(navBarWidth, configsHeight, groupMembersWidth, groupMembersHeight)
            self.membersScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.membersScrollArea.setWidgetResizable(True)
            self.membersScrollArea.setWidget(self.groupMembersContainer)
        else:
            self.membersScrollArea.setWidget(self.groupMembersContainer)
            self.membersScrollArea.show()

        self.membersScrollArea.update()
        self.membersScrollArea.viewport().update()
        if hasattr(self, "membersFilterContainer"):
            self.membersFilterContainer.raise_()

        return True if members_data else False
            
    # Atualiza a lista de membros
    def refresh_group_members(self, group):
        render = self.load_group_members(group)
        if render:
            self.groupMembersContainer.show()
            self.membersScrollArea.show()

    # Move o marcador para o grupo selecionado
    def select_group(self, widget, group):
        for w in self.groups:
            w.setStyleSheet("background-color: " + backgroundColor + "; padding: 15px;")
        self.selectedGroupHighlight.move(groupsX - 8, windowHeight // 20 + ((windowHeight // 30 + groupsSize) * self.groups.index(widget)) - 8)
        widget.setStyleSheet("background-color: #7a7a7a; padding: 15px;")
        self.current_group = group
        self.refresh_group_members(group)
        self.refresh_atts(group)

    def load_atts(self, group):
        self.current_atts = []

        atts_data = groups_atts[group]
        
        if hasattr(self, 'attsSearchWidget'):
            self.clear_search_bar(self.attsSearchWidget)

        if not hasattr(self, "attsContainer"):
            self.attsContainer = QtWidgets.QWidget(self.centralwidget)
            self.attsContainer.setObjectName("attsContainer")
            self.attsContainer.setGeometry(attsX, attsY + configsHeight, attsWidth, attsHeight)
            self.attsContainer.show()
            self.attsContainer.setVisible(True)
        else:
            for child in self.attsContainer.findChildren(QtWidgets.QFrame, "attContainer"):
                child.setParent(None)
                child.deleteLater()

        if atts_data:

            # Área em que será possível rolar a tela para baixo (equivalente à área das atts)
            self.attsScrollArea = QtWidgets.QScrollArea(self.centralwidget)
            self.attsScrollArea.setObjectName("attsScrollArea")
            self.attsScrollArea.setGeometry(attsX, attsY + configsHeight, attsWidth, attsHeight)
            self.style_scroll_bar(self.attsScrollArea)
            self.attsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.attsScrollArea.setWidgetResizable(True)
            self.attsScrollArea.setWidget(self.attsContainer)

            required_height_for_asa = len(atts_data) * (attContainerHeight + defaultMargin)
            self.attsContainer.setMinimumSize(attsWidth, required_height_for_asa)

            for i, att in enumerate(atts_data):

                # Container dos dados
                container = QtWidgets.QFrame(self.attsContainer)
                container.setObjectName("attContainer")
                container.setGeometry(0, 0 + (attContainerHeight + defaultMargin) * i, attContainerWidth, attContainerHeight)  # Set geometry to fill the container
                container.setStyleSheet("background-color: " + containerColor + ";")
                container.show()

                self.current_font.setPointSize(11)
                att_img_path = "gui/assets/images/joined_green.svg" if att['missao'] == 'entrou' else "gui/assets/images/left_red.svg"
                attImg = QSvgWidget(att_img_path, container)
                attImg.setObjectName("attImg")
                attImg.setFixedSize(45, 45)
                attImg.move(attsWidth // 20, 15)
                attImg.show()
                # Espaço destinado ao nome do membro
                att_nickname = att['nickname']
                att_action = 'entrou' if att['missao'] == 'entrou' else 'saiu'
                attName = QtWidgets.QLabel(container)
                attName.setTextFormat(Qt.TextFormat.RichText)
                attName.setObjectName("attName")
                attName.setFont(self.current_font)
                attName.setText(f'<b>{att_nickname}</b>') # {att_action}')
                attName.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                attName.move(attsWidth // 20 + 45 + 20, int(15 + (45)/2 - attName.size().height()/2))
                attName.show()

                attAction = QtWidgets.QLabel(container)
                attAction.setObjectName("attAction")
                attAction.setFont(self.current_font)
                attAction.setText(att_action)
                attAction.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                attAction.move(attsWidth // 20 + 45 + 20 + attName.size().width() + 5, int(15 + (45)/2 - attAction.size().height()/2))
                attAction.show()

                # group_index = find_group_index(group)
                # att_group_display_name = groups[group_index][2]
                # groupLabel = QtWidgets.QLabel(container)
                # groupLabel.setTextFormat(Qt.TextFormat.RichText)
                # groupLabel.setObjectName("groupLabel")
                # groupLabel.move(attsWidth // 20, 10 + attLabel.size().height() + 5)
                # groupLabel.setFont(self.current_font)
                # groupLabel.setText(f'<b><font color="{groups[group_index][1]}">{att_group_display_name}</font></b>')
                # groupLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                # groupLabel.show()
                
                # Data da att
                self.current_font.setPointSize(11)
                datetimeLabel = QtWidgets.QLabel(container)
                datetimeLabel.setGeometry(attsWidth // 20, attContainerHeight - 30, attsWidth, 30)
                datetimeLabel.setFont(self.current_font)
                datetimeLabel.setStyleSheet("color: #c7c7c7;")
                day = att['isAdmin'][:2]
                month = date_displays[int(att['isAdmin'][3:5]) - 1]
                year = att['isAdmin'][6:10]
                time = att['isAdmin'][13:]
                datetimeLabel.setText(f'{day} {month} {year} - {time}')
                datetimeLabel.show()

                self.current_atts.append(container)
                
            return True
        return False

    def refresh_atts(self, group):
        render = self.load_atts(group)
        if render:
            self.attsContainer.show()
            self.attsScrollArea.show()

    def highlight_results(self, results):
        for result in results:
            result.setStyleSheet("background-color: " + searchHighlightedColor + ";")

    def highlight_selected_result(self, step, search_type):
        if search_type == "members":
            scroll_area = self.membersScrollArea
            container = self.configsContainer
            current_items = self.current_members
            searched_items = self.searched_members
            searched_highlighted_index = self.searched_highlighted_member_index
            container_height = groupMembersContainerHeight

        if search_type == "atts":
            scroll_area = self.attsScrollArea
            container = self.attsTop
            current_items = self.current_atts
            searched_items = self.searched_atts
            searched_highlighted_index = self.searched_highlighted_att_index
            container_height = attContainerHeight

        results_tracker = container.findChild(QtWidgets.QLabel, "resultsTracker")
        next_button = container.findChild(QSvgWidget, "nextButton")
        back_button = container.findChild(QSvgWidget, "backButton")

        if searched_items != []:
            if searched_highlighted_index + step == len(searched_items):
                new_shi = 0
            elif searched_highlighted_index + step < 0:
                new_shi = len(searched_items) - 1
            else:
                new_shi = searched_highlighted_index + step

            searched_items[searched_highlighted_index].setStyleSheet("background-color: " + searchHighlightedColor + ";")
            searched_items[new_shi].setStyleSheet("background-color: " + searchSelectedHighlightedColor + ";")

            index_in_items = current_items.index(searched_items[new_shi])
            container_required_height = container_height + defaultMargin
            y_position = index_in_items * container_required_height

            scroll_area.verticalScrollBar().setValue(y_position)
            scroll_area.update()
            scroll_area.viewport().update()

            if search_type == "members":
                self.searched_highlighted_member_index = new_shi
            elif search_type == "atts":
                self.searched_highlighted_att_index = new_shi
            
            searched_highlighted_index = new_shi

            results_tracker.setStyleSheet("color: " + fontcolor + ";")
            
            displayed_length = str(len(searched_items)) if len(searched_items) < 1000 else "999+"

            results_tracker.setText(str(searched_highlighted_index + 1) + " de " + displayed_length)
            next_button.load('gui/assets/images/down_arrow_white.svg')
            back_button.load('gui/assets/images/up_arrow_white.svg')
        else:
            displayed_length = str(len(current_items)) if len(current_items) < 1000 else "999+"
            # results_tracker.setStyleSheet("color: #d96868;")
            results_tracker.setText("---")
            next_button.load('gui/assets/images/down_arrow_disabled.svg')
            back_button.load('gui/assets/images/up_arrow_disabled.svg')

    def style_scroll_bar(self, scroll_bar):
        scroll_bar.setStyleSheet("""
    QScrollBar:vertical {
        border: none;
        background: #f0f0f0;
        width: 10px;
    }
    QScrollBar::handle:vertical {
        background: #c0c0c0; 
        min-height: 20px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        background: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
""")
        
    def clear_search_bar(self, widget):
        results_tracker = widget.findChild(QtWidgets.QLabel, "resultsTracker")
        next_button = widget.findChild(QSvgWidget, "nextButton")
        back_button = widget.findChild(QSvgWidget, "backButton")

        widget.findChild(QtWidgets.QLineEdit, "searchBar").setText('')

        results_tracker.setStyleSheet("color: " + fontcolor + ";")
        results_tracker.setText("---")

        next_button.load('gui/assets/images/down_arrow_disabled.svg')
        back_button.load('gui/assets/images/up_arrow_disabled.svg')

    def refresh_screen(self, group):
        self.refresh_group_members(group)
        self.refresh_atts(group)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = GUI_MainWindow()
        self.ui.setupUi(self)
    
def match_nicknames(prompt, lst, attributes):
    results = []
    for container in lst:
        flag = 0
        if attributes:
            for attr in attributes:
                if prompt != '' and prompt.lower() in container.findChild(QtWidgets.QWidget, attr).text().lower():
                    flag = 1
                    results.append(container)
                    break
        if not flag:
            container.setStyleSheet("background-color: " + containerColor + ";")
    return results

'''
############################################################
############################################################
#####        FUNÇÕES DE COMUNICAÇÃO COM A API          #####
############################################################
############################################################
'''

def run_client_thread(window):
        t = threading.Thread(target=run_client, args=(window,))
        t.start()

def update_realtime_list(table, lst, key):
    lst[key] = read_table(table)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    groups_members['acesso_a_base'] = read_table('acesso_a_base')
    groups_atts['acesso_a_base'] = read_table('acesso_a_base_atts')
    # for i in range(4):
    #     commit_changes('acesso_a_base_atts', 'Nick-aleatorio', 'entrou', '21/07/2024 - 12:00:00')
    for i in range(1, len(groups)):
        t_group = threading.Thread(target=update_realtime_list, args=(groups[i][0], groups_members, groups[i][0]))
        t_group.start()
        t_atts = threading.Thread(target=update_realtime_list, args=(groups[i][0] + '_atts', groups_atts, groups[i][0]))
        t_atts.start()
    main_window = MainWindow()
    run_client_thread(main_window)
    main_window.show()
    sys.exit(app.exec())

