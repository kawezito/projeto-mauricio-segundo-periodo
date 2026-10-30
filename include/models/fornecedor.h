#ifndef FORNECEDOR_H
#define FORNECEDOR_H

#include "common.h"

/**
 * @file fornecedor.h
 * @brief Estrutura de dados que representa o fornecedor/laboratório farmacêutico.
 */

typedef struct {
    int id;
    char razao_social[TAM_NOME];
    char cnpj[TAM_CNPJ];
    char telefone[TAM_TELEFONE];
    char contato[TAM_NOME];
} Fornecedor;

#endif /* FORNECEDOR_H */
