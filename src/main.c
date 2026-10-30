#include "repositories/database.h"
#include "repositories/cliente_repo.h"
#include "ui/clientes_view.h"
#include <gtk/gtk.h>
#include <stdio.h>

/**
 * @file main.c
 * @brief Ponto de entrada da aplicação desktop de Farmácia em GTK 3.
 */

static void activate(GtkApplication *app, gpointer user_data) {
    (void)user_data;

    // 1. Cria a janela principal do sistema
    GtkWidget *window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "Farmácia Pague Menos - Gestão de Clientes");
    gtk_window_set_default_size(GTK_WINDOW(window), 950, 600);
    gtk_window_set_position(GTK_WINDOW(window), GTK_WIN_POS_CENTER);

    // 2. Cria a View de Clientes e anexa na janela
    GtkWidget *view = clientes_view_criar();
    gtk_container_add(GTK_CONTAINER(window), view);

    // 3. Exibe todos os componentes visuais
    gtk_widget_show_all(window);
}

int main(int argc, char **argv) {
    // 1. Inicializa o banco de dados e cria as tabelas se não existirem
    if (database_inicializar() != 0) {
        fprintf(stderr, "Falha ao inicializar banco de dados local.\n");
        return 1;
    }

    // 2. Conecta o banco de dados ao repositório de clientes
    cliente_repo_inicializar(database_obter_conexao());

    // 3. Cria a aplicação GTK
    GtkApplication *app = gtk_application_new("br.com.paguemenos.farmacia", G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);

    // 4. Roda o loop principal de eventos da interface gráfica
    int status = g_application_run(G_APPLICATION(app), argc, argv);

    // 5. Finalização e limpeza de memória
    g_object_unref(app);
    database_fechar_conexao();

    return status;
}
