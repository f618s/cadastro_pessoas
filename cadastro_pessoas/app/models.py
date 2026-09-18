"""Modelos de dados da aplicação."""

from dataclasses import dataclass, fields


@dataclass
class Pessoa:
    """Representa os dados de uma pessoa cadastrada.

    Usar um dataclass em vez de dicionários soltos deixa explícito quais
    campos existem, evita erros de digitação em chaves de dicionário e
    facilita a conversão de/para o banco de dados e para o formulário.
    """

    id: int | None = None
    tipo_documento: str = "CPF"
    documento: str = ""
    nome: str = ""
    email: str = ""
    celular: str = ""
    cep: str = ""
    logradouro: str = ""
    numero: str = ""
    complemento: str = ""
    bairro: str = ""
    cidade: str = ""
    estado: str = ""

    @classmethod
    def campos_banco(cls):
        """Nomes dos campos que são persistidos (todos exceto o id)."""
        return [campo.name for campo in fields(cls) if campo.name != "id"]
