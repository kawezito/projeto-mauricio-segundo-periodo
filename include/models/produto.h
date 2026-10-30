#ifndef PRODUTO_H
#define PRODUTO_H

#include "common.h"

/**
 * @file produto.h
 * @brief Estrutura de dados que representa um medicamento ou produto da farmácia.
 */

typedef struct {
    int id;                          /* Identificador único no banco */
    char codigo_barras[TAM_CODIGO];  /* Código de barras / identificação rápida */
    char nome[TAM_NOME];             /* Nome comercial do medicamento */
    char principio_ativo[TAM_NOME];  /* Princípio ativo / descrição */
    int fornecedor_id;               /* ID do fornecedor/laboratório */
    double preco_custo;              /* Preço de aquisição */
    double preco_venda;              /* Preço de venda ao consumidor */
    int quantidade_estoque;          /* Saldo em estoque */
    int estoque_minimo;              /* Limite para alerta de reposição */
    char data_validade[TAM_DATA];    /* Data de validade (YYYY-MM-DD) */
} Produto;

#endif /* PRODUTO_H */
