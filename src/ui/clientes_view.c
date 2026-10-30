#include "../../include/ui/clientes_view.h"
#include "../../include/services/cliente_service.h"
#include "../../include/models/cliente.h"
#include "../../include/common.h"

#include <gtk/gtk.h>
#include <stdlib.h>
#include <string.h>

/**
 * @file clientes_view.c
 * @brief Implementação da tela de gestão e cadastro de clientes em GTK 3.
 */

/* Índices das colunas da tabela GtkTreeView */
enum {
    COL_ID = 0,
    COL_NOME,
    COL_CPF,
    COL_TELEFONE,
    COL_EMAIL,
    COL_CIDADE,
    NUM_COLS
};

/* Estrutura para guardar os ponteiros dos widgets da tela */
typedef struct {
    GtkWidget *entry_busca;
    GtkWidget *tree_view;
    GtkListStore *list_store;
} ClientesViewWidgets;

/* Mostra diálogo com mensagem para o usuário */
static void mostrar_mensagem(GtkWindow *parent, GtkMessageType tipo, const char *msg) {
    GtkWidget *dialog = gtk_message_dialog_new(parent,
                                               GTK_DIALOG_MODAL | GTK_DIALOG_DESTROY_WITH_PARENT,
                                               tipo,
                                               GTK_BUTTONS_OK,
                                               "%s", msg);
    gtk_dialog_run(GTK_DIALOG(dialog));
    gtk_widget_destroy(dialog);
}

/* Recarrega a tabela chamando a camada de serviço */
static void recarregar_tabela(ClientesViewWidgets *widgets, const char *termo) {
    gtk_list_store_clear(widgets->list_store);

    Cliente *lista = NULL;
    int quantidade = 0;

    int status = cliente_service_buscar_por_termo(termo, &lista, &quantidade);
    if (status != STATUS_OK || lista == NULL) {
        return;
    }

    GtkTreeIter iter;
    for (int i = 0; i < quantidade; i++) {
        char nome_completo[120];
        snprintf(nome_completo, sizeof(nome_completo), "%s %s", lista[i].nome, lista[i].sobrenome);

        char localidade[80];
        snprintf(localidade, sizeof(localidade), "%s/%s", lista[i].cidade, lista[i].estado);

        gtk_list_store_append(widgets->list_store, &iter);
        gtk_list_store_set(widgets->list_store, &iter,
                           COL_ID, lista[i].id,
                           COL_NOME, nome_completo,
                           COL_CPF, lista[i].cpf,
                           COL_TELEFONE, lista[i].telefone,
                           COL_EMAIL, lista[i].email,
                           COL_CIDADE, localidade,
                           -1);
    }

    // Libera a memória alocada pelo repositório
    free(lista);
}

/* Callback disparado ao clicar no botão "Buscar" ou dar Enter na pesquisa */
static void on_btn_buscar_clicked(GtkWidget *btn, gpointer user_data) {
    (void)btn;
    ClientesViewWidgets *widgets = (ClientesViewWidgets*)user_data;
    const char *termo = gtk_entry_get_text(GTK_ENTRY(widgets->entry_busca));
    recarregar_tabela(widgets, termo);
}

