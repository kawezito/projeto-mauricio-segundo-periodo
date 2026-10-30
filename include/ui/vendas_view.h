#ifndef VENDAS_VIEW_H
#define VENDAS_VIEW_H

#include <gtk/gtk.h>

/**
 * @file vendas_view.h
 * @brief Componentes visuais para o Ponto de Venda (PDV) e consulta do histórico.
 */

GtkWidget* vendas_view_criar(void);
GtkWidget* vendas_view_historico_criar(void);

#endif /* VENDAS_VIEW_H */
