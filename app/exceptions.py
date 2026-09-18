"""Exceções específicas do domínio da aplicação.

Centralizar as exceções aqui facilita que a camada de interface saiba
exatamente o que aconteceu e escolha a mensagem adequada para o usuário,
em vez de propagar exceções genéricas (Exception) que escondem a causa
real do problema.
"""


class CepInvalidoError(ValueError):
    """O CEP informado não possui um formato válido."""


class CepNaoEncontradoError(LookupError):
    """O CEP possui formato válido, mas não foi localizado."""


class CepConexaoError(ConnectionError):
    """Houve falha de rede/serviço ao consultar o CEP."""


class CepRespostaInvalidaError(RuntimeError):
    """O serviço respondeu, mas em um formato inesperado."""


class BancoDadosError(Exception):
    """Erro ao acessar/gravar no banco de dados local."""


class ExportacaoPdfError(Exception):
    """Erro ao gerar o arquivo PDF com os cadastros."""
