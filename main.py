from PyQt5 import QtCore, QtGui, QtWidgets
from sly import Lexer, Parser
import os
import copy
import networkx as nx
import matplotlib.pyplot as plt
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
import random


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
    rules = "exp : term exp'\n" \
            "exp' : or term exp' |\n" \
            "term : factor term'\n" \
            "term' : and factor term' |\n" \
            "factor : operand factor'\n" \
            "factor' : comop operand factor' |\n" \
            "comop : > | = | <\n" \
            "operand : ! operand | identifier"
    variables = ['exp', "exp'", 'term', "term'", 'factor', "factor'", 'comop', 'operand']
    terminals = ['or', '', 'and', '>', '=', '<', '!', 'identifier']
    productions = {'exp': ["term exp'"],
                   "exp'": ["or term exp'", ''],
                   'term': ["factor term'"],
                   "term'": ["and factor term'", ''],
                   'factor': ["operand factor'"],
                   "factor'": ["comop operand factor'", ''],
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
             "exp'": ['', 'or'],
             "term'": ['', 'and'],
             "factor'": ['', '>', '<', '='],
             'comop': ['>', '<', '=']}
    follow = {'exp': ['$'],
              "exp'": ['$'],
              'term': ['$', 'or'],
              "term'": ['$', 'or'],
              'factor': ['$', 'and', 'or'],
              "factor'": ['$', 'and', 'or'],
              'comop': ['!', 'identifier'],
              'operand': ['or', '>', '<', '$', '=', 'and']}
    parsing_table = {'exp': {'identifier': "term exp'", '!': "term exp'"},
                     "exp'": {'or': "or term exp'", '$': ''},
                     'term': {'identifier': "factor term'", '!': "factor term'"},
                     "term'": {'and': "and factor term'", '$': '', 'or': ''},
                     'factor': {'identifier': "operand factor'", '!': "operand factor'"},
                     "factor'": {'>': "comop operand factor'", '<': "comop operand factor'", '=': "comop operand factor'", '$': '', 'and': '', 'or': ''},
                     'comop': {'>': '>', '=': '=', '<': '<'}, 'operand': {'!': '! operand', 'identifier': 'identifier'}}
    grammer = Grammar(variables, terminals, start_var, productions)
    parser = Parser(grammer)
    parser.set_table(parsing_table)
    input = input.split(" ")
    for index, elem in enumerate(input):
        if elem != ">" and elem != "<" and elem != "=" and elem != "!" and elem != "and" and elem != "or":
            input[index] = "identifier"
    return parser.parse(process, input, verbose=True)


class dfaprev(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DFA Preview")
        self.image_lbl = QtWidgets.QLabel()
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.image_lbl)
        self.image_lbl.setPixmap(QtGui.QPixmap(resource_path("ourdfa2.jpg")))


