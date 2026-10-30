#ifndef PRODUTO_REPO_H
#define PRODUTO_REPO_H

#include "models/produto.h"

/**
 * @file produto_repo.h
 * @brief Contrato de persistência para as operações com produtos e medicamentos.
 */

StatusCode produto_repo_inserir(const Produto *produto, int *id_gerado);
StatusCode produto_repo_atualizar(const Produto *produto);
StatusCode produto_repo_excluir(int id);
StatusCode produto_repo_buscar_por_id(int id, Produto *saida);
StatusCode produto_repo_buscar_por_codigo(const char *codigo, Produto *saida);
StatusCode produto_repo_listar_todos(Produto **lista, int *quantidade);
StatusCode produto_repo_buscar_por_nome(const char *termo, Produto **lista, int *quantidade);
StatusCode produto_repo_atualizar_estoque(int id, int nova_quantidade);

#endif /* PRODUTO_REPO_H */
