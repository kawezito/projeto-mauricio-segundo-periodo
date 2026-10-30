#ifndef DATABASE_H
#define DATABASE_H

#include <sqlite3.h>

sqlite3* database_obter_conexao();

void database_fechar_conexao();

int database_inicializar();

#endif