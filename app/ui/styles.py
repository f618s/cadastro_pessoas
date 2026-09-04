"""Folha de estilos (QSS) da aplicação.

Manter o estilo em um único lugar evita repetição e permite ajustar o
visual da aplicação inteira em um só ponto. O seletor `[erro="true"]`
é usado para destacar campos inválidos (ver ui/widgets/base.py).
"""

ESTILO_APLICACAO = """
QMainWindow, QWidget#areaCentral {
    background-color: #f2f4f7;
}

QLabel#titulo {
    font-size: 22px;
    font-weight: 700;
    color: #1c2733;
}

QLabel#subtitulo {
    font-size: 13px;
    color: #5b6b7b;
    margin-bottom: 4px;
}

QLabel#rotuloCampo {
    color: #34424f;
    font-weight: 600;
}

QLabel#mensagemErroCampo {
    color: #c0392b;
    font-size: 11px;
}

QGroupBox {
    background-color: #ffffff;
    border: 1px solid #dbe1e8;
    border-radius: 10px;
    margin-top: 14px;
    padding: 18px 14px 14px 14px;
    font-weight: 700;
    color: #263238;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #1976d2;
}

QLineEdit, QComboBox {
    padding: 7px 8px;
    border: 1px solid #cbd1d8;
    border-radius: 6px;
    background-color: #ffffff;
    color: #1c2733;
    selection-background-color: #90caf9;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #1976d2;
}

QLineEdit:disabled, QComboBox:disabled {
    background-color: #eef1f4;
    color: #90a0ac;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1c2733;
    border: 1px solid #cbd1d8;
    outline: none;
    selection-background-color: #1976d2;
    selection-color: #ffffff;
    padding: 2px;
}

QComboBox QAbstractItemView::item {
    min-height: 26px;
    padding: 2px 8px;
}

QLineEdit[erro="true"], QComboBox[erro="true"] {
    border: 1px solid #d32f2f;
    background-color: #fff5f5;
}

QPushButton {
    padding: 8px 16px;
    border-radius: 6px;
    background-color: #1976d2;
    color: white;
    font-weight: 600;
    border: none;
}

QPushButton:hover {
    background-color: #1565c0;
}

QPushButton:pressed {
    background-color: #0d47a1;
}

QPushButton:disabled {
    background-color: #b0bec5;
    color: #eceff1;
}

QPushButton#botaoSecundario {
    background-color: #eceff1;
    color: #37474f;
}

QPushButton#botaoSecundario:hover {
    background-color: #dfe4e8;
}

QPushButton#botaoPerigo {
    background-color: #c0392b;
}

QPushButton#botaoPerigo:hover {
    background-color: #a5281c;
}

QTableWidget {
    background-color: white;
    color: #1c2733;
    border: 1px solid #dbe1e8;
    border-radius: 6px;
    gridline-color: #e7ebef;
    selection-background-color: #bbdefb;
    selection-color: #102a43;
}

QHeaderView::section {
    background-color: #eef2f6;
    color: #34424f;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #dbe1e8;
    font-weight: 600;
}

QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #dbe1e8;
}

QStatusBar QLabel {
    padding: 2px 6px;
}

QToolTip {
    background-color: #263238;
    color: white;
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
}
"""
