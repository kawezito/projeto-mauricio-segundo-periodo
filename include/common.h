#ifndef COMMON_H
#define COMMON_H

/**
 * @file common.h
 * @brief Tipos comuns, códigos de status/erro e constantes globais do sistema.
 */

/* Códigos de retorno padronizados para serviços e repositórios */
typedef enum {
    STATUS_OK = 0,
    ERR_GENERICO = -1,
    ERR_NAO_ENCONTRADO = -2,
    ERR_DADO_INVALIDO = -3,
    ERR_ESTOQUE_INSUFICIENTE = -4,
    ERR_PRODUTO_VENCIDO = -5,
    ERR_BANCO_DADOS = -6,
    ERR_REGISTRO_DUPLICADO = -7
} StatusCode;

/* Limites de tamanho para strings e buffers */
#define MAX_NOME 50
#define MAX_SOBRENOME 50
#define MAX_CPF 16
#define MAX_RG 16
#define MAX_EMAIL 80
#define MAX_TELEFONE 20
#define MAX_ENDERECO 120
#define MAX_NUMERO 10
#define MAX_BAIRRO 50
#define MAX_CIDADE 50
#define MAX_ESTADO 4
#define MAX_CEP 12

#define TAM_DESCRICAO 255
#define TAM_CODIGO 32
#define TAM_CNPJ 20
#define TAM_DATA 11 /* Formato YYYY-MM-DD */

#endif /* COMMON_H */