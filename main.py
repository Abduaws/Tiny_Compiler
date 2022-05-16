from PyQt5 import QtCore, QtGui, QtWidgets
from sly import Lexer, Parser
import os
import copy

process = [["Stack"], ["Input"], ["Move"]]

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
class Compiler(Lexer):
    tokens = {NUMBER, ID,
              EQ, LT, LE, GT, GE, NE, OPERATION_AND, OPERATION_OR, OPERATION_NOT, OPEN_BRACKET, CLOSED_BRACKET}
    ignore = ' \t'
    OPEN_BRACKET = r'[(]'
    CLOSED_BRACKET = r'[)]'
    EQ = r'=='
    LE = r'<='
    LT = r'<'
    GE = r'>='
    GT = r'>'
    NE = r'!='
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ignore_comment = r'\#.*'
    OPERATION_AND = r'[&][&]'
    OPERATION_OR = r'[|][|]'
    OPERATION_NOT = r'!'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        raise ValueError('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1
class Grammar():

    def __init__(self, V=None, T=None, S=None, P=None):
        if V:
            self.variables = V
        else:
            self.variables = []

        if S:
            self.start = S
        else:
            self.start = ''

        if T:
            self.terminals = T
        else:
            self.terminals = []

        if P:
            self.productions = P
        else:
            self.productions = {}

    def __str__(self):
        '''Prints out G(V, T, S, P)'''
        s = 'Grammar \n'
        s = s + 'Start Symbol \n' + str(self.start) + '\n'
        s = s + 'Terminals \n' + str(self.terminals) + '\n'
        s = s + 'Variables \n' + str(self.variables) + '\n'
        s = s + 'Productions \n' + str(self.productions) + '\n'
        return s
class Parser:

    def __init__(self, grammar=None, table=None):
        if table:
            self.table = table
        else:
            self.table = {}

        self.grammar = grammar
        self.stack = []

    def set_table(self, table):
        self.table = table

    def set_grammar(self, grammar):
        self.grammar = grammar

    def parse(self, process, input, verbose=False):
        self.stack = []
        stack = self.stack
        grammar = self.grammar
        table = self.table
        stack.append('$')
        stack.append(grammar.start)
        input.append('$')
        next = input.pop(0)

        while stack and next:
            input_copy = copy.deepcopy(input)
            input_copy.insert(0, next)
            process[0].append(copy.deepcopy(stack))
            process[1].append(input_copy)
            if verbose: print(input, 'next :', next)
            tos = stack.pop()
            if verbose: print(stack, 'tos : ', tos)

            if tos in grammar.variables:
                p = table[tos].get(next, None)
                if p == None:
                    return False
                if p != '':
                    process[2].append(f"{tos} -> {p}")
                    stack.extend(p.split(" ")[::-1])
                else:
                    process[2].append(f"{tos} -> ε")
            else:
                if next == tos:
                    if input:
                        process[2].append(f"pop -> {next}")
                        next = input.pop(0)

                else:
                    print("String does not belong to the Grammar")
                    return False

        return True
def parse(process, input:str):
    rules = "exp : term exp`\n" \
            "exp` : or term |\n" \
            "term : factor term`\n" \
            "term` : and factor |\n" \
            "factor : operand factor`\n" \
            "factor` : comop operand |\n" \
            "comop : > | = | <\n" \
            "operand : ! operand | identifier"
    variables = ['exp', 'exp`', 'term', 'term`', 'factor', 'factor`', 'comop', 'operand']
    terminals = ['or', '', 'and', '>', '=', '<', '!', 'identifier']
    productions = {'exp': ['term exp`'],
                   'exp`': ['or term', ''],
                   'term': ['factor term`', ''],
                   'term`': ['and factor'],
                   'factor': ['operand factor`'],
                   'factor`': ['comop operand', ''],
                   'comop': ['>', '=', '<'],
                   'operand': ['! operand', 'identifier']}
    start_var = "exp"
    first = {'or': ['or'],
             '': [''],
             'and': ['and'],
             '>': ['>'],
             '=': ['='],
             '<': ['<'],
             '!': ['!'],
             'identifier': ['identifier'],
             'exp': ['identifier', '!'],
             'term': ['identifier', '!'],
             'factor': ['identifier', '!'],
             'operand': ['identifier', '!'],
             'exp`': ['', 'or'],
             'term`': ['', 'and'],
             'factor`': ['<', '>', '', '='],
             'comop': ['<', '>', '=']}
    follow = {'exp': ['$'],
              'exp`': ['$'],
              'term': ['$', 'or'],
              'term`': ['$', 'or'],
              'factor': ['$', 'and', 'or'],
              'factor`': ['$', 'and', 'or'],
              'comop': ['identifier', '!'],
              'operand': ['and', '=', '<', '>', '$', 'or']}
    parsing_table = {'exp': {'identifier': 'term exp`', '!': 'term exp`'},
                     'exp`': {'or': 'or term', '$': ''},
                     'term': {'identifier': 'factor term`', '!': 'factor term`'},
                     'term`': {'and': 'and factor', '$': '', 'or': ''},
                     'factor': {'identifier': 'operand factor`', '!': 'operand factor`'},
                     'factor`': {'<': 'comop operand', '>': 'comop operand', '=': 'comop operand', '$': '', 'and': '',
                                 'or': ''},
                     'comop': {'>': '>', '=': '=', '<': '<'}, 'operand': {'!': '! operand', 'identifier': 'identifier'}}
    grammer = Grammar(variables, terminals, start_var, productions)
    parser = Parser(grammer)
    parser.set_table(parsing_table)
    return parser.parse(process, input.split(" "), verbose=False)
class dfaprev(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DFA Preview")
        self.image_lbl = QtWidgets.QLabel()
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.image_lbl)
        self.image_lbl.setPixmap(QtGui.QPixmap(resource_path("ourdfa2.jpg")))


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Tiny Language Compiler")
        MainWindow.resize(1123, 600)
        MainWindow.setFixedSize(1123, 600)
        MainWindow.setWindowIcon(QtGui.QIcon(resource_path("icon.png")))
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.setInterval(400)
        self.timer.timeout.connect(self.update_status)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tokentable = QtWidgets.QTableWidget(self.centralwidget)
        self.tokentable.setGeometry(QtCore.QRect(460, 41, 651, 491))
        self.tokentable.setObjectName("tokentable")
        self.tokentable.setColumnCount(5)
        self.tokentable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Token Type")
        self.tokentable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Token Value")
        self.tokentable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Token LineNo")
        self.tokentable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Token Index")
        self.tokentable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Current State")
        self.tokentable.setHorizontalHeaderItem(4, item)
        self.codeinput = QtWidgets.QTextEdit(self.centralwidget)
        self.codeinput.setGeometry(QtCore.QRect(10, 40, 441, 411))
        self.codeinput.setObjectName("codeinput")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 0, 191, 41))
        self.codeinput.setFontPointSize(10)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setPointSizeF(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(60, 480, 306, 80))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.compilebtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.compilebtn.setObjectName("compilebtn")
        self.verticalLayout.addWidget(self.compilebtn)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.regexbtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.regexbtn.setObjectName("regexbtn")
        self.horizontalLayout.addWidget(self.regexbtn)
        self.dfabtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.dfabtn.setObjectName("dfabtn")
        self.horizontalLayout.addWidget(self.dfabtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(460, 0, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(470, 530, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.parsetable = QtWidgets.QTableWidget(self.centralwidget)
        self.parsetable.setGeometry(QtCore.QRect(10, 39, 1101, 481))
        self.parsetable.setShowGrid(True)
        self.parsetable.setWordWrap(True)
        self.parsetable.setCornerButtonEnabled(True)
        self.parsetable.setObjectName("parsetable")
        self.parsetable.setColumnCount(3)
        self.parsetable.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.parsetable.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.parsetable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.parsetable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.parsetable.setHorizontalHeaderItem(2, item)
        self.parsetable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.parseinput = QtWidgets.QLineEdit(self.centralwidget)
        self.parseinput.setGeometry(QtCore.QRect(20, 530, 481, 31))
        self.parseinput.setText("")
        self.parseinput.setObjectName("parseinput")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(510, 529, 591, 31))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.parsebtn = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.parsebtn.setObjectName("parsebtn")
        self.horizontalLayout_2.addWidget(self.parsebtn)
        self.astbtn = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.astbtn.setObjectName("astbtn")
        self.horizontalLayout_2.addWidget(self.astbtn)
        self.parsetreebtn = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.parsetreebtn.setObjectName("parsetreebtn")
        self.horizontalLayout_2.addWidget(self.parsetreebtn)
        self.parselabel = QtWidgets.QLabel(self.centralwidget)
        self.parselabel.setGeometry(QtCore.QRect(470, 0, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.parselabel.setFont(font)
        self.parselabel.setObjectName("parselabel")
        self.backbtn = QtWidgets.QPushButton(self.centralwidget)
        self.backbtn.setGeometry(QtCore.QRect(990, 10, 93, 21))
        self.backbtn.setObjectName("backbtn")
        self.maincompilebtn = QtWidgets.QPushButton(self.centralwidget)
        self.maincompilebtn.setGeometry(QtCore.QRect(340, 290, 191, 131))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.maincompilebtn.setFont(font)
        self.maincompilebtn.setObjectName("maincompilebtn")
        self.mainparsebtn = QtWidgets.QPushButton(self.centralwidget)
        self.mainparsebtn.setGeometry(QtCore.QRect(570, 290, 191, 131))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.mainparsebtn.setFont(font)
        self.mainparsebtn.setObjectName("mainparsebtn")
        self.mainlabel = QtWidgets.QLabel(self.centralwidget)
        self.mainlabel.setGeometry(QtCore.QRect(170, 130, 821, 121))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.mainlabel.setFont(font)
        self.mainlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.mainlabel.setObjectName("mainlabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)


        if True:
            self.codeinput.setDisabled(True)
            self.label.setDisabled(True)
            self.label_3.setDisabled(True)
            self.label_2.setDisabled(True)
            self.tokentable.setDisabled(True)
            self.dfabtn.setDisabled(True)
            self.regexbtn.setDisabled(True)
            self.compilebtn.setDisabled(True)
            self.codeinput.setHidden(True)
            self.label.setHidden(True)
            self.label_3.setHidden(True)
            self.label_2.setHidden(True)
            self.tokentable.setHidden(True)
            self.dfabtn.setHidden(True)
            self.regexbtn.setHidden(True)
            self.compilebtn.setHidden(True)
            self.astbtn.setDisabled(True)
            self.parsebtn.setDisabled(True)
            self.parsetreebtn.setDisabled(True)
            self.parseinput.setDisabled(True)
            self.parselabel.setDisabled(True)
            self.parsetable.setDisabled(True)
            self.astbtn.setHidden(True)
            self.parsebtn.setHidden(True)
            self.parsetreebtn.setHidden(True)
            self.parseinput.setHidden(True)
            self.parselabel.setHidden(True)
            self.parsetable.setHidden(True)
            self.backbtn.setDisabled(True)
            self.backbtn.setHidden(True)


        self.process = [["Stack"], ["Input"], ["Move"]]
        self.status = ""
        self.codeinput.setFontPointSize(10)
        self.compilebtn.clicked.connect(self.compile)
        self.dfabtn.clicked.connect(self.show_dfa)
        self.regexbtn.clicked.connect(self.show_regex)
        self.mainparsebtn.clicked.connect(self.mainparse_click)
        self.maincompilebtn.clicked.connect(self.maincompile_click)
        self.backbtn.clicked.connect(self.backbtn_click)
        self.parsebtn.clicked.connect(self.parse)
        self.timer.start()
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Tiny Language Compiler"))
        self.codeinput.setPlaceholderText(_translate("MainWindow", "Please Enter Code Here!"))

        self.label.setText(_translate("MainWindow", "Insert Code: "))
        self.compilebtn.setText(_translate("MainWindow", "Compile"))
        self.regexbtn.setText(_translate("MainWindow", "Show Regular Expressions"))
        self.dfabtn.setText(_translate("MainWindow", "Preview Compiler DFA"))
        self.label_2.setText(_translate("MainWindow", "Token List:"))
        self.label_3.setText(_translate("MainWindow", "Status: "))
        item = self.parsetable.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "0"))
        item = self.parsetable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Stack"))
        item = self.parsetable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Input"))
        item = self.parsetable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Move"))
        self.parseinput.setPlaceholderText(_translate("MainWindow", "Enter Code To Parse!"))
        self.parsebtn.setText(_translate("MainWindow", "Parse"))
        self.astbtn.setText(_translate("MainWindow", "Show AST"))
        self.parsetreebtn.setText(_translate("MainWindow", "Show Parse Tree"))
        self.parselabel.setText(_translate("MainWindow", "LL(1) Parser"))
        self.backbtn.setText(_translate("MainWindow", "Back"))
        self.maincompilebtn.setText(_translate("MainWindow", "Compile"))
        self.mainparsebtn.setText(_translate("MainWindow", "Parse"))
        self.mainlabel.setText(_translate("MainWindow", "Welcome To Tiny Language Compiler!"))
    def backbtn_click(self):
        if self.astbtn.isHidden() == False:
            self.astbtn.setDisabled(True)
            self.parsebtn.setDisabled(True)
            self.parsetreebtn.setDisabled(True)
            self.parseinput.setDisabled(True)
            self.parselabel.setDisabled(True)
            self.parsetable.setDisabled(True)
            self.astbtn.setHidden(True)
            self.parsebtn.setHidden(True)
            self.parsetreebtn.setHidden(True)
            self.parseinput.setHidden(True)
            self.parselabel.setHidden(True)
            self.parsetable.setHidden(True)
            self.backbtn.setDisabled(False)
            self.backbtn.setHidden(False)
        else:
            self.codeinput.setDisabled(True)
            self.label.setDisabled(True)
            self.label_3.setDisabled(True)
            self.label_2.setDisabled(True)
            self.tokentable.setDisabled(True)
            self.dfabtn.setDisabled(True)
            self.regexbtn.setDisabled(True)
            self.compilebtn.setDisabled(True)
            self.codeinput.setHidden(True)
            self.label.setHidden(True)
            self.label_3.setHidden(True)
            self.label_2.setHidden(True)
            self.tokentable.setHidden(True)
            self.dfabtn.setHidden(True)
            self.regexbtn.setHidden(True)
            self.compilebtn.setHidden(True)
            self.backbtn.setDisabled(False)
            self.backbtn.setHidden(False)

        self.mainlabel.setDisabled(False)
        self.mainparsebtn.setDisabled(False)
        self.maincompilebtn.setDisabled(False)
        self.mainlabel.setHidden(False)
        self.mainparsebtn.setHidden(False)
        self.maincompilebtn.setHidden(False)
        self.backbtn.setDisabled(True)
        self.backbtn.setHidden(True)
    def maincompile_click(self):
        self.mainlabel.setDisabled(True)
        self.mainparsebtn.setDisabled(True)
        self.maincompilebtn.setDisabled(True)
        self.mainlabel.setHidden(True)
        self.mainparsebtn.setHidden(True)
        self.maincompilebtn.setHidden(True)

        self.codeinput.setDisabled(False)
        self.label.setDisabled(False)
        self.label_3.setDisabled(False)
        self.label_2.setDisabled(False)
        self.tokentable.setDisabled(False)
        self.dfabtn.setDisabled(False)
        self.regexbtn.setDisabled(False)
        self.compilebtn.setDisabled(False)
        self.codeinput.setHidden(False)
        self.label.setHidden(False)
        self.label_3.setHidden(False)
        self.label_2.setHidden(False)
        self.tokentable.setHidden(False)
        self.dfabtn.setHidden(False)
        self.regexbtn.setHidden(False)
        self.compilebtn.setHidden(False)
        self.backbtn.setDisabled(False)
        self.backbtn.setHidden(False)
    def mainparse_click(self):
        self.mainlabel.setDisabled(True)
        self.mainparsebtn.setDisabled(True)
        self.maincompilebtn.setDisabled(True)
        self.mainlabel.setHidden(True)
        self.mainparsebtn.setHidden(True)
        self.maincompilebtn.setHidden(True)

        self.astbtn.setDisabled(False)
        self.parsebtn.setDisabled(False)
        self.parsetreebtn.setDisabled(False)
        self.parseinput.setDisabled(False)
        self.parselabel.setDisabled(False)
        self.parsetable.setDisabled(False)
        self.astbtn.setHidden(False)
        self.parsebtn.setHidden(False)
        self.parsetreebtn.setHidden(False)
        self.parseinput.setHidden(False)
        self.parselabel.setHidden(False)
        self.parsetable.setHidden(False)
        self.backbtn.setDisabled(False)
        self.backbtn.setHidden(False)
    def update_status(self):
        if self.status == "":
            if self.label_3.text() == "Status: ":self.label_3.setText("Status: Waiting")
            else:self.label_3.setText("Status: ")
        else:
            self.label_3.setText(self.status)
            self.timer.stop()
    def show_regex(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("RegExp")
        msg.setWindowIcon(QtGui.QIcon(resource_path("icon.png")))
        msg.setText("Current Regular Expressions: ")
        msg.setIcon(QtWidgets.QMessageBox.Information)
        lexer = Compiler()
        msg.setInformativeText(f"ID RegExp: {lexer.ID}\n"
              f"NUM RegExp: [-|ε][0-9]+\n"
              f"EQUAL TO RegExp: {lexer.EQ}\n"
              f"NOT EQUAL TO RegExp: {lexer.NE}\n"
              f"LESS THAN RegExp: {lexer.LT}\n"
              f"GREATER THAN RegExp: {lexer.GT}\n"
              f"LESS THAN OR EQUAL RegExp: {lexer.LE}\n"
              f"GREATER THAN OR EQUAL RegExp: {lexer.GE}\n"
              f"OR OPERATOR RegExp: {lexer.OPERATION_OR}\n"
              f"AND OPERATOR RegExp: {lexer.OPERATION_AND}\n"
              f"NOT OPERATOR RegExp: {lexer.OPERATION_NOT}\n"
              f"OPEN BRACKET RegExp: {lexer.OPEN_BRACKET}\n"
              f"CLOSED BRACKET RegExp: {lexer.CLOSED_BRACKET}\n"
              f"The Full DFA RegExp: NUMBER|ID|ε|[[[NOT*[NUMBER|ID]]|[NUMBER|ID]][EQ|LE|LT|GE|GT|NE|AND|OR]]*[[NOT*[NUMBER|ID]]|[NUMBER|ID]]|[NOT*[NUMBER|ID]]\n")
        x = msg.exec_()
    def show_dfa(self):
        dialog = dfaprev(MainWindow)
        dialog.show()
    def get_next_state(self, token, current_state):
        if current_state == "START":
            if token == "ID" or token == "NUMBER":
                current_state = "NUMBER_OR_ID"
            elif token == "OPERATION_NOT":
                current_state = "IN_OPERATION"
            else:
                current_state = "FAILED"
        elif current_state == "NUMBER_OR_ID":
            if token == "EQ" or token == "LE" or token == "LT" or token == "GE" or token == "GT" or token == "NE" or token == "OPERATION_AND" or token == "OPERATION_OR":
                current_state = "IN_OPERATION"
            else:
                current_state = "FAILED"
        elif current_state == "IN_OPERATION":
            if token == "ID" or token == "NUMBER":
                current_state = "NUMBER_OR_ID"
            elif token == "OPERATION_NOT":
                current_state = "IN_OPERATION"
            else:
                current_state = "FAILED"
        elif current_state == "FAILED":
            current_state = "FAILED"
        return current_state
    def compile(self):
        lexer = Compiler()
        env = {}
        data = self.codeinput.toPlainText()
        if not data:
            self.status = ""
            self.tokentable.setRowCount(0)
        vwidth = self.tokentable.verticalHeader().width()
        hwidth = self.tokentable.horizontalHeader().length()
        swidth = self.tokentable.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
        fwidth = self.tokentable.frameWidth() * 2
        self.tokentable.setFixedWidth(vwidth + hwidth + swidth + fwidth)
        counter = 1
        current_state = "START"
        try:
            for tok in lexer.tokenize(data):
                self.tokentable.setRowCount(counter)
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(counter))
                self.tokentable.setVerticalHeaderItem(counter - 1, item)
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(tok.type))
                self.tokentable.setItem(counter - 1, 0, item)
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(tok.value))
                self.tokentable.setItem(counter - 1, 1, item)
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(tok.lineno))
                self.tokentable.setItem(counter - 1, 2, item)
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(tok.index))
                self.tokentable.setItem(counter - 1, 3, item)
                item = QtWidgets.QTableWidgetItem()
                if str(tok.type) != "OPEN_BRACKET" and str(tok.type) != "CLOSED_BRACKET":
                    current_state = self.get_next_state(str(tok.type), current_state)
                    item.setText(str(current_state))
                else:
                    item.setText(str(""))
                self.tokentable.setItem(counter - 1, 4, item)
                counter += 1
        except ValueError as e:
            self.tokentable.setRowCount(0)
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Error")
            msg.setWindowIcon(QtGui.QIcon(resource_path("icon.png")))
            msg.setText("Compilation Error: ")
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setInformativeText(str(e))
            x = msg.exec_()
            return
        self.timer.start()
        try:
            if data:
                minus = 2
                while self.tokentable.item(counter-minus, 4).text() == "":
                    minus += 1
                if self.tokentable.item(counter-minus, 4).text() == "NUMBER_OR_ID":
                    self.status = "Status: Parsing Success"
                else:
                    self.status = "Status: Parsing Failed"
        except:
            self.status = "Status: Parsing Failed"
    def parse(self):
        self.parsetable.setRowCount(0)
        self.process = [["Stack"], ["Input"], ["Move"]]
        if self.parseinput.text():
            parse(self.process, input=self.parseinput.text())
            self.parsetable.setRowCount(0)
            self.parsetable.setColumnCount(3)
            self.parsetable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
            item = QtWidgets.QTableWidgetItem()
            item.setText("Stack")
            self.parsetable.setHorizontalHeaderItem(0, item)
            item = QtWidgets.QTableWidgetItem()
            item.setText("Input")
            self.parsetable.setHorizontalHeaderItem(1, item)
            item = QtWidgets.QTableWidgetItem()
            item.setText("Move")
            self.parsetable.setHorizontalHeaderItem(2, item)
            counter = 1
            max_index = 0
            for arr in self.process[0]:
                if len(arr) > len(self.process[0][max_index]): max_index = self.process[0].index(arr)
            try:
                for index in range(1, len(self.process[0])):
                    self.parsetable.setRowCount(counter)
                    item = QtWidgets.QTableWidgetItem()
                    item.setText(str(counter))
                    self.parsetable.setVerticalHeaderItem(counter - 1, item)
                    item = QtWidgets.QTableWidgetItem()
                    item.setText(str(self.process[0][index]))
                    self.parsetable.setItem(counter - 1, 0, item)
                    item = QtWidgets.QTableWidgetItem()
                    item.setText(str(self.process[1][index]))
                    self.parsetable.setItem(counter - 1, 1, item)
                    item = QtWidgets.QTableWidgetItem()
                    item.setText(str(self.process[2][index]))
                    self.parsetable.setItem(counter - 1, 2, item)
                    counter += 1
            except:
                item = QtWidgets.QTableWidgetItem()
                item.setText("Done")
                self.parsetable.setItem(counter - 1, 2, item)
                pass

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())