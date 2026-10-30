#ifndef CLIENTE_SERVICE_H
#define CLIENTE_SERVICE_H

#include "models/cliente.h"
#include <stdbool.h>

/**
 * @file cliente_service.h
 * @brief Regras de negócio e validações cadastrais para clientes da farmácia.
 */

bool cliente_service_validar_cpf(const char *cpf);
StatusCode cliente_service_cadastrar(const Cliente *cliente, int *id_gerado);
StatusCode cliente_service_buscar_por_termo(const char *termo, Cliente **lista, int *quantidade);

#endif /* CLIENTE_SERVICE_H */
