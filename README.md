# Tiny Language Compiler

## Overview

The Tiny Language Compiler is a simple compiler for a custom programming language. It features a lexer, parser, and visual representations of abstract syntax trees (AST) and parse trees. The application is built using PyQt5 for the graphical user interface, and it employs NetworkX and Matplotlib for visualizing the structures of the language.

## Features

- **Lexical Analysis**: The compiler includes a lexer that tokenizes input code into meaningful symbols.
- **Parsing**: The parser checks the syntactical correctness of the input code against a defined grammar.
- **Abstract Syntax Tree Visualization**: Users can visualize the AST generated from the input code.
- **Parse Tree Visualization**: Users can visualize the parse tree, showing how the input code is derived from the grammar.
- **Interactive GUI**: The application provides a user-friendly interface for compiling and parsing code, displaying tokens, and visualizing trees.

## Requirements

- Python 3.x
- PyQt5
- NetworkX
- Matplotlib
- SLY (Simple Lex-Yacc)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/tiny-language-compiler.git
    cd tiny-language-compiler
    ```
2. Install the required packages:
    ```bash
    pip install PyQt5 networkx matplotlib sly
    ```
3. Run the application:
    ```bash
    python main.py
    ```

## Usage

1. **Compiling Code**:
   - Enter your code in the provided text area.
   - Click the "Compile" button to tokenize and analyze the code.
   - The tokens will be displayed in the token table.

2. **Parsing Code**:
   - Enter the code you want to parse in the input field.
   - Click the "Parse" button to check its syntactical correctness.
   - The parsing process will be shown in the parse table.

3. **Visualizing AST and Parse Trees**:
   - After a successful parse, you can visualize the AST and parse tree by clicking the respective buttons.

4. **Viewing Regular Expressions**:
   - Click the "Show Regular Expressions" button to view the current regular expressions used by the lexer.

5. **DFA Preview**:
   - Click the "Preview Compiler DFA" button to view the deterministic finite automaton related to the language.
