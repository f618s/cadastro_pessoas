"""Funções utilitárias compartilhadas pelos widgets de formulário."""

from PySide6.QtWidgets import QWidget


def marcar_erro(widget: QWidget, tem_erro: bool) -> None:
    """Aplica/remove o destaque visual de erro em um campo (QSS [erro=...])."""
    widget.setProperty("erro", tem_erro)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def limpar_erros(*widgets: QWidget) -> None:
    for widget in widgets:
        marcar_erro(widget, False)
