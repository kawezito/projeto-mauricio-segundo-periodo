#ifndef VENDA_H
#define VENDA_H

#include "common.h"
#include "item_venda.h"

/**
 * @file venda.h
 * @brief Estrutura de dados que representa uma transação de venda finalizada no PDV.
 */

#define MAX_ITENS_VENDA 100

typedef struct {
    int id;
    int cliente_id;                  /* Opcional (0 para cliente não identificado) */
    char cliente_nome[TAM_NOME];
    char data_hora[20];              /* Formato YYYY-MM-DD HH:MM:SS */
    double valor_total;
    double desconto;
    ItemVenda itens[MAX_ITENS_VENDA];
    int total_itens;
} Venda;

#endif /* VENDA_H */
