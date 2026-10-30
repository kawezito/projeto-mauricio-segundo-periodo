#ifndef FORNECEDOR_REPO_H
#define FORNECEDOR_REPO_H

#include "models/fornecedor.h"

/**
 * @file fornecedor_repo.h
 * @brief Contrato de persistência para as informações de fornecedores/distribuidores.
 */

StatusCode fornecedor_repo_inserir(const Fornecedor *fornecedor, int *id_gerado);
StatusCode fornecedor_repo_buscar_por_id(int id, Fornecedor *saida);
StatusCode fornecedor_repo_listar_todos(Fornecedor **lista, int *quantidade);

#endif /* FORNECEDOR_REPO_H */
