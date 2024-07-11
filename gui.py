import json
from PyQt5 import QtCore, QtGui, QtWidgets
import threading
import os
import random


windowSizeX = 1070
windowSizeY = 650


highlightedGroupThickness = 8

groupMembersSizeX = 560
configsSizeX = groupMembersSizeX
configsSizeY = 40
groupMembersSizeY = windowSizeY - configsSizeY

centralX = 0
centralY = 0

groupMembersContainerSizeY = 80
groupMembersContainerMargin = 15
fontcolor = "#FFFFFF"
backgroundColor = "#2e2e2e"
highlightedColor = "#7a7a7a"
containerColor = "#474747"
contrastColor = "#cfcfcf"
disabledColor = "#919191"
groups = [item for item in os.listdir('api/logs')]

class GUI_MainWindow():
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(windowSizeX, windowSizeY)
        MainWindow.setFixedSize(windowSizeX, windowSizeY)
        MainWindow.setWindowIcon(QtGui.QIcon('assets/images/CORE.png'))
        MainWindow.setStyleSheet("background-color:" + backgroundColor + ";")

        # Este widget basicamente é o widget-pai. Ele serve para ser parent de todos os principais containers
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("color: " + fontcolor + ";")


        # Grupos na barra de navegação
        self.groups = []
        self.groupsSize = windowSizeX//10 - 30
        self.groupsX = (self.groupsSize//2 - self.groupsSize//4) - 3

        self.current_group = 'acesso_a_base'

        self.navBarSize = windowSizeX// 10 if len(groups) <= 6 else 0 # TODO : Alterar para valor correto

        # Barra de navegação entre grupos
        self.navBar = QtWidgets.QFrame(self.centralwidget)
        self.navBar.setObjectName("navBar")
        self.navBar.setGeometry(QtCore.QRect(centralX, centralY, windowSizeX//10, windowSizeY))
        self.navBar.setStyleSheet("background-color:" + backgroundColor + ";")

        # Linha que separa a navBar do conteúdo dos grupos [UNICAMENTE COSMÉTICA]
        self.lineNavContent = QtWidgets.QFrame(self.centralwidget)
        self.lineNavContent.setGeometry(QtCore.QRect(windowSizeX//10, centralY, 5, windowSizeY))
        self.lineNavContent.setStyleSheet("QFrame { background-color: red; }")
        self.lineNavContent.setFrameShape(QtWidgets.QFrame.VLine)
        self.lineNavContent.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.lineNavContent.setObjectName("line")
        
        # Marcador de qual grupo está selecionado para visualização
        self.selectedGroupHighlight = QtWidgets.QFrame(self.centralwidget)
        self.selectedGroupHighlight.setObjectName("selectedGroupHighlight")
        self.selectedGroupHighlight.setGeometry(QtCore.QRect(self.groupsX - highlightedGroupThickness,
                                                             windowSizeY//20 - highlightedGroupThickness,
                                                             self.groupsSize + highlightedGroupThickness*2,
                                                             self.groupsSize + highlightedGroupThickness*2))
        self.selectedGroupHighlight.setStyleSheet("background-color: " + highlightedColor + "; border-radius: 25px;")

        # Criação dos símbolos dos grupos na navbar
        # Depende da quantidade de grupos, se tiver até 6 não tem scroll, se tiver mais de 6, tem
        if len(groups) <= 6:
            self.navBarSize = windowSizeX//10
            for i in range(len(groups)):
                self.group = QtWidgets.QLabel(self.centralwidget)
                self.group.setObjectName(groups[i])
                self.group.setGeometry(QtCore.QRect(self.groupsX, windowSizeY//20 + ((windowSizeY//30+self.groupsSize)*i), self.groupsSize, self.groupsSize))
                self.group.setText(groups[i]) # Este comando pode ser útil no futuro
                self.group.setPixmap(QtGui.QPixmap('assets/images/' + groups[i] + '.png'))
                bgColor = backgroundColor if i > 0 else highlightedColor
                self.group.setStyleSheet("background-color: " + bgColor + ";")
                self.group.setScaledContents(True)
                self.group.mousePressEvent = lambda event, i=i, group=self.group: self.select_group(group, groups[i])
                self.group.show()

                self.groups.append(self.group)
        else:
            self.navBarSize = 0 # Algum outro valor com base no tamanho do scroll
            pass
            # TODO : Implementar o caso em que há mais de 6 grupos

        # Aba de configurações/filtros de exibição
        self.configsContainer = QtWidgets.QFrame(self.centralwidget)
        self.configsContainer.setObjectName("configsContainer")
        self.configsContainer.setGeometry(self.navBarSize, centralY, configsSizeX, configsSizeY)
        self.configsContainer.setStyleSheet("background-color: " + backgroundColor + "; border-right: 1px solid; border-color: " + contrastColor + ";")
        self.configsContainer.show()

        self.admins_first = QtWidgets.QCheckBox(self.configsContainer)
        sizePolicy = QtWidgets.QSizePolicy(
                                        QtWidgets.QSizePolicy.Preferred,
                                        self.admins_first.sizePolicy().verticalPolicy()
                                        ) # Com esse comando, agora esse QLabel só tem a width necessária para o texto
        self.admins_first.setSizePolicy(sizePolicy)
        self.admins_first.setGeometry(configsSizeX//4 - self.admins_first.size().width()//2, 0, configsSizeX//2, configsSizeY)
        self.admins_first.setStyleSheet("border: none;")
        self.admins_first.setText("Admins primeiro")
        self.admins_first.setObjectName("admins_first")
        self.admins_first.mousePressEvent = lambda event: self.toggle_admins_first()
        self.admins_first.show()

        self.show_admins = QtWidgets.QCheckBox(self.configsContainer)
        sizePolicy = QtWidgets.QSizePolicy(
                        QtWidgets.QSizePolicy.Preferred,
                        self.show_admins.sizePolicy().verticalPolicy()
                        ) # Com esse comando, agora esse QLabel só tem a width necessária para o texto
        self.show_admins.setSizePolicy(sizePolicy)
        self.show_admins.setGeometry(configsSizeX//4 - self.show_admins.size().width()//2 + configsSizeX//2, 0, configsSizeX//2, configsSizeY)
        self.show_admins.setStyleSheet("border: none;")
        self.show_admins.setText("Mostrar admins")
        self.show_admins.setObjectName("show_admins")
        self.show_admins.mousePressEvent = lambda event: self.toggle_show_admins()
        self.show_admins.setChecked(True)
        self.show_admins.show()


        self.load_group_members('acesso_a_base') # Carrega as informações de um grupo qualquer 
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
            self.admins_first.setStyleSheet("color: " + fontcolor + "; border: none") # Cor da fonte normal

        else:
            self.show_admins.setChecked(False)
            self.admins_first.setEnabled(False)
            self.admins_first.setStyleSheet("color: " + disabledColor + "; border: none") # Cor da fonte desabilitada

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
        self.groupMembersContainer.setGeometry(self.navBarSize, configsSizeY, groupMembersSizeX, groupMembersSizeY)
        self.groupMembersContainer.show()
        self.groupMembersContainer.setVisible(True)

        # Área em que será possível rolar a tela para baixo (equivalente à área dos membros)
        self.membersScrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.membersScrollArea.setObjectName("membersScrollArea")
        self.membersScrollArea.setStyleSheet("background-color: " + backgroundColor + "; border-top: none;")
        self.membersScrollArea.setGeometry(self.navBarSize, configsSizeY, groupMembersSizeX, groupMembersSizeY)
        self.membersScrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.membersScrollArea.setWidgetResizable(True)
        self.membersScrollArea.setWidget(self.groupMembersContainer)

        # Aqui, é apenas setada a altura o scroll deverá cobrir
        required_height_for_msa = len(members_data) * (groupMembersContainerSizeY + groupMembersContainerMargin)
        self.groupMembersContainer.setMinimumSize(groupMembersSizeX, required_height_for_msa)

        font = QtGui.QFont()

        # Criando e populando os containers cada um com informações de cada membro do grupo
        for i, member in enumerate(members_data):
            font.setPointSize(14)

            # Container dos dados
            self.container = QtWidgets.QFrame(self.groupMembersContainer)
            self.container.setGeometry(0, 0 + (groupMembersContainerSizeY+groupMembersContainerMargin)*i, groupMembersSizeX, 80)  # Set geometry to fill the container
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
            self.user_name.move(groupMembersSizeX//5, 10)
            sizePolicy = QtWidgets.QSizePolicy(
                                        QtWidgets.QSizePolicy.Preferred,
                                        self.user_name.sizePolicy().verticalPolicy()
                                        ) # Com esse comando, agora esse QLabel só tem a width necessária para o texto
            self.user_name.setSizePolicy(sizePolicy)
            self.user_name.setFont(font)
            self.user_name.setText(member['nickname'])
            self.user_name.show()

            font.setPointSize(11)
            # Missão do membro
            self.motto = QtWidgets.QLabel(self.container)
            self.motto.setGeometry(groupMembersSizeX//5, 40, groupMembersSizeX, 30)
            self.motto.setFont(font)
            self.motto.setStyleSheet("color: #c7c7c7;")
            self.motto.setText(member['mission'])
            self.motto.show()
    
            if member['isAdmin']: # Caso seja adm, é adicionada a coroa ao lado do nome
                pass
                self.adm_crown_img = QtWidgets.QLabel(self.container)
                self.adm_crown_img.setGeometry(QtCore.QRect(groupMembersSizeX//5 + self.user_name.size().width() + 10, 12, 20, 20))
                self.adm_crown_img.setPixmap(QtGui.QPixmap('assets/images/adm.png'))
                self.adm_crown_img.setScaledContents(True)
                self.adm_crown_img.setObjectName("admImg" + str(i))
                self.adm_crown_img.show()
    
    # Move o marcador para o grupo selecionado
    def select_group(self, widget, group):
        for w in self.groups:
            w.setStyleSheet("background-color: " + backgroundColor + ";")
        self.selectedGroupHighlight.move(self.groupsX - 8, windowSizeY//20 + ((windowSizeY//30+self.groupsSize)*self.groups.index(widget)) - 8)
        widget.setStyleSheet("background-color: #7a7a7a;")
        self.current_group = group
        self.refresh_group_members(group)

    # Atualiza a lista de membros
    def refresh_group_members(self, group):
        self.load_group_members(group)
        self.groupMembersContainer.show()
        self.membersScrollArea.show()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = GUI_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())