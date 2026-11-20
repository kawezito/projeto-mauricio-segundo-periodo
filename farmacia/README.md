# Sistema de Gerenciamento de Farmácia — Arquitetura SOLID e Desacoplada

Sistema desenvolvido em **Python 3.12+** orientado pelos princípios **SOLID**, utilizando **Inversão de Dependência (DIP)** com interfaces abstratas (`abc.ABC`), **Container de Injeção de Dependências dedicado**, **Interface do Terminal (CLI) totalmente desacoplada** e **Banco de Dados SQLite com Prepared Statements**, transações atômicas via **Unit of Work** e **Manipulação de Arquivos (CSV com UTF-8)** para a exportação de relatórios.

---

## 1. Visão Geral e Princípios SOLID Aplicados

O projeto foi desenhado para garantir total desacoplamento entre camadas:

- **S - Single Responsibility Principle (SRP / Responsabilidade Única):**
  - `models/`: Representam apenas entidades e regras estruturais de dados de domínio.
  - `repositories/`: Responsabilidade estrita de comunicação e persistência SQL.
  - `services/`: Responsabilidade estrita de orquestração de regras de negócio e validações.
  - `exporters/`: Responsabilidade exclusiva de formatação e gravação física de arquivos (CSV).
  - `database/unit_of_work.py`: Responsabilidade única de controle transacional atômico (`commit`/`rollback`).
  - `container.py`: Responsabilidade única de configuração, instanciação e amarração de dependências (Composition Root / DI Container).
  - `cli/terminal_interface.py`: Responsabilidade exclusiva da apresentação e menus interativos com o usuário no terminal.
  - `main.py`: Ponto de entrada ultra-enxuto (~20 linhas), apenas inicia o container e dispara a interface.

- **O - Open/Closed Principle (OCP / Aberto para Extensão, Fechado para Modificação):**
  - O `RelatorioService` aceita qualquer exportador que implemente `IReportExporter`. Novos formatos (JSON, Excel, PDF) não exigem alteração no serviço.
  - A interface de usuário é totalmente desacoplada: se for necessário adicionar uma interface gráfica (Tkinter) ou Web API (FastAPI), **não é preciso modificar os serviços, nem repositórios, nem o container**, bastando criar uma nova interface de apresentação.

- **L - Liskov Substitution Principle (LSP / Substituição de Liskov):**
  - As implementações concretas (`MedicamentoRepository`, `SqliteUnitOfWork`, `CsvReportExporter`) implementam estritamente os contratos abstratos (`IMedicamentoRepository`, `IUnitOfWork`, `IReportExporter`), podendo ser substituídas sem efeitos colaterais.

- **I - Interface Segregation Principle (ISP / Segregação de Interfaces):**
  - Em vez de uma interface genérica e inchada, foram criadas interfaces especialistas e coesas: `IMedicamentoRepository`, `IClienteRepository`, `IVendaRepository`, `IEstoqueRepository`, `IUnitOfWork` e `IReportExporter`.

- **D - Dependency Inversion Principle (DIP / Inversão de Dependência):**
  - Módulos de alto nível (Services) não dependem de módulos de baixo nível (SQLite / Sistema de Arquivos). Ambos dependem de abstrações (`interfaces/`).
  - `VendaService` e `EstoqueService` recebem `IUnitOfWork` e interfaces de repositórios por injeção de dependência no construtor `__init__`.

---

## 2. Estrutura de Diretórios

```text
farmacia/
│
├── main.py                     # Ponto de entrada minimalista da aplicação (~20 linhas)
├── container.py                # Container de Injeção de Dependências (Composition Root)
├── exceptions.py               # Exceções de negócio da aplicação
│
├── cli/                        # Camada de apresentação no Terminal (desacoplada da main)
│   ├── __init__.py
│   └── terminal_interface.py   # Menus interativos, validações de entrada e navegação
│
├── interfaces/                 # Abstrações e Contratos (DIP e ISP)
│   ├── __init__.py
│   ├── repositories.py         # IMedicamentoRepository, IClienteRepository, IVendaRepository, IEstoqueRepository
│   ├── transaction.py          # IUnitOfWork (Contrato de transação atômica)
│   └── exporter.py             # IReportExporter (Contrato de exportação física de relatórios)
│
├── database/                   # Infraestrutura de banco de dados
│   ├── __init__.py
│   ├── connection.py           # Fábrica de conexões SQLite e ativação de chaves estrangeiras
│   ├── schema.sql              # DDL com tabelas, integridade referencial e índices
│   └── unit_of_work.py         # Implementação concreta SqliteUnitOfWork (IUnitOfWork)
│
├── repositories/               # Implementações concretas de persistência SQLite com Prepared Statements
│   ├── __init__.py
│   ├── medicamento_repository.py
│   ├── cliente_repository.py
│   ├── estoque_repository.py
│   └── venda_repository.py
│
├── exporters/                  # Implementações concretas de manipulação física de arquivos
│   ├── __init__.py
│   └── csv_exporter.py         # CsvReportExporter (IReportExporter com UTF-8 e delimiter ';')
│
├── services/                   # Camada de negócio 100% desacoplada (depende só de interfaces)
│   ├── __init__.py
│   ├── medicamento_service.py
│   ├── cliente_service.py
│   ├── estoque_service.py
│   ├── venda_service.py
│   └── relatorio_service.py
│
├── models/                     # Entidades puras do domínio
│   ├── __init__.py
│   ├── medicamento.py
│   ├── cliente.py
│   ├── venda.py
│   ├── item_venda.py
│   └── movimentacao_estoque.py
│
├── data/                       # Armazenamento local do banco SQLite
│   └── farmacia.db
│
├── reports/                    # Relatórios CSV gerados em tempo de execução
│   └── .gitkeep
│
└── docs/                       # Documentação técnica e acadêmica
    ├── casos_de_uso_mvp.md
    └── estruturas_programacao.md
```

---

## 3. Como Executar

```bash
python3 main.py
```
