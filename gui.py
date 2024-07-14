import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
import os

windowWidth = 1070
windowHeight = 650

highlightedGroupThickness = 8

groupMembersWidth = 560
configsWidth = groupMembersWidth
configsHeight = 40
groupMembersHeight = windowHeight - configsHeight

centralX = 0
centralY = 0

groupMembersContainerHeight = 80
groupMembersContainerMargin = 15
fontcolor = "#FFFFFF"
backgroundColor = "#2e2e2e"
highlightedColor = "#7a7a7a"
containerColor = "#474747"
contrastColor = "#cfcfcf"
disabledColor = "#919191"
searchHighlightedColor = "#696969"
searchSelectedHighlightedColor = "#a87b13"
groups = [item for item in os.listdir('api/logs')]

class GUI_MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(windowWidth, windowHeight)
        MainWindow.setFixedSize(windowWidth, windowHeight)
        MainWindow.setWindowIcon(QtGui.QIcon('assets/images/CORE.png'))
        MainWindow.setStyleSheet("background-color:" + backgroundColor + ";")

        # Este widget basicamente é o widget-pai. Ele serve para ser parent de todos os principais containers
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("color: " + fontcolor + ";")

        self.current_members = []
        self.searched_members = []
        # Grupos na barra de navegação
        self.groups = []
        self.groupsSize = windowWidth // 10 - 30
        self.groupsX = (self.groupsSize // 2 - self.groupsSize // 4) - 3

        self.current_group = 'acesso_a_base'

        self.navBarSize = windowWidth // 10 if len(groups) <= 6 else 0  # TODO : Alterar para valor correto

        # Barra de navegação entre grupos
        self.navBar = QtWidgets.QFrame(self.centralwidget)
        self.navBar.setObjectName("navBar")
        self.navBar.setGeometry(QtCore.QRect(centralX, centralY, windowWidth // 10, windowHeight))
        self.navBar.setStyleSheet("background-color:" + backgroundColor + ";")

        # Linha que separa a navBar do conteúdo dos grupos [UNICAMENTE COSMÉTICA]
        self.lineNavContent = QtWidgets.QFrame(self.centralwidget)
        self.lineNavContent.setGeometry(QtCore.QRect(windowWidth // 10, centralY, 5, windowHeight))
        self.lineNavContent.setStyleSheet("QFrame { background-color: red; }")
        self.lineNavContent.setFrameShape(QtWidgets.QFrame.VLine)
        self.lineNavContent.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.lineNavContent.setObjectName("line")

        # Marcador de qual grupo está selecionado para visualização
        self.selectedGroupHighlight = QtWidgets.QFrame(self.centralwidget)
        self.selectedGroupHighlight.setObjectName("selectedGroupHighlight")
        self.selectedGroupHighlight.setGeometry(QtCore.QRect(self.groupsX - highlightedGroupThickness,
                                                             windowHeight // 20 - highlightedGroupThickness,
                                                             self.groupsSize + highlightedGroupThickness * 2,
                                                             self.groupsSize + highlightedGroupThickness * 2))
        self.selectedGroupHighlight.setStyleSheet("background-color: " + highlightedColor + "; border-radius: 25px;")

        # Criação dos símbolos dos grupos na navbar
        # Depende da quantidade de grupos, se tiver até 6 não tem scroll, se tiver mais de 6, tem
        if len(groups) <= 6:
            self.navBarSize = windowWidth // 10
            for i in range(len(groups)):
                self.group = QtWidgets.QLabel(self.centralwidget)
                self.group.setObjectName(groups[i])
                self.group.setGeometry(QtCore.QRect(self.groupsX,
                                                    windowHeight // 20 + ((windowHeight // 30 + self.groupsSize) * i),
                                                    self.groupsSize,
                                                    self.groupsSize
                ))
                self.group.setPixmap(QtGui.QPixmap('assets/images/' + groups[i] + '.png'))
                bgColor = backgroundColor if i > 0 else highlightedColor
                self.group.setStyleSheet("background-color: " + bgColor + ";")
                self.group.setScaledContents(True)
                self.group.mousePressEvent = lambda event, i=i, group=self.group: self.select_group(group, groups[i])
                self.group.show()

                self.groups.append(self.group)
        else:
            self.navBarSize = 0  # Algum outro valor com base no tamanho do scroll
            pass
            # TODO : Implementar o caso em que há mais de 6 grupos

        # Aba de configurações/filtros de exibição
        self.configsContainer = QtWidgets.QFrame(self.centralwidget)
        self.configsContainer.setObjectName("configsContainer")
        self.configsContainer.setGeometry(self.navBarSize, centralY, configsWidth, configsHeight)
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
        self.admins_first.show()

        self.load_group_members('acesso_a_base')  # Carrega as informações de um grupo qualquer 
        # TODO : Decidir o grupo inicial (talvez passe a ser aquele mais genérico com os logs de todos os grupos cadastrados)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

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

    def consult_file(self, group):
        # Consultando arquivo e carregando dados
        with open('api/logs/' + group + '/' + group + '_membros.json', 'r', encoding='utf-8') as file:
            members_data = json.load(file)

        if not self.show_admins.isChecked():
            members_data = [member for member in members_data if not member['isAdmin']]
            return members_data
        if self.admins_first.isChecked():
            members_data = sorted(members_data, key=lambda x: x['isAdmin'], reverse=True)
            return members_data

        return members_data

    # Carrega as informações do grupo selecionado (principal função da GUI)
    def load_group_members(self, group):
        members_data = self.consult_file(group)
        # Um container para os membros do grupo, o nome é bastante intuitivo
        self.groupMembersContainer = QtWidgets.QWidget(self.centralwidget)
        self.groupMembersContainer.setObjectName("groupMembersContainer")
        self.groupMembersContainer.setGeometry(self.navBarSize, configsHeight, groupMembersWidth, groupMembersHeight)
        self.groupMembersContainer.show()
        self.groupMembersContainer.setVisible(True)

        # Área em que será possível rolar a tela para baixo (equivalente à área dos membros)
        self.membersScrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.membersScrollArea.setObjectName("membersScrollArea")
        self.membersScrollArea.setStyleSheet("#membersScrollArea { background-color: " + backgroundColor + "; border-top: none; border-right: 1px solid; border-left: 1px solid; border-color: " + contrastColor + "; }")
        self.membersScrollArea.setGeometry(self.navBarSize, configsHeight, groupMembersWidth, groupMembersHeight)
        self.membersScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.membersScrollArea.setWidgetResizable(True)
        self.membersScrollArea.setWidget(self.groupMembersContainer)

        # Aqui, é apenas setada a altura o scroll deverá cobrir
        required_height_for_msa = len(members_data) * (groupMembersContainerHeight + groupMembersContainerMargin)
        self.groupMembersContainer.setMinimumSize(groupMembersWidth, required_height_for_msa)

        self.current_font = QtGui.QFont()

        # Criando e populando os containers cada um com informações de cada membro do grupo
        for i, member in enumerate(members_data):
            self.current_font.setPointSize(14)

            # Container dos dados
            self.container = QtWidgets.QFrame(self.groupMembersContainer)
            self.container.setGeometry(0, 0 + (groupMembersContainerHeight + groupMembersContainerMargin) * i, groupMembersWidth, 80)  # Set geometry to fill the container
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            self.container.setSizePolicy(sizePolicy)
            self.container.setStyleSheet("background-color: " + containerColor + ";")
            self.container.show()

            # Imagem associada ao usuário (nesse momento está enchendo linguiça)
            self.user_image = QtWidgets.QLabel(self.container)
            self.user_image.setGeometry(QtCore.QRect(15, 5, 70, 70))
            self.user_image.setPixmap(QtGui.QPixmap('assets/images/user_white.png'))
            self.user_image.setScaledContents(True)
            self.user_image.setObjectName("userImg" + str(i))
            self.user_image.show()

            # Espaço destinado ao nome do membro
            self.user_name = QtWidgets.QLabel(self.container)
            self.user_name.setObjectName("user_name")
            self.user_name.move(groupMembersWidth // 5, 10)
            self.user_name.setFont(self.current_font)
            self.user_name.setText(member['nickname'])
            self.user_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.user_name.show()

            self.current_font.setPointSize(11)
            # Missão do membro
            self.motto = QtWidgets.QLabel(self.container)
            self.motto.setGeometry(groupMembersWidth // 5, 40, groupMembersWidth, 30)
            self.motto.setFont(self.current_font)
            self.motto.setStyleSheet("color: #c7c7c7;")
            self.motto.setText(member['mission'])
            self.motto.show()

            if member['isAdmin']:  # Caso seja adm, é adicionada a coroa ao lado do nome
                pass
                self.adm_crown_img = QtWidgets.QLabel(self.container)
                self.adm_crown_img.setGeometry(QtCore.QRect(groupMembersWidth // 5 + self.user_name.size().width() + 10, 12, 20, 20))
                self.adm_crown_img.setPixmap(QtGui.QPixmap('assets/images/adm.png'))
                self.adm_crown_img.setScaledContents(True)
                self.adm_crown_img.setObjectName("admImg" + str(i))
                self.adm_crown_img.show()
            
            self.current_members.append(self.container)

    # Atualiza a lista de membros
    def refresh_group_members(self, group):
        self.load_group_members(group)
        self.groupMembersContainer.show()
        self.membersScrollArea.show()

    # Move o marcador para o grupo selecionado
    def select_group(self, widget, group):
        for w in self.groups:
            w.setStyleSheet("background-color: " + backgroundColor + ";")
        self.selectedGroupHighlight.move(self.groupsX - 8, windowHeight // 20 + ((windowHeight // 30 + self.groupsSize) * self.groups.index(widget)) - 8)
        widget.setStyleSheet("background-color: #7a7a7a;")
        self.current_group = group
        self.refresh_group_members(group)

    def highlight_results(self, results):
        for result in results:
            result.setStyleSheet("background-color: " + searchHighlightedColor + ";")

    def highlight_selected_result(self, step):
        if self.searched_members != []:
            if self.searched_highlighted_member_index + step == len(self.searched_members):
                new_shmi = 0
            elif self.searched_highlighted_member_index + step < 0:
                new_shmi = len(self.searched_members) - 1
            else:
                new_shmi = self.searched_highlighted_member_index + step
            self.searched_members[self.searched_highlighted_member_index].setStyleSheet("background-color: " + searchHighlightedColor + ";")
            self.searched_members[new_shmi].setStyleSheet("background-color: " + searchSelectedHighlightedColor + ";")
            index_in_members = self.current_members.index(self.searched_members[new_shmi])
            container_required_height = groupMembersContainerHeight + groupMembersContainerMargin
            y_position = index_in_members * container_required_height
            self.membersScrollArea.verticalScrollBar().setValue(y_position)
            self.searched_highlighted_member_index = new_shmi

            self.nextButton.load('assets/images/down_arrow_white.svg')
            self.backButton.load('assets/images/up_arrow_white.svg')
            self.resultsTracker.setStyleSheet("color: " + fontcolor + ";")
            self.resultsTracker.setText(str(self.searched_highlighted_member_index + 1) + " de " + str(len(self.searched_members)))
        else:
            self.nextButton.load('assets/images/down_arrow_disabled.svg')
            self.backButton.load('assets/images/up_arrow_disabled.svg')
            self.resultsTracker.setStyleSheet("color: #d96868;")
            self.resultsTracker.setText("0 de 0")

    def close_search_bar(self):
        match_nicknames('', self.current_members)
        self.ctrlFContainer.hide()



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = GUI_MainWindow()
        self.ui.setupUi(self)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F and event.modifiers() == Qt.ControlModifier:
            self.handleCtrlF()
            event.accept()

    def handleCtrlF(self):
        self.ui.ctrlFContainer = QtWidgets.QFrame(self.ui.configsContainer)
        self.ui.ctrlFContainer.setGeometry(15 + self.ui.show_admins.size().width() + 15 + self.ui.admins_first.size().width() + 10,
                                           0,
                                           configsWidth - (30 + self.ui.show_admins.size().width() + 15 + self.ui.admins_first.size().width() + 15),
                                           configsHeight)
        self.ui.ctrlFContainer.setObjectName("ctrlFContainer")
        self.ui.ctrlFContainer.setStyleSheet("#ctrlFContainer { background-color: " + backgroundColor + "; border: 1px solid white}")
        self.ui.ctrlFContainer.show()
        self.ui.searchBar = QtWidgets.QLineEdit(self.ui.ctrlFContainer)
        self.ui.searchBarWidth = 150
        self.ui.searchBarSpace = self.ui.searchBarWidth + 10
        self.ui.searchBar.setGeometry(10, int(configsHeight*0.2), self.ui.searchBarWidth, int(configsHeight*0.6))
        self.ui.searchBar.setStyleSheet("background-color: #FFFFFF; color: #000000; padding-left: 3px;")
        self.ui.current_font.setPointSize(12)
        self.ui.searchBar.setFont(self.ui.current_font)
        self.ui.searchBar.installEventFilter(self)
        self.ui.searchBar.show()

        self.ui.searchNavUtilsY = self.ui.ctrlFContainer.size().height()//2 - 10

        self.ui.resultsTracker = QtWidgets.QLabel(self.ui.ctrlFContainer)
        self.ui.resultsTracker.setText("---")
        self.ui.resultsTracker.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.ui.resultsTracker.setFixedSize(60, int(configsHeight*0.6))
        self.ui.resultsTracker.move(self.ui.searchBarSpace + 5, configsHeight//2 - self.ui.resultsTracker.size().height()//2)
        self.ui.resultsTracker.show()

        
        self.ui.backButton = QSvgWidget("assets/images/up_arrow_disabled.svg", self.ui.ctrlFContainer)
        self.ui.backButton.setObjectName("backButton")
        self.ui.backButton.setGeometry(self.ui.searchBarSpace + 60 + 10, self.ui.searchNavUtilsY, 20, 20)
        self.ui.backButton.setStyleSheet("background-color: " + backgroundColor + ";")
        self.ui.backButton.mousePressEvent = lambda event: self.ui.highlight_selected_result(-1)
        self.ui.backButton.show()

        self.ui.nextButton = QSvgWidget("assets/images/down_arrow_disabled.svg", self.ui.ctrlFContainer)
        self.ui.nextButton.setObjectName("nextButton")
        self.ui.nextButton.setGeometry(self.ui.searchBarSpace + 5 + 60 + 5 + 20 + 5, self.ui.searchNavUtilsY, 20, 20)
        self.ui.nextButton.setStyleSheet("background-color: " + backgroundColor + ";")
        self.ui.nextButton.mousePressEvent = lambda event: self.ui.highlight_selected_result(1)
        self.ui.nextButton.show()

        self.ui.closeCtrlFButton = QSvgWidget("assets/images/close_x_white.svg", self.ui.ctrlFContainer)
        self.ui.closeCtrlFButton.setObjectName("closeCtrlFButton")
        self.ui.closeCtrlFButton.setFixedSize(15, 20)
        self.ui.closeCtrlFButton.move(self.ui.searchBarSpace + 5 + 60 + 10 + (20 + 5)*2,
                                      configsHeight//2 - self.ui.closeCtrlFButton.size().height()//2
        )
        self.ui.closeCtrlFButton.setStyleSheet("background-color: " + backgroundColor + ";")
        self.ui.closeCtrlFButton.mousePressEvent = lambda event: self.ui.close_search_bar()
        self.ui.closeCtrlFButton.show()

        self.ui.searchBar.setFocus()

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and source is self.ui.searchBar):
            if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
                prompt = self.ui.searchBar.text()
                self.ui.searched_members = match_nicknames(prompt, self.ui.current_members)
                self.ui.highlight_results(self.ui.searched_members)
                self.ui.searched_highlighted_member_index = 0
                self.ui.highlight_selected_result(0)
        return False
    
def match_nicknames(prompt, list):
    results = []
    for container in list:
        if prompt != '' and prompt.lower() in container.findChild(QtWidgets.QLabel, "user_name").text().lower():
            results.append(container)
        else:
            container.setStyleSheet("background-color: " + containerColor + ";")
    return results

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
