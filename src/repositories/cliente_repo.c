#include "../../include/repositories/cliente_repo.h"
#include "../../include/repositories/database.h"

#include <sqlite3.h>
#include <stdio.h>
#include <stdlib.h>

/**
 * @file cliente_repo.c
 * @brief Contrato de persistência para as operações com os clientes
 */

static sqlite3 *db = NULL;

void cliente_repo_inicializar(sqlite3 *conexao)
{
    db = conexao;
}

int cliente_repo_inserir(const Cliente *cliente, int *id_gerado)
{
    if (!db)
        return ERR_BANCO_DADOS;

    const char *sql = "INSERT INTO clientes ("
                      "   nome, sobrenome, cpf, rg, email, telefone, "
                      "   endereco, numero, bairro, cidade, estado, cep"
                      ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);";
    sqlite3_stmt *stmt;

    // Preparação da Query
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK)
    {
        return ERR_BANCO_DADOS;
    }

    // 3. Vincula os valores de forma 100% segura (Bind)
    // O índice começa em 1 para a primeira interrogação '?'
    sqlite3_bind_text(stmt, 1, cliente->nome, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, cliente->sobrenome, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 3, cliente->cpf, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 4, cliente->rg, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 5, cliente->email, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 6, cliente->telefone, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 7, cliente->endereco, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 8, cliente->numero, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 9, cliente->bairro, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 10, cliente->cidade, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 11, cliente->estado, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 12, cliente->cep, -1, SQLITE_STATIC);

    // Grava os dados
    int resultado = sqlite3_step(stmt);
    StatusCode status;

    if (resultado == SQLITE_DONE)
    {
        if (id_gerado != NULL)
        {
            *id_gerado = (int)sqlite3_last_insert_rowid(db);
        }
        status = STATUS_OK;
    }
    else if (resultado == SQLITE_CONSTRAINT)
    {
        // ERRO: Tentou cadastrar um CPF que já existe que o banco gerou no autoincrement
        fprintf(stderr, "Erro: CPF Já cadastrado no sistema.\n");
        status = ERR_REGISTRO_DUPLICADO;
    }
    else
    {
        fprintf(stderr, "Erro ao executar INSERT: %s\n", sqlite3_errmsg(db));
        status = ERR_BANCO_DADOS;
    }

    // Liberar o statement
    sqlite3_finalize(stmt);

    return status;
}

int cliente_repo_buscar_por_id(int id, Cliente *saida)
{
    if (!db)
        return ERR_BANCO_DADOS;
    if (saida == NULL)
        return ERR_DADO_INVALIDO;

    const char *sql = "SELECT id, nome, sobrenome, cpf, rg, email, telefone, "
                      "       endereco, numero, bairro, cidade, estado, cep "
                      "FROM clientes WHERE id = ?;";
    sqlite3_stmt *stmt;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK)
    {
        return ERR_BANCO_DADOS;
    }
    sqlite3_bind_int(stmt, 1, id);

    int resultado = sqlite3_step(stmt);
    StatusCode status;

    if (resultado == SQLITE_ROW)
    {
        saida->id = sqlite3_column_int(stmt, 0);
        snprintf(saida->nome, sizeof(saida->nome), "%s", sqlite3_column_text(stmt, 1));
        snprintf(saida->sobrenome, sizeof(saida->sobrenome), "%s", sqlite3_column_text(stmt, 2));
        snprintf(saida->cpf, sizeof(saida->cpf), "%s", sqlite3_column_text(stmt, 3));
        snprintf(saida->rg, sizeof(saida->rg), "%s", sqlite3_column_text(stmt, 4));
        snprintf(saida->email, sizeof(saida->email), "%s", sqlite3_column_text(stmt, 5));
        snprintf(saida->telefone, sizeof(saida->telefone), "%s", sqlite3_column_text(stmt, 6));
        snprintf(saida->endereco, sizeof(saida->endereco), "%s", sqlite3_column_text(stmt, 7));
        snprintf(saida->numero, sizeof(saida->numero), "%s", sqlite3_column_text(stmt, 8));
        snprintf(saida->bairro, sizeof(saida->bairro), "%s", sqlite3_column_text(stmt, 9));
        snprintf(saida->cidade, sizeof(saida->cidade), "%s", sqlite3_column_text(stmt, 10));
        snprintf(saida->estado, sizeof(saida->estado), "%s", sqlite3_column_text(stmt, 11));
        snprintf(saida->cep, sizeof(saida->cep), "%s", sqlite3_column_text(stmt, 12));

        status = STATUS_OK;
    }
    else if (resultado == SQLITE_DONE)
    {
        status = ERR_NAO_ENCONTRADO; // Corrigido: era == (comparação) e agora é = (atribuição)
    }
    else
    {
        fprintf(stderr, "Erro ao buscar cliente: %s\n", sqlite3_errmsg(db));
        status = ERR_BANCO_DADOS;
    }

    sqlite3_finalize(stmt);

    return status;
}

