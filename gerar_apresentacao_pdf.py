import os
import sys

class PDFBuilder:
    def __init__(self, w=1280, h=720):
        self.w = w
        self.h = h
        self.pages = []
        
    def add_page(self):
        page = Page(self.w, self.h)
        self.pages.append(page)
        return page
        
    def build(self) -> bytes:
        out = []
        out.append(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        
        objects = {}
        curr_id = 1
        
        cat_id = curr_id; curr_id += 1
        pages_id = curr_id; curr_id += 1
        
        font_reg_id = curr_id; curr_id += 1
        font_bold_id = curr_id; curr_id += 1
        font_mono_id = curr_id; curr_id += 1
        font_monobold_id = curr_id; curr_id += 1
        
        page_ids = []
        content_ids = []
        for _ in self.pages:
            page_ids.append(curr_id); curr_id += 1
            content_ids.append(curr_id); curr_id += 1
            
        objects[cat_id] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode('ascii')
        kids_str = " ".join(f"{pid} 0 R" for pid in page_ids)
        objects[pages_id] = f"<< /Type /Pages /Kids [{kids_str}] /Count {len(page_ids)} >>".encode('ascii')
        
        objects[font_reg_id] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
        objects[font_bold_id] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
        objects[font_mono_id] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>"
        objects[font_monobold_id] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold /Encoding /WinAnsiEncoding >>"
        
        font_res = f"<< /F_Reg {font_reg_id} 0 R /F_Bold {font_bold_id} 0 R /F_Mono {font_mono_id} 0 R /F_MonoBold {font_monobold_id} 0 R >>"
        
        for i, page in enumerate(self.pages):
            pid = page_ids[i]
            cid = content_ids[i]
            stream_data = page.get_stream()
            
            objects[pid] = (
                f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {self.w} {self.h}] "
                f"/Resources << /Font {font_res} >> /Contents {cid} 0 R >>"
            ).encode('ascii')
            
            objects[cid] = (
                f"<< /Length {len(stream_data)} >>\nstream\n".encode('ascii') +
                stream_data +
                b"\nendstream"
            )
            
        xref_offsets = {}
        body = bytearray()
        for header_part in out:
            body.extend(header_part)
            
        for obj_id in sorted(objects.keys()):
            xref_offsets[obj_id] = len(body)
            body.extend(f"{obj_id} 0 obj\n".encode('ascii'))
            body.extend(objects[obj_id])
            body.extend(b"\nendobj\n")
            
        startxref = len(body)
        body.extend(f"xref\n0 {curr_id}\n".encode('ascii'))
        body.extend(b"0000000000 65535 f \n")
        for obj_id in range(1, curr_id):
            offset = xref_offsets[obj_id]
            body.extend(f"{offset:010d} 00000 n \n".encode('ascii'))
            
        body.extend(
            f"trailer\n<< /Size {curr_id} /Root {cat_id} 0 R >>\nstartxref\n{startxref}\n%%EOF".encode('ascii')
        )
        return bytes(body)

def escape_pdf(text: str) -> str:
    text = text.replace("•", "-")
    text = text.replace("—", "-")
    text = text.replace("“", "\"").replace("”", "\"")
    text = text.replace("’", "'").replace("‘", "'")
    
    res = []
    for ch in text:
        if ch == '\\':
            res.append('\\\\')
        elif ch == '(':
            res.append('\\(')
        elif ch == ')':
            res.append('\\)')
        elif ch == '|':
            res.append('-')
        else:
            try:
                b = ch.encode('cp1252')[0]
                if 32 <= b <= 126:
                    res.append(ch)
                else:
                    res.append(f"\\{b:03o}")
            except UnicodeEncodeError:
                res.append("?")
    return "".join(res)

class Page:
    def __init__(self, w=1280, h=720):
        self.w = w
        self.h = h
        self.ops = []
        
    def to_pdf_y(self, y):
        return self.h - y

    def fill_rect(self, x, y, w, h, rgb):
        py = self.to_pdf_y(y + h)
        r, g, b = rgb
        self.ops.append(f"{r:.3f} {g:.3f} {b:.3f} rg {x:.2f} {py:.2f} {w:.2f} {h:.2f} re f")

    def stroke_rect(self, x, y, w, h, rgb, stroke_w=1):
        py = self.to_pdf_y(y + h)
        r, g, b = rgb
        self.ops.append(f"{r:.3f} {g:.3f} {b:.3f} RG {stroke_w:.2f} w {x:.2f} {py:.2f} {w:.2f} {h:.2f} re S")

    def round_rect(self, x, y, w, h, rad, fill_rgb=None, stroke_rgb=None, stroke_w=1):
        py = self.to_pdf_y(y + h)
        k = rad * 0.5522847498
        p = []
        p.append(f"{x+rad:.2f} {py:.2f} m")
        p.append(f"{x+w-rad:.2f} {py:.2f} l")
        p.append(f"{x+w-rad+k:.2f} {py:.2f} {x+w:.2f} {py+rad-k:.2f} {x+w:.2f} {py+rad:.2f} c")
        p.append(f"{x+w:.2f} {py+h-rad:.2f} l")
        p.append(f"{x+w:.2f} {py+h-rad+k:.2f} {x+w-rad+k:.2f} {py+h:.2f} {x+w-rad:.2f} {py+h:.2f} c")
        p.append(f"{x+rad:.2f} {py+h:.2f} l")
        p.append(f"{x+rad-k:.2f} {py+h:.2f} {x:.2f} {py+h-rad+k:.2f} {x:.2f} {py+h-rad:.2f} c")
        p.append(f"{x:.2f} {py+rad:.2f} l")
        p.append(f"{x:.2f} {py+rad-k:.2f} {x+rad-k:.2f} {py:.2f} {x+rad:.2f} {py:.2f} c")
        p.append("h")
        
        cmd = " ".join(p)
        if fill_rgb and stroke_rgb:
            fr, fg, fb = fill_rgb
            sr, sg, sb = stroke_rgb
            self.ops.append(f"{fr:.3f} {fg:.3f} {fb:.3f} rg {sr:.3f} {sg:.3f} {sb:.3f} RG {stroke_w:.2f} w {cmd} B")
        elif fill_rgb:
            fr, fg, fb = fill_rgb
            self.ops.append(f"{fr:.3f} {fg:.3f} {fb:.3f} rg {cmd} f")
        elif stroke_rgb:
            sr, sg, sb = stroke_rgb
            self.ops.append(f"{sr:.3f} {sg:.3f} {sb:.3f} RG {stroke_w:.2f} w {cmd} s")

    def circle(self, cx, cy, rad, fill_rgb=None, stroke_rgb=None, stroke_w=1):
        self.round_rect(cx - rad, cy - rad, rad * 2, rad * 2, rad, fill_rgb, stroke_rgb, stroke_w)

    def line(self, x1, y1, x2, y2, rgb=(1, 1, 1), stroke_w=1, dashed=None):
        py1 = self.to_pdf_y(y1)
        py2 = self.to_pdf_y(y2)
        r, g, b = rgb
        if dashed:
            self.ops.append(f"[{dashed} {dashed}] 0 d")
        self.ops.append(f"{r:.3f} {g:.3f} {b:.3f} RG {stroke_w:.2f} w {x1:.2f} {py1:.2f} m {x2:.2f} {py2:.2f} l S")
        if dashed:
            self.ops.append("[] 0 d")

    def text(self, x, y, text_str, font="F_Bold", size=16, rgb=(1, 1, 1)):
        py = self.to_pdf_y(y)
        r, g, b = rgb
        escaped = escape_pdf(text_str)
        self.ops.append(f"BT /{font} {size} Tf {r:.3f} {g:.3f} {b:.3f} rg {x:.2f} {py:.2f} Td ({escaped}) Tj ET")

    def text_center(self, cx, y, text_str, font="F_Bold", size=16, rgb=(1, 1, 1)):
        factor = 0.55 if font == "F_Reg" else (0.60 if "Mono" in font else 0.58)
        approx_w = len(text_str) * size * factor
        self.text(cx - approx_w / 2, y, text_str, font=font, size=size, rgb=rgb)

    def slide_header(self, slide_num, total_slides, section_title, question_hint=None):
        # Clean academic header
        self.fill_rect(0, 0, 1280, 60, (0.08, 0.10, 0.15))
        self.line(0, 60, 1280, 60, (0.20, 0.25, 0.35), stroke_w=1.2)
        
        # Institution tag
        self.text(60, 36, "UFAL • Bacharelado em Sistemas de Informação", font="F_Bold", size=11, rgb=(0.55, 0.65, 0.80))
        
        # Center title
        title_full = f"{slide_num:02d}. {section_title}"
        self.text(380, 36, title_full, font="F_Bold", size=13, rgb=(1.0, 1.0, 1.0))
        
        # Student info right
        self.text(990, 36, f"Kawe Firmino • Slide {slide_num}/{total_slides}", font="F_Reg", size=11, rgb=(0.60, 0.70, 0.85))
        
        # If question hint exists, show a subtle prompt anchor
        if question_hint:
            self.round_rect(60, 75, 1160, 28, 6, fill_rgb=(0.11, 0.14, 0.22), stroke_rgb=(0.22, 0.30, 0.45), stroke_w=1)
            self.text(75, 94, f"Pergunta do Roteiro: \"{question_hint}\"", font="F_Bold", size=11, rgb=(0.20, 0.75, 0.95))

    def get_stream(self) -> bytes:
        return "\n".join(self.ops).encode('latin1')

builder = PDFBuilder(1280, 720)

# Clean, professional Academic Dark Palette (Human & Elegant, not AI-glitzy)
C_BG = (0.07, 0.09, 0.13)            # Clean Dark Charcoal/Navy Slate
C_CARD = (0.11, 0.14, 0.20)          # Structured Academic Card
C_CARD_ALT = (0.09, 0.11, 0.16)
C_BORDER = (0.22, 0.28, 0.38)        # Clean architectural border
C_ACCENT_BLUE = (0.20, 0.55, 0.95)   # Academic Royal Blue
C_ACCENT_TEAL = (0.10, 0.75, 0.65)   # Clean Medical Teal
C_TEXT_WHITE = (0.98, 0.98, 0.98)
C_TEXT_LIGHT = (0.85, 0.88, 0.92)
C_TEXT_MUTED = (0.60, 0.65, 0.75)
C_CODE_BG = (0.05, 0.07, 0.10)


# ==========================================
# SLIDE 1: CAPA ACADÊMICA
# ==========================================
s1 = builder.add_page()
s1.fill_rect(0, 0, 1280, 720, C_BG)

# Top Bar
s1.fill_rect(0, 0, 1280, 8, C_ACCENT_BLUE)

s1.text(80, 110, "UNIVERSIDADE FEDERAL DE ALAGOAS - UFAL", font="F_Bold", size=14, rgb=C_TEXT_MUTED)
s1.text(80, 132, "CAMPUS DE ARAPIRACA • CURSO DE SISTEMAS DE INFORMAÇÃO", font="F_Bold", size=14, rgb=C_ACCENT_TEAL)
s1.text(80, 154, "DISCIPLINA: LÓGICA DE PROGRAMAÇÃO / ENGENHARIA DE SOFTWARE", font="F_Reg", size=13, rgb=C_TEXT_MUTED)

s1.line(80, 175, 1200, 175, C_BORDER, stroke_w=1.5)

# Main Titles
s1.text(80, 255, "Sistema de Gerenciamento de Farmácia", font="F_Bold", size=44, rgb=C_TEXT_WHITE)
s1.text(80, 305, "Drogaria Vida & Saúde: PDV, Controle de Estoque e Persistência", font="F_Bold", size=22, rgb=C_ACCENT_BLUE)

s1.text(80, 360, "Apresentação Final do Projeto Prático de Programação Estruturada", font="F_Reg", size=16, rgb=C_TEXT_LIGHT)
s1.text(80, 385, "Desenvolvimento orientado a Requisitos, Casos de Uso, MVP e Princípios SOLID", font="F_Reg", size=16, rgb=C_TEXT_LIGHT)

