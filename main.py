from PyQt5 import QtCore, QtGui, QtWidgets
from sly import Lexer, Parser
import os


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

    def parse(self, input, verbose=False):
        self.stack = []
        stack = self.stack
        grammar = self.grammar
        table = self.table
        stack.append('$')
        stack.append(grammar.start)
        input.append('$')
        next = input.pop(0)

        while stack and next:
            if verbose: print(input, 'next :', next)
            tos = stack.pop()
            if verbose: print(stack, 'tos : ', tos)

            if tos in grammar.variables:
                p = table[tos].get(next, None)
                if p == None:
                    return False
                if p != '':
                    stack.extend(p.split(" ")[::-1])
            else:
                if next == tos:
                    if input:
                        next = input.pop(0)

                else:
                    print("String does not belong to the Grammar")
                    return False

        return True
def parse(input:str):

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
    return parser.parse(input.split(" "), verbose=True)
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
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)


        self.status = ""
        self.codeinput.setFontPointSize(10)
        self.compilebtn.clicked.connect(self.compile)
        self.dfabtn.clicked.connect(self.show_dfa)
        self.regexbtn.clicked.connect(self.show_regex)
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
        parser = ParserZ()
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
        tree = parser.parse(lexer.tokenize(data))
        print(tree)
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


if __name__ == "__main__":
    input = 'identifier > identifier or identifier and identifier'
    print(parse(input))

    # import sys
    # app = QtWidgets.QApplication(sys.argv)
    # MainWindow = QtWidgets.QMainWindow()
    # ui = Ui_MainWindow()
    # ui.setupUi(MainWindow)
    # MainWindow.show()
    # sys.exit(app.exec_())