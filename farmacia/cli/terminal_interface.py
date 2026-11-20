from container import Container
from exceptions import FarmaciaError


class TerminalInterface:
    def __init__(self, container: Container):
        self.container = container
        
        self.med_service = container.med_service
        self.cli_service = container.cli_service
        self.est_service = container.est_service
        self.venda_service = container.venda_service
        self.rel_service = container.rel_service

    def menu_medicamentos(self):
        while True:
            print("\n" + "=" * 50)
            print("GERENCIAMENTO DE MEDICAMENTOS")
            print("=" * 50)
            print("1. Cadastrar Medicamento")
            print("2. Listar Todos os Medicamentos")
            print("3. Pesquisar por Nome")
            print("4. Pesquisar por Código")
            print("5. Alterar Medicamento")
            print("6. Excluir Medicamento")
            print("0. Voltar ao Menu Principal")
            opcao = input("\nEscolha uma opção: ").strip()

            match opcao:
                case "1":
                    try:
                        codigo = input("Código único: ").strip()
                        nome = input("Nome comercial: ").strip()
                        fabricante = input("Fabricante: ").strip()
                        categoria = input("Categoria: ").strip()
                        apresentacao = input("Apresentação: ").strip()
                        preco = input("Preço de venda (R$): ").strip()
                        estoque = input("Quantidade em estoque inicial [0]: ").strip() or "0"
                        estoque_minimo = input("Quantidade mínima de alerta [0]: ").strip() or "0"
                        validade = input("Data de validade (AAAA-MM-DD): ").strip()

                        med = self.med_service.cadastrar({
                            "codigo": codigo,
                            "nome": nome,
                            "fabricante": fabricante,
                            "categoria": categoria,
                            "apresentacao": apresentacao,
                            "preco": preco,
                            "estoque": int(estoque),
                            "estoque_minimo": int(estoque_minimo),
                            "data_validade": validade,
                        })
                        print(f"\n[SUCESSO] Medicamento '{med.nome}' cadastrado com sucesso! ID: {med.id}")
                    except FarmaciaError as err:
                        print(f"\n[ERRO] {err}")
                    except ValueError:
                        print("\n[ERRO] Valores numéricos inválidos.")

                case "2":
                    meds = self.med_service.listar_todos()
                    print(f"\n--- Total de Medicamentos: {len(meds)} ---")
                    if not meds:
                        print("Nenhum medicamento cadastrado.")
                    for m in meds:
                        print(f"ID: {m.id} | Código: {m.codigo:<10} | {m.nome:<25} | R$ {m.preco_em_reais():>6.2f} | Estoque: {m.estoque:>3} un. | Validade: {m.data_validade}")

                case "3":
                    termo = input("Digite parte do nome: ").strip()
                    encontrados = self.med_service.pesquisar_por_nome(termo)
                    print(f"\nEncontrados ({len(encontrados)}):")
                    for m in encontrados:
                        print(f"ID: {m.id} | Código: {m.codigo} | {m.nome} | R$ {m.preco_em_reais():.2f} | Estoque: {m.estoque}")

                case "4":
                    codigo = input("Digite o código do medicamento: ").strip()
                    try:
                        m = self.med_service.buscar_por_codigo(codigo)
                        print(f"\nID: {m.id} | Código: {m.codigo} | {m.nome}")
                        print(f"Fabricante: {m.fabricante} | Categoria: {m.categoria} | Apresentação: {m.apresentacao}")
                        print(f"Preço: R$ {m.preco_em_reais():.2f} | Estoque: {m.estoque} | Mínimo: {m.estoque_minimo} | Validade: {m.data_validade}")
                    except FarmaciaError as err:
                        print(f"\n[ERRO] {err}")

                case "5":
                    try:
                        med_id = int(input("ID do medicamento para alterar: ").strip())
                        med = self.med_service.buscar_por_id(med_id)
                        print(f"Alterando: {med.nome}")

                        nome = input(f"Novo nome [{med.nome}]: ").strip() or med.nome
                        fabricante = input(f"Novo fabricante [{med.fabricante}]: ").strip() or med.fabricante
                        categoria = input(f"Nova categoria [{med.categoria}]: ").strip() or med.categoria
                        apresentacao = input(f"Nova apresentação [{med.apresentacao}]: ").strip() or med.apresentacao
                        preco = input(f"Novo preço [{med.preco_em_reais():.2f}]: ").strip() or str(med.preco_em_reais())
                        validade = input(f"Nova validade [{med.data_validade}]: ").strip() or med.data_validade
                        minimo = input(f"Novo estoque mínimo [{med.estoque_minimo}]: ").strip() or str(med.estoque_minimo)

                        self.med_service.atualizar(med_id, {
                            "codigo": med.codigo,
                            "nome": nome,
                            "fabricante": fabricante,
                            "categoria": categoria,
                            "apresentacao": apresentacao,
                            "preco": preco,
                            "estoque": med.estoque,
                            "estoque_minimo": int(minimo),
                            "data_validade": validade,
                        })
                        print("\n[SUCESSO] Medicamento atualizado!")
                    except FarmaciaError as err:
                        print(f"\n[ERRO] {err}")
                    except ValueError:
                        print("\n[ERRO] Entrada inválida.")

                case "6":
                    try:
                        med_id = int(input("ID do medicamento a excluir: ").strip())
                        self.med_service.excluir(med_id)
                        print("\n[SUCESSO] Medicamento removido com sucesso!")
                    except FarmaciaError as err:
                        print(f"\n[BLOQUEIO] {err}")
                    except ValueError:
                        print("\n[ERRO] ID inválido.")

                case "0":
                    break

                case _:
                    print("\n[AVISO] Opção inválida. Digite uma opção entre 0 e 6.")

    def menu_clientes(self):
        while True:
            print("\n" + "=" * 50)
            print("GERENCIAMENTO DE CLIENTES")
            print("=" * 50)
            print("1. Cadastrar Cliente")
            print("2. Listar Todos os Clientes")
            print("3. Pesquisar Cliente por Nome")
            print("4. Alterar Cliente")
            print("5. Excluir Cliente")
            print("0. Voltar ao Menu Principal")
            opcao = input("\nEscolha uma opção: ").strip()

            match opcao:
                case "1":
                    try:
                        nome = input("Nome completo: ").strip()
                        telefone = input("Telefone (opcional): ").strip()
                        email = input("E-mail (opcional): ").strip()
                        c = self.cli_service.cadastrar({"nome": nome, "telefone": telefone, "email": email})
                        print(f"\n[SUCESSO] Cliente '{c.nome}' cadastrado com sucesso! ID: {c.id}")
                    except FarmaciaError as err:
                        print(f"\n[ERRO] {err}")

                case "2":
                    clis = self.cli_service.listar_todos()
                    print(f"\n--- Total de Clientes: {len(clis)} ---")
                    if not clis:
                        print("Nenhum cliente cadastrado.")
                    for c in clis:
                        print(f"ID: {c.id} | Nome: {c.nome:<25} | Telefone: {c.telefone or 'N/A':<15} | E-mail: {c.email or 'N/A'}")

                case "3":
                    termo = input("Digite o nome ou parte dele: ").strip()
                    encontrados = self.cli_service.pesquisar_por_nome(termo)
                    print(f"\nEncontrados ({len(encontrados)}):")
                    for c in encontrados:
                        print(f"ID: {c.id} | Nome: {c.nome} | Telefone: {c.telefone or 'N/A'}")

                case "4":
                    try:
                        c_id = int(input("ID do cliente a alterar: ").strip())
                        cli = self.cli_service.buscar_por_id(c_id)
                        nome = input(f"Novo nome [{cli.nome}]: ").strip() or cli.nome
                        telefone = input(f"Novo telefone [{cli.telefone or ''}]: ").strip() or cli.telefone
                        email = input(f"Novo email [{cli.email or ''}]: ").strip() or cli.email

                        self.cli_service.atualizar(c_id, {"nome": nome, "telefone": telefone, "email": email})
                        print("\n[SUCESSO] Dados do cliente atualizados!")
                    except FarmaciaError as err:
                        print(f"\n[ERRO] {err}")
                    except ValueError:
                        print("\n[ERRO] ID inválido.")

                case "5":
                    try:
                        c_id = int(input("ID do cliente a excluir: ").strip())
                        self.cli_service.excluir(c_id)
                        print("\n[SUCESSO] Cliente excluído!")
                    except FarmaciaError as err:
                        print(f"\n[BLOQUEIO] {err}")
                    except ValueError:
                        print("\n[ERRO] ID inválido.")

                case "0":
                    break

                case _:
                    print("\n[AVISO] Opção inválida. Digite uma opção entre 0 e 5.")

    def menu_estoque(self):
        while True:
            print("\n" + "=" * 50)
            print("CONTROLE DE ESTOQUE")
            print("=" * 50)
            print("1. Registrar Entrada de Estoque (Reposição)")
            print("2. Consultar Medicamentos com Estoque Baixo")
            print("3. Consultar Medicamentos Zerados (Sem Estoque)")
            print("4. Consultar Medicamentos Próximos do Vencimento")
            print("5. Histórico de Movimentações de Estoque")
            print("0. Voltar ao Menu Principal")
            opcao = input("\nEscolha uma opção: ").strip()

            match opcao:
                case "1":
                    try:
                        med_id = int(input("ID do medicamento: ").strip())
                        qtd = int(input("Quantidade a adicionar: ").strip())
                        motivo = input("Motivo/Descrição da entrada: ").strip() or "Entrada manual de reposição"
                        res = self.est_service.registrar_entrada(med_id, qtd, descricao=motivo)
                        print(f"\n[SUCESSO] Entrada confirmada!")
                        print(f"Medicamento: {res['medicamento_nome']} | Estoque anterior: {res['estoque_anterior']} | Novo estoque: {res['novo_estoque']}")
                    except FarmaciaError as err:
                        print(f"\n[ERRO] {err}")
                    except ValueError:
                        print("\n[ERRO] Valores numéricos inválidos.")

                case "2":
                    baixos = self.est_service.consultar_estoque_baixo()
                    print(f"\n--- Medicamentos com Estoque Baixo ({len(baixos)}) ---")
                    if not baixos:
                        print("Nenhum medicamento em nível crítico.")
                    for m in baixos:
                        print(f"Código: {m.codigo} | {m.nome:<25} | Estoque Atual: {m.estoque:>3} | Mínimo: {m.estoque_minimo:>3}")

                case "3":
                    zerados = self.est_service.consultar_sem_estoque()
                    print(f"\n--- Medicamentos com Estoque Zerado ({len(zerados)}) ---")
                    if not zerados:
                        print("Nenhum produto zerado.")
                    for m in zerados:
                        print(f"Código: {m.codigo} | {m.nome}")

                case "4":
                    dias = input("Verificar vencimento nos próximos quantos dias? [30]: ").strip() or "30"
                    try:
                        vencendo = self.est_service.consultar_proximos_vencimento(dias=int(dias))
                        print(f"\n--- Medicamentos Vencendo em até {dias} dias ({len(vencendo)}) ---")
                        if not vencendo:
                            print("Nenhum medicamento com vencimento próximo.")
                        for m in vencendo:
                            print(f"Código: {m.codigo} | {m.nome:<25} | Validade: {m.data_validade} | Estoque: {m.estoque}")
                    except ValueError:
                        print("\n[ERRO] Dias inválidos.")

                case "5":
                    movs = self.est_service.listar_historico_movimentacoes()
                    print(f"\n--- Histórico de Movimentações ({len(movs)}) ---")
                    for mv in movs[:15]:
                        print(f"{mv.get('data_movimentacao')} | Tipo: {mv.get('tipo'):<7} | Qtd: {mv.get('quantidade'):>3} un. | {mv.get('medicamento_nome')} | {mv.get('descricao')}")

                case "0":
                    break

                case _:
                    print("\n[AVISO] Opção inválida. Digite uma opção entre 0 e 5.")

    def menu_vendas(self):
        while True:
            print("\n" + "=" * 50)
            print("PONTO DE VENDA (PDV) / REGISTRO DE VENDAS")
            print("=" * 50)
            print("1. Nova Venda (Carrinho de Compras)")
            print("2. Consultar Todas as Vendas")
            print("3. Consultar Venda por ID (Detalhes e Itens)")
            print("4. Resumo Financeiro por Período")
            print("0. Voltar ao Menu Principal")
            opcao = input("\nEscolha uma opção: ").strip()

            match opcao:
                case "1":
                    cli_id_input = input("ID do Cliente (vazio para venda sem cadastro): ").strip()
                    cliente_id = int(cli_id_input) if cli_id_input else None

                    if cliente_id:
                        try:
                            c = self.cli_service.buscar_por_id(cliente_id)
                            print(f"Cliente: {c.nome}")
                        except FarmaciaError as err:
                            print(f"[AVISO] {err}. Prosseguindo sem cliente.")
                            cliente_id = None

                    carrinho = []
                    while True:
                        codigo_ou_id = input("ID ou Código do medicamento ('F' para finalizar): ").strip()
                        if codigo_ou_id.upper() == "F":
                            break

                        try:
                            if codigo_ou_id.isdigit() and len(codigo_ou_id) < 6:
                                med = self.med_service.buscar_por_id(int(codigo_ou_id))
                            else:
                                med = self.med_service.buscar_por_codigo(codigo_ou_id)

                            print(f"Selecionado: {med.nome} | Preço: R$ {med.preco_em_reais():.2f} | Estoque: {med.estoque}")
                            qtd = int(input("Quantidade: ").strip())
                            if qtd <= 0:
                                print("[ERRO] Quantidade deve ser maior que zero.")
                                continue

                            carrinho.append({"medicamento_id": med.id, "quantidade": qtd})
                            print(f"[OK] {qtd} un. de '{med.nome}' adicionadas ao carrinho.")
                        except FarmaciaError as err:
                            print(f"[ERRO] {err}")
                        except ValueError:
                            print("[ERRO] Entrada inválida.")

                    if not carrinho:
                        print("\n[AVISO] Venda cancelada: carrinho vazio.")
                        continue

                    try:
                        venda = self.venda_service.registrar_venda(itens=carrinho, cliente_id=cliente_id)
                        print(f"\nVENDA #{venda.id} FINALIZADA COM SUCESSO!")
                        print(f"Data: {venda.data_venda}")
                        print(f"Cliente: {venda.cliente_nome or 'Não Identificado'}")
                        print(f"TOTAL: R$ {venda.valor_total_em_reais():.2f}")
                        for it in venda.itens:
                            print(f"  - {it.medicamento_nome} | Qtd: {it.quantidade} | Unit: R$ {it.preco_unitario_em_reais():.2f} | Subtotal: R$ {it.subtotal_em_reais():.2f}")
                    except FarmaciaError as err:
                        print(f"\n[FALHA NA VENDA] {err}")

                case "2":
                    vendas = self.venda_service.listar_todas()
                    print(f"\n--- Histórico de Vendas ({len(vendas)}) ---")
                    for v in vendas:
                        total_itens = sum(it.quantidade for it in v.itens)
                        print(f"Venda #{v.id:>3} | Data: {v.data_venda} | Cliente: {v.cliente_nome or 'Balcão':<20} | {total_itens:>2} itens | Total: R$ {v.valor_total_em_reais():>7.2f}")

                case "3":
                    try:
                        v_id = int(input("Digite o ID da venda: ").strip())
                        v = self.venda_service.buscar_por_id(v_id)
                        print(f"\nDETALHES DA VENDA #{v.id}")
                        print(f"Data: {v.data_venda} | Cliente: {v.cliente_nome or 'Não Identificado'}")
                        print(f"Total: R$ {v.valor_total_em_reais():.2f}")
                        for it in v.itens:
                            print(f" {it.medicamento_nome:<25} | Qtd: {it.quantidade:>2} | R$ {it.subtotal_em_reais():>6.2f}")
                    except FarmaciaError as err:
                        print(f"\n[ERRO] {err}")
                    except ValueError:
                        print("\n[ERRO] ID inválido.")

                case "4":
                    inicio = input("Data Inicial (AAAA-MM-DD): ").strip() + "T00:00:00"
                    fim = input("Data Final   (AAAA-MM-DD): ").strip() + "T23:59:59"
                    try:
                        res = self.venda_service.consultar_resumo_periodo(inicio, fim)
                        print(f"\nTotal de vendas: {res['total_vendas']}")
                        print(f"Faturamento: R$ {res['valor_total_reais']:.2f}")
                    except FarmaciaError as err:
                        print(f"\n[ERRO] {err}")

                case "0":
                    break

                case _:
                    print("\n[AVISO] Opção inválida. Digite uma opção entre 0 e 4.")

    def menu_relatorios_arquivos(self):
        while True:
            print("\n" + "=" * 50)
            print("RELATÓRIOS E EXPORTAÇÃO CSV")
            print("=" * 50)
            print("1. Ranking dos Medicamentos Mais Vendidos")
            print("2. Exportar Relatório de Estoque para CSV (UTF-8)")
            print("3. Exportar Histórico de Vendas para CSV (UTF-8)")
            print("4. Exibir Caminho dos Arquivos")
            print("0. Voltar ao Menu Principal")

            opcao = input("\nEscolha uma opção: ").strip()

            match opcao:
                case "1":
                    limite = input("Quantidade no ranking [10]: ").strip() or "10"
                    mais = self.rel_service.relatorio_medicamentos_mais_vendidos(limite=int(limite))
                    print(f"\n--- Top {len(mais)} Medicamentos Mais Vendidos ---")
                    for idx, item in enumerate(mais, 1):
                        receita = item.get("receita_total_reais", item.get("receita_total_centavos", 0) / 100)
                        print(f"{idx}º. {item['nome']:<25} | {item['total_unidades_vendidas']:>3} un. | R$ {receita:>7.2f}")

                case "2":
                    caminho = self.rel_service.exportar_estoque_csv()
                    print(f"\n[SUCESSO] Relatório de Estoque salvo em CSV: {caminho}")

                case "3":
                    caminho = self.rel_service.exportar_vendas_csv()
                    print(f"\n[SUCESSO] Histórico de Vendas salvo em CSV: {caminho}")

                case "4":
                    print(f"\nBanco de Dados (SQLite):      {self.container.db_path}")
                    print(f"Diretório de Relatórios (CSV): {self.container.reports_dir}")

                case "0":
                    break

                case _:
                    print("\n[AVISO] Opção inválida. Digite uma opção entre 0 e 4.")

    def iniciar(self):
        while True:
            print("\n" + "=" * 60)
            print("  SISTEMA DE GERENCIAMENTO DE FARMÁCIA (TERMINAL CLI)")
            print("=" * 60)
            print("1. Medicamentos (Cadastro, Busca, Edição, Exclusão)")
            print("2. Clientes (Cadastro, Consulta, Edição)")
            print("3. Estoque (Entradas, Nível Baixo, Vencimento)")
            print("4. Vendas / PDV (Carrinho, Baixa Automática, Validação)")
            print("5. Relatórios e Exportação CSV (UTF-8)")
            print("0. Sair do Sistema")
            print("=" * 60)

            opcao = input("Digite a opção desejada: ").strip()

            match opcao:
                case "1":
                    self.menu_medicamentos()
                case "2":
                    self.menu_clientes()
                case "3":
                    self.menu_estoque()
                case "4":
                    self.menu_vendas()
                case "5":
                    self.menu_relatorios_arquivos()
                case "0":
                    print("\nEncerrando o sistema...")
                    break
                case _:
                    print("\n[AVISO] Opção inválida. Digite um número de 0 a 5.")
