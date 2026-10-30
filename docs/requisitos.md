# Especificação de Requisitos do Sistema

Este documento reúne os requisitos funcionais e não funcionais do Sistema Desktop de Farmácia (Inspirado na Rede Pague Menos), modelado para ser implementado em **Linguagem C** com interface gráfica **GTK**.

---

## 1. Requisitos Funcionais (RF)

Os requisitos funcionais definem as ações, fluxos de dados e comportamentos que o sistema deve oferecer aos usuários (operadores de caixa, atendentes e gerentes farmacêuticos).

### Módulo: Gestão de Produtos e Medicamentos
- **RF01 - Cadastro de Produtos:** O sistema deve permitir o cadastro de novos medicamentos/produtos, contendo no mínimo: código (ou código de barras), nome comercial, princípio ativo/descrição, fabricante/fornecedor, preço de custo, preço unitário de venda, data de validade e quantidade inicial em estoque.
- **RF02 - Consulta e Listagem de Produtos:** O sistema deve permitir a visualização tabulada dos produtos cadastrados, exibindo seus dados principais.
- **RF03 - Edição de Produtos:** O sistema deve possibilitar a alteração de dados cadastrais de um produto previamente registrado (por exemplo: preço de venda, nome e lote).
- **RF04 - Exclusão de Produtos:** O sistema deve permitir a remoção lógica ou física de um produto, impedindo a exclusão caso existam registros de vendas atrelados para manter a consistência histórica.
- **RF05 - Pesquisa Rápida de Produtos:** O sistema deve disponibilizar busca ágil de produtos por **nome** (busca parcial/prefixo) ou por **código identificador**.

### Módulo: Controle de Estoque e Validade
- **RF06 - Controle de Quantidade em Estoque:** O sistema deve manter atualizada a quantidade de unidades disponíveis de cada produto, decrementando o estoque no ato da venda e permitindo incremento por reposição.
- **RF07 - Alerta de Estoque Mínimo:** O sistema deve sinalizar visualmente produtos com quantidade abaixo de um limite pré-definido (ex.: menos de 5 unidades).
- **RF08 - Controle de Validade:** O sistema deve permitir monitorar as datas de vencimento dos medicamentos, sinalizando produtos vencidos ou próximos do vencimento (ex.: vencendo nos próximos 30 dias) e bloqueando sua inclusão em novas vendas.

### Módulo: Gestão de Clientes e Fornecedores
- **RF09 - Cadastro de Clientes:** O sistema deve permitir registrar clientes com dados básicos: código/ID, nome completo, CPF/documento, telefone e e-mail (possibilitando vincular a venda para programas de fidelidade, comum na rede Pague Menos).
- **RF10 - Consulta de Clientes:** O sistema deve possibilitar a busca e visualização de clientes cadastrados por nome ou CPF.
- **RF11 - Registro de Fornecedores:** O sistema deve permitir o registro básico de informações de fornecedores/laboratórios (ID, razão social, CNPJ e telefone de contato), vinculando os produtos aos seus respectivos distribuidores.

### Módulo: Ponto de Venda (PDV) e Vendas
- **RF12 - Registro de Venda:** O sistema deve permitir a abertura de uma venda, adição de múltiplos itens (produtos e quantidades), associação opcional a um cliente e finalização da operação.
- **RF13 - Cálculo Automático do Total:** O sistema deve calcular dinamicamente o subtotal por item (preço unitário × quantidade) e o valor total acumulado da venda, suportando eventuais descontos.
- **RF14 - Validação de Disponibilidade:** O sistema deve validar se a quantidade solicitada na venda está disponível em estoque antes de autorizar a inclusão do item.
- **RF15 - Histórico e Consulta de Vendas:** O sistema deve permitir a consulta às vendas já realizadas, exibindo identificador da venda, data/hora, cliente, valor total e a lista detalhada dos itens comercializados.

---

## 2. Requisitos Não Funcionais (RNF)

Os requisitos não funcionais determinam a qualidade, desempenho, usabilidade e restrições arquiteturais da aplicação.

### RNF01 - Usabilidade e Interface Gráfica
- A interface deve ser desenvolvida em **GTK**, com janelas e diálogos organizados de forma clara e intuitiva.
- Deve fornecer mensagens de feedback ao usuário (confirmações de salvamento, diálogos de erro para estoque insuficiente ou campos obrigatórios vazios).
- O fluxo de tela do PDV deve ser rápido, minimizando cliques e permitindo operação ágil pelo teclado.

### RNF02 - Organização e Modularidade do Código
- O código-fonte deve ser modularizado em C, respeitando estritamente a separação entre:
  - **Models:** estruturas de dados puras (`struct`).
  - **Repositories:** rotinas de leitura e escrita de dados.
  - **Services:** regras de negócio, cálculos e validações.
  - **UI:** montagem dos componentes visuais e callbacks do GTK.
- Não deve haver código de interface dentro dos repositórios, nem regras de negócio pesadas dentro dos callbacks de clique de botão.

### RNF03 - Manutenibilidade e Legibilidade
- Nomes de funções e variáveis em padrão claro e padronizado (snake_case com prefixos por módulo, ex.: `produto_repo_salvar()`, `venda_service_calcular_total()`).
- Divisão rigorosa em arquivos de cabeçalho (`.h`) com protótipos de funções e arquivos de implementação (`.c`).
- Compilação limpa gerenciada via `Makefile`, sem dependências circulares.

### RNF04 - Confiabilidade e Integridade dos Dados
- Tratamento explícito de ponteiros nulos (`NULL`) e gerenciamento seguro de memória (`malloc`/`free`) para evitar vazamentos de memória (*memory leaks*).
- Validação das entradas antes de persistir (valores não negativos, datas válidas, strings não vazias).
- Garantia de que a venda e a baixa do estoque ocorram de forma atômica/consistente (se falhar uma etapa, a transação não deve corromper os dados).

### RNF05 - Desempenho e Ambiente de Execução
- A aplicação deve ser leve, com tempo de resposta imperceptível nas buscas e cadastros locais.
- Compatibilidade primária com sistemas Linux desktop com suporte ao GTK 3 / 4.
