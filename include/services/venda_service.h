#ifndef VENDA_SERVICE_H
#define VENDA_SERVICE_H

#include "models/venda.h"

/**
 * @file venda_service.h
 * @brief Regras de negócio relacionadas à efetivação de vendas, cálculos e consistência.
 */

/* Inicialização de uma nova venda em memória antes da finalização */
void venda_service_iniciar(Venda *venda, int cliente_id, const char *cliente_nome);
StatusCode venda_service_adicionar_item(Venda *venda, int produto_id, int quantidade);
StatusCode venda_service_remover_item(Venda *venda, int indice_item);
double venda_service_calcular_total(const Venda *venda, double desconto_percentual);

/* Conclusão: valida estoque de cada item, decrementa estoque e salva venda */
StatusCode venda_service_finalizar(Venda *venda, double desconto, int *venda_id_gerada);

#endif /* VENDA_SERVICE_H */
