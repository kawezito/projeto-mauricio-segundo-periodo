#include "../../include/repositories/database.h"
#include <stdio.h>

#define DB_PATH "data/farmacia.db"

static sqlite3 *db_instance = NULL;

sqlite3* database_obter_conexao() {
    if (db_instance == NULL) {
        if(sqlite3_open(DB_PATH, &db_instance) != SQLITE_OK) {
            fprintf(stderr, "Erro ao abrir o banco de dados: %s\n", sqlite3_errmsg(db_instance));
            return NULL;
        }
    }
    return db_instance;
}

void database_fechar_conexao() {
    if(db_instance != NULL) {
        sqlite3_close(db_instance);
        db_instance = NULL;
    }
}

int database_inicializar() {
    sqlite3 *db = database_obter_conexao();
    if (!db) return -1;

    char *err_msg = NULL;

   const char *sql_criar_tabela_clientes = 
        "CREATE TABLE IF NOT EXISTS clientes ("
        "   id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
        "   nome        TEXT NOT NULL,"
        "   sobrenome   TEXT NOT NULL,"
        "   cpf         TEXT UNIQUE NOT NULL,"
        "   rg          TEXT,"
        "   email       TEXT,"
        "   telefone    TEXT,"
        "   endereco    TEXT,"
        "   numero      TEXT,"
        "   bairro      TEXT,"
        "   cidade      TEXT,"
        "   estado      TEXT,"
        "   cep         TEXT"
        ");";

    // script com as tabelas do sistema
    if(sqlite3_exec(db, sql_criar_tabela_clientes, 0, 0, &err_msg) != SQLITE_OK) {
        fprintf(stderr, "Erro ao criar tabelas: %s\n", err_msg);
        return -1;
    }

    return 0;
}