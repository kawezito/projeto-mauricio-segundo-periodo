# Sistema de Farmácia Desktop (Inspirado na Rede Pague Menos)

Sistema de gestão farmacêutica desktop desenvolvido em **Linguagem C** com interface gráfica **GTK**.

---

## 1. Visão Geral

O projeto visa simular as principais operações do dia a dia de uma farmácia moderna, como controle de estoque de medicamentos, monitoramento de validade, cadastro de clientes, vínculo com fornecedores e ponto de venda (PDV) com cálculo de totais e histórico de transações.

---

## 2. Tecnologias Utilizadas

- **Linguagem:** C (C99 ou C11)
- **Interface Gráfica:** GTK (GTK 3 / GTK 4 via `pkg-config`)
- **Build System:** `Makefile`
- **Controle de Versão:** Git
- **Persistência de Dados (Recomendado):** SQLite3 (ou arquivos binários estruturados `FILE*`, dependendo da exigência acadêmica)

---

## 3. Estrutura de Diretórios

```text
.
├── Makefile                     # Script de compilação da aplicação
├── README.md                    # Apresentação do projeto e instruções
├── .gitignore                   # Arquivos ignorados pelo Git
├── docs/                        # Documentação de requisitos e arquitetura
│   ├── requisitos.md            # Especificação dos requisitos funcionais e não funcionais
│   └── arquitetura.md           # Decisões arquiteturais, módulos e fluxo de dados
├── include/                     # Arquivos de cabeçalho (.h)
│   ├── common.h                 # Constantes globais, enums de status e tipos utilitários
│   ├── models/                  # Definições das structs das entidades do sistema
│   │   ├── produto.h
│   │   ├── cliente.h
│   │   ├── fornecedor.h
│   │   ├── venda.h
│   │   └── item_venda.h
│   ├── repositories/            # Contratos de persistência e acesso a dados
│   │   ├── produto_repo.h
│   │   ├── cliente_repo.h
│   │   ├── fornecedor_repo.h
│   │   └── venda_repo.h
│   ├── services/                # Contratos das regras de negócio e validações
│   │   ├── estoque_service.h
│   │   ├── venda_service.h
│   │   └── cliente_service.h
│   └── ui/                      # Contratos para criação e renderização de janelas GTK
│       ├── main_window.h
│       ├── produtos_view.h
│       ├── vendas_view.h
│       └── clientes_view.h
├── src/                         # Implementação do código-fonte (.c)
│   ├── main.c                   # Ponto de entrada (inicialização do GTK e loop principal)
│   ├── models/                  # Funções de criação/destruição de modelos (se necessário)
│   ├── repositories/            # Implementação do acesso aos dados (SQL / arquivos)
│   ├── services/                # Implementação das regras de negócio
│   └── ui/                      # Telas, diálogos e callbacks da interface GTK
└── data/                        # Diretório para armazenamento do banco SQLite ou arquivos
```

Consulte os arquivos na pasta [docs/](file:///home/kawe/Área de trabalho/Projetos SI/Projeto Do Mauricio/docs) para detalhes completos de requisitos e arquitetura.