int cliente_repo_buscar_por_cpf(const char *cpf, Cliente *saida)
{ 
    if (!db)
        return ERR_BANCO_DADOS;
    if (saida == NULL)
        return ERR_DADO_INVALIDO;

    const char *sql = "SELECT id, nome, sobrenome, cpf, rg, email, telefone, "
                      "       endereco, numero, bairro, cidade, estado, cep "
                      "FROM clientes WHERE cpf = ?;";
    sqlite3_stmt *stmt;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK)
    {
        return ERR_BANCO_DADOS;
    }

    // Corrigido: índice 1 (pois é a primeira e única interrogação '?' da query)
    sqlite3_bind_text(stmt, 1, cpf, -1, SQLITE_STATIC);

    // Corrigido: faltava executar o step para obter o 'resultado'
    int resultado = sqlite3_step(stmt);
    StatusCode status;

    if (resultado == SQLITE_ROW)
    {
        saida->id = sqlite3_column_int(stmt, 0);
        snprintf(saida->nome, sizeof(saida->nome), "%s", sqlite3_column_text(stmt, 1));
        snprintf(saida->sobrenome, sizeof(saida->sobrenome), "%s", sqlite3_column_text(stmt, 2));
        snprintf(saida->cpf, sizeof(saida->cpf), "%s", sqlite3_column_text(stmt, 3));
        snprintf(saida->rg, sizeof(saida->rg), "%s", sqlite3_column_text(stmt, 4));
        snprintf(saida->email, sizeof(saida->email), "%s", sqlite3_column_text(stmt, 5));
        snprintf(saida->telefone, sizeof(saida->telefone), "%s", sqlite3_column_text(stmt, 6));
        snprintf(saida->endereco, sizeof(saida->endereco), "%s", sqlite3_column_text(stmt, 7));
        snprintf(saida->numero, sizeof(saida->numero), "%s", sqlite3_column_text(stmt, 8));
        snprintf(saida->bairro, sizeof(saida->bairro), "%s", sqlite3_column_text(stmt, 9));
        snprintf(saida->cidade, sizeof(saida->cidade), "%s", sqlite3_column_text(stmt, 10));
        snprintf(saida->estado, sizeof(saida->estado), "%s", sqlite3_column_text(stmt, 11));
        snprintf(saida->cep, sizeof(saida->cep), "%s", sqlite3_column_text(stmt, 12));

        status = STATUS_OK;
    }
    else if (resultado == SQLITE_DONE)
    {
        status = ERR_NAO_ENCONTRADO;
    }
    else
    {
        fprintf(stderr, "Erro ao buscar cliente por CPF: %s\n", sqlite3_errmsg(db));
        status = ERR_BANCO_DADOS;
    }

    sqlite3_finalize(stmt);

    return status;
}

int cliente_repo_listar_todos(Cliente **lista, int *quantidade) {
    if (!db) return ERR_BANCO_DADOS;
    if (lista == NULL || quantidade == NULL) return ERR_DADO_INVALIDO;

    const char *sql = "SELECT id, nome, sobrenome, cpf, rg, email, telefone, "
                      "       endereco, numero, bairro, cidade, estado, cep "
                      "FROM clientes ORDER BY nome ASC;";
    sqlite3_stmt *stmt;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return ERR_BANCO_DADOS;
    }

    // Inicializa a lista dinâmica na memória
    int capacidade = 10;
    int total = 0;
    Cliente *vetor = malloc(capacidade * sizeof(Cliente));
    if (vetor == NULL) {
        sqlite3_finalize(stmt);
        return ERR_GENERICO;
    }

    // Enquanto houver linhas retornadas do banco
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        // Se o vetor encher, dobra a capacidade na memória
        if (total >= capacidade) {
            capacidade *= 2;
            Cliente *temp = realloc(vetor, capacidade * sizeof(Cliente));
            if (temp == NULL) {
                free(vetor);
                sqlite3_finalize(stmt);
                return ERR_GENERICO;
            }
            vetor = temp;
        }

        // Preenche o cliente na posição atual (total)
        vetor[total].id = sqlite3_column_int(stmt, 0);
        snprintf(vetor[total].nome,      sizeof(vetor[total].nome),      "%s", sqlite3_column_text(stmt, 1));
        snprintf(vetor[total].sobrenome, sizeof(vetor[total].sobrenome), "%s", sqlite3_column_text(stmt, 2));
        snprintf(vetor[total].cpf,       sizeof(vetor[total].cpf),       "%s", sqlite3_column_text(stmt, 3));
        snprintf(vetor[total].rg,        sizeof(vetor[total].rg),        "%s", sqlite3_column_text(stmt, 4));
        snprintf(vetor[total].email,     sizeof(vetor[total].email),     "%s", sqlite3_column_text(stmt, 5));
        snprintf(vetor[total].telefone,  sizeof(vetor[total].telefone),  "%s", sqlite3_column_text(stmt, 6));
        snprintf(vetor[total].endereco,  sizeof(vetor[total].endereco),  "%s", sqlite3_column_text(stmt, 7));
        snprintf(vetor[total].numero,    sizeof(vetor[total].numero),    "%s", sqlite3_column_text(stmt, 8));
        snprintf(vetor[total].bairro,    sizeof(vetor[total].bairro),    "%s", sqlite3_column_text(stmt, 9));
        snprintf(vetor[total].cidade,    sizeof(vetor[total].cidade),    "%s", sqlite3_column_text(stmt, 10));
        snprintf(vetor[total].estado,    sizeof(vetor[total].estado),    "%s", sqlite3_column_text(stmt, 11));
        snprintf(vetor[total].cep,       sizeof(vetor[total].cep),       "%s", sqlite3_column_text(stmt, 12));

        total++;
    }

    sqlite3_finalize(stmt);

    // Devolve o vetor de clientes e a quantidade total encontrada
    *lista = vetor;
    *quantidade = total;

    return STATUS_OK;
}