/* Diálogo para cadastrar um novo cliente */
static void on_btn_novo_cliente_clicked(GtkWidget *btn, gpointer user_data) {
    ClientesViewWidgets *widgets = (ClientesViewWidgets*)user_data;
    GtkWindow *parent = GTK_WINDOW(gtk_widget_get_toplevel(btn));

    GtkWidget *dialog = gtk_dialog_new_with_buttons("Novo Cliente",
                                                    parent,
                                                    GTK_DIALOG_MODAL | GTK_DIALOG_DESTROY_WITH_PARENT,
                                                    "_Cancelar", GTK_RESPONSE_CANCEL,
                                                    "_Salvar", GTK_RESPONSE_ACCEPT,
                                                    NULL);

    GtkWidget *content_area = gtk_dialog_get_content_area(GTK_DIALOG(dialog));
    GtkWidget *grid = gtk_grid_new();
    gtk_grid_set_row_spacing(GTK_GRID(grid), 8);
    gtk_grid_set_column_spacing(GTK_GRID(grid), 12);
    gtk_container_set_border_width(GTK_CONTAINER(grid), 15);

    // Campos de entrada do formulário
    GtkWidget *ent_nome      = gtk_entry_new();
    GtkWidget *ent_sobrenome = gtk_entry_new();
    GtkWidget *ent_cpf       = gtk_entry_new();
    GtkWidget *ent_rg        = gtk_entry_new();
    GtkWidget *ent_telefone  = gtk_entry_new();
    GtkWidget *ent_email     = gtk_entry_new();
    GtkWidget *ent_endereco  = gtk_entry_new();
    GtkWidget *ent_numero    = gtk_entry_new();
    GtkWidget *ent_bairro    = gtk_entry_new();
    GtkWidget *ent_cidade    = gtk_entry_new();
    GtkWidget *ent_estado    = gtk_entry_new();
    GtkWidget *ent_cep       = gtk_entry_new();

    // Montagem do formulário no Grid (Linha x Coluna)
    int row = 0;
    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("Nome:"), 0, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_nome, 1, row++, 3, 1);

    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("Sobrenome:"), 0, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_sobrenome, 1, row++, 3, 1);

    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("CPF:"), 0, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_cpf, 1, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("RG:"), 2, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_rg, 3, row++, 1, 1);

    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("Telefone:"), 0, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_telefone, 1, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("E-mail:"), 2, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_email, 3, row++, 1, 1);

    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("Endereço:"), 0, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_endereco, 1, row, 2, 1);
    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("Nº:"), 3, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_numero, 4, row++, 1, 1);

    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("Bairro:"), 0, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_bairro, 1, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("CEP:"), 2, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_cep, 3, row++, 1, 1);

    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("Cidade:"), 0, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_cidade, 1, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), gtk_label_new("UF:"), 2, row, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), ent_estado, 3, row++, 1, 1);

    gtk_container_add(GTK_CONTAINER(content_area), grid);
    gtk_widget_show_all(dialog);

    // Loop do diálogo modal
    while (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {
        Cliente c;
        memset(&c, 0, sizeof(Cliente));

        snprintf(c.nome,      sizeof(c.nome),      "%s", gtk_entry_get_text(GTK_ENTRY(ent_nome)));
        snprintf(c.sobrenome, sizeof(c.sobrenome), "%s", gtk_entry_get_text(GTK_ENTRY(ent_sobrenome)));
        snprintf(c.cpf,       sizeof(c.cpf),       "%s", gtk_entry_get_text(GTK_ENTRY(ent_cpf)));
        snprintf(c.rg,        sizeof(c.rg),        "%s", gtk_entry_get_text(GTK_ENTRY(ent_rg)));
        snprintf(c.telefone,  sizeof(c.telefone),  "%s", gtk_entry_get_text(GTK_ENTRY(ent_telefone)));
        snprintf(c.email,     sizeof(c.email),     "%s", gtk_entry_get_text(GTK_ENTRY(ent_email)));
        snprintf(c.endereco,  sizeof(c.endereco),  "%s", gtk_entry_get_text(GTK_ENTRY(ent_endereco)));
        snprintf(c.numero,    sizeof(c.numero),    "%s", gtk_entry_get_text(GTK_ENTRY(ent_numero)));
        snprintf(c.bairro,    sizeof(c.bairro),    "%s", gtk_entry_get_text(GTK_ENTRY(ent_bairro)));
        snprintf(c.cidade,    sizeof(c.cidade),    "%s", gtk_entry_get_text(GTK_ENTRY(ent_cidade)));
        snprintf(c.estado,    sizeof(c.estado),    "%s", gtk_entry_get_text(GTK_ENTRY(ent_estado)));
        snprintf(c.cep,       sizeof(c.cep),       "%s", gtk_entry_get_text(GTK_ENTRY(ent_cep)));

        int id_gerado = 0;
        int status = cliente_service_cadastrar(&c, &id_gerado);

        if (status == STATUS_OK) {
            mostrar_mensagem(GTK_WINDOW(dialog), GTK_MESSAGE_INFO, "Cliente cadastrado com sucesso!");
            recarregar_tabela(widgets, ""); // Atualiza a lista
            break;
        } else if (status == ERR_REGISTRO_DUPLICADO) {
            mostrar_mensagem(GTK_WINDOW(dialog), GTK_MESSAGE_ERROR, "Já existe um cliente com este CPF cadastrado.");
        } else if (status == ERR_DADO_INVALIDO) {
            mostrar_mensagem(GTK_WINDOW(dialog), GTK_MESSAGE_WARNING, "Verifique os dados! Nome, sobrenome e CPF válido são obrigatórios.");
        } else {
            mostrar_mensagem(GTK_WINDOW(dialog), GTK_MESSAGE_ERROR, "Erro ao gravar no banco de dados.");
        }
    }

    gtk_widget_destroy(dialog);
}