# Identification Box (Lower Left)
s1.round_rect(80, 440, 520, 190, 10, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
s1.text(105, 475, "EQUIPE E ORIENTAÇÃO:", font="F_Bold", size=13, rgb=C_ACCENT_TEAL)
s1.text(105, 510, "Aluno / Desenvolvedor:", font="F_Bold", size=13, rgb=C_TEXT_MUTED)
s1.text(285, 510, "Kawe Firmino", font="F_Bold", size=14, rgb=C_TEXT_WHITE)

s1.text(105, 542, "Professor / Avaliador:", font="F_Bold", size=13, rgb=C_TEXT_MUTED)
s1.text(285, 542, "Prof. Maurício", font="F_Bold", size=14, rgb=C_TEXT_WHITE)

s1.text(105, 574, "Período Letivo:", font="F_Bold", size=13, rgb=C_TEXT_MUTED)
s1.text(285, 574, "2º Período - Sistemas de Informação", font="F_Reg", size=13, rgb=C_TEXT_WHITE)

s1.text(105, 606, "Local / Ano:", font="F_Bold", size=13, rgb=C_TEXT_MUTED)
s1.text(285, 606, "Arapiraca - AL • 2026", font="F_Reg", size=13, rgb=C_TEXT_WHITE)

# Summary of Defense Requirements (Lower Right)
s1.round_rect(630, 440, 570, 190, 10, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
s1.text(655, 475, "ESTRUTURA DE AVALIAÇÃO DA APRESENTAÇÃO (10~15 MIN):", font="F_Bold", size=13, rgb=C_ACCENT_BLUE)

checklist = [
    ("1.", "Demandas encontradas no estabelecimento e objetivos traçados"),
    ("2.", "Requisitos desenvolvidos (Funcionais e Não Funcionais - Valente Cap. 3)"),
    ("3.", "O que foi atendido pelo software (MVP e escopo)"),
    ("4.", "Quais e onde foram utilizadas as 7 estruturas obrigatórias no código"),
    ("5.", "Cronograma de atividades semanais e demonstração ao vivo no terminal"),
]

cy = 508
for num, item_txt in checklist:
    s1.text(655, cy, num, font="F_Bold", size=12, rgb=C_ACCENT_TEAL)
    s1.text(675, cy, item_txt, font="F_Reg", size=12, rgb=C_TEXT_LIGHT)
    cy += 24


# ==========================================
# SLIDE 2: FUNDAMENTAÇÃO TEÓRICA (VALENTE, CAP. 3)
# ==========================================
s2 = builder.add_page()
s2.fill_rect(0, 0, 1280, 720, C_BG)
s2.slide_header(2, 11, "Fundamentação Teórica: Engenharia de Requisitos")

s2.text(60, 105, "A Importância dos Requisitos Segundo a Literatura Técnica", font="F_Bold", size=26, rgb=C_TEXT_WHITE)
s2.text(60, 130, "Referência: VALENTE, Marco Tulio. Engenharia de Software Moderna. Belo Horizonte, 2020. Capítulo 3.", font="F_Reg", size=13, rgb=C_TEXT_MUTED)

# Quote 1 Box
s2.round_rect(60, 160, 1160, 130, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
s2.round_rect(80, 175, 140, 24, 4, fill_rgb=(0.08, 0.20, 0.35))
s2.text(92, 191, "VALENTE (2020, p. 84)", font="F_Bold", size=10, rgb=C_ACCENT_BLUE)

s2.text(80, 222, "\"A definição dos requisitos é uma etapa crucial da construção de qualquer sistema de software.", font="F_Bold", size=15, rgb=C_TEXT_WHITE)
s2.text(80, 246, "De nada adianta ter um sistema com o melhor design, implementado na mais moderna linguagem,", font="F_Bold", size=15, rgb=C_TEXT_WHITE)
s2.text(80, 270, "usando o melhor processo de desenvolvimento, com alta cobertura de testes e ele não atender às necessidades de seus usuários.\"", font="F_Bold", size=15, rgb=C_ACCENT_TEAL)

# Quote 2 Box
s2.round_rect(60, 310, 1160, 115, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
s2.round_rect(80, 325, 140, 24, 4, fill_rgb=(0.08, 0.20, 0.35))
s2.text(92, 341, "VALENTE (2020, p. 89)", font="F_Bold", size=10, rgb=C_ACCENT_BLUE)

s2.text(80, 372, "\"Requisitos são a 'ponte' que liga um problema do mundo real", font="F_Bold", size=17, rgb=C_TEXT_WHITE)
s2.text(80, 398, "a um sistema de software que o soluciona.\"", font="F_Bold", size=17, rgb=C_ACCENT_TEAL)

# Application in our Project Box
s2.round_rect(60, 445, 1160, 235, 8, fill_rgb=C_CARD_ALT, stroke_rgb=C_ACCENT_TEAL, stroke_w=1.5)
s2.text(85, 475, "COMO ESSA BASE TEÓRICA FOI APLICADA NO PROJETO DA FARMÁCIA:", font="F_Bold", size=13, rgb=C_ACCENT_TEAL)

app_points = [
    ("1. Compreensão do Domínio:", "Mapeamento prévio da rotina de balcão e regras de lote antes de escrever código."),
    ("2. Requisitos como Ponte:", "Especificação de RFs e RNFs garantindo integridade de estoque e agilidade no caixa."),
    ("3. Histórias de Usuário:", "Necessidades modeladas no padrão INVEST (Cartão, Conversa e Confirmação/DoD)."),
    ("4. Entrega de Valor (MVP):", "Foco no núcleo de valor imediato (PDV + Estoque + CSV) sem complexidades prematuras."),
]

ay = 505
for title, desc in app_points:
    s2.text(85, ay, title, font="F_Bold", size=13, rgb=C_TEXT_WHITE)
    s2.text(320, ay, desc, font="F_Reg", size=13, rgb=C_TEXT_LIGHT)
    ay += 36


# ==========================================
# SLIDE 3: PERGUNTA 1 - DEMANDAS ENCONTRADAS
# ==========================================
s3 = builder.add_page()
s3.fill_rect(0, 0, 1280, 720, C_BG)
s3.slide_header(3, 11, "Demandas Encontradas no Estabelecimento", question_hint="Quais foram as demandas encontradas no estabelecimento para o projeto?")

s3.text(60, 130, "Cenário Operacional Observado na Farmácia de Balcão", font="F_Bold", size=24, rgb=C_TEXT_WHITE)
s3.text(60, 155, "Identificação dos problemas reais de rotina que justificaram a construção do sistema:", font="F_Reg", size=14, rgb=C_TEXT_MUTED)

# 3 Columns
col_w = 360
col_h = 490

demands = [
    (
        "DEMANDA 1: CONTROLE MANUAL",
        "Cadernos, Fichas e Rasuras",
        [
            "Registro de entrada e saída feito em cadernos de papel sujeitos a rasuras e extravios;",
            "Anotações ilegíveis dificultando a identificação exata de medicamentos e apresentações;",
            "Falta total de rastreabilidade sobre qual funcionário realizou reposições ou alterações;",
            "Histórico inexistente para consulta rápida de compras anteriores de clientes recorrentes."
        ],
        (0.85, 0.35, 0.35)
    ),
    (
        "DEMANDA 2: GARGALO NO CAIXA",
        "Lentidão no Balcão e Erros de Soma",
        [
            "Atendente precisava consultar preços manualmente em tabelas impressas;",
            "Cálculo de subtotais e trocos feito manualmente na calculadora, gerando erros;",
            "Formação de filas em horários de pico devido à demora no fechamento de cada venda;",
            "Conflito de conferência no fechamento diário do caixa por inconsistências manuais."
        ],
        C_ACCENT_TEAL
    ),
    (
        "DEMANDA 3: RUPTURA E VENCIMENTO",
        "Descontrole de Estoque e Validade",
        [
            "Inexistência de alerta preventivo quando o estoque atinge o nível mínimo de segurança;",
            "Medicamentos essenciais esgotavam no estoque físico sem a equipe perceber a tempo;",
            "Perda financeira e risco sanitário por remédios que passavam da data de validade na prateleira;",
            "Falta de relatórios estruturados para envio de pedidos programados às distribuidoras."
        ],
        C_ACCENT_BLUE
    ),
]

for i, (tag, title, bullets, col) in enumerate(demands):
    dx = 60 + i * (col_w + 40)
    dy = 185
    s3.round_rect(dx, dy, col_w, col_h, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
    
    s3.round_rect(dx + 20, dy + 20, col_w - 40, 26, 4, fill_rgb=(0.08, 0.12, 0.20))
    s3.text(dx + 30, dy + 37, tag, font="F_Bold", size=10, rgb=col)
    
    s3.text(dx + 20, dy + 75, title, font="F_Bold", size=16, rgb=C_TEXT_WHITE)
    s3.line(dx + 20, dy + 95, dx + col_w - 20, dy + 95, C_BORDER, stroke_w=1)
    
    by = dy + 125
    for b in bullets:
        s3.text(dx + 22, by, "-", font="F_Bold", size=13, rgb=col)
        # wrap
        words = b.split(" ")
        s3.text(dx + 35, by, " ".join(words[:5]), font="F_Reg", size=12, rgb=C_TEXT_LIGHT)
        s3.text(dx + 35, by + 18, " ".join(words[5:10]), font="F_Reg", size=12, rgb=C_TEXT_LIGHT)
        if len(words) > 10:
            s3.text(dx + 35, by + 36, " ".join(words[10:]), font="F_Reg", size=12, rgb=C_TEXT_LIGHT)
            by += 18
        by += 44


# ==========================================
# SLIDE 4: PERGUNTA 2 - OBJETIVOS DO PROJETO
# ==========================================
s4 = builder.add_page()
s4.fill_rect(0, 0, 1280, 720, C_BG)
s4.slide_header(4, 11, "Objetivos Traçados para o Projeto", question_hint="Quais foram os objetivos traçados para o seu projeto?")

s4.text(60, 130, "Objetivo Geral e Objetivos Específicos do Sistema", font="F_Bold", size=24, rgb=C_TEXT_WHITE)
s4.text(60, 155, "Metas claras alinhadas para sanar as demandas operacionais identificadas:", font="F_Reg", size=14, rgb=C_TEXT_MUTED)

# General Goal Banner
s4.round_rect(60, 180, 1160, 85, 8, fill_rgb=C_CARD, stroke_rgb=C_ACCENT_TEAL, stroke_w=1.5)
s4.text(85, 208, "OBJETIVO GERAL:", font="F_Bold", size=12, rgb=C_ACCENT_TEAL)
s4.text(85, 235, "Desenvolver um sistema modular em Python com interface de terminal (CLI) e banco SQLite, capaz de", font="F_Bold", size=15, rgb=C_TEXT_WHITE)
s4.text(85, 255, "automatizar as operações de balcão (PDV), garantir 100% de consistência no estoque e exportar relatórios físicos em CSV.", font="F_Bold", size=15, rgb=C_TEXT_WHITE)

# 3 Specific Goals
goals = [
    (
        "OBJETIVO ESPECÍFICO 1",
        "Automatizar o Ponto de Venda (PDV) e Atendimento Rápido",
        "Permitir que o operador localize medicamentos por código ou nome parcial em menos de 1 segundo, adicione múltiplos itens ao carrinho dinâmico e conclua a venda com cálculo exato de subtotais e totais.",
        "Meta prática: Reduzir o tempo médio de atendimento de 3 minutos para menos de 30 segundos por cliente."
    ),
    (
        "OBJETIVO ESPECÍFICO 2",
        "Garantir Integridade e Bloqueio de Estoque Insuficiente",
        "Implementar transações atômicas no padrão Unit of Work com SQLite: caso qualquer item da compra não possua saldo em estoque, a venda inteira é abortada (princípio 'Tudo ou Nada').",
        "Meta prática: Eliminar 100% das divergências entre o estoque físico e o estoque registrado no sistema."
    ),
    (
        "OBJETIVO ESPECÍFICO 3",
        "Prover Gestão de Validade, Alertas e Exportação em Planilhas CSV",
        "Fornecer ao farmacêutico listagens instantâneas de medicamentos em estoque crítico (<= mínimo) e com validade próxima, além de exportador físico para arquivos .csv codificados em UTF-8 com separador ';'.",
        "Meta prática: Permitir planejamento de compras antecipado e conferência financeira no Excel/LibreOffice."
    ),
]

gy = 285
for tag, title, desc, meta in goals:
    s4.round_rect(60, gy, 1160, 125, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
    
    s4.round_rect(80, gy + 15, 170, 22, 4, fill_rgb=(0.08, 0.16, 0.28))
    s4.text(92, gy + 30, tag, font="F_Bold", size=10, rgb=C_ACCENT_BLUE)
    
    s4.text(265, gy + 30, title, font="F_Bold", size=15, rgb=C_TEXT_WHITE)
    s4.line(80, gy + 48, 1200, gy + 48, C_BORDER, stroke_w=1)
    
    s4.text(80, gy + 72, desc, font="F_Reg", size=13, rgb=C_TEXT_LIGHT)
    s4.text(80, gy + 98, f"• {meta}", font="F_Bold", size=12, rgb=C_ACCENT_TEAL)
    
    gy += 140


# ==========================================
# SLIDE 5: PERGUNTA 3 - REQUISITOS DO SISTEMA
# ==========================================
s5 = builder.add_page()
s5.fill_rect(0, 0, 1280, 720, C_BG)
s5.slide_header(5, 11, "Requisitos Desenvolvidos (RFs e RNFs)", question_hint="Quais os requisitos desenvolvidos para o seu projeto?")

s5.text(60, 130, "Requisitos Funcionais (O que o sistema faz) e Não Funcionais (Como faz)", font="F_Bold", size=24, rgb=C_TEXT_WHITE)
s5.text(60, 155, "Especificação técnica fundamentada no Capítulo 3 do Valente (p. 90-93):", font="F_Reg", size=14, rgb=C_TEXT_MUTED)

# 2 Columns for RF and RNF
cw = 560
ch = 490

# Left: RF
s5.round_rect(60, 185, cw, ch, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
s5.round_rect(80, 200, 240, 26, 4, fill_rgb=(0.08, 0.22, 0.20))
s5.text(95, 218, "REQUISITOS FUNCIONAIS (RF)", font="F_Bold", size=12, rgb=C_ACCENT_TEAL)

rfs = [
    ("RF01 - Catálogo de Medicamentos:", "Cadastrar, atualizar dados, listar e pesquisar medicamentos por nome ou código único."),
    ("RF02 - Ponto de Venda (PDV):", "Adicionar medicamentos sequencialmente ao carrinho dinâmico com subtotal e cliente opcional."),
    ("RF03 - Baixa Atômica de Estoque:", "Decrementar a quantidade física vendida diretamente no banco na confirmação da venda."),
    ("RF04 - Bloqueio de Estoque Insuficiente:", "Impedir a finalização da compra caso a quantidade pedida supere o estoque disponível."),
    ("RF05 - Entrada de Lotes (Reposição):", "Registrar reposições no estoque com quantidade positiva, data/hora e motivo da entrada."),
    ("RF06 - Alertas de Validade e Estoque Mínimo:", "Filtrar e exibir medicamentos com estoque <= estoque_minimo ou prazo de validade crítico."),
    ("RF07 - Exportação de Relatórios CSV:", "Gerar arquivos físicos .csv tabulados na pasta reports/ para análise gerencial externa.")
]

rf_y = 245
for title, desc in rfs:
    s5.text(80, rf_y, title, font="F_Bold", size=12, rgb=C_TEXT_WHITE)
    words = desc.split(" ")
    s5.text(80, rf_y + 16, " ".join(words[:8]), font="F_Reg", size=11, rgb=C_TEXT_LIGHT)
    s5.text(80, rf_y + 30, " ".join(words[8:]), font="F_Reg", size=11, rgb=C_TEXT_LIGHT)
    rf_y += 50

# Right: RNF
s5.round_rect(660, 185, cw, ch, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
s5.round_rect(680, 200, 270, 26, 4, fill_rgb=(0.08, 0.18, 0.32))
s5.text(695, 218, "REQUISITOS NÃO FUNCIONAIS (RNF)", font="F_Bold", size=12, rgb=C_ACCENT_BLUE)

rnfs = [
    ("RNF01 - Banco de Dados Relacional (SQLite):", "Persistência em banco relacional local (data/farmacia.db) com Prepared Statements (?) contra injection."),
    ("RNF02 - Integridade Referencial Ativa:", "Chaves estrangeiras (PRAGMA foreign_keys = ON) assegurando que vendas e itens dependam de entidades válidas."),
    ("RNF03 - Consistência Transacional (UoW):", "Padrão Unit of Work garantindo transações atômicas com commit() e rollback() seguro em caso de falha."),
    ("RNF04 - Precisão Monetária em Centavos:", "Armazenamento de moeda em inteiros (preco_centavos) evitando discrepâncias de ponto flutuante."),
    ("RNF05 - Desempenho no Terminal (< 1s):", "Tempo de resposta instantâneo nas pesquisas com criação de índices nos campos mais consultados."),
    ("RNF06 - Arquitetura Desacoplada (SOLID):", "Separação total entre camadas de Apresentação (CLI), Domínio (Services) e Infraestrutura (Repositories)."),
    ("RNF07 - Formatação Padrão de Arquivos CSV:", "Arquivos gerados com encoding UTF-8 (compatível com acentuação) e delimitador ponto e vírgula (;).")
]

rnf_y = 245
for title, desc in rnfs:
    s5.text(680, rnf_y, title, font="F_Bold", size=12, rgb=C_TEXT_WHITE)
    words = desc.split(" ")
    s5.text(680, rnf_y + 16, " ".join(words[:8]), font="F_Reg", size=11, rgb=C_TEXT_LIGHT)
    s5.text(680, rnf_y + 30, " ".join(words[8:]), font="F_Reg", size=11, rgb=C_TEXT_LIGHT)
    rnf_y += 50


# ==========================================
# SLIDE 6: HISTÓRIAS DE USUÁRIOS (INVEST - VALENTE SEÇÃO 3.3)
# ==========================================
s6 = builder.add_page()
s6.fill_rect(0, 0, 1280, 720, C_BG)
s6.slide_header(6, 11, "Histórias de Usuários (User Stories - INVEST)")

s6.text(60, 130, "Mapeamento Ágil de Necessidades dos Usuários (Valente, p. 94-96)", font="F_Bold", size=24, rgb=C_TEXT_WHITE)
s6.text(60, 155, "Formato: Cartão (Card) + Conversas (Conversation) + Confirmação / Critérios de Aceite (Confirmation):", font="F_Reg", size=14, rgb=C_TEXT_MUTED)

# US01 Box
s6.round_rect(60, 185, 1160, 230, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
s6.round_rect(80, 200, 190, 24, 4, fill_rgb=(0.08, 0.18, 0.32))
s6.text(92, 216, "US01 - OPERADOR DE CAIXA", font="F_Bold", size=10, rgb=C_ACCENT_BLUE)

s6.text(80, 248, "Como atendente de balcão / operador de caixa,", font="F_Bold", size=17, rgb=C_TEXT_WHITE)
s6.text(80, 272, "quero pesquisar medicamentos por nome ou código e registrar vendas no PDV com cálculo automático,", font="F_Reg", size=15, rgb=C_ACCENT_TEAL)
s6.text(80, 296, "para agilizar o atendimento, eliminar filas e assegurar que nenhum valor seja calculado errado.", font="F_Reg", size=15, rgb=C_TEXT_LIGHT)

s6.line(80, 320, 1200, 320, C_BORDER, stroke_w=1)
s6.text(80, 342, "CRITÉRIOS DE ACEITAÇÃO (CONFIRMAÇÃO / DOD):", font="F_Bold", size=11, rgb=C_TEXT_MUTED)
s6.text(80, 366, "[+] Busca case-insensitive retornando preço e saldo;", font="F_Reg", size=12, rgb=C_TEXT_LIGHT)
s6.text(480, 366, "[+] Recalcular subtotal e total a cada item;", font="F_Reg", size=12, rgb=C_TEXT_LIGHT)
s6.text(860, 366, "[+] Bloquear venda se saldo for menor que pedido.", font="F_Reg", size=12, rgb=C_TEXT_LIGHT)

# US02 Box
s6.round_rect(60, 435, 1160, 230, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
s6.round_rect(80, 450, 220, 24, 4, fill_rgb=(0.08, 0.22, 0.20))
s6.text(92, 466, "US02 - FARMACÊUTICO / GERENTE", font="F_Bold", size=10, rgb=C_ACCENT_TEAL)

s6.text(80, 498, "Como farmacêutico responsável / gerente da farmácia,", font="F_Bold", size=17, rgb=C_TEXT_WHITE)
s6.text(80, 522, "quero consultar medicamentos em nível crítico de estoque e exportar o relatório de vendas em CSV,", font="F_Reg", size=15, rgb=C_ACCENT_BLUE)
s6.text(80, 546, "para repor medicamentos essenciais a tempo, evitar vencimentos e conferir o faturamento do caixa.", font="F_Reg", size=15, rgb=C_TEXT_LIGHT)

s6.line(80, 570, 1200, 570, C_BORDER, stroke_w=1)
s6.text(80, 592, "CRITÉRIOS DE ACEITAÇÃO (CONFIRMAÇÃO / DOD):", font="F_Bold", size=11, rgb=C_TEXT_MUTED)
s6.text(80, 616, "[+] Filtro imediato onde estoque <= estoque_minimo;", font="F_Reg", size=12, rgb=C_TEXT_LIGHT)
s6.text(480, 616, "[+] Comparação de datas no formato ISO 8601;", font="F_Reg", size=12, rgb=C_TEXT_LIGHT)
s6.text(860, 616, "[+] Gravação física de arquivo CSV na pasta reports/.", font="F_Reg", size=12, rgb=C_TEXT_LIGHT)


# ==========================================
# SLIDE 7: DIAGRAMA UML DE CASOS DE USO (DRAW.IO)
# ==========================================
s7 = builder.add_page()
s7.fill_rect(0, 0, 1280, 720, C_BG)
s7.slide_header(7, 11, "Casos de Uso e Diagrama UML (Software Draw.io)")

s7.text(60, 125, "Modelagem Formal de Casos de Uso (Valente, p. 97-100)", font="F_Bold", size=24, rgb=C_TEXT_WHITE)
s7.text(60, 148, "Arquivo editável gerado no projeto: docs/diagrama_casos_de_uso.drawio (abrir em app.diagrams.net)", font="F_Reg", size=13, rgb=C_ACCENT_TEAL)

# Draw.io Blueprint Canvas
dw_x, dw_y, dw_w, dw_h = 60, 175, 1160, 495
s7.round_rect(dw_x, dw_y, dw_w, dw_h, 8, fill_rgb=(0.98, 0.98, 0.99), stroke_rgb=(0.70, 0.75, 0.82), stroke_w=1.5)

# System Boundary
sb_x, sb_y, sb_w, sb_h = dw_x + 200, dw_y + 15, 760, 465
s7.round_rect(sb_x, sb_y, sb_w, sb_h, 4, fill_rgb=(1.0, 1.0, 1.0), stroke_rgb=(0.30, 0.35, 0.45), stroke_w=1.8)
s7.text_center(sb_x + sb_w / 2, sb_y + 22, "Sistema de Gerenciamento de Farmácia (Drogaria Vida & Saúde)", font="F_Bold", size=13, rgb=(0.1, 0.15, 0.25))

# Actor 1: Caixa (Left)
ax1 = dw_x + 90
ay1 = dw_y + 230
s7.circle(ax1, ay1 - 50, 18, fill_rgb=(0.88, 0.92, 0.96), stroke_rgb=(0.15, 0.22, 0.33), stroke_w=2)
s7.line(ax1, ay1 - 32, ax1, ay1 + 18, rgb=(0.15, 0.22, 0.33), stroke_w=2)
s7.line(ax1 - 25, ay1 - 14, ax1 + 25, ay1 - 14, rgb=(0.15, 0.22, 0.33), stroke_w=2)
s7.line(ax1, ay1 + 18, ax1 - 20, ay1 + 65, rgb=(0.15, 0.22, 0.33), stroke_w=2)
s7.line(ax1, ay1 + 18, ax1 + 20, ay1 + 65, rgb=(0.15, 0.22, 0.33), stroke_w=2)
s7.text_center(ax1, ay1 + 86, "Operador de Caixa", font="F_Bold", size=11, rgb=(0.15, 0.22, 0.33))
s7.text_center(ax1, ay1 + 100, "/ Atendente", font="F_Bold", size=11, rgb=(0.15, 0.22, 0.33))

# Actor 2: Gerente (Right)
ax2 = dw_x + dw_w - 90
ay2 = dw_y + 230
s7.circle(ax2, ay2 - 50, 18, fill_rgb=(0.88, 0.92, 0.96), stroke_rgb=(0.15, 0.22, 0.33), stroke_w=2)
s7.line(ax2, ay2 - 32, ax2, ay2 + 18, rgb=(0.15, 0.22, 0.33), stroke_w=2)
s7.line(ax2 - 25, ay2 - 14, ax2 + 25, ay2 - 14, rgb=(0.15, 0.22, 0.33), stroke_w=2)
s7.line(ax2, ay2 + 18, ax2 - 20, ay2 + 65, rgb=(0.15, 0.22, 0.33), stroke_w=2)
s7.line(ax2, ay2 + 18, ax2 + 20, ay2 + 65, rgb=(0.15, 0.22, 0.33), stroke_w=2)
s7.text_center(ax2, ay2 + 86, "Farmacêutico", font="F_Bold", size=11, rgb=(0.15, 0.22, 0.33))
s7.text_center(ax2, ay2 + 100, "/ Gerente de Loja", font="F_Bold", size=11, rgb=(0.15, 0.22, 0.33))

# Draw.io Use Cases
cases = [
    ("uc01", "UC01: Realizar Venda no PDV", sb_x + 40, sb_y + 45, 230, 46, (0.85, 0.92, 0.99), (0.15, 0.45, 0.85), (0.05, 0.2, 0.5)),
    ("uc02", "UC02: Validar Estoque (Tudo ou Nada)", sb_x + 460, sb_y + 35, 240, 40, (0.99, 0.92, 0.92), (0.85, 0.2, 0.2), (0.6, 0.1, 0.1)),
    ("uc03", "UC03: Calcular Subtotais e Total", sb_x + 460, sb_y + 88, 240, 40, (0.99, 0.92, 0.92), (0.85, 0.2, 0.2), (0.6, 0.1, 0.1)),
    ("uc04", "UC04: Identificar Cliente no Balcão", sb_x + 40, sb_y + 115, 220, 40, (0.92, 0.98, 0.94), (0.1, 0.65, 0.3), (0.05, 0.4, 0.15)),
    
    ("uc05", "UC05: Cadastrar / Atualizar Medicamentos", sb_x + 220, sb_y + 180, 300, 44, (0.93, 0.96, 1.0), (0.25, 0.5, 0.9), (0.1, 0.25, 0.55)),
    ("uc06", "UC06: Registrar Entrada de Estoque (Lotes)", sb_x + 220, sb_y + 235, 300, 44, (0.93, 0.96, 1.0), (0.25, 0.5, 0.9), (0.1, 0.25, 0.55)),
    ("uc07", "UC07: Consultar Estoque Crítico e Validade", sb_x + 220, sb_y + 290, 300, 44, (0.93, 0.96, 1.0), (0.25, 0.5, 0.9), (0.1, 0.25, 0.55)),
    ("uc08", "UC08: Exportar Relatórios em Planilhas CSV", sb_x + 220, sb_y + 345, 300, 44, (0.93, 0.96, 1.0), (0.25, 0.5, 0.9), (0.1, 0.25, 0.55)),
    ("uc09", "UC09: Gerenciar Cadastro de Clientes", sb_x + 220, sb_y + 400, 300, 44, (0.93, 0.96, 1.0), (0.25, 0.5, 0.9), (0.1, 0.25, 0.55)),
]

for cid, title, cx, cy, cw, ch, f_col, s_col, t_col in cases:
    s7.round_rect(cx, cy, cw, ch, ch/2, fill_rgb=f_col, stroke_rgb=s_col, stroke_w=1.5)
    s7.text_center(cx + cw/2, cy + ch/2 + 4, title, font="F_Bold", size=11, rgb=t_col)

# Connections
s7.line(ax1 + 30, ay1 - 10, sb_x + 40, sb_y + 68, rgb=(0.2, 0.3, 0.45), stroke_w=1.5)
s7.line(ax1 + 30, ay1 + 20, sb_x + 220, sb_y + 422, rgb=(0.2, 0.3, 0.45), stroke_w=1.5)

# <<include>>
s7.line(sb_x + 270, sb_y + 60, sb_x + 460, sb_y + 55, rgb=(0.85, 0.2, 0.2), stroke_w=1.2, dashed=4)
s7.text(sb_x + 310, sb_y + 54, "<<include>>", font="F_Bold", size=9, rgb=(0.85, 0.2, 0.2))

s7.line(sb_x + 270, sb_y + 75, sb_x + 460, sb_y + 105, rgb=(0.85, 0.2, 0.2), stroke_w=1.2, dashed=4)
s7.text(sb_x + 310, sb_y + 100, "<<include>>", font="F_Bold", size=9, rgb=(0.85, 0.2, 0.2))

# <<extend>>
s7.line(sb_x + 150, sb_y + 115, sb_x + 150, sb_y + 91, rgb=(0.1, 0.65, 0.3), stroke_w=1.2, dashed=4)
s7.text(sb_x + 158, sb_y + 108, "<<extend>>", font="F_Bold", size=9, rgb=(0.1, 0.65, 0.3))

# Gerente lines
for tgt_y in [sb_y + 202, sb_y + 257, sb_y + 312, sb_y + 367, sb_y + 422]:
    s7.line(ax2 - 30, ay2, sb_x + 520, tgt_y, rgb=(0.2, 0.3, 0.45), stroke_w=1.5)


# ==========================================
# SLIDE 8: PERGUNTA 4 - O QUE FOI ATENDIDO PELO PROJETO (MVP)
# ==========================================
s8 = builder.add_page()
s8.fill_rect(0, 0, 1280, 720, C_BG)
s8.slide_header(8, 11, "O Que Foi Atendido pelo Projeto (MVP Entregue)", question_hint="O que foi atendido pelo seu projeto?")

s8.text(60, 130, "Produto Mínimo Viável Entregue vs. Escopo Futuro (Valente, p. 101-103)", font="F_Bold", size=24, rgb=C_TEXT_WHITE)
s8.text(60, 155, "Validação prática da hipótese de valor do negócio no menor tempo e com alta confiabilidade:", font="F_Reg", size=14, rgb=C_TEXT_MUTED)

# Table of Scope: Present in MVP vs Future
s8.round_rect(60, 185, 680, 485, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
s8.text(80, 212, "MATRIZ DE ATENDIMENTO DE ESCOPO DO MVP:", font="F_Bold", size=13, rgb=C_ACCENT_TEAL)

# Table Headers
s8.round_rect(80, 230, 640, 28, 4, fill_rgb=(0.08, 0.12, 0.20))
s8.text(90, 248, "Funcionalidade Mapeada", font="F_Bold", size=11, rgb=C_TEXT_MUTED)
s8.text(380, 248, "Status no MVP", font="F_Bold", size=11, rgb=C_TEXT_MUTED)
s8.text(500, 248, "Impacto no Negócio", font="F_Bold", size=11, rgb=C_TEXT_MUTED)

matrix_rows = [
    ("Cadastro e Catálogo de Medicamentos", "[ENTREGUE]", "Preços e estoque inicial ativos", C_ACCENT_TEAL),
    ("Ponto de Venda (PDV) com Carrinho", "[ENTREGUE]", "Atendimento ágil no balcão", C_ACCENT_TEAL),
    ("Bloqueio de Venda sem Estoque", "[ENTREGUE]", "Consistência 'Tudo ou Nada'", C_ACCENT_TEAL),
    ("Registro de Reposição de Lotes", "[ENTREGUE]", "Rastreabilidade de entradas", C_ACCENT_TEAL),
    ("Alertas de Estoque Mínimo e Validade", "[ENTREGUE]", "Prevenção contra desabastecimento", C_ACCENT_TEAL),
    ("Persistência em Banco SQLite (FK)", "[ENTREGUE]", "Integridade relacional dos dados", C_ACCENT_TEAL),
    ("Exportação de Planilhas em CSV", "[ENTREGUE]", "Conferência externa no Excel", C_ACCENT_TEAL),
    ("Emissão de Nota Fiscal Eletrônica (NFC-e)", "[PÓS-MVP]", "Depende de certificado digital SEFAZ", (0.85, 0.60, 0.20)),
    ("Integração com Maquininha TEF", "[PÓS-MVP]", "Operado via POS físico de balcão", (0.85, 0.60, 0.20)),
    ("Integração com SNGPC / ANVISA", "[PÓS-MVP]", "Complexidade desnecessária no MVP", (0.85, 0.60, 0.20)),
]

my = 278
for feat, status, impact, col in matrix_rows:
    s8.text(90, my, feat, font="F_Reg", size=11, rgb=C_TEXT_WHITE)
    s8.text(380, my, status, font="F_Bold", size=11, rgb=col)
    s8.text(500, my, impact, font="F_Reg", size=11, rgb=C_TEXT_LIGHT)
    s8.line(80, my + 6, 720, my + 6, (0.14, 0.18, 0.26), stroke_w=1)
    my += 23

# Terminal Proof / Receipt Box (Right Side)
s8.round_rect(760, 185, 460, 485, 8, fill_rgb=(0.96, 0.96, 0.93), stroke_rgb=(0.75, 0.75, 0.75), stroke_w=1.5)

s8.text_center(990, 220, "DROGARIA VIDA & SAÚDE", font="F_MonoBold", size=14, rgb=(0.1, 0.1, 0.1))
s8.text_center(990, 238, "Av. Fernandes Lima, 1020 - Centro - Arapiraca", font="F_Mono", size=10, rgb=(0.3, 0.3, 0.3))
s8.text_center(990, 252, "CNPJ: 12.345.678/0001-90", font="F_Mono", size=10, rgb=(0.3, 0.3, 0.3))
s8.line(780, 262, 1200, 262, (0.5, 0.5, 0.5), stroke_w=1, dashed=3)

s8.text(780, 280, "COMPROVANTE DE VENDA: #00042", font="F_MonoBold", size=11, rgb=(0.1, 0.1, 0.1))
s8.text(780, 296, "DATA: 19/11/2026 19:30   CAIXA: 01", font="F_Mono", size=10, rgb=(0.3, 0.3, 0.3))
s8.text(780, 312, "CLIENTE: Consumidor Avulso", font="F_Mono", size=10, rgb=(0.3, 0.3, 0.3))
s8.line(780, 322, 1200, 322, (0.5, 0.5, 0.5), stroke_w=1)

s8.text(780, 338, "ITEM COD  DESC             QTD  PRECO   TOTAL", font="F_MonoBold", size=10, rgb=(0.1, 0.1, 0.1))
s8.line(780, 346, 1200, 346, (0.5, 0.5, 0.5), stroke_w=1, dashed=2)

receipt_data = [
    ("01", "M01", "Dipirona 500mg", "2 un", "12.50", "25.00"),
    ("02", "M04", "Amoxicilina 500", "1 un", "28.90", "28.90"),
    ("03", "M07", "Vitamina C 1g", "2 un", "15.00", "30.00"),
]

ry = 368
for i_num, i_cod, i_desc, i_qtd, i_pr, i_tot in receipt_data:
    s8.text(780, ry, f"{i_num}   {i_cod}  {i_desc:<16} {i_qtd}  {i_pr}  {i_tot}", font="F_Mono", size=10, rgb=(0.1, 0.1, 0.1))
    ry += 20

s8.line(780, ry + 6, 1200, ry + 6, (0.5, 0.5, 0.5), stroke_w=1, dashed=3)

s8.text(780, ry + 28, "SUBTOTAL:                        R$ 83,90", font="F_MonoBold", size=11, rgb=(0.1, 0.1, 0.1))
s8.text(780, ry + 46, "DESCONTO:                        R$  0,00", font="F_Mono", size=10, rgb=(0.3, 0.3, 0.3))
s8.text(780, ry + 70, "TOTAL GERAL:                     R$ 83,90", font="F_MonoBold", size=14, rgb=(0.80, 0.15, 0.15))

s8.line(780, ry + 86, 1200, ry + 86, (0.5, 0.5, 0.5), stroke_w=1)
s8.text_center(990, ry + 110, "ESTOQUE: BAIXA ATÔMICA EFETUADA!", font="F_MonoBold", size=11, rgb=(0.08, 0.50, 0.25))
s8.text_center(990, ry + 130, "Arquivo CSV gerado em: reports/relatorio_vendas.csv", font="F_Mono", size=9, rgb=(0.3, 0.3, 0.3))
s8.text_center(990, ry + 150, "Obrigado pela preferência! Volte sempre!", font="F_Mono", size=10, rgb=(0.2, 0.2, 0.2))


# ==========================================
# SLIDE 9: PERGUNTA 5 - MAPEAMENTO DAS ESTRUTURAS OBRIGATÓRIAS
# ==========================================
s9 = builder.add_page()
s9.fill_rect(0, 0, 1280, 720, C_BG)
s9.slide_header(9, 11, "Mapeamento das Estruturas no Código (Pontuação da Rubrica)", question_hint="Quais e onde foram utilizadas as estruturas no código?")

s9.text(60, 125, "Comprovação de Uso das Estruturas Obrigatórias (1,0 Ponto Cada)", font="F_Bold", size=24, rgb=C_TEXT_WHITE)
s9.text(60, 148, "Mapeamento exato de arquivo, método e linha comprovando o cumprimento de todas as exigências:", font="F_Reg", size=13, rgb=C_TEXT_MUTED)

# Big Table of Required Programming Structures
s9.round_rect(60, 175, 1160, 500, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)

# Table Header
s9.round_rect(80, 190, 1120, 30, 4, fill_rgb=(0.08, 0.14, 0.24))
s9.text(90, 210, "Estrutura Exigida (1,0 pt)", font="F_Bold", size=11, rgb=C_ACCENT_TEAL)
s9.text(320, 210, "Arquivo no Projeto", font="F_Bold", size=11, rgb=C_ACCENT_TEAL)
s9.text(590, 210, "Função / Método", font="F_Bold", size=11, rgb=C_ACCENT_TEAL)
s9.text(820, 210, "Aplicação Prática no Domínio da Farmácia", font="F_Bold", size=11, rgb=C_ACCENT_TEAL)

struct_rows = [
    ("Condicionais (if/else)", "services/medicamento_service.py", "cadastrar(), atualizar()", "Bloqueio de preços/estoque negativos e validação de validade."),
    ("Seleção (match/case)", "cli/terminal_interface.py", "iniciar(), menu_*()", "Roteamento das opções de navegação e comandos do usuário."),
    ("Laço while (Caso Real)", "cli/terminal_interface.py", "menu_*(), registrar_venda()", "Loop contínuo dos menus e processamento do carrinho no PDV."),
    ("Laço for", "services/venda_service.py", "registrar_venda()", "Varredura sequencial dos itens da compra e baixa atômica de estoque."),
    ("Subprogramas / Funções", "services/* e repositories/*", "Múltiplos métodos modulares", "Divisão estrita de responsabilidades em funções coesas (SRP)."),
    ("Listas Dinâmicas", "models/venda.py, services/*", "carrinho, self.itens", "Armazenamento dos itens da cesta e listas retornadas de consultas."),
    ("Matrizes (list[list])", "services/relatorio_service.py", "gerar_matriz_estoque()", "Montagem de grade bidimensional com cabeçalho e dados tabulados."),
    ("Cadeias de Caracteres", "repositories/medicamento_repo.py", "buscar_por_nome(), _validar()", "Uso de .strip(), .lower(), LIKE insensível e datas ISO 8601."),
    ("Dicionários e Tuplas", "models/*.py, repositories/*", "to_dict(), cursor.execute()", "Dicionários para serialização e tuplas em Prepared Statements."),
    ("Arquivos Físicos (CSV)", "exporters/csv_exporter.py", "exportar()", "Gravação em disco com open() e csv.writer(delimiter=';', utf-8)."),
    ("Banco SQLite Relacional", "database/schema.sql, repo/*", "SqliteUnitOfWork, cursor", "Tabelas com Foreign Keys, transações atômicas e índices."),
]

s_y = 242
for struct_name, file_path, func_name, expl in struct_rows:
    s9.text(90, s_y, struct_name, font="F_Bold", size=11, rgb=C_TEXT_WHITE)
    s9.text(320, s_y, file_path, font="F_Mono", size=10, rgb=C_ACCENT_BLUE)
    s9.text(590, s_y, func_name, font="F_Mono", size=10, rgb=C_ACCENT_TEAL)
    s9.text(820, s_y, expl, font="F_Reg", size=10, rgb=C_TEXT_LIGHT)
    s9.line(80, s_y + 6, 1200, s_y + 6, (0.14, 0.18, 0.26), stroke_w=1)
    s_y += 24


# ==========================================
# SLIDE 10: ATIVIDADES SEMANAIS (CRONOGRAMA DE EXECUÇÃO - 0,5 PONTO)
# ==========================================
s10 = builder.add_page()
s10.fill_rect(0, 0, 1280, 720, C_BG)
s10.slide_header(10, 11, "Atividades Semanais e Cronograma de Execução (0,5 Ponto)", question_hint="Atividades semanais (0,5 ponto)")

s10.text(60, 130, "Evolução do Projeto ao Longo das Semanas de Desenvolvimento", font="F_Bold", size=24, rgb=C_TEXT_WHITE)
s10.text(60, 155, "Registro das entregas iterativas do ciclo de vida do software:", font="F_Reg", size=14, rgb=C_TEXT_MUTED)

# 5 Weeks Cards
weeks = [
    (
        "SEMANA 1",
        "Levantamento e Requisitos (Valente Cap. 3)",
        [
            "Visita ao estabelecimento e observação da rotina de balcão;",
            "Leitura e fichamento do Capítulo 3 de Marco Tulio Valente;",
            "Identificação das dores de negócio (demandas da farmácia);",
            "Mapeamento inicial de RFs, RNFs e hipóteses do MVP."
        ],
        C_ACCENT_TEAL
    ),
    (
        "SEMANA 2",
        "Modelagem de Casos de Uso e Histórias",
        [
            "Elaboração das Histórias de Usuários com critérios INVEST;",
            "Modelagem do Diagrama UML de Casos de Uso no Draw.io;",
            "Definição das relações <<include>> e <<extend>> na venda;",
            "Criação do schema relacional SQL com chaves estrangeiras."
        ],
        C_ACCENT_BLUE
    ),
    (
        "SEMANA 3",
        "Arquitetura, Models e Repositórios SQL",
        [
            "Criação das entidades de domínio (Medicamento, Cliente, Venda);",
            "Implementação dos Repositories SQLite com Prepared Statements;",
            "Construção do SqliteUnitOfWork para controle transacional;",
            "Estruturação do container de injeção de dependências."
        ],
        C_ACCENT_TEAL
    ),
    (
        "SEMANA 4",
        "Camada de Serviços e Regras de Negócio",
        [
            "Desenvolvimento de MedicamentoService, VendaService e EstoqueService;",
            "Implementação da regra de bloqueio 'Tudo ou Nada' sem estoque;",
            "Aplicação das estruturas condicionais, laços while/for e listas;",
            "Testes de consistência financeira e baixa atômica de saldo."
        ],
        C_ACCENT_BLUE
    ),
    (
        "SEMANA 5",
        "Interface CLI, Exportação CSV e MVP Final",
        [
            "Construção da interface no terminal com menus em match/case;",
            "Implementação de CsvReportExporter com matrizes bidimensionais;",
            "Geração física de relatórios e comprovantes na pasta reports/;",
            "Validação final dos requisitos para a apresentação da disciplina."
        ],
        C_ACCENT_TEAL
    ),
]

w_width = 220
for i, (sem_tag, sem_title, tasks, col) in enumerate(weeks):
    wx = 60 + i * (w_width + 15)
    wy = 185
    wh = 485
    s10.round_rect(wx, wy, w_width, wh, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
    
    s10.round_rect(wx + 15, wy + 15, w_width - 30, 24, 4, fill_rgb=(0.08, 0.14, 0.24))
    s10.text(wx + 25, wy + 31, sem_tag, font="F_Bold", size=10, rgb=col)
    
    # Title
    words = sem_title.split(" ")
    s10.text(wx + 15, wy + 62, " ".join(words[:2]), font="F_Bold", size=13, rgb=C_TEXT_WHITE)
    s10.text(wx + 15, wy + 78, " ".join(words[2:]), font="F_Bold", size=13, rgb=C_TEXT_WHITE)
    s10.line(wx + 15, wy + 94, wx + w_width - 15, wy + 94, C_BORDER, stroke_w=1)
    
    # Task Bullets
    ty = wy + 120
    for t in tasks:
        s10.text(wx + 16, ty, "-", font="F_Bold", size=12, rgb=col)
        t_words = t.split(" ")
        s10.text(wx + 26, ty, " ".join(t_words[:3]), font="F_Reg", size=10, rgb=C_TEXT_LIGHT)
        s10.text(wx + 26, ty + 14, " ".join(t_words[3:6]), font="F_Reg", size=10, rgb=C_TEXT_LIGHT)
        if len(t_words) > 6:
            s10.text(wx + 26, ty + 28, " ".join(t_words[6:]), font="F_Reg", size=10, rgb=C_TEXT_LIGHT)
            ty += 14
        ty += 34


# ==========================================
# SLIDE 11: DEMONSTRAÇÃO PRÁTICA E CONCLUSÃO
# ==========================================
s11 = builder.add_page()
s11.fill_rect(0, 0, 1280, 720, C_BG)
s11.slide_header(11, 11, "Demonstração Prática e Encerramento (10~15 Minutos)")

s11.text(60, 125, "Roteiro da Demonstração ao Vivo no Terminal CLI", font="F_Bold", size=26, rgb=C_TEXT_WHITE)
s11.text(60, 150, "Demonstração prática dos fluxos reais para validação pela banca examinadora:", font="F_Reg", size=14, rgb=C_TEXT_MUTED)

# Demo Steps Box (Left)
s11.round_rect(60, 180, 680, 485, 8, fill_rgb=C_CARD, stroke_rgb=C_BORDER, stroke_w=1.5)
s11.text(85, 212, "PASSO A PASSO DA DEMONSTRAÇÃO DO SOFTWARE:", font="F_Bold", size=13, rgb=C_ACCENT_TEAL)

steps = [
    ("Passo 1: Inicialização Limpa", "Executar '$ python3 main.py' e exibir o menu principal operando com laço while e match/case."),
    ("Passo 2: Pesquisa e Catálogo", "Consultar medicamento por código ou termo parcial, demonstrando busca insensível a maiúsculas (LIKE)."),
    ("Passo 3: Ponto de Venda (PDV)", "Iniciar venda no balcão, adicionar múltiplos itens com cálculo automático de subtotais e identificação opcional."),
    ("Passo 4: Validação de Erro (Rollback)", "Tentar vender quantidade superior ao estoque físico e comprovar o lançamento de EstoqueInsuficienteError."),
    ("Passo 5: Conclusão da Venda e UoW", "Concluir venda válida comprovando a baixa atômica de saldo e geração do cupom na tela."),
    ("Passo 6: Exportação de Arquivos CSV", "Acessar menu de relatórios, gerar arquivo físico em reports/ e abrir o arquivo CSV para verificação."),
]

sy = 245
for step_title, step_desc in steps:
    s11.text(85, sy, f"• {step_title}:", font="F_Bold", size=13, rgb=C_TEXT_WHITE)
    s11.text(85, sy + 18, step_desc, font="F_Reg", size=11, rgb=C_TEXT_LIGHT)
    sy += 44

# Conclusion and Evaluation Checklist (Right)
s11.round_rect(760, 180, 460, 485, 8, fill_rgb=C_CARD_ALT, stroke_rgb=C_ACCENT_BLUE, stroke_w=1.5)
s11.text(785, 212, "CHECKLIST DE CONFORMIDADE DA RUBRICA:", font="F_Bold", size=13, rgb=C_ACCENT_BLUE)

rubric_checks = [
    ("1,0 pt", "if/else e/ou match/case", "IMPLEMENTADO E DEMONSTRADO"),
    ("1,0 pt", "while e/ou for", "IMPLEMENTADO E DEMONSTRADO"),
    ("1,0 pt", "Subprogramas / Funções", "IMPLEMENTADO E DEMONSTRADO"),
    ("1,0 pt", "Matrizes e Listas", "IMPLEMENTADO E DEMONSTRADO"),
    ("1,0 pt", "Strings e formatações", "IMPLEMENTADO E DEMONSTRADO"),
    ("1,0 pt", "Dicionários / Tuplas", "IMPLEMENTADO E DEMONSTRADO"),
    ("1,0 pt", "Arquivos físicos (CSV)", "IMPLEMENTADO E DEMONSTRADO"),
    ("2,5 pt", "Apresentação (5 perguntas)", "TOTALMENTE COBERTO NOS SLIDES"),
    ("0,5 pt", "Atividades semanais", "DETALHADO NO SLIDE 10"),
    ("10,0", "NOTA TOTAL ESPERADA", "CONFORMIDADE INTEGRAL"),
]

ry = 242
for pts, item_n, st in rubric_checks:
    s11.text(785, ry, pts, font="F_Bold", size=11, rgb=C_ACCENT_TEAL if pts != "10,0" else (1.0, 0.8, 0.2))
    s11.text(835, ry, item_n, font="F_Reg", size=11, rgb=C_TEXT_WHITE)
    s11.text(980, ry, st, font="F_Bold", size=9, rgb=C_TEXT_MUTED if pts != "10,0" else (1.0, 0.8, 0.2))
    s11.line(785, ry + 6, 1200, ry + 6, (0.16, 0.20, 0.28), stroke_w=1)
    ry += 24

# Terminal command box
s11.round_rect(785, 510, 410, 60, 6, fill_rgb=C_CODE_BG, stroke_rgb=C_BORDER, stroke_w=1.2)
s11.text(805, 535, "$ cd farmacia && python3 main.py", font="F_MonoBold", size=12, rgb=C_ACCENT_TEAL)
s11.text(805, 555, "Sistema pronto para execução imediata no terminal", font="F_Reg", size=10, rgb=C_TEXT_MUTED)

s11.text(785, 610, "Muito obrigado pela atenção!", font="F_Bold", size=18, rgb=C_TEXT_WHITE)
s11.text(785, 635, "Aberto a dúvidas e arguição da banca examinadora.", font="F_Reg", size=13, rgb=C_ACCENT_TEAL)


# Save PDF to project paths
pdf_bytes = builder.build()

paths = [
    "/home/kawe/Área de trabalho/Projetos SI/Projeto Do Mauricio/apresentacao_sistema_farmacia.pdf",
    "/home/kawe/Área de trabalho/Projetos SI/Projeto Do Mauricio/docs/apresentacao_sistema_farmacia.pdf",
    "/home/kawe/Área de trabalho/Projetos SI/Projeto Do Mauricio/farmacia/docs/apresentacao_sistema_farmacia.pdf",
]

for p in paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(pdf_bytes)
    print(f"Saved: {p}")

print("Clean Academic Presentation created successfully!")
