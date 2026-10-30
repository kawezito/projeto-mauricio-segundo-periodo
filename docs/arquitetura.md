# Documento de Arquitetura e Decisões de Projeto

Este documento detalha o desenho arquitetural do sistema de farmácia, a justificativa das tecnologias escolhidas, o fluxo de comunicação entre camadas e o roteiro sugerido para a implementação futura.

---

## 1. Decisão Tecnológica: Camada de Persistência

Para um sistema desenvolvido em **Linguagem C**, temos duas abordagens principais de persistência para o contexto acadêmico:

### Opção 1 (Recomendada): SQLite3 (`libsqlite3-dev`)
- **Justificativa:** 
  - O SQLite é uma biblioteca embutida (*serverless*), escrita em C puro, que armazena todo o banco de dados em um único arquivo local (`data/farmacia.db`).
  - Não requer instalação ou configuração de servidores de banco (como MySQL ou PostgreSQL).
  - Garante integridade referencial via chaves estrangeiras (ex.: evitar exclusão de produto vendido, integridade dos itens de venda).
  - Facilita buscas eficientes por nome (`LIKE '%...%'`) e ordenações por validade com queries simples.
- **Instalação no Linux:** `sudo apt-get install libsqlite3-dev` e linkagem com `-lsqlite3`.

### Opção 2 (Alternativa Acadêmica): Arquivos Binários / Estruturados (`FILE*`, `fread`, `fwrite`)
- **Justificativa:**
  - Caso o professor ou a ementa da disciplina exija especificamente o uso de manipulação direta de arquivos em C sem dependências externas.
  - Gravação de structs diretamente em disco (`data/produtos.dat`, `data/vendas.dat`).
- **Nota de Design:** Graças à camada `repositories/`, a substituição entre SQLite e arquivos binários é transparente para o restante do sistema: apenas o código dentro de `repositories/*.c` precisará ser ajustado, mantendo a UI e os Services intactos.

---

## 2. Padrão Arquitetural e Fluxo de Comunicação

O sistema adota uma arquitetura em **Camadas (Layered Architecture)** adaptada para C procedural estruturado:

```
[ Interface Gráfica (GTK) ]  <-- Captura eventos do usuário e exibe dados
         │
         ▼
[ Camada de Serviços (Services) ] <-- Validações, cálculos e regras de negócio
         │
         ▼
[ Camada de Repositórios (Repositories) ] <-- CRUD e persistência (SQLite / Arquivo)
         │
         ▼
[ Modelos / Entidades (Models) ] <-- Structs compartilhadas entre todas as camadas
```

### Regras de Separação de Responsabilidades:
1. **Models (`include/models/`):** Apenas declarações de `struct` (ex: `Produto`, `Cliente`, `Venda`, `ItemVenda`). Não conhecem telas nem banco.
2. **Repositories (`include/repositories/` e `src/repositories/`):** Realizam apenas operações diretas de I/O de dados (ex: `produto_repo_inserir()`, `produto_repo_buscar_por_id()`). Não devem ter validações de tela ou regras de negócio.
3. **Services (`include/services/` e `src/services/`):** Coordenam a lógica:
   - Exemplo: Antes de registrar venda, o `venda_service` consulta o estoque via `produto_repo`, verifica se o produto está vencido, calcula os totais com desconto, salva a venda via `venda_repo` e dá baixa no estoque.
4. **UI (`include/ui/` e `src/ui/`):** Constrói janelas, botões, tabelas (`GtkTreeView` ou `GtkColumnView`) e diálogos. Seus callbacks apenas chamam funções de `Services`, recebem o código de retorno/status e exibem mensagens amigáveis na tela.

---

## 3. Roteiro Sugerido de Implementação (Passo a Passo)

Para programar o sistema de forma incremental, segura e sem sobrecarga, recomenda-se a seguinte sequência:

### Fase 1: Fundação e Modelos de Dados
1. Definir as structs em `include/models/` (`produto.h`, `cliente.h`, `fornecedor.h`, `venda.h`, `item_venda.h`).
2. Criar `include/common.h` com códigos de erro/retorno universais (`STATUS_OK`, `ERR_ESTOQUE_INSUFICIENTE`, `ERR_PRODUTO_VENCIDO`, etc.).
3. Configurar o `Makefile` básico para compilar o executável com as flags do GTK (`pkg-config --cflags --libs gtk+-3.0` ou `gtk4`).

### Fase 2: Camada de Persistência (Repositories)
1. Implementar o repositório de produtos e fornecedores (`produto_repo.c`, `fornecedor_repo.c`).
2. Implementar o repositório de clientes (`cliente_repo.c`).
3. Criar testes simples via linha de comando ou funções em `main.c` para certificar que os dados são salvos e recuperados corretamente.

### Fase 3: Regras de Negócio (Services)
1. Implementar `estoque_service.c` (validação de entrada de produtos, verificação de datas de validade e alertas de estoque mínimo).
2. Implementar `venda_service.c` (cálculo de totais, verificação de disponibilidade, baixa de estoque e montagem da transação de venda).

### Fase 4: Interface Gráfica Básica (GTK)
1. Montar a janela principal (`main_window.c`) com menu de navegação ou abas (Notebook) para:
   - Produtos / Estoque
   - Vendas (PDV)
   - Clientes
   - Histórico
2. Implementar a tela de listagem e formulário de cadastro/edição de produtos (`produtos_view.c`).
3. Implementar tela de cadastro e busca de clientes (`clientes_view.c`).

### Fase 5: Ponto de Venda (PDV) e Histórico
1. Implementar a tela de vendas (`vendas_view.c`) com campo de busca de produto por código/nome, tabela de itens adicionados e exibição do valor total em tempo real.
2. Integrar a finalização da venda com emissão de diálogo de sucesso e baixa no estoque.
3. Implementar a tela de consulta ao histórico de vendas e detalhes de itens.

### Fase 6: Polimento e Tratamento de Erros
1. Adicionar filtros visuais (destaque para remédios próximos da data de vencimento).
2. Checagem de vazamentos de memória com `valgrind`.
3. Ajustes cosméticos e usabilidade na interface GTK.
