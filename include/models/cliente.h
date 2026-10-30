#ifndef CLIENTE_H
#define CLIENTE_H

#include "common.h"

/**
 * @file cliente.h
 * @brief Estrutura de dados que representa o cliente da farmácia.
 */

typedef struct {
    int id;
    char nome[MAX_NOME];
    char sobrenome[MAX_SOBRENOME];
    char cpf[MAX_CPF];
    char rg[MAX_RG];
    char email[MAX_EMAIL];
    char telefone[MAX_TELEFONE];
    char endereco[MAX_ENDERECO];
    char numero[MAX_NUMERO];
    char bairro[MAX_BAIRRO];
    char cidade[MAX_CIDADE];
    char estado[MAX_ESTADO];
    char cep[MAX_CEP];
} Cliente;

#endif /* CLIENTE_H */
