"""Integração com a API pública ViaCEP.

Este módulo não sabe nada sobre PySide6/QThread - ele só sabe consultar
o serviço e traduzir os possíveis problemas em exceções específicas
(app.exceptions), o que facilita testar e reaproveitar em outro contexto.
"""

import logging

import requests

from app.constants import TIMEOUT_CONSULTA_CEP
from app.exceptions import (
    CepConexaoError,
    CepInvalidoError,
    CepNaoEncontradoError,
    CepRespostaInvalidaError,
)
from app.validators import somente_numeros

logger = logging.getLogger(__name__)


def consultar_cep(cep: str) -> dict:
    """Consulta um CEP na API ViaCEP e retorna os dados de endereço.

    Levanta:
        CepInvalidoError: formato de CEP inválido (não chega a consultar).
        CepNaoEncontradoError: CEP com formato válido, mas inexistente.
        CepConexaoError: problema de rede, timeout ou serviço indisponível.
        CepRespostaInvalidaError: o serviço respondeu algo que não é o
            JSON esperado (por exemplo, uma página de erro em HTML).
    """
    cep_numerico = somente_numeros(cep)

    if len(cep_numerico) != 8:
        raise CepInvalidoError("O CEP deve possuir 8 dígitos. Exemplo: 01001-000.")

    url = f"https://viacep.com.br/ws/{cep_numerico}/json/"

    try:
        resposta = requests.get(url, timeout=TIMEOUT_CONSULTA_CEP)
        resposta.raise_for_status()
    except requests.exceptions.Timeout as erro:
        logger.warning("Timeout ao consultar CEP %s: %s", cep_numerico, erro)
        raise CepConexaoError(
            "A consulta demorou muito para responder. Verifique sua "
            "conexão com a internet e tente novamente."
        ) from erro
    except requests.exceptions.ConnectionError as erro:
        logger.warning("Falha de conexão ao consultar CEP %s: %s", cep_numerico, erro)
        raise CepConexaoError(
            "Não foi possível conectar ao serviço de CEP. Verifique sua "
            "conexão com a internet."
        ) from erro
    except requests.exceptions.HTTPError as erro:
        logger.warning("Erro HTTP ao consultar CEP %s: %s", cep_numerico, erro)
        raise CepConexaoError(
            "O serviço de CEP retornou um erro e não pôde ser consultado "
            "no momento. Tente novamente mais tarde."
        ) from erro
    except requests.exceptions.RequestException as erro:
        logger.warning("Erro de requisição ao consultar CEP %s: %s", cep_numerico, erro)
        raise CepConexaoError(
            "O serviço de CEP está indisponível no momento. Tente "
            "novamente mais tarde."
        ) from erro

    try:
        dados = resposta.json()
    except ValueError as erro:
        logger.error("Resposta não-JSON do ViaCEP para %s: %s", cep_numerico, erro)
        raise CepRespostaInvalidaError(
            "O serviço de CEP retornou uma resposta em formato inesperado."
        ) from erro

    if not isinstance(dados, dict):
        raise CepRespostaInvalidaError(
            "O serviço de CEP retornou uma resposta em formato inesperado."
        )

    if dados.get("erro"):
        raise CepNaoEncontradoError(
            "O CEP informado não foi encontrado. Verifique os números "
            "digitados."
        )

    return {
        "logradouro": dados.get("logradouro", "") or "",
        "bairro": dados.get("bairro", "") or "",
        "cidade": dados.get("localidade", "") or "",
        "estado": dados.get("uf", "") or "",
    }
