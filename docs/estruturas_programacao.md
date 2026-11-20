# Mapeamento das Estruturas de Programação Obrigatórias e Princípios SOLID

Este documento serve como guia para a apresentação acadêmica do projeto, indicando exatamente onde cada conceito exigido e os princípios SOLID foram implementados.

---

## 1. Mapeamento das Estruturas de Programação Obrigatórias (1,0 ponto cada)

| Estrutura Exigida | Arquivo Onde Foi Implementada | Função / Método Correspondente | Explicação Didática da Utilização |
| :--- | :--- | :--- | :--- |
| **Condicionais (`if/else`)** | `farmacia/services/medicamento_service.py`<br>`farmacia/services/venda_service.py` | `cadastrar()`, `atualizar()`<br>`registrar_venda()` | Validação de campos obrigatórios, bloqueio de preços ou estoque negativos, detecção de estoque insuficiente e verificação de vencimento. |
| **Comando de Seleção (`match/case` / `switch`)** | `farmacia/cli/terminal_interface.py` | Todos os métodos `menu_*()` e `iniciar()` | Implementação moderna do `switch/case` em Python (PEP 634), roteando opções de navegação e comandos do usuário. |
| **Laço `while` (Caso Real)** | `farmacia/services/venda_service.py`<br>`farmacia/cli/terminal_interface.py` | `registrar_venda()`<br>`menu_*()` | Processamento sequencial e ordenado dos itens do carrinho de compras e laço contínuo dos menus da CLI. |
| **Laço `for`** | `farmacia/services/relatorio_service.py`<br>`farmacia/services/venda_service.py` | `gerar_matriz_estoque()`<br>`registrar_venda()` | Iteração sobre listas de medicamentos e vendas para tabulação de dados e baixa atômica de estoque. |
| **Subprogramas / Funções** | Em todos os arquivos de `services/`, `repositories/` e `cli/` | Múltiplos métodos modulares | Divisão de responsabilidades com funções curtas e reutilizáveis (ex: `buscar_por_id`, `registrar_entrada`, `exportar`). |
| **Listas** | `farmacia/models/venda.py`<br>`farmacia/services/venda_service.py` | `self.itens`, carrinho | Armazenamento dinâmico dos itens da venda e listas de medicamentos retornadas pelas consultas. |
| **Matrizes (`list[list]`)** | `farmacia/services/relatorio_service.py` | `gerar_matriz_estoque()`<br>`gerar_matriz_vendas()` | Montagem de grade bidimensional (cabeçalho na linha 0 e dados nas linhas subsequentes) para tabulação e exportação. |
| **Cadeias de Caracteres (`strings`)** | `farmacia/repositories/medicamento_repository.py`<br>`farmacia/services/medicamento_service.py` | `buscar_por_nome()`<br>`_validar_data()` | Uso de `.strip()`, `.lower()`, formatações de data ISO 8601 e buscas com `LIKE` insensíveis a maiúsculas/minúsculas. |
| **Estruturas (Dicionários/Tuplas)** | `farmacia/models/*.py`<br>`farmacia/repositories/*.py` | `to_dict()`<br>`cursor.execute(sql, (...))` | Dicionários em `to_dict()`, tuplas nos parâmetros das Prepared Statements (`cursor.execute(sql, (params,))`). |
| **Manipulação de Arquivos (`csv`)** | `farmacia/exporters/csv_exporter.py` | `exportar()` | Abertura (`open()`) e escrita física com `csv.writer(..., delimiter=';')` em formato UTF-8, gravando os arquivos na pasta `reports/` (1,0 ponto do requisito). |
| **Banco de Dados Relacional (SQLite + Prepared Statements)** | `farmacia/database/`<br>`farmacia/repositories/*.py` | `get_connection()`<br>`init_db()`<br>`cursor.execute(sql, (params,))` | Persistência com integridade referencial (FK), controle transacional com Unit of Work e parametrização segura (`?`). |

---

## 2. Mapeamento dos Princípios SOLID

| Princípio | Onde Foi Aplicado | Demonstração Prática |
| :--- | :--- | :--- |
| **S - Single Responsibility (SRP)** | Toda a estrutura modular | `models` apenas estruturam dados; `repositories` apenas executam SQL; `services` apenas tratam regras de negócio; `exporters` apenas gravam arquivos em disco; `container.py` apenas injeta dependências; `cli` apenas cuida da tela. |
| **O - Open/Closed (OCP)** | `services/relatorio_service.py`<br>`interfaces/exporter.py` | Aberto para novos formatos de relatório (JSON, Excel, PDF) implementando `IReportExporter`, sem modificar o código do serviço. |
| **L - Liskov Substitution (LSP)** | `repositories/*.py`<br>`database/unit_of_work.py` | As classes concretas implementam estritamente as classes abstratas base (`IMedicamentoRepository`, `IUnitOfWork`), podendo ser trocadas sem quebrar o sistema. |
| **I - Interface Segregation (ISP)** | `interfaces/repositories.py` | Interfaces coesas e segregadas por domínio (`IMedicamentoRepository`, `IClienteRepository`, `IVendaRepository`, `IEstoqueRepository`), sem forçar métodos não utilizados. |
| **D - Dependency Inversion (DIP)** | `services/*.py`<br>`container.py` | Serviços dependem exclusivamente de interfaces abstratas (`ABC`). Nenhum serviço importa `sqlite3` ou classes concretas de repositório. As dependências são injetadas centralizadamente pelo `Container`. |
