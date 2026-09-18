"""Camada de acesso ao banco de dados (SQLite).

Todas as exceções específicas do sqlite3 são capturadas aqui e traduzidas
para BancoDadosError com uma mensagem amigável. Assim, a interface gráfica
nunca precisa saber o que é "database is locked" ou um "IntegrityError" -
ela só recebe uma mensagem pronta para mostrar ao usuário.
"""

import logging
import sqlite3
from pathlib import Path

from app.exceptions import BancoDadosError
from app.models import Pessoa

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, caminho_banco: Path):
        self.caminho_banco = caminho_banco
        self._preparar_banco()

    # ------------------------------------------------------------------
    # Infraestrutura
    # ------------------------------------------------------------------

    def _conectar(self):
        try:
            conexao = sqlite3.connect(self.caminho_banco, timeout=5)
            conexao.execute("PRAGMA foreign_keys = ON")
            return conexao
        except sqlite3.OperationalError as erro:
            logger.exception("Falha ao conectar ao banco de dados")
            raise BancoDadosError(
                "Não foi possível acessar o arquivo do banco de dados.\n"
                f"Verifique se o local '{self.caminho_banco}' existe e se "
                "você possui permissão de leitura/escrita.\n\n"
                f"Detalhes técnicos: {erro}"
            ) from erro

    def _preparar_banco(self):
        try:
            with self._conectar() as conexao:
                conexao.execute("""
                    CREATE TABLE IF NOT EXISTS pessoas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo_documento TEXT NOT NULL,
                        documento TEXT NOT NULL,
                        nome TEXT NOT NULL,
                        email TEXT NOT NULL,
                        celular TEXT NOT NULL,
                        cep TEXT NOT NULL,
                        logradouro TEXT NOT NULL,
                        numero TEXT NOT NULL,
                        complemento TEXT,
                        bairro TEXT NOT NULL,
                        cidade TEXT NOT NULL,
                        estado TEXT NOT NULL
                    )
                """)
                conexao.commit()
        except sqlite3.Error as erro:
            logger.exception("Falha ao preparar a tabela do banco de dados")
            raise BancoDadosError(
                "Não foi possível preparar o banco de dados local.\n\n"
                f"Detalhes técnicos: {erro}"
            ) from erro

    # ------------------------------------------------------------------
    # Operações
    # ------------------------------------------------------------------

    def inserir(self, pessoa: Pessoa) -> int:
        try:
            with self._conectar() as conexao:
                cursor = conexao.execute(
                    f"""
                    INSERT INTO pessoas ({", ".join(Pessoa.campos_banco())})
                    VALUES ({", ".join("?" for _ in Pessoa.campos_banco())})
                    """,
                    [getattr(pessoa, campo) for campo in Pessoa.campos_banco()],
                )
                conexao.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as erro:
            logger.exception("Violação de integridade ao inserir pessoa")
            raise BancoDadosError(
                "Não foi possível salvar: os dados violam uma restrição "
                f"do banco de dados.\n\nDetalhes técnicos: {erro}"
            ) from erro
        except sqlite3.OperationalError as erro:
            logger.exception("Banco ocupado/indisponível ao inserir pessoa")
            raise BancoDadosError(
                "O banco de dados está ocupado ou indisponível no "
                "momento. Tente novamente em instantes.\n\n"
                f"Detalhes técnicos: {erro}"
            ) from erro
        except sqlite3.Error as erro:
            logger.exception("Erro inesperado do sqlite ao inserir pessoa")
            raise BancoDadosError(
                f"Não foi possível salvar o cadastro.\n\nDetalhes técnicos: {erro}"
            ) from erro

    def atualizar(self, pessoa: Pessoa) -> None:
        if pessoa.id is None:
            raise BancoDadosError("Cadastro sem identificador não pode ser atualizado.")

        campos = Pessoa.campos_banco()
        atribuicoes = ", ".join(f"{campo} = ?" for campo in campos)

        try:
            with self._conectar() as conexao:
                cursor = conexao.execute(
                    f"UPDATE pessoas SET {atribuicoes} WHERE id = ?",
                    [getattr(pessoa, campo) for campo in campos] + [pessoa.id],
                )
                conexao.commit()

                if cursor.rowcount == 0:
                    raise BancoDadosError(
                        "Este cadastro não existe mais no banco de dados "
                        "(pode ter sido excluído por outra sessão)."
                    )
        except sqlite3.Error as erro:
            logger.exception("Erro ao atualizar pessoa")
            raise BancoDadosError(
                f"Não foi possível atualizar o cadastro.\n\nDetalhes técnicos: {erro}"
            ) from erro

    def listar(self, termo_pesquisa: str = ""):
        try:
            with self._conectar() as conexao:
                if termo_pesquisa:
                    curinga = f"%{termo_pesquisa}%"
                    cursor = conexao.execute(
                        """
                        SELECT id, nome, documento, email, celular, cidade, estado
                        FROM pessoas
                        WHERE nome LIKE ? OR documento LIKE ? OR email LIKE ?
                        ORDER BY nome
                        """,
                        (curinga, curinga, curinga),
                    )
                else:
                    cursor = conexao.execute(
                        """
                        SELECT id, nome, documento, email, celular, cidade, estado
                        FROM pessoas
                        ORDER BY nome
                        """
                    )
                return cursor.fetchall()
        except sqlite3.Error as erro:
            logger.exception("Erro ao listar pessoas")
            raise BancoDadosError(
                f"Não foi possível carregar os cadastros.\n\nDetalhes técnicos: {erro}"
            ) from erro

    def buscar_por_id(self, pessoa_id: int) -> Pessoa | None:
        campos = Pessoa.campos_banco()
        try:
            with self._conectar() as conexao:
                cursor = conexao.execute(
                    f"SELECT id, {', '.join(campos)} FROM pessoas WHERE id = ?",
                    (pessoa_id,),
                )
                linha = cursor.fetchone()

                if linha is None:
                    return None

                return Pessoa(**dict(zip(["id"] + campos, linha)))
        except sqlite3.Error as erro:
            logger.exception("Erro ao buscar pessoa por id")
            raise BancoDadosError(
                f"Não foi possível carregar o cadastro selecionado.\n\n"
                f"Detalhes técnicos: {erro}"
            ) from erro

    def excluir(self, pessoa_id: int) -> None:
        try:
            with self._conectar() as conexao:
                conexao.execute("DELETE FROM pessoas WHERE id = ?", (pessoa_id,))
                conexao.commit()
        except sqlite3.Error as erro:
            logger.exception("Erro ao excluir pessoa")
            raise BancoDadosError(
                f"Não foi possível excluir o cadastro.\n\nDetalhes técnicos: {erro}"
            ) from erro