int cliente_repo_buscar_por_nome(const char *termo, Cliente **lista, int *quantidade) {
    if (!db) return ERR_BANCO_DADOS;
    if (termo == NULL || lista == NULL || quantidade == NULL) return ERR_DADO_INVALIDO;

    const char *sql = "SELECT id, nome, sobrenome, cpf, rg, email, telefone, "
                      "       endereco, numero, bairro, cidade, estado, cep "
                      "FROM clientes WHERE nome LIKE ? OR sobrenome LIKE ? "
                      "ORDER BY nome ASC;";
    sqlite3_stmt *stmt;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return ERR_BANCO_DADOS;
    }

    // Monta o padrão de busca com % (ex: "%Maria%")
    char padrao[120];
    snprintf(padrao, sizeof(padrao), "%%%s%%", termo);

    // Vincula nas duas interrogações: nome (1) e sobrenome (2)
    sqlite3_bind_text(stmt, 1, padrao, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, padrao, -1, SQLITE_STATIC);

    int capacidade = 10;
    int total = 0;
    Cliente *vetor = malloc(capacidade * sizeof(Cliente));
    if (vetor == NULL) {
        sqlite3_finalize(stmt);
        return ERR_GENERICO;
    }

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        if (total >= capacidade) {
            capacidade *= 2;
            Cliente *temp = realloc(vetor, capacidade * sizeof(Cliente));
            if (temp == NULL) {
                free(vetor);
                sqlite3_finalize(stmt);
                return ERR_GENERICO;
            }
            vetor = temp;
        }

        vetor[total].id = sqlite3_column_int(stmt, 0);
        snprintf(vetor[total].nome,      sizeof(vetor[total].nome),      "%s", sqlite3_column_text(stmt, 1));
        snprintf(vetor[total].sobrenome, sizeof(vetor[total].sobrenome), "%s", sqlite3_column_text(stmt, 2));
        snprintf(vetor[total].cpf,       sizeof(vetor[total].cpf),       "%s", sqlite3_column_text(stmt, 3));
        snprintf(vetor[total].rg,        sizeof(vetor[total].rg),        "%s", sqlite3_column_text(stmt, 4));
        snprintf(vetor[total].email,     sizeof(vetor[total].email),     "%s", sqlite3_column_text(stmt, 5));
        snprintf(vetor[total].telefone,  sizeof(vetor[total].telefone),  "%s", sqlite3_column_text(stmt, 6));
        snprintf(vetor[total].endereco,  sizeof(vetor[total].endereco),  "%s", sqlite3_column_text(stmt, 7));
        snprintf(vetor[total].numero,    sizeof(vetor[total].numero),    "%s", sqlite3_column_text(stmt, 8));
        snprintf(vetor[total].bairro,    sizeof(vetor[total].bairro),    "%s", sqlite3_column_text(stmt, 9));
        snprintf(vetor[total].cidade,    sizeof(vetor[total].cidade),    "%s", sqlite3_column_text(stmt, 10));
        snprintf(vetor[total].estado,    sizeof(vetor[total].estado),    "%s", sqlite3_column_text(stmt, 11));
        snprintf(vetor[total].cep,       sizeof(vetor[total].cep),       "%s", sqlite3_column_text(stmt, 12));

        total++;
    }

    sqlite3_finalize(stmt);

    *lista = vetor;
    *quantidade = total;

    return STATUS_OK;
}
