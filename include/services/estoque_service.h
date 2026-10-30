#ifndef ESTOQUE_SERVICE_H
#define ESTOQUE_SERVICE_H

#include "models/produto.h"
#include <stdbool.h>

/**
 * @file estoque_service.h
 * @brief Regras de negócio relacionadas a produtos, reposição, estoque mínimo e validade.
 */

StatusCode estoque_service_cadastrar_produto(const Produto *produto, int *id_gerado);
StatusCode estoque_service_atualizar_produto(const Produto *produto);
StatusCode estoque_service_remover_produto(int id);
StatusCode estoque_service_adicionar_estoque(int produto_id, int quantidade_adicional);

/* Validações e verificações de negócio */
bool estoque_service_is_vencido(const char *data_validade);
bool estoque_service_is_proximo_vencimento(const char *data_validade, int dias_limite);
bool estoque_service_tem_estoque_suficiente(int produto_id, int quantidade_desejada);
StatusCode estoque_service_listar_em_alerta(Produto **lista, int *quantidade);

#endif /* ESTOQUE_SERVICE_H */
