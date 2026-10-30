#ifndef VENDA_REPO_H
#define VENDA_REPO_H

#include "models/venda.h"

/**
 * @file venda_repo.h
 * @brief Contrato de persistência para as operações com vendas e seus itens.
 */

StatusCode venda_repo_registrar(const Venda *venda, int *id_gerado);
StatusCode venda_repo_listar_todas(Venda **lista, int *quantidade);
StatusCode venda_repo_buscar_por_id(int id, Venda *saida);
StatusCode venda_repo_listar_itens(int venda_id, ItemVenda **itens, int *quantidade);

#endif /* VENDA_REPO_H */
