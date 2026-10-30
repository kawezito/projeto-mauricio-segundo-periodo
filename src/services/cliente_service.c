#include "../../include/services/cliente_service.h"
#include "../../include/repositories/cliente_repo.h"

#include <string.h>
#include <ctype.h>
#include <stdlib.h>
#include <stdbool.h>

/**
 * @file cliente_service.c
 * @brief Regras de negócio e validações cadastrais para clientes da farmácia.
 */

/**
 * @brief Valida o algoritmo oficial do CPF (Dígitos verificadores - Módulo 11).
 * Aceita tanto "12345678900" quanto "123.456.789-00".
 */
bool cliente_service_validar_cpf(const char *cpf) {
    if (cpf == NULL) return false;

    // 1. Extrai apenas os números do CPF (remove pontos e traços)
    char digitos[12];
    int j = 0;
    for (int i = 0; cpf[i] != '\0' && j < 11; i++) {
        if (isdigit(cpf[i])) {
            digitos[j++] = cpf[i];
        }
    }
    digitos[j] = '\0';

    // Precisa ter exatamente 11 dígitos numéricos
    if (j != 11) return false;

    // 2. Rejeita CPFs com todos os dígitos repetidos (ex: "11111111111")
    bool todos_iguais = true;
    for (int i = 1; i < 11; i++) {
        if (digitos[i] != digitos[0]) {
            todos_iguais = false;
            break;
        }
    }
    if (todos_iguais) return false;

    // 3. Cálculo do primeiro dígito verificador
    int soma = 0;
    for (int i = 0; i < 9; i++) {
        soma += (digitos[i] - '0') * (10 - i);
    }
    int resto = (soma * 10) % 11;
    if (resto == 10 || resto == 11) resto = 0;
    if (resto != (digitos[9] - '0')) return false;

    // 4. Cálculo do segundo dígito verificador
    soma = 0;
    for (int i = 0; i < 10; i++) {
        soma += (digitos[i] - '0') * (11 - i);
    }
    resto = (soma * 10) % 11;
    if (resto == 10 || resto == 11) resto = 0;
    if (resto != (digitos[10] - '0')) return false;

    return true; // CPF válido!
}

/**
 * @brief Aplica regras de negócio antes de cadastrar o cliente no banco.
 */
int cliente_service_cadastrar(const Cliente *cliente, int *id_gerado) {
    if (cliente == NULL) {
        return ERR_DADO_INVALIDO;
    }

    // Regra 1: Nome e Sobrenome não podem ser vazios
    if (strlen(cliente->nome) == 0 || strlen(cliente->sobrenome) == 0) {
        return ERR_DADO_INVALIDO;
    }

    // Regra 2: CPF deve ser válido pelo algoritmo oficial
    if (!cliente_service_validar_cpf(cliente->cpf)) {
        return ERR_DADO_INVALIDO;
    }

    // Regra 3: Não pode existir outro cliente com o mesmo CPF
    Cliente existente;
    if (cliente_repo_buscar_por_cpf(cliente->cpf, &existente) == STATUS_OK) {
        return ERR_REGISTRO_DUPLICADO;
    }

    // Passou por todas as validações de negócio, repassa para o repositório gravar
    return cliente_repo_inserir(cliente, id_gerado);
}

/**
 * @brief Busca clientes por termo (se termo estiver vazio, lista todos).
 */
int cliente_service_buscar_por_termo(const char *termo, Cliente **lista, int *quantidade) {
    if (lista == NULL || quantidade == NULL) {
        return ERR_DADO_INVALIDO;
    }

    // Se o usuário não digitou nada na busca, lista todos os clientes cadastrados
    if (termo == NULL || strlen(termo) == 0) {
        return cliente_repo_listar_todos(lista, quantidade);
    }

    // Caso contrário, busca por nome/sobrenome
    return cliente_repo_buscar_por_nome(termo, lista, quantidade);
}
