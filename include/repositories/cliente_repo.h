#ifndef CLIENTE_REPO_H
#define CLIENTE_REPO_H

#include "models/cliente.h"
#include <sqlite3.h>

/**
 * @file cliente_repo.h
 * @brief Contrato de persistência para as operações com clientes.
 */

void cliente_repo_inicializar(sqlite3 *conexao);
StatusCode cliente_repo_inserir(const Cliente *cliente, int *id_gerado);
StatusCode cliente_repo_buscar_por_id(int id, Cliente *saida);
StatusCode cliente_repo_buscar_por_cpf(const char *cpf, Cliente *saida);
StatusCode cliente_repo_listar_todos(Cliente **lista, int *quantidade);
StatusCode cliente_repo_buscar_por_nome(const char *termo, Cliente **lista, int *quantidade);

#endif /* CLIENTE_REPO_H */
