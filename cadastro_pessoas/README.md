# Sistema de Cadastro de Pessoas — PySide6

Aplicação desktop para cadastro de pessoas (física ou jurídica), com
consulta automática de endereço por CEP, validação completa dos dados e
persistência em banco de dados local SQLite.

## Como executar

```bash
# 1. Crie e ative um ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute a aplicação
python main.py
```

Requer Python 3.10+ (por causa do uso de `int | None` nas anotações de tipo).

Na primeira execução, um arquivo `cadastro.db` é criado automaticamente
na pasta do projeto — não é necessário nenhum passo manual de configuração
de banco de dados. Um arquivo `app.log` também é criado, com o registro
de eventos e erros para facilitar o diagnóstico de problemas.

## Estrutura do projeto

```
cadastro_pessoas/
├── main.py                     # Ponto de entrada: logging, tratamento
│                                  global de erros e inicialização
├── app/
│   ├── constants.py             # Lista de estados, nome do banco, timeouts
│   ├── exceptions.py            # Exceções específicas do domínio
│   ├── models.py                # Dataclass Pessoa
│   ├── validators.py            # Validação (CPF/CNPJ/e-mail/...) e máscaras
│   ├── services/
│   │   ├── database.py          # Acesso ao SQLite (inserir/atualizar/listar/excluir)
│   │   └── viacep.py            # Cliente da API ViaCEP
│   ├── workers/
│   │   └── cep_worker.py        # Consulta de CEP em thread separada (QThread)
│   └── ui/
│       ├── styles.py            # Folha de estilos (QSS) centralizada
│       ├── main_window.py       # Janela principal (orquestra os widgets)
│       └── widgets/
│           ├── personal_data_form.py   # Bloco "Dados pessoais"
│           ├── address_form.py         # Bloco "Endereço" + consulta de CEP
│           └── person_table.py         # Tabela de cadastros + pesquisa
└── requirements.txt
```

## Principais funcionalidades

- **Cadastro de pessoa física ou jurídica**, com troca dinâmica entre CPF
  e CNPJ (incluindo validação do dígito verificador de ambos).
- **Máscaras automáticas** aplicadas enquanto o usuário digita: CPF/CNPJ,
  celular e CEP.
- **Validação campo a campo**, com os campos inválidos destacados em
  vermelho na tela e uma lista clara do que precisa ser corrigido (nunca
  uma mensagem genérica de "dados inválidos").
- **Consulta automática de endereço pelo CEP** (API ViaCEP), executada em
  uma thread separada para a interface nunca travar durante a consulta.
  Foram tratados separadamente os cenários de: CEP com formato inválido,
  CEP inexistente, falha de conexão/timeout, serviço indisponível e
  resposta em formato inesperado — cada um com uma mensagem específica.
- **Edição de cadastros existentes**: um duplo clique em qualquer linha da
  tabela (ou o botão "Editar selecionado") carrega os dados no formulário
  para alteração.
- **Exclusão de cadastros**, sempre com confirmação prévia.
- **Pesquisa** por nome, documento ou e-mail na lista de cadastros.
- **Confirmação antes de perder dados**: ao clicar em "Limpar" com o
  formulário preenchido, a aplicação pergunta antes de apagar.
- **Tratamento de erros do banco de dados** (arquivo sem permissão, banco
  ocupado por outro processo, violação de integridade etc.), sempre com
  mensagem amigável — nunca um `Traceback` cru na tela.
- **Captura global de exceções não previstas**: caso algo escape de todos
  os tratamentos específicos, a aplicação mostra um aviso amigável (em vez
  de fechar sem explicação) e registra os detalhes técnicos em `app.log`.

## Principais decisões de desenvolvimento

- **Organização em módulos por responsabilidade** (validação, acesso a
  dados, consulta de CEP, cada bloco da interface) em vez de concentrar
  tudo em uma única classe/arquivo, facilitando manutenção e testes.
- **Consulta de CEP em `QThread`** em vez de `QApplication.processEvents()`,
  evitando que a interface fique instável se o usuário interagir com a
  janela durante uma consulta lenta, e permitindo encerrar a aplicação
  com segurança mesmo com uma consulta em andamento.
- **Exceções próprias** (`app/exceptions.py`) em vez de deixar exceções de
  bibliotecas de terceiros (sqlite3, requests) vazarem para a interface,
  o que manteria a UI acoplada a detalhes de implementação dessas
  bibliotecas.
- **Destaque visual de campo com erro** via propriedade dinâmica do Qt
  (`erro="true"` + QSS), assim o usuário identifica visualmente onde está
  o problema, além de ler a mensagem.
