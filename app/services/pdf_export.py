"""Exportação da tabela de cadastros para PDF.

Usamos apenas módulos que já vêm junto com o PySide6 (QtGui.QTextDocument
+ QtPrintSupport.QPrinter), sem depender de nenhuma biblioteca externa
(como reportlab). A ideia é montar uma tabela em HTML e "imprimir" esse
documento em um arquivo PDF.
"""

import html
import logging
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QPageLayout, QTextDocument
from PySide6.QtPrintSupport import QPrinter

from app.exceptions import ExportacaoPdfError

logger = logging.getLogger(__name__)

COLUNAS_EXPORTACAO = ["Nome", "Documento", "E-mail", "Celular", "Cidade", "Estado"]


def _montar_html(registros, termo_pesquisa: str) -> str:
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")

    linha_filtro = ""
    if termo_pesquisa:
        linha_filtro = f"<p>Filtro aplicado: <b>{html.escape(termo_pesquisa)}</b></p>"

    linhas_html = []
    for registro in registros:
        # registro = (id, nome, documento, email, celular, cidade, estado)
        _id, nome, documento, email, celular, cidade, estado = registro
        celulas = "".join(
            f"<td>{html.escape(str(valor) if valor is not None else '')}</td>"
            for valor in (nome, documento, email, celular, cidade, estado)
        )
        linhas_html.append(f"<tr>{celulas}</tr>")

    cabecalho_html = "".join(f"<th>{html.escape(c)}</th>" for c in COLUNAS_EXPORTACAO)

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 10pt; color: #1c2733; }}
            h1 {{ font-size: 16pt; color: #1976d2; margin-bottom: 2px; }}
            p.sub {{ color: #5b6b7b; margin-top: 0; margin-bottom: 12px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #cbd1d8; padding: 5px 6px; text-align: left; }}
            th {{ background-color: #eef2f6; }}
            tr:nth-child(even) td {{ background-color: #f7f9fb; }}
        </style>
    </head>
    <body>
        <h1>Cadastro de Pessoas</h1>
        <p class="sub">Gerado em {data_geracao} — {len(registros)} registro(s)</p>
        {linha_filtro}
        <table>
            <thead><tr>{cabecalho_html}</tr></thead>
            <tbody>{''.join(linhas_html)}</tbody>
        </table>
    </body>
    </html>
    """


def exportar_para_pdf(caminho: Path, registros, termo_pesquisa: str = "") -> None:
    """Gera um PDF com os registros informados.

    Levanta ExportacaoPdfError se não for possível criar o arquivo (por
    exemplo, pasta sem permissão de escrita, ou o arquivo estar aberto em
    outro programa no momento).
    """
    try:
        documento = QTextDocument()
        documento.setHtml(_montar_html(registros, termo_pesquisa))

        impressora = QPrinter(QPrinter.PrinterMode.HighResolution)
        impressora.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        impressora.setOutputFileName(str(caminho))
        impressora.setPageMargins(QMarginsF(15, 15, 15, 15), QPageLayout.Unit.Millimeter)

        documento.print_(impressora)

        # QPrinter não levanta exceção sozinho em muitos casos de falha
        # (ex: pasta sem permissão) - o arquivo simplesmente não é criado.
        # Conferimos explicitamente para não deixar o usuário achar que
        # deu certo quando na verdade não gerou nada.
        if not caminho.exists() or caminho.stat().st_size == 0:
            raise ExportacaoPdfError(
                "O arquivo PDF não pôde ser criado. Verifique se você tem "
                "permissão de escrita nessa pasta e se o arquivo não está "
                "aberto em outro programa."
            )
    except ExportacaoPdfError:
        raise
    except OSError as erro:
        logger.exception("Erro de sistema de arquivos ao exportar PDF")
        raise ExportacaoPdfError(
            "Não foi possível salvar o arquivo PDF no local escolhido.\n"
            f"Detalhes técnicos: {erro}"
        ) from erro
    except Exception as erro:
        logger.exception("Erro inesperado ao exportar PDF")
        raise ExportacaoPdfError(
            f"Ocorreu um erro inesperado ao gerar o PDF.\n\nDetalhes técnicos: {erro}"
        ) from erro
