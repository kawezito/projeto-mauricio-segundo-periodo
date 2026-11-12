# Sistema de Gerenciamento de Farmácia — Etapa 1: Núcleo do Sistema (100% Manipulação de Arquivos)

Sistema desenvolvido em **Python 3.12+** utilizando exclusivamente **Manipulação de Arquivos (JSON e CSV)** para o gerenciamento completo de medicamentos, clientes, estoque, vendas e relatórios analíticos via **Terminal Interativo (CLI)**.

---

## 1. Visão Geral e Objetivo Acadêmico

Este projeto tem finalidade acadêmica e atende rigorosamente ao critério de **Manipulação de Arquivos**, operando **sem dependência de banco de dados ou bibliotecas externas**.

Toda a persistência das entidades é realizada em arquivos estruturados `.json` na pasta `data/`, e os relatórios tabulares são gerados em arquivos `.csv` na pasta `reports/` utilizando codificação UTF-8.

---

## 2. Tecnologias Utilizadas

- **Linguagem:** Python 3.12+ (apenas módulos nativos)
- **Manipulação de Arquivos:**
  - Biblioteca `json` para persistência dos dados (`data/*.json` com indentação e UTF-8)
  - Biblioteca `csv` para exportação de relatórios tabulares (`reports/*.csv`)
- **Datas e Horários:** Biblioteca `datetime` no padrão ISO 8601
- **Precisão Monetária:** Valores armazenados em centavos inteiros e operados com `Decimal`
- **Modelos:** Orientação a Objetos com `__init__`, `self` e `to_dict()`
- **Testes Automatizados:** Biblioteca `unittest` com arquivos temporários voláteis (`tempfile`)

---

## 3. Estrutura de Diretórios

```text
farmacia/
│
├── main.py                     # Menu interativo via terminal (CLI)
├── exceptions.py               # Exceções de negócio personalizadas
│
├── data/                       # Arquivos físicos de persistência JSON
│   ├── medicamentos.json       # Cadastro e estoque de medicamentos
│   ├── clientes.json           # Cadastro de clientes
│   ├── vendas.json             # Histórico de vendas e itens
│   └── movimentacoes.json      # Livro de movimentações de estoque
│
├── models/
│   ├── __init__.py
│   ├── medicamento.py
│   ├── cliente.py
│   ├── venda.py
│   ├── item_venda.py
│   └── movimentacao_estoque.py
│
├── repositories/               # Camada de leitura e escrita física de arquivos
│   ├── __init__.py
│   ├── medicamento_repository.py
│   ├── cliente_repository.py
│   ├── venda_repository.py
│   └── estoque_repository.py
│
├── services/                   # Camada de regras de negócio e validações
│   ├── __init__.py
│   ├── medicamento_service.py
│   ├── cliente_service.py
│   ├── estoque_service.py
│   ├── venda_service.py
│   └── relatorio_service.py
│
├── reports/                    # Relatórios exportados em formato CSV (UTF-8)
│   └── .gitkeep
│
├── tests/                      # Bateria de testes automatizados com arquivos
│   ├── __init__.py
│   ├── test_medicamento.py
│   ├── test_cliente.py
│   ├── test_estoque.py
│   ├── test_venda.py
│   └── test_relatorio.py
│
└── docs/
    └── estruturas_programacao.md
```

---

## 4. Requisitos Funcionais Implementados

- **RF01 — Cadastro de Medicamentos:** Validação de campos obrigatórios, código único, preço e data em `data/medicamentos.json`.
- **RF02 — Consulta de Medicamentos:** Busca por ID, código, categoria e pesquisa por nome (case-insensitive).
- **RF03 — Alteração de Medicamentos:** Atualização direta no arquivo JSON.
- **RF04 — Exclusão de Medicamentos:** Bloqueio de exclusão se o produto tiver vendas registradas em `vendas.json`.
- **RF05 — Controle de Estoque:** Entradas manuais gravadas em `movimentacoes.json` e atualização do estoque em `medicamentos.json`.
- **RF06 — Consulta de Estoque:** Alertas de estoque baixo (`estoque <= estoque_minimo`), zerado e validade próxima.
- **RF07 — Registro de Vendas:** Validação de disponibilidade de estoque via **laço `while`**, cálculo automático de subtotais e total, baixa atômica e gravação em `vendas.json`.
- **RF08 — Histórico de Vendas:** Consulta detalhada por ID, período e resumo financeiro.
- **RF09 — Cadastro de Clientes:** Cadastro opcional em `data/clientes.json` com exclusão protegida.
- **RF10 — Relatórios:** Dados tabulares e estatísticas de vendas.
- **RF11 — Exportação CSV:** Geração de arquivos CSV com cabeçalho e delimitador `;` em `reports/`.

---

## 5. Como Executar o Sistema

```bash
cd farmacia
python3 main.py
```

Você terá acesso ao menu interativo de terminal com todas as opções para cadastrar, consultar, registrar vendas e exportar arquivos.

---

## 6. Como Executar os Testes Automatizados

```bash
cd farmacia
python3 -m unittest discover -s tests -p "test_*.py"
```

Todos os 14 testes rodam sobre diretórios temporários isolados em memória e testam a leitura e escrita real dos arquivos.
