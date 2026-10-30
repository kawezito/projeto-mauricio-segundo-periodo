#include "../../include/models/cliente.h"
#include <string.h>

// Limpar Struct
void cliente_inicializar(Cliente *c) {
    c->id = 0;
    c->nome[0] = '\0';
    c->sobrenome[0] = '\0';
    c->cpf[0] = '\0';
    c->rg[0] = '\0';
    c->email[0] = '\0';
    c->telefone[0] = '\0';
    c->endereco[0] = '\0';
    c->numero[0] = '\0';
    c->bairro[0] = '\0';
    c->cidade[0] = '\0';
    c->estado[0] = '\0';
    c->cep[0] = '\0';
}