"""Pruebas del analizador léxico de Mini-C."""

import pytest

from minic.lexer import Lexer, Token, TokenType
from minic.output import format_diagnostic, format_token
from minic.parser import Parser


def test_specification_case_1() -> None:
    """Caso 1 de la sección 7 de la especificación:

    Fuente:
    int2 = 12abc;
    whilex == -5
    """
    source = "int2 = 12abc;\nwhilex == -5"
    tokens, diagnostics = Lexer(source).scan()

    assert diagnostics == []

    formatted = [format_token(t) for t in tokens]
    expected = [
        "IDENTIFIER 'int2' 1 1",
        "ASSIGN '=' 1 6",
        "INTEGER_LITERAL '12' 1 8",
        "IDENTIFIER 'abc' 1 10",
        "SEMICOLON ';' 1 13",
        "IDENTIFIER 'whilex' 2 1",
        "EQUAL_EQUAL '==' 2 8",
        "MINUS '-' 2 11",
        "INTEGER_LITERAL '5' 2 12",
        "EOF '' 2 13",
    ]
    assert formatted == expected
    assert tokens[2].literal == 12
    assert tokens[8].literal == 5


def test_specification_case_2_with_errors() -> None:
    """Caso 2 de la sección 7 de la especificación (con errores):

    Fuente:
    int x = @;
    x ! = 0; // fin
    """
    source = "int x = @;\nx ! = 0; // fin"
    tokens, diagnostics = Lexer(source).scan()

    formatted_tokens = [format_token(t) for t in tokens]
    expected_tokens = [
        "KW_INT 'int' 1 1",
        "IDENTIFIER 'x' 1 5",
        "ASSIGN '=' 1 7",
        "SEMICOLON ';' 1 10",
        "IDENTIFIER 'x' 2 1",
        "ASSIGN '=' 2 5",
        "INTEGER_LITERAL '0' 2 7",
        "SEMICOLON ';' 2 8",
        "IDENTIFIER 'fin' 2 13",
        "EOF '' 2 16",
    ]
    assert formatted_tokens == expected_tokens

    formatted_diagnostics = [format_diagnostic(d) for d in diagnostics]
    expected_diagnostics = [
        "LEX001 error 1:9 Carácter no reconocido: '@'",
        "LEX001 error 2:3 Carácter no reconocido: '!'",
        "LEX001 error 2:10 Carácter no reconocido: '/'",
        "LEX001 error 2:11 Carácter no reconocido: '/'",
    ]
    assert formatted_diagnostics == expected_diagnostics


def test_empty_source() -> None:
    tokens, diagnostics = Lexer("").scan()
    assert diagnostics == []
    assert len(tokens) == 1
    assert tokens[0] == Token(TokenType.EOF, "", None, 1, 1)


def test_tabs_and_carriage_return_positions() -> None:
    """Un carácter de tabulación cuenta como 1 columna.

    \\r suelto cuenta como 1 columna y no abre línea nueva.
    """
    source = "\t\rx"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    assert len(tokens) == 2
    assert tokens[0] == Token(TokenType.IDENTIFIER, "x", None, 1, 3)
    assert tokens[1] == Token(TokenType.EOF, "", None, 1, 4)


def test_newline_increments_line_resets_column() -> None:
    source = "a\nb\n\nc"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    assert tokens[0] == Token(TokenType.IDENTIFIER, "a", None, 1, 1)
    assert tokens[1] == Token(TokenType.IDENTIFIER, "b", None, 2, 1)
    assert tokens[2] == Token(TokenType.IDENTIFIER, "c", None, 4, 1)


def test_integer_literal_values() -> None:
    source = "0 007 12345"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    assert tokens[0].literal == 0
    assert tokens[1].literal == 7
    assert tokens[2].literal == 12345


def test_all_symbols_and_keywords() -> None:
    source = "int while = + - == != ( ) { } ;"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    types = [t.type for t in tokens]
    expected = [
        TokenType.KW_INT,
        TokenType.KW_WHILE,
        TokenType.ASSIGN,
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.EQUAL_EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert types == expected


def test_parser_integration() -> None:
    """Verifica que Parser acepte la salida de Lexer."""
    source = "int x = 10;"
    tokens, _ = Lexer(source).scan()
    parser = Parser(tokens)
    assert parser._tokens == tokens
