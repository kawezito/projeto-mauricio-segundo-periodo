#ifndef ITEM_VENDA_H
#define ITEM_VENDA_H

#include "common.h"

/**
 * @file item_venda.h
 * @brief Estrutura de dados que representa um item individual pertencente a uma venda.
 */

typedef struct {
    int id;
    int venda_id;
    int produto_id;
    char nome_produto[TAM_NOME];
    int quantidade;
    double preco_unitario;
    double subtotal;
} ItemVenda;

#endif /* ITEM_VENDA_H */