/* Constrói e retorna a View principal de Clientes */
GtkWidget* clientes_view_criar(void) {
    ClientesViewWidgets *widgets = g_malloc0(sizeof(ClientesViewWidgets));

    GtkWidget *box_principal = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_container_set_border_width(GTK_CONTAINER(box_principal), 15);

    // 1. Barra Superior (Busca e Botão de Novo Cliente)
    GtkWidget *box_topo = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    GtkWidget *lbl_busca = gtk_label_new("Buscar:");
    widgets->entry_busca = gtk_entry_new();
    gtk_entry_set_placeholder_text(GTK_ENTRY(widgets->entry_busca), "Digite o nome ou sobrenome...");
    gtk_widget_set_hexpand(widgets->entry_busca, TRUE);

    GtkWidget *btn_buscar = gtk_button_new_with_label("Buscar");
    GtkWidget *btn_novo = gtk_button_new_with_label("+ Novo Cliente");

    gtk_box_pack_start(GTK_BOX(box_topo), lbl_busca, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(box_topo), widgets->entry_busca, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(box_topo), btn_buscar, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(box_topo), btn_novo, FALSE, FALSE, 0);

    gtk_box_pack_start(GTK_BOX(box_principal), box_topo, FALSE, FALSE, 0);

    // 2. Modelo de Dados da Tabela (ListStore)
    widgets->list_store = gtk_list_store_new(NUM_COLS,
                                             G_TYPE_INT,     // ID
                                             G_TYPE_STRING,  // Nome Completo
                                             G_TYPE_STRING,  // CPF
                                             G_TYPE_STRING,  // Telefone
                                             G_TYPE_STRING,  // E-mail
                                             G_TYPE_STRING); // Cidade/UF

    // 3. Componente da Tabela (TreeView)
    widgets->tree_view = gtk_tree_view_new_with_model(GTK_TREE_MODEL(widgets->list_store));
    g_object_unref(widgets->list_store);

    // Configuração das colunas visuais
    const char *titulos[] = {"ID", "Nome Completo", "CPF", "Telefone", "E-mail", "Cidade/UF"};
    for (int i = 0; i < NUM_COLS; i++) {
        GtkCellRenderer *renderer = gtk_cell_renderer_text_new();
        GtkTreeViewColumn *col = gtk_tree_view_column_new_with_attributes(titulos[i], renderer, "text", i, NULL);
        gtk_tree_view_append_column(GTK_TREE_VIEW(widgets->tree_view), col);
    }

    // Scroll para a tabela
    GtkWidget *scrolled_window = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled_window),
                                   GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);
    gtk_container_add(GTK_CONTAINER(scrolled_window), widgets->tree_view);
    gtk_widget_set_vexpand(scrolled_window, TRUE);

    gtk_box_pack_start(GTK_BOX(box_principal), scrolled_window, TRUE, TRUE, 0);

    // Conectar eventos dos botões
    g_signal_connect(btn_buscar, "clicked", G_CALLBACK(on_btn_buscar_clicked), widgets);
    g_signal_connect(widgets->entry_busca, "activate", G_CALLBACK(on_btn_buscar_clicked), widgets);
    g_signal_connect(btn_novo, "clicked", G_CALLBACK(on_btn_novo_cliente_clicked), widgets);

    // Libera a struct de widgets quando o box for destruído
    g_signal_connect_swapped(box_principal, "destroy", G_CALLBACK(g_free), widgets);

    // Carrega os clientes iniciais
    recarregar_tabela(widgets, "");

    return box_principal;
}
