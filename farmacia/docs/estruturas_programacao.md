# Mapeamento das Estruturas de Programação Obrigatórias

Este documento serve como guia rápido para a apresentação acadêmica do projeto, indicando exatamente onde cada conceito exigido pelo professor foi implementado.

| Estrutura Exigida | Arquivo Onde Foi Implementada | Função / Método Correspondente | Explicação Didática da Utilização |
| :--- | :--- | :--- | :--- |
| **Condicionais (`if/else`)** | `services/medicamento_service.py`<br>`services/venda_service.py` | `cadastrar()`, `atualizar()`<br>`registrar_venda()` | Utilizado para validação de campos obrigatórios, bloqueio de preços ou estoque negativos, detecção de estoque insuficiente e verificação de vencimento. |
| **Laço `while` (Caso Real)** | `services/venda_service.py` | `registrar_venda()` | Processamento sequencial e ordenado dos itens contidos no carrinho de compras, acumulando demandas e subtotais item a item. |
| **Laço `for`** | `services/relatorio_service.py`<br>`services/venda_service.py` | `gerar_matriz_estoque()`<br>`registrar_venda()` | Utilizado para percorrer listas de medicamentos e vendas para montagem de relatórios e baixa atômica de estoque. |
| **Subprogramas / Funções** | Em todos os arquivos de `services/` e `repositories/` | Múltiplos métodos modulares | Divisão clara de responsabilidades com métodos curtos e reutilizáveis (ex: `buscar_por_id`, `registrar_entrada`, `exportar_csv`). |
| **Listas** | `models/venda.py`<br>`services/venda_service.py` | `self.itens`, carrinho | Armazenamento dinâmico dos itens da venda e listas de medicamentos retornadas pelas consultas. |
| **Matrizes (`list[list]`)** | `services/relatorio_service.py` | `gerar_matriz_estoque()`<br>`gerar_matriz_vendas()` | Montagem de uma grade bidimensional (cabeçalho na linha 0 e dados nas linhas subsequentes) para tabulação e exportação. |
| **Cadeias de Caracteres (`strings`)** | `repositories/medicamento_repository.py`<br>`services/medicamento_service.py` | `buscar_por_nome()`<br>`_validar_data()` | Uso de `.strip()`, `.lower()`, formatações de data ISO 8601 e buscas com `LIKE` insensíveis a maiúsculas/minúsculas. |
| **Estruturas (Dicionários)** | `models/*.py`<br>`services/relatorio_service.py` | `to_dict()`<br>`relatorio_estoque_atual()` | Transporte de informações estruturadas entre camadas e preparação dos dados que serão consumidos pela futura interface Tkinter. |
| **Manipulação de Arquivos (`csv` e `json`)**| `services/relatorio_service.py`<br>`services/arquivo_service.py` | `exportar_matriz_para_csv()`<br>`_salvar_json()` | Criação e escrita física de relatórios em CSV (UTF-8 com delimitador `;`) e persistência simultânea de todo o estado do sistema em arquivos `.json` na pasta `data/`. |

