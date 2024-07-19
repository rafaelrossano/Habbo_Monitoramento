from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
import socket
import threading
import sqlite3
# from api.db_functions import read_table
# from api.config import *
from shared_variables import groups_members, groups_members_lock, groups_atts, groups_atts_lock
from gui_tools import read_table, run_client

groups = [("acesso_a_base", '#ff3333', '[DIC] Acesso à Base ®'),
          ("corpo_executivo", '#ededed', '[DIC] Corpo Executivo ®'),
          ("corpo_executivo_superior", '#cfcfcf', '[DIC] Corpo Executivo Superior ®'),
          ("oficiais", '#fc5b5b', '[DIC] Oficiais ®'),
          ("oficiais_superiores", '#fbc900', '[DIC] Oficiais Superiores ®'),
          ("pracas", '#0acf02', '[DIC] Praças ®'),
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

navBarSize = windowWidth // 10 if len(groups) <= 6 else 0  # TODO : Alterar para valor correto
groupsSize = navBarSize - 30
groupsX = int(navBarSize/2 - groupsSize/2)

attsX = navBarSize + groupMembersWidth
attsY = 0
attsWidth = windowWidth - (navBarSize + groupMembersWidth)
attsHeight = windowHeight - configsHeight

attContainerWidth = attsWidth
attContainerHeight = 100

centralX = 0
centralY = 0

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

class SearchWidget(QtWidgets.QFrame):
    def __init__(self, ui, parent, x, y, width, height, object_name, background_color, search_bar_width, items_type):
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

        searchNavUtilsY = self.size().height()//2 - 10
        self.resultsTracker = QtWidgets.QLabel(self)
        self.resultsTracker.setObjectName("resultsTracker")
        self.resultsTracker.setText("---")
        self.resultsTracker.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.resultsTracker.setFixedSize(60, int(height*0.6))
        self.resultsTracker.move(searchBarSpace + 5, height//2 - self.resultsTracker.size().height()//2)

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

class GUI_MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
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

        self.current_atts = []
        self.searched_atts = []
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
        self.lineNavContent.setFrameShape(QtWidgets.QFrame.VLine)
        self.lineNavContent.setFrameShadow(QtWidgets.QFrame.Sunken)
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
        if len(groups) <= 6:
            navBarSize = windowWidth // 10
            for i in range(len(groups)):
                self.group = QtWidgets.QLabel(self.centralwidget)
                self.group.setObjectName(groups[i][0])
                self.group.setGeometry(QtCore.QRect(groupsX,
                                                    windowHeight // 20 + ((windowHeight // 30 + groupsSize) * i),
                                                    groupsSize,
                                                    groupsSize
                ))
                self.group.setPixmap(QtGui.QPixmap('gui/assets/images/' + groups[i][0] + '.png'))
                bgColor = backgroundColor if i > 0 else highlightedColor
                self.group.setStyleSheet("background-color: " + bgColor + ";")
                self.group.setScaledContents(True)
                self.group.mousePressEvent = lambda event, i=i, group=self.group: self.select_group(group, groups[i][0])
                self.group.show()

                self.groups.append(self.group)
        else:
            navBarSize = 0  # Algum outro valor com base no tamanho do scroll
            pass
            # TODO : Implementar o caso em que há mais de 6 grupos

        # Aba de configurações/filtros de exibição
        self.configsContainer = QtWidgets.QFrame(self.centralwidget)
        self.configsContainer.setObjectName("configsContainer")
        self.configsContainer.setGeometry(navBarSize, centralY, configsWidth, configsHeight)
        self.configsContainer.setStyleSheet("#configsContainer { background-color: " + backgroundColor + "; border-right: 1px solid; border-left: 1px solid; border-color: " + contrastColor + "; }")
        self.configsContainer.show()

        self.show_admins = QtWidgets.QCheckBox(self.configsContainer)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            self.show_admins.sizePolicy().verticalPolicy()
        )  # Com esse comando, agora esse QLabel só tem a width necessária para o texto
        self.show_admins.setSizePolicy(sizePolicy)
        self.show_admins.move(15, configsHeight//2 - 5)
        self.show_admins.setStyleSheet("border: none;")
        self.show_admins.setText("Mostrar admins")
        self.show_admins.setObjectName("show_admins")
        self.show_admins.mousePressEvent = lambda event: self.toggle_show_admins()
        self.show_admins.setChecked(True)
        self.show_admins.show()

        self.admins_first = QtWidgets.QCheckBox(self.configsContainer)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            self.admins_first.sizePolicy().verticalPolicy()
        )  # Com esse comando, agora esse QLabel só tem a width necessária para o texto
        self.admins_first.setSizePolicy(sizePolicy)
        self.admins_first.move(15 + self.show_admins.size().width() + 15, configsHeight // 2 - 5)
        self.admins_first.setStyleSheet("border: none;")
        self.admins_first.setText("Admins primeiro")
        self.admins_first.setObjectName("admins_first")
        self.admins_first.mousePressEvent = lambda event: self.toggle_admins_first()
        self.admins_first.setChecked(True)
        self.admins_first.show()


        # self.membersSearchContainer = QtWidgets.QFrame(self.configsContainer)
        # self.membersSearchContainer.setGeometry(15 + self.show_admins.size().width() + 15 + self.admins_first.size().width() + 10,
        #                                    0,
        #                                    configsWidth - (30 + self.show_admins.size().width() + 15 + self.admins_first.size().width() + 15),
        #                                    configsHeight)
        # self.membersSearchContainer.setObjectName("membersSearchContainer")
        # self.membersSearchContainer.setStyleSheet("#membersSearchContainer { background-color: " + backgroundColor + ";}")
        # self.membersSearchContainer.show()
        # self.membersSearchBar = QtWidgets.QLineEdit(self.membersSearchContainer)
        # self.membersSearchBar.setObjectName("membersSearchBar")
        # self.membersSearchBarWidth = 150
        # self.membersSearchBarSpace = self.membersSearchBarWidth + 10
        # self.membersSearchBar.setGeometry(10, int(configsHeight*0.2), self.membersSearchBarWidth, int(configsHeight*0.6))
        # self.membersSearchBar.setStyleSheet("background-color: #FFFFFF; color: #000000; padding-left: 3px;")
        # self.current_font.setPointSize(12)
        # self.current_font.setBold(False)
        # self.membersSearchBar.setFont(self.current_font)
        # self.membersSearchBar.installEventFilter(self)
        # self.membersSearchBar.setPlaceholderText("buscar...")
        # self.membersSearchBar.show()

        # self.searchNavUtilsY = self.membersSearchContainer.size().height()//2 - 10
        # self.membersResultsTracker = QtWidgets.QLabel(self.membersSearchContainer)
        # self.membersResultsTracker.setText("---")
        # self.membersResultsTracker.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # self.membersResultsTracker.setFixedSize(60, int(configsHeight*0.6))
        # self.membersResultsTracker.move(self.membersSearchBarSpace + 5, configsHeight//2 - self.membersResultsTracker.size().height()//2)
        # self.membersResultsTracker.show()

        
        # self.membersBackButton = QSvgWidget("gui/assets/images/up_arrow_disabled.svg", self.membersSearchContainer)
        # self.membersBackButton.setObjectName("membersBackButton")
        # self.membersBackButton.setGeometry(self.membersSearchBarSpace + 60 + 10, self.searchNavUtilsY, 20, 20)
        # self.membersBackButton.mousePressEvent = lambda event: self.highlight_selected_result(-1)
        # self.membersBackButton.show()

        # self.membersNextButton = QSvgWidget("gui/assets/images/down_arrow_disabled.svg", self.membersSearchContainer)
        # self.membersNextButton.setObjectName("membersNextButton")
        # self.membersNextButton.setGeometry(self.membersSearchBarSpace + 5 + 60 + 5 + 20 + 5, self.searchNavUtilsY, 20, 20)
        # self.membersNextButton.mousePressEvent = lambda event: self.highlight_selected_result(1)
        # self.membersNextButton.show()

        # self.closeCtrlFButton = QSvgWidget("gui/assets/images/close_x_white.svg", self.membersSearchContainer)
        # self.closeCtrlFButton.setObjectName("closeCtrlFButton")
        # self.closeCtrlFButton.setFixedSize(15, 20)
        # self.closeCtrlFButton.move(self.membersSearchBarSpace + 5 + 60 + 10 + (20 + 5)*2,
        #                               configsHeight//2 - self.closeCtrlFButton.size().height()//2
        # )
        # self.closeCtrlFButton.setStyleSheet("background-color: " + backgroundColor + ";")
        # self.closeCtrlFButton.mousePressEvent = lambda event: self.close_search_bar()
        # self.closeCtrlFButton.show()

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
        # self.current_font.setBold(True)
        self.attsLabel.setFont(self.current_font)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Expanding   # Allow vertical expansion
        )
        self.attsLabel.setSizePolicy(sizePolicy)
        self.attsLabel.setAlignment(Qt.AlignVCenter)
        self.attsLabel.move(10, 10)

        self.refreshButton = QSvgWidget("gui/assets/images/refresh_white.svg", self.attsTop)
        self.refreshButton.setObjectName("refreshButton")
        self.refreshButton.setFixedSize(20, 20)
        self.refreshButton.mousePressEvent = lambda event: self.refresh_screen(self.current_group)
        self.refreshButton.move(attsWidth - 30, configsHeight//2 - self.refreshButton.size().height()//2)        # self.refreshButton.mousePressEvent = lambda event: 
        self.refreshButton.show()

        self.membersSearchWidget = SearchWidget(
            ui=self, 
            parent=self.configsContainer,
            x=15 + self.show_admins.size().width() + 15 + self.admins_first.size().width() + 10,
            y=0,
            width=configsWidth - (30 + self.show_admins.size().width() + 15 + self.admins_first.size().width() + 15),
            height=configsHeight,
            object_name="membersSearchWidget",
            background_color=backgroundColor,
            search_bar_width=150,
            items_type="members",
        )
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
        )

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

    def eventFilter(self, source, event):
        membersSearchBar = self.configsContainer.findChild(QtWidgets.QWidget, 'membersSearchWidget').findChild(QtWidgets.QLineEdit, 'searchBar')
        attsSearchWidget = self.attsTop.findChild(QtWidgets.QWidget, 'attsSearchWidget')
        if attsSearchWidget:
            attsSearchBar = attsSearchWidget.findChild(QtWidgets.QLineEdit, 'searchBar')
        if (event.type() == QtCore.QEvent.KeyPress):
            if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
                if source is membersSearchBar:
                    prompt = membersSearchBar.text()
                    self.searched_members = match_nicknames(prompt, self.current_members, "user_name")
                    self.highlight_results(self.searched_members)
                    self.searched_highlighted_member_index = 0
                    self.highlight_selected_result(0, "members")
                if source is attsSearchBar:
                    prompt = attsSearchBar.text()
                    self.searched_atts = match_nicknames(prompt, self.current_atts, "attLabel")
                    self.highlight_results(self.searched_atts)
                    self.searched_highlighted_att_index = 0
                    self.highlight_selected_result(0, "atts")
        return False

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
        # Esta checkbox também controla a checkbox de "Admins primeiro", pois, se não há admins, ela fica desabilitada
        if not self.show_admins.isChecked():
            self.show_admins.setChecked(True)
            self.admins_first.setEnabled(True)
            self.admins_first.setStyleSheet("color: " + fontcolor + "; border: none")  # Cor da fonte normal

        else:
            self.show_admins.setChecked(False)
            self.admins_first.setEnabled(False)
            self.admins_first.setStyleSheet("color: " + disabledColor + "; border: none")  # Cor da fonte desabilitada

        self.refresh_group_members(self.current_group)

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

        if members_data:
            # Um container para os membros do grupo, o nome é bastante intuitivo
            self.groupMembersContainer = QtWidgets.QWidget(self.centralwidget)
            self.groupMembersContainer.setObjectName("groupMembersContainer")
            self.groupMembersContainer.setGeometry(navBarSize, configsHeight, groupMembersWidth, groupMembersHeight)
            self.groupMembersContainer.show()
            self.groupMembersContainer.setVisible(True)

            # Área em que será possível rolar a tela para baixo (equivalente à área dos membros)
            self.membersScrollArea = QtWidgets.QScrollArea(self.centralwidget)
            self.membersScrollArea.setObjectName("membersScrollArea")
            self.membersScrollArea.setStyleSheet("#membersScrollArea { background-color: " + backgroundColor + "; border-top: none; border-right: 1px solid; border-left: 1px solid; border-color: " + contrastColor + "; }")
            self.membersScrollArea.setGeometry(navBarSize, configsHeight, groupMembersWidth, groupMembersHeight)
            self.membersScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.membersScrollArea.setWidgetResizable(True)
            self.membersScrollArea.setWidget(self.groupMembersContainer)

            # Aqui, é apenas setada a altura o scroll deverá cobrir
            required_height_for_msa = len(members_data) * (groupMembersContainerHeight + defaultMargin)
            self.groupMembersContainer.setMinimumSize(groupMembersWidth, required_height_for_msa)


            # Criando e populando os containers cada um com informações de cada membro do grupo
            for i, member in enumerate(members_data):
                self.current_font.setPointSize(14)

                # Container dos dados
                container = QtWidgets.QFrame(self.groupMembersContainer)
                container.setGeometry(0, 0 + (groupMembersContainerHeight + defaultMargin) * i, groupMembersWidth, 80)  # Set geometry to fill the container
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
                container.setSizePolicy(sizePolicy)
                container.setStyleSheet("background-color: " + containerColor + ";")
                container.show()

                # Imagem associada ao usuário (nesse momento está enchendo linguiça)
                user_image = QtWidgets.QLabel(container)
                user_image.setGeometry(QtCore.QRect(15, 5, 70, 70))
                user_image.setPixmap(QtGui.QPixmap('gui/assets/images/user_white.png'))
                user_image.setScaledContents(True)
                user_image.setObjectName("userImg" + str(i))
                user_image.show()

                # Espaço destinado ao nome do membro
                user_name = QtWidgets.QLabel(container)
                user_name.setObjectName("user_name")
                user_name.move(groupMembersWidth // 5, 10)
                user_name.setFont(self.current_font)
                user_name.setText(member['nickname'])
                user_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
                user_name.show()

                self.current_font.setPointSize(11)
                # Missão do membro
                motto = QtWidgets.QLabel(container)
                motto.setGeometry(groupMembersWidth // 5, 40, groupMembersWidth, 30)
                motto.setFont(self.current_font)
                motto.setStyleSheet("color: #c7c7c7;")
                motto.setText(member['missao'])
                motto.show()

                if member['isAdmin'] == '1':  # Caso seja adm, é adicionada a coroa ao lado do nome
                    adm_crown_img = QtWidgets.QLabel(container)
                    adm_crown_img.setGeometry(QtCore.QRect(groupMembersWidth // 5 + user_name.size().width() + 10, 12, 20, 20))
                    adm_crown_img.setPixmap(QtGui.QPixmap('gui/assets/images/adm.png'))
                    adm_crown_img.setScaledContents(True)
                    adm_crown_img.setObjectName("admImg" + str(i))
                    adm_crown_img.show()

                self.current_members.append(container)

            return True
        return False
            
    # Atualiza a lista de membros
    def refresh_group_members(self, group):
        render = self.load_group_members(group)
        if render:
            self.groupMembersContainer.show()
            self.membersScrollArea.show()

    # Move o marcador para o grupo selecionado
    def select_group(self, widget, group):
        for w in self.groups:
            w.setStyleSheet("background-color: " + backgroundColor + ";")
        self.selectedGroupHighlight.move(groupsX - 8, windowHeight // 20 + ((windowHeight // 30 + groupsSize) * self.groups.index(widget)) - 8)
        widget.setStyleSheet("background-color: #7a7a7a;")
        self.current_group = group
        self.refresh_group_members(group)
        self.refresh_atts(group)

    def load_atts(self, group):
        self.current_atts = []
        atts_data = groups_atts['acesso_a_base']

        self.attsContainer = QtWidgets.QWidget(self.centralwidget)
        self.attsContainer.setObjectName("attsContainer")
        self.attsContainer.setGeometry(attsX, attsY + configsHeight, attsWidth, attsHeight)
        self.attsContainer.show()
        self.attsContainer.setVisible(True)

        # Área em que será possível rolar a tela para baixo (equivalente à área das atts)
        self.attsScrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.attsScrollArea.setObjectName("attsScrollArea")
        self.attsScrollArea.setGeometry(attsX, attsY + configsHeight, attsWidth, attsHeight)
        self.attsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.attsScrollArea.setWidgetResizable(True)
        self.attsScrollArea.setWidget(self.attsContainer)

        required_height_for_asa = len(atts_data) * (attContainerHeight + defaultMargin)
        self.attsContainer.setMinimumSize(attsWidth, required_height_for_asa)

        for i, att in enumerate(atts_data):

            # Container dos dados
            container = QtWidgets.QFrame(self.attsContainer)
            container.setGeometry(0, 0 + (attContainerHeight + defaultMargin) * i, attContainerWidth, attContainerHeight)  # Set geometry to fill the container
            # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            # container.setSizePolicy(sizePolicy)
            container.setStyleSheet("background-color: " + containerColor + ";")
            container.show()

            self.current_font.setPointSize(10)
            att_img_path = "gui/assets/images/joined_green.svg" if att['missao'] == 'entrou' else "gui/assets/images/left_red.svg"
            attImg = QSvgWidget(att_img_path, container)
            attImg.setObjectName("attImg")
            attImg.setFixedSize(45, 45)
            attImg.move(attsWidth // 20, 15)
            attImg.show()
            # Espaço destinado ao nome do membro
            att_nickname = att['nickname']
            att_action = 'entrou' if att['missao'] == 'entrou' else 'saiu'
            attLabel = QtWidgets.QLabel(container)
            attLabel.setTextFormat(Qt.RichText)
            attLabel.setObjectName("attLabel")
            attLabel.setFont(self.current_font)
            attLabel.setText(f'<b>{att_nickname}</b> {att_action}')
            attLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
            attLabel.move(attsWidth // 20 + 45 + 20, int(15 + (45)/2 - attLabel.size().height()/2))
            # attLabel.setStyleSheet("background-color: red;")
            attLabel.show()

            # group_index = find_group_index(group)
            # att_group_display_name = groups[group_index][2]
            # groupLabel = QtWidgets.QLabel(container)
            # groupLabel.setTextFormat(Qt.RichText)
            # groupLabel.setObjectName("groupLabel")
            # groupLabel.move(attsWidth // 20, 10 + attLabel.size().height() + 5)
            # groupLabel.setFont(self.current_font)
            # groupLabel.setText(f'<b><font color="{groups[group_index][1]}">{att_group_display_name}</font></b>')
            # groupLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
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

    def refresh_atts(self, group):
        self.load_atts(group)
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

            if search_type == "members":
                self.searched_highlighted_member_index = new_shi
            elif search_type == "atts":
                self.searched_highlighted_att_index = new_shi
            
            searched_highlighted_index = new_shi

            results_tracker.setStyleSheet("color: " + fontcolor + ";")
            results_tracker.setText(str(searched_highlighted_index + 1) + " de " + str(len(searched_items)))
            next_button.load('gui/assets/images/down_arrow_white.svg')
            back_button.load('gui/assets/images/up_arrow_white.svg')
        else:
            results_tracker.setStyleSheet("color: #d96868;")
            results_tracker.setText("0 de 0")
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

    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_F and event.modifiers() == Qt.ControlModifier:
    #         self.handleCtrlF()
    #         event.accept()

    # def handleCtrlF(self):
    #     self.ui.ctrlFContainer = QtWidgets.QFrame(self.ui.configsContainer)
    #     self.ui.ctrlFContainer.setGeometry(15 + self.ui.show_admins.size().width() + 15 + self.ui.admins_first.size().width() + 10,
    #                                        0,
    #                                        configsWidth - (30 + self.ui.show_admins.size().width() + 15 + self.ui.admins_first.size().width() + 15),
    #                                        configsHeight)
    #     self.ui.ctrlFContainer.setObjectName("ctrlFContainer")
    #     self.ui.ctrlFContainer.setStyleSheet("#ctrlFContainer { background-color: " + backgroundColor + ";}")
    #     self.ui.ctrlFContainer.show()
    #     self.ui.searchBar = QtWidgets.QLineEdit(self.ui.ctrlFContainer)
    #     self.ui.searchBarWidth = 150
    #     self.ui.searchBarSpace = self.ui.searchBarWidth + 10
    #     self.ui.searchBar.setGeometry(10, int(configsHeight*0.2), self.ui.searchBarWidth, int(configsHeight*0.6))
    #     self.ui.searchBar.setStyleSheet("background-color: #FFFFFF; color: #000000; padding-left: 3px;")
    #     self.ui.current_font.setPointSize(12)
    #     self.ui.current_font.setBold(False)
    #     self.ui.searchBar.setFont(self.ui.current_font)
    #     self.ui.searchBar.installEventFilter(self)
    #     self.ui.searchBar.show()

    #     self.ui.searchNavUtilsY = self.ui.ctrlFContainer.size().height()//2 - 10
    #     self.ui.resultsTracker = QtWidgets.QLabel(self.ui.ctrlFContainer)
    #     self.ui.resultsTracker.setText("---")
    #     self.ui.resultsTracker.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
    #     self.ui.resultsTracker.setFixedSize(60, int(configsHeight*0.6))
    #     self.ui.resultsTracker.move(self.ui.searchBarSpace + 5, configsHeight//2 - self.ui.resultsTracker.size().height()//2)
    #     self.ui.resultsTracker.show()

        
    #     self.ui.backButton = QSvgWidget("gui/assets/images/up_arrow_disabled.svg", self.ui.ctrlFContainer)
    #     self.ui.backButton.setObjectName("backButton")
    #     self.ui.backButton.setGeometry(self.ui.searchBarSpace + 60 + 10, self.ui.searchNavUtilsY, 20, 20)
    #     self.ui.backButton.mousePressEvent = lambda event: self.ui.highlight_selected_result(-1)
    #     self.ui.backButton.show()

    #     self.ui.nextButton = QSvgWidget("gui/assets/images/down_arrow_disabled.svg", self.ui.ctrlFContainer)
    #     self.ui.nextButton.setObjectName("nextButton")
    #     self.ui.nextButton.setGeometry(self.ui.searchBarSpace + 5 + 60 + 5 + 20 + 5, self.ui.searchNavUtilsY, 20, 20)
    #     self.ui.nextButton.mousePressEvent = lambda event: self.ui.highlight_selected_result(1)
    #     self.ui.nextButton.show()

    #     self.ui.closeCtrlFButton = QSvgWidget("gui/assets/images/close_x_white.svg", self.ui.ctrlFContainer)
    #     self.ui.closeCtrlFButton.setObjectName("closeCtrlFButton")
    #     self.ui.closeCtrlFButton.setFixedSize(15, 20)
    #     self.ui.closeCtrlFButton.move(self.ui.searchBarSpace + 5 + 60 + 10 + (20 + 5)*2,
    #                                   configsHeight//2 - self.ui.closeCtrlFButton.size().height()//2
    #     )
    #     self.ui.closeCtrlFButton.setStyleSheet("background-color: " + backgroundColor + ";")
    #     self.ui.closeCtrlFButton.mousePressEvent = lambda event: self.ui.close_search_bar()
    #     self.ui.closeCtrlFButton.show()

    #     self.ui.searchBar.setFocus()

    # # def eventFilter(self, source, event):
    # #     if (event.type() == QtCore.QEvent.KeyPress and source is self.ui.searchBar):
    # #         if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
    # #             prompt = self.ui.searchBar.text()
    # #             self.ui.searched_members = match_nicknames(prompt, self.ui.current_members)
    # #             self.ui.highlight_results(self.ui.searched_members)
    # #             self.ui.searched_highlighted_member_index = 0
    # #             self.ui.highlight_selected_result(0)
    # #         if (event.key() == Qt.Key_Escape and source is self.ui.searchBar):
    # #             self.ui.close_search_bar()
    # #     return False

    
def match_nicknames(prompt, lst, attribute):
    results = []
    for container in lst:
        if prompt != '' and prompt.lower() in container.findChild(QtWidgets.QLabel, attribute).text().lower():
            results.append(container)
        else:
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
    for i in range(1, len(groups)):
        t_group = threading.Thread(target=update_realtime_list, args=(groups[i][0], groups_members, groups[i][0]))
        t_group.start()
        t_atts = threading.Thread(target=update_realtime_list, args=(groups[i][0] + '_atts', groups_atts, groups[i][0]))
        t_atts.start()
        # groups_members[group[0]] = read_table(group[0])
        # groups_atts[group[0]] = read_table(group[0] + '_atts')
    main_window = MainWindow()
    run_client_thread(main_window)
    main_window.show()
    sys.exit(app.exec_())