def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    '''
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
    Licensed under Creative Commons Attribution-Share Alike

    If the graph is a tree this will return the positions to plot this in a
    hierarchical layout.

    G: the graph (must be a tree)

    root: the root node of current branch
    - if the tree is directed and this is not given,
      the root will be found and used
    - if the tree is directed and this is given, then
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given,
      then a random choice will be used.

    width: horizontal space allocated for this branch - avoids overlap with other branches

    vert_gap: gap between levels of hierarchy

    vert_loc: vertical location of root

    xcenter: horizontal location of root
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  # allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''

        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                     vert_loc=vert_loc - vert_gap, xcenter=nextx,
                                     pos=pos, parent=root)
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


def draw_ast(text:str, verbose=False):
    tree = nx.DiGraph()
    nodes = []
    text = text.split(" ")
    labels = dict()
    for index, element in enumerate(text): labels[index] = [element, element]
    for index in range(0, len(text)): nodes.append(index)
    while True:
        if verbose:
            print(labels)
            print(nodes)
        if len(nodes) == 1:
            act_labels = dict()
            for node in list(tree.nodes):
                if node in list(tree.nodes): act_labels[node] = labels[node][1]
            if verbose:print(labels)
            pos = hierarchy_pos(tree)
            #pos = graphviz_layout(tree, prog="dot")
            nx.draw_networkx(tree, pos=pos, labels=act_labels, node_size=[len(act_labels[node]) * 300 for node in list(tree.nodes)])
            plt.get_current_fig_manager().set_window_title("Abstract Syntax Tree Visualizer")
            plt.tight_layout()
            plt.show()
            break
        flag = False
        for index in range(0, len(nodes)):
            if labels[nodes[index]][0] == "!":
                child = nodes[index + 1]
                if labels[child][0] == "!":continue
                parent = max(nodes) + 1
                labels[parent] = ["! " + labels[child][1], "!"]
                tree.add_edge(parent, child)
                nodes.pop(index)
                nodes.pop(index)
                nodes.insert(index, parent)
                flag = True
                break
        if flag: continue
        flag = False
        for index in range(0, len(nodes)):
            if labels[nodes[index]][0] == "and":
                left = nodes[index - 1]
                right = nodes[index + 1]
                parent = max(nodes) + 1
                labels[parent] = [labels[left][1] + " and " + labels[right][1], "and"]
                tree.add_edge(parent, left)
                tree.add_edge(parent, right)
                nodes.pop(index - 1)
                nodes.pop(index - 1)
                nodes.pop(index - 1)
                nodes.insert(index - 1, parent)
                flag = True
                break
        if flag: continue
        flag = False
        for index in range(0, len(nodes)):
            if labels[nodes[index]][0] == "or":
                left = nodes[index-1]
                right = nodes[index+1]
                parent = max(nodes)+1
                labels[parent] = [labels[left][1] + " or " + labels[right][1], "or"]
                tree.add_edge(parent, left)
                tree.add_edge(parent, right)
                nodes.pop(index - 1)
                nodes.pop(index - 1)
                nodes.pop(index - 1)
                nodes.insert(index - 1, parent)
                flag = True
                break
        if flag: continue

        for index in range(0, len(nodes)):
            if labels[nodes[index]][0] == ">":
                left = nodes[index - 1]
                right = nodes[index + 1]
                parent = max(nodes) + 1
                labels[parent] = [labels[left][1] + " > " + labels[right][1], ">"]
                tree.add_edge(parent, left)
                tree.add_edge(parent, right)
                nodes.pop(index - 1)
                nodes.pop(index - 1)
                nodes.pop(index - 1)
                nodes.insert(index - 1, parent)
                break
            elif labels[nodes[index]][0] == "<":
                left = nodes[index - 1]
                right = nodes[index + 1]
                parent = max(nodes) + 1
                labels[parent] = [labels[left][1] + " < " + labels[right][1], "<"]
                tree.add_edge(parent, left)
                tree.add_edge(parent, right)
                nodes.pop(index - 1)
                nodes.pop(index - 1)
                nodes.pop(index - 1)
                nodes.insert(index - 1, parent)
                break
            elif labels[nodes[index]][0] == "=":
                left = nodes[index - 1]
                right = nodes[index + 1]
                parent = max(nodes) + 1
                labels[parent] = [labels[left][1] + " = " + labels[right][1], "="]
                tree.add_edge(parent, left)
                tree.add_edge(parent, right)
                nodes.pop(index - 1)
                nodes.pop(index - 1)
                nodes.pop(index - 1)
                nodes.insert(index - 1, parent)
                break


def draw_parse_tree(moves:list, verbose=False):
    tree = nx.DiGraph()
    nodes = []
    labels = dict()
    labels[0] = "exp"
    nodes.append(0)
    tree.add_node(0)
    for move in moves:
        temp_m = move.split("->")
        temp_prod = temp_m[1]
        temp_prod = temp_prod.split(" ")
        while "" in temp_prod:temp_prod.remove("")
        parent_index = 0
        if temp_m[0].strip() == "pop": continue
        for index in range(0, len(nodes)):
            if labels[nodes[index]] == temp_m[0].strip():
                parent_index = index
                break
        if len(temp_prod) == 3:
            left = max(nodes) + 1
            mid = left + 1
            right = mid + 1
            labels[left] = temp_prod[0]
            labels[mid] = temp_prod[1]
            labels[right] = temp_prod[2]
            tree.add_edge(nodes[parent_index], left)
            tree.add_edge(nodes[parent_index], mid)
            tree.add_edge(nodes[parent_index], right)
            if verbose:print(f"Parent {nodes[parent_index]} : {labels[nodes[parent_index]]}, left {left} : {labels[left]}, mid {mid} : {labels[mid]}, right {right} : {labels[right]}")
            nodes.pop(parent_index)
            nodes.insert(parent_index, left)
            nodes.insert(parent_index, mid)
            nodes.insert(parent_index, right)
        elif len(temp_prod) == 2:
            left = max(nodes) + 1
            right = left + 1
            labels[left] = temp_prod[0]
            labels[right] = temp_prod[1]
            tree.add_edge(nodes[parent_index], left)
            tree.add_edge(nodes[parent_index], right)
            if verbose:print(f"Parent {nodes[parent_index]} : {labels[nodes[parent_index]]}, left {left} : {labels[left]}, right {right} : {labels[right]}")
            nodes.pop(parent_index)
            nodes.insert(parent_index, left)
            nodes.insert(parent_index, right)
        else:
            child = max(nodes) + 1
            labels[child] = temp_prod[0]
            tree.add_edge(nodes[parent_index], child)
            if verbose:print(f"Parent {nodes[parent_index]} : {labels[nodes[parent_index]]}, child {child} : {labels[child]}")
            nodes.pop(parent_index)
            nodes.insert(parent_index, child)
    pos = graphviz_layout(tree, prog="dot")
    nx.draw_networkx(tree, pos=pos, labels=labels, node_size=[len(labels[node]) * 260 for node in list(tree.nodes)])
    plt.tight_layout()
    plt.get_current_fig_manager().set_window_title("Parse Tree Visualizer")
    plt.show()


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
        self.astbtn.clicked.connect(self.ast_click)
        self.parsetreebtn.clicked.connect(self.parse_tree_click)
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
            print(parse(self.process, input=self.parseinput.text()))
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
                if self.parsetable.item(self.parsetable.rowCount()-1, 0).text() == "['$']" and self.parsetable.item(self.parsetable.rowCount()-1, 1).text() == "['$']":
                    item.setText("Success!")
                    self.popup("Result", "Information", "Parsing Successful!", f"Parsing Finished in {self.parsetable.rowCount()} Steps")
                else:
                    item.setText("Fail!")
                    self.popup("Result", "err", "Parsing Failed!", f"Parsing Failed at Step {self.parsetable.rowCount()}")
                self.parsetable.setItem(counter - 1, 2, item)

    def ast_click(self):
        if self.parsetable.item(self.parsetable.rowCount()-1, 2).text() != "Success!":
            self.popup("Error", "err", "Failure", "Please Make Sure Parsing is Successful")
        else:
            try: draw_ast(self.parseinput.text(), verbose=False)
            except: self.popup("Error", "err", "Failure", "Please Make Sure Parsing is Successful")

    def parse_tree_click(self):
        try: draw_parse_tree(self.process[-1][1::], False)
        except: self.popup("Error", "err", "Failure", "Please Make Sure Parsing is Successful")

    def popup(self, title, msg_type,msg_title, msg_info, extra=""):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(title)
        msg.setWindowIcon(QtGui.QIcon(resource_path("icon.png")))
        msg.setText(msg_title)
        if msg_type == "warn": msg.setIcon(QtWidgets.QMessageBox.Warning)
        elif msg_type == "err": msg.setIcon(QtWidgets.QMessageBox.Critical)
        else:msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setInformativeText(msg_info)
        if extra != "" : msg.setDetailedText(extra)
        x = msg.exec_()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())