"""Validação e formatação (máscara) dos campos do formulário.

Manter validação e formatação separadas da interface gráfica permite
testá-las isoladamente e reaproveitá-las em qualquer lugar (por exemplo,
em um futuro formulário de edição ou em testes automatizados).
"""

import re


def somente_numeros(valor: str) -> str:
    """Remove tudo que não for dígito."""
    return re.sub(r"\D", "", valor or "")


# --------------------------------------------------------------------------
# Validações
# --------------------------------------------------------------------------

def validar_cpf(cpf: str) -> bool:
    cpf = somente_numeros(cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[9]):
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0

    return resto == int(cpf[10])


def validar_cnpj(cnpj: str) -> bool:
    cnpj = somente_numeros(cnpj)

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    if digito1 != int(cnpj[12]):
        return False

    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return digito2 == int(cnpj[13])


def validar_documento(tipo: str, documento: str) -> bool:
    """Valida CPF ou CNPJ de acordo com o tipo selecionado."""
    if tipo == "CPF":
        return validar_cpf(documento)
    if tipo == "CNPJ":
        return validar_cnpj(documento)
    return False


def validar_email(email: str) -> bool:
    padrao = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(padrao, (email or "").strip()) is not None


def validar_celular(celular: str) -> bool:
    """Celular brasileiro: DDD (2 dígitos) + 9 dígitos, iniciando em 9."""
    celular = somente_numeros(celular)
    return len(celular) == 11 and celular[2] == "9"


def validar_cep(cep: str) -> bool:
    cep = somente_numeros(cep)
    return len(cep) == 8


# --------------------------------------------------------------------------
# Formatação / máscaras
# --------------------------------------------------------------------------

def formatar_cpf(cpf: str) -> str:
    cpf = somente_numeros(cpf)[:11]
    partes = []
    if len(cpf) > 0:
        partes.append(cpf[:3])
    if len(cpf) > 3:
        partes.append(cpf[3:6])
    if len(cpf) > 6:
        partes.append(cpf[6:9])
    texto = ".".join(partes[:3])
    if len(cpf) > 9:
        texto += f"-{cpf[9:11]}"
    return texto


def formatar_cnpj(cnpj: str) -> str:
    cnpj = somente_numeros(cnpj)[:14]
    texto = cnpj
    if len(cnpj) > 2:
        texto = f"{cnpj[:2]}.{cnpj[2:]}"
    if len(cnpj) > 5:
        texto = f"{texto[:6]}.{texto[6:]}"
    if len(cnpj) > 8:
        texto = f"{texto[:10]}/{texto[10:]}"
    if len(cnpj) > 12:
        texto = f"{texto[:15]}-{texto[15:]}"
    return texto


def formatar_documento(tipo: str, valor: str) -> str:
    if tipo == "CNPJ":
        return formatar_cnpj(valor)
    return formatar_cpf(valor)


def formatar_celular(celular: str) -> str:
    celular = somente_numeros(celular)[:11]
    if len(celular) <= 2:
        return celular
    if len(celular) <= 7:
        return f"({celular[:2]}) {celular[2:]}"
    return f"({celular[:2]}) {celular[2:7]}-{celular[7:]}"


def formatar_cep(cep: str) -> str:
    cep = somente_numeros(cep)[:8]
    if len(cep) <= 5:
        return cep
    return f"{cep[:5]}-{cep[5:]}"
