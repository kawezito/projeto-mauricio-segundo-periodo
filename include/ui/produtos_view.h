#ifndef PRODUTOS_VIEW_H
#define PRODUTOS_VIEW_H

#include <gtk/gtk.h>

/**
 * @file produtos_view.h
 * @brief Componentes visuais para catálogo, cadastro e controle de estoque de produtos.
 */

GtkWidget* produtos_view_criar(void);
void produtos_view_atualizar_tabela(GtkWidget *view);

#endif /* PRODUTOS_VIEW_H */
