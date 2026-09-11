import sqlite3
import hashlib
import random
import os
import subprocess
import webbrowser
import sys
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.ticker as mticker
    MATPLOTLIB_DISPONIVEL = True
except ImportError:
    MATPLOTLIB_DISPONIVEL = False
    
def resource_path(relative_path):
    """Obtém o caminho correto dos recursos no desenvolvimento e no executável."""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.ticker as mticker
    MATPLOTLIB_DISPONIVEL = True
except ImportError:
    MATPLOTLIB_DISPONIVEL = False

class SistemaSalaoPaixaoFilhos:
    
 
    
    
    
    
    def __init__(self, root):
        self.root = root
        self.root.title("Salão de Festas Paixão e Filhos - Sistema de Gestão & Controlo Financeiro")
        
        # Correção do specifier da janela eliminando caracteres inválidos
        self.root.geometry("1300x800")
        
        # Paleta de Cores Elegante e Moderna (Tons de Rosa, Magenta e Escuros)
        self.COR_BG = "#1A1519"          # Fundo Principal Escuro Suave
        self.COR_CARD = "#2A1E25"        # Fundo dos Cards e Enquadramentos
        self.COR_TEXTO = "#FCE7F3"       # Texto Claro Roseado
        self.COR_ROSA_VIVO = "#F472B6"   # Rosa de Destaque / Elementos Ativos
        self.COR_MAGENTA = "#DB2777"     # Magenta para Botões e Ações Principais
        self.COR_MUTED = "#9D174D"       # Rosa Escuro para Detalhes Secundários
        
        self.root.configure(bg=self.COR_BG)
        
        # Variáveis de controlo interno
        self.utilizador_atual = None 
        self.utilizador_atual_id = None
        self.cargo_atual = None
        self.reserva_id_selecionado = None 
        self.logo_img = None  
        
        # Inicializacoes do sistema
        self.inicializar_bd()
        self._carregar_logo()
        self.ecran_login()

    def inicializar_bd(self):
        """Cria e atualiza a estrutura de tabelas relacionais com controlo de cargos"""
        self.conn = sqlite3.connect("salao_paixao_filhos.db")
        self.cursor = self.conn.cursor()
        
        # Habilitar suporte a chaves estrangeiras no SQLite
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # Tabela de utilizadores atualizada para conter o cargo do funcionário
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilizadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT UNIQUE, 
                password TEXT,
                cargo TEXT
            )
        """)
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS servicos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, descricao TEXT, preco_base REAL)")
        
        # Tabela de Reservas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                numero_registo TEXT UNIQUE,
                cliente TEXT, 
                evento TEXT, 
                pacote TEXT, 
                descricao_pacote TEXT, 
                data TEXT, 
                valor_total REAL, 
                responsavel TEXT,
                num_convidados INTEGER
            )
        """)
        
        # Tabela Financeira
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS financeiro (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                reserva_id INTEGER,
                tipo TEXT, 
                descricao TEXT, 
                valor REAL, 
                data TEXT,
                FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()
        
        # Garantir a existência do Administrador Padrão
        self.cursor.execute("SELECT * FROM utilizadores WHERE username = 'admin'")
        if not self.cursor.fetchone():
            pwd_hash = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute("INSERT INTO utilizadores (username, password, cargo) VALUES (?, ?, ?)", ("admin", pwd_hash, "Administrador"))
            self.conn.commit()

        # === TABELAS DO MODULO DE PATRIMONIO ===
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patrimonio_categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                descricao TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patrimonio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                descricao TEXT,
                categoria_id INTEGER,
                quantidade_total INTEGER DEFAULT 1,
                quantidade_disponivel INTEGER DEFAULT 1,
                quantidade_alugada INTEGER DEFAULT 0,
                quantidade_manutencao INTEGER DEFAULT 0,
                estado_fisico TEXT DEFAULT 'NOVO',
                situacao_operacional TEXT DEFAULT 'DISPONIVEL',
                valor_aquisicao REAL DEFAULT 0,
                data_aquisicao TEXT,
                localizacao TEXT,
                observacoes TEXT,
                ativo INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (categoria_id) REFERENCES patrimonio_categorias(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patrimonio_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patrimonio_id INTEGER NOT NULL,
                operacao TEXT NOT NULL,
                estado_anterior TEXT,
                estado_novo TEXT,
                situacao_anterior TEXT,
                situacao_nova TEXT,
                quantidade_anterior INTEGER,
                quantidade_nova INTEGER,
                descricao TEXT,
                responsavel TEXT,
                data_operacao TEXT,
                FOREIGN KEY (patrimonio_id) REFERENCES patrimonio(id) ON DELETE CASCADE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS aluguer_patrimonio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_aluguer TEXT UNIQUE NOT NULL,
                cliente TEXT NOT NULL,
                data_aluguer TEXT NOT NULL,
                data_inicio TEXT,
                data_devolucao_prevista TEXT,
                data_devolucao_efetiva TEXT,
                estado TEXT DEFAULT 'RESERVADO',
                valor_total REAL DEFAULT 0,
                valor_pago REAL DEFAULT 0,
                valor_pendente REAL DEFAULT 0,
                observacoes TEXT,
                responsavel TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS aluguer_patrimonio_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluguer_id INTEGER NOT NULL,
                patrimonio_id INTEGER NOT NULL,
                quantidade INTEGER DEFAULT 1,
                valor_unitario REAL DEFAULT 0,
                valor_total REAL DEFAULT 0,
                estado_saida TEXT DEFAULT 'BOM',
                quantidade_devolvida INTEGER DEFAULT 0,
                estado_devolucao TEXT,
                observacoes TEXT,
                FOREIGN KEY (aluguer_id) REFERENCES aluguer_patrimonio(id) ON DELETE CASCADE,
                FOREIGN KEY (patrimonio_id) REFERENCES patrimonio(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS aluguer_patrimonio_pagamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluguer_id INTEGER NOT NULL,
                valor REAL NOT NULL,
                data_pagamento TEXT,
                forma_pagamento TEXT,
                descricao TEXT,
                responsavel TEXT,
                created_at TEXT,
                FOREIGN KEY (aluguer_id) REFERENCES aluguer_patrimonio(id) ON DELETE CASCADE
            )
        """)

        # Inserir categorias padrao
        categorias_padrao = [
            ("Mesas", "Mesas para eventos"),
            ("Cadeiras", "Cadeiras para eventos"),
            ("Som", "Equipamentos de som"),
            ("Iluminacao", "Equipamentos de iluminacao"),
            ("Decoracao", "Materiais de decoracao"),
            ("Equipamentos", "Equipamentos diversos"),
            ("Estruturas", "Tendas, toldos e estruturas"),
            ("Utensilios", "Utensilios e acessorios"),
            ("Outros", "Outros patrimonios")
        ]
        for nome, desc in categorias_padrao:
            self.cursor.execute("INSERT OR IGNORE INTO patrimonio_categorias (nome, descricao) VALUES (?, ?)", (nome, desc))
        self.conn.commit()

    def ecran_login(self):
        """Interface gráfica do ecrã de Autenticação com design refinado"""
        self.limpar_ecran()
        self.utilizador_atual = None
        self.cargo_atual = None
        
        frame_login = tk.Frame(self.root, bg=self.COR_CARD, bd=1, relief="flat")
        frame_login.place(relx=0.5, rely=0.5, anchor="center", width=440, height=540)
        
        # Logo na tela de login
        if self.logo_img_login:
            lbl_logo = tk.Label(frame_login, image=self.logo_img_login, bg=self.COR_CARD)
            lbl_logo.pack(pady=(15, 5))
        
        tk.Label(frame_login, text="PAIXAO E FILHOS", font=("Helvetica", 22, "bold"), fg=self.COR_ROSA_VIVO, bg=self.COR_CARD).pack(pady=(5, 5))
        tk.Label(frame_login, text="Salao de Festas & Eventos", font=("Helvetica", 11, "italic"), fg=self.COR_TEXTO, bg=self.COR_CARD).pack(pady=0)
        
        tk.Label(frame_login, text="Utilizador:", font=("Helvetica", 11, "bold"), fg=self.COR_TEXTO, bg=self.COR_CARD).pack(anchor="w", padx=45, pady=(30, 5))
        self.ent_user = tk.Entry(frame_login, font=("Helvetica", 12), bg=self.COR_BG, fg="#FFFFFF", insertbackground="white", bd=0)
        self.ent_user.pack(fill="x", padx=45, ipady=8)
        
        tk.Label(frame_login, text="Palavra-passe:", font=("Helvetica", 11, "bold"), fg=self.COR_TEXTO, bg=self.COR_CARD).pack(anchor="w", padx=45, pady=(15, 5))
        self.ent_pass = tk.Entry(frame_login, font=("Helvetica", 12), show="*", bg=self.COR_BG, fg="#FFFFFF", insertbackground="white", bd=0)
        self.ent_pass.pack(fill="x", padx=45, ipady=8)
        
        frame_btn_entrar = tk.Frame(frame_login, bg=self.COR_MAGENTA, cursor="hand2")
        frame_btn_entrar.pack(fill="x", padx=45, pady=40, ipady=10)
        lbl_btn_entrar = tk.Label(frame_btn_entrar, text="ENTRAR NO SISTEMA",
                                  font=("Helvetica", 11, "bold"), fg="#FFFFFF",
                                  bg=self.COR_MAGENTA, anchor="center")
        lbl_btn_entrar.pack(fill="both", expand=True)

        def _entrar_hover_in(e):
            frame_btn_entrar.configure(bg="#C2185B")
            lbl_btn_entrar.configure(bg="#C2185B")
        def _entrar_hover_out(e):
            frame_btn_entrar.configure(bg=self.COR_MAGENTA)
            lbl_btn_entrar.configure(bg=self.COR_MAGENTA)

        for w in [frame_btn_entrar, lbl_btn_entrar]:
            w.bind("<Enter>", _entrar_hover_in)
            w.bind("<Leave>", _entrar_hover_out)
            w.bind("<Button-1>", lambda e: self.processar_login())

    def processar_login(self):
        """Verifica as credenciais inseridas e armazena o cargo correspondente"""
        user = self.ent_user.get()
        pwd = self.ent_pass.get()
        pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
        
        self.cursor.execute("SELECT id, cargo FROM utilizadores WHERE username = ? AND password = ?", (user, pwd_hash))
        resultado = self.cursor.fetchone()
        
        if resultado:
            self.utilizador_atual = user
            self.utilizador_atual_id = resultado[0]
            self.cargo_atual = resultado[1]
            self.construir_dashboard_principal()
        else:
            messagebox.showerror("Erro de Acesso", "Utilizador ou Palavra-passe incorretos!")

    def construir_dashboard_principal(self):
        """Monta o ambiente com menu lateral adaptável ao cargo logado"""
        self.limpar_ecran()
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=self.COR_CARD, fieldbackground=self.COR_CARD, foreground=self.COR_TEXTO, rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background=self.COR_MUTED, foreground="#FFFFFF", font=("Helvetica", 10, "bold"), borderwidth=0)
        style.map("Treeview", background=[('selected', self.COR_MAGENTA)])

        sidebar = tk.Frame(self.root, bg=self.COR_CARD, width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        if self.logo_img:
            lbl_logo = tk.Label(sidebar, image=self.logo_img, bg=self.COR_CARD)
            lbl_logo.pack(pady=(20, 0), anchor="center")
        
        tk.Label(sidebar, text="Paixão e Filhos", font=("Helvetica", 16, "bold"), fg=self.COR_ROSA_VIVO, bg=self.COR_CARD).pack(pady=(5, 5))
        tk.Label(sidebar, text=f"Sessão: {self.cargo_atual}", font=("Helvetica", 9, "italic"), fg=self.COR_TEXTO, bg=self.COR_CARD).pack(pady=(0, 20))
        
        menu_items = []
        
        if self.cargo_atual == "Gerente":
            menu_items.append(("Reservas & Festas", self.mostrar_aba_reservas))
        else:
            if self.cargo_atual == "Administrador":
                menu_items.append(("Resumo Financeiro", self.mostrar_aba_resumo))
                menu_items.append(("Registar Utilizadores", self.mostrar_aba_utilizadores))
                
            menu_items.append(("Servicos & Pacotes", self.mostrar_aba_servicos))
            menu_items.append(("Reservas & Festas", self.mostrar_aba_reservas))
            menu_items.append(("Patrimonio", self.mostrar_aba_patrimonio))
            menu_items.append(("Aluguer Patrimonio", self.mostrar_aba_aluguer_patrimonio))
            menu_items.append(("Dashboard Patrimonio", self.mostrar_aba_dashboard_patrimonio))
            
            if self.cargo_atual in ["Administrador", "Secretaria"]:
                menu_items.append(("Fluxo de Caixa", self.mostrar_aba_financeiro))
                
        menu_items.append(("Terminar Sessao", self._confirmar_terminar_sessao))
        
        for text, cmd in menu_items:
            is_sair = "Terminar" in text
            bg_color = "#991B1B" if is_sair else self.COR_CARD
            fg_color = "#FFFFFF" if is_sair else self.COR_TEXTO
            hover_bg = "#B91C1C" if is_sair else "#3D2E36"

            frame_item = tk.Frame(sidebar, bg=bg_color, cursor="hand2")
            frame_item.pack(fill="x", ipady=12, pady=1)
            frame_item.pack_propagate(False)
            frame_item.configure(height=44)

            lbl = tk.Label(frame_item, text=f"   {text}", font=("Helvetica", 11),
                           fg=fg_color, bg=bg_color, anchor="w", padx=10)
            lbl.pack(fill="both", expand=True)

            def _on_enter(e, f=frame_item, l=lbl, bg=hover_bg):
                f.configure(bg=bg)
                l.configure(bg=bg)

            def _on_leave(e, f=frame_item, l=lbl, bg=bg_color):
                f.configure(bg=bg)
                l.configure(bg=bg)

            def _on_click(e, c=cmd):
                c()

            for widget in [frame_item, lbl]:
                widget.bind("<Enter>", _on_enter)
                widget.bind("<Leave>", _on_leave)
                widget.bind("<Button-1>", _on_click)

        self.conteudo = tk.Frame(self.root, bg=self.COR_BG)
        self.conteudo.pack(side="right", fill="both", expand=True, padx=25, pady=25)

        if self.cargo_atual == "Gerente":
            self.mostrar_aba_reservas()
        elif self.cargo_atual == "Administrador":
            self.mostrar_aba_resumo()
        else:
            self.mostrar_aba_reservas()

    def limpar_ecran(self):
        """Remove todos os componentes da janela principal (usado na troca de ecrãs)"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def limpar_conteudo(self):
        """Limpa apenas a area de conteudo central para carregar uma nova aba"""
        for widget in self.conteudo.winfo_children():
            widget.destroy()

    def _confirmar_terminar_sessao(self):
        """Mostra dialog de confirmacao antes de terminar a sessao"""
        if messagebox.askyesno("Terminar Sessao", "Tem certeza que deseja terminar a sessao?"):
            self.ecran_login()

    def _carregar_logo(self):
        """Carrega a imagem da logo do ficheiro logo.png e cria versoes redimensionadas"""
        self.logo_img = None
        self.logo_img_login = None
        try:
            img_original = tk.PhotoImage(file=resource_path("logo.png"))
            w, h = img_original.width(), img_original.height()

            # Versao para sidebar (largura max 150px)
            max_sidebar = 150
            if w > max_sidebar:
                escala = w // max_sidebar
                if escala < 1:
                    escala = 1
                self.logo_img = img_original.subsample(escala, escala)
            else:
                self.logo_img = img_original

            # Versao para login (largura max 110px)
            max_login = 110
            if w > max_login:
                escala = w // max_login
                if escala < 1:
                    escala = 1
                self.logo_img_login = img_original.subsample(escala, escala)
            else:
                self.logo_img_login = img_original
        except Exception:
            self.logo_img = None
            self.logo_img_login = None

    # =====================================================================
    # CALENDAR DATE PICKER
    # =====================================================================
    def _criar_calendario(self, parent, entry_widget):
        """Cria um widget de calendario para selecionar data"""
        janela = tk.Toplevel(parent)
        janela.title("Selecionar Data")
        janela.geometry("300x320")
        janela.configure(bg=self.COR_BG)
        janela.transient(parent)
        janela.grab_set()

        data_atual = datetime.now()
        mes_atual = [data_atual.month, data_atual.year]

        frame_cal = tk.Frame(janela, bg=self.COR_BG)
        frame_cal.pack(fill="both", expand=True, padx=10, pady=10)

        # Navegacao
        frame_nav = tk.Frame(frame_cal, bg=self.COR_BG)
        frame_nav.pack(fill="x", pady=(0, 5))

        meses_pt = ["", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        lbl_mes = tk.Label(frame_nav, text="", font=("Helvetica", 11, "bold"), fg="#FFFFFF", bg=self.COR_BG)
        lbl_mes.pack(side="left", expand=True)

        def _mes_anterior():
            mes_atual[0] -= 1
            if mes_atual[0] < 1:
                mes_atual[0] = 12
                mes_atual[1] -= 1
            _atualizar_calendario()

        def _mes_proximo():
            mes_atual[0] += 1
            if mes_atual[0] > 12:
                mes_atual[0] = 1
                mes_atual[1] += 1
            _atualizar_calendario()

        btn_prev = tk.Label(frame_nav, text=" < ", font=("Helvetica", 12, "bold"), fg="#FFFFFF", bg=self.COR_MAGENTA, cursor="hand2")
        btn_prev.pack(side="left")
        btn_prev.bind("<Button-1>", lambda e: _mes_anterior())

        btn_next = tk.Label(frame_nav, text=" > ", font=("Helvetica", 12, "bold"), fg="#FFFFFF", bg=self.COR_MAGENTA, cursor="hand2")
        btn_next.pack(side="right")
        btn_next.bind("<Button-1>", lambda e: _mes_proximo())

        # Dias da semana
        frame_dias = tk.Frame(frame_cal, bg=self.COR_BG)
        frame_dias.pack(fill="x")
        for dia in ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]:
            tk.Label(frame_dias, text=dia, font=("Helvetica", 8, "bold"), fg=self.COR_ROSA_VIVO, bg=self.COR_BG, width=4).pack(side="left")

        frame_grid = tk.Frame(frame_cal, bg=self.COR_BG)
        frame_grid.pack(fill="both", expand=True)

        def _atualizar_calendario():
            for w in frame_grid.winfo_children():
                w.destroy()
            lbl_mes.config(text=f"{meses_pt[mes_atual[0]]} {mes_atual[1]}")

            import calendar
            cal = calendar.monthcalendar(mes_atual[1], mes_atual[0])
            for semana in cal:
                frame_semana = tk.Frame(frame_grid, bg=self.COR_BG)
                frame_semana.pack(fill="x")
                for dia in semana:
                    if dia == 0:
                        tk.Label(frame_semana, text="", width=4, bg=self.COR_BG).pack(side="left")
                    else:
                        lbl_dia = tk.Label(frame_semana, text=str(dia), font=("Helvetica", 9),
                                          fg="#FFFFFF", bg=self.COR_CARD, width=4, cursor="hand2")
                        lbl_dia.pack(side="left", padx=1, pady=1)

                        def _selecionar_dia(d=dia):
                            data_str = f"{d:02d}/{mes_atual[0]:02d}/{mes_atual[1]}"
                            entry_widget.delete(0, "end")
                            entry_widget.insert(0, data_str)
                            janela.destroy()

                        lbl_dia.bind("<Button-1>", lambda e, d=dia: _selecionar_dia(d))
                        lbl_dia.bind("<Enter>", lambda e, l=lbl_dia: l.configure(bg=self.COR_MAGENTA))
                        lbl_dia.bind("<Leave>", lambda e, l=lbl_dia: l.configure(bg=self.COR_CARD))

        _atualizar_calendario()

    def _criar_botao(self, pai, texto, comando, bg="#DB2777", fg="#FFFFFF",
                     hover_bg=None, font_size=10, anchor="w", padx=10, fill="x",
                     ipady=6, pady=1, side=None, **pack_kw):
        """Cria um botao usando Label (compativel com macOS) com efeito hover"""
        if hover_bg is None:
            hover_bg = bg

        frame_btn = tk.Frame(pai, bg=bg, cursor="hand2")
        lbl = tk.Label(frame_btn, text=texto, font=("Helvetica", font_size, "bold"),
                       fg=fg, bg=bg, anchor=anchor, padx=padx)
        lbl.pack(fill="both", expand=True)

        def _enter(e):
            frame_btn.configure(bg=hover_bg)
            lbl.configure(bg=hover_bg)
        def _leave(e):
            frame_btn.configure(bg=bg)
            lbl.configure(bg=bg)
        def _click(e):
            comando()

        for w in [frame_btn, lbl]:
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)
            w.bind("<Button-1>", _click)

        if side:
            frame_btn.pack(side=side, ipady=ipady, pady=pady, **pack_kw)
        else:
            frame_btn.pack(fill=fill, ipady=ipady, pady=pady, **pack_kw)

        return frame_btn

    # =====================================================================
    # ABA 1: DASHBOARD GERAL & RESUMO FINANCEIRO (APENAS ADMIN)
    # =====================================================================
    def carregar_dados_dashboard(self, ano=None, mes=None):
        """Busca dados do SQLite filtrados por ano/mes e retorna dict com todos os KPIs"""
        dados = {}

        filtro_reservas = ""
        filtro_financeiro = ""
        params_reservas = []
        params_financeiro = []
        if ano and mes and mes != "Todos":
            filtro_reservas = "WHERE data_criacao LIKE ?"
            params_reservas = [f"%/{mes.zfill(2)}/{ano}"]
            filtro_financeiro = "WHERE data_criacao LIKE ?"
            params_financeiro = [f"%/{mes.zfill(2)}/{ano}"]
        elif ano:
            filtro_reservas = "WHERE data_criacao LIKE ?"
            params_reservas = [f"%/{ano}"]
            filtro_financeiro = "WHERE data_criacao LIKE ?"
            params_financeiro = [f"%/{ano}"]

        # Receita total (entradas)
        self.cursor.execute(f"SELECT SUM(valor) FROM financeiro WHERE tipo = 'ENTRADA' {filtro_financeiro.replace('WHERE', 'AND') if filtro_financeiro else ''}", params_financeiro)
        r = self.cursor.fetchone()
        dados["receita_total"] = r[0] if r and r[0] else 0.0

        # Despesas totais (saidas)
        self.cursor.execute(f"SELECT SUM(valor) FROM financeiro WHERE tipo = 'SAIDA' {filtro_financeiro.replace('WHERE', 'AND') if filtro_financeiro else ''}", params_financeiro)
        r = self.cursor.fetchone()
        dados["despesas_totais"] = r[0] if r and r[0] else 0.0

        # Total de reservas
        self.cursor.execute(f"SELECT COUNT(*) FROM reservas {filtro_reservas}", params_reservas)
        r = self.cursor.fetchone()
        dados["total_reservas"] = r[0] if r else 0

        # Ticket medio
        dados["ticket_medio"] = dados["receita_total"] / dados["total_reservas"] if dados["total_reservas"] > 0 else 0.0

        # Total de convidados
        self.cursor.execute(f"SELECT SUM(num_convidados) FROM reservas {filtro_reservas}", params_reservas)
        r = self.cursor.fetchone()
        dados["total_convidados"] = r[0] if r and r[0] else 0

        # Lucro liquido
        dados["lucro_liquido"] = dados["receita_total"] - dados["despesas_totais"]

        # Dados para grafico de linha: receita mensal do ano selecionado
        ano_ref = ano if ano else str(datetime.now().year)
        self.cursor.execute("SELECT data, tipo, valor FROM financeiro WHERE data LIKE ?", [f"%/{ano_ref}"])
        transacoes = self.cursor.fetchall()
        meses_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        receita_mensal = [0.0] * 12
        despesa_mensal = [0.0] * 12
        for data_str, tipo, valor in transacoes:
            try:
                partes = data_str.split("/")
                mes_idx = int(partes[1]) - 1
                if 0 <= mes_idx < 12:
                    if tipo == "ENTRADA":
                        receita_mensal[mes_idx] += valor
                    else:
                        despesa_mensal[mes_idx] += valor
            except (ValueError, IndexError):
                continue
        dados["meses_labels"] = meses_pt
        dados["receita_mensal"] = receita_mensal
        dados["despesa_mensal"] = despesa_mensal

        # Dados para grafico de torta: distribuicao por tipo de evento
        self.cursor.execute(f"SELECT evento, COUNT(*) as qtd FROM reservas {filtro_reservas} GROUP BY evento ORDER BY qtd DESC", params_reservas)
        dados["eventos_distribuicao"] = self.cursor.fetchall()

        # Dados para grafico de barras: pacotes mais reservados
        self.cursor.execute(f"SELECT pacote, COUNT(*) as qtd FROM reservas {filtro_reservas} GROUP BY pacote ORDER BY qtd DESC", params_reservas)
        dados["pacotes_popularidade"] = self.cursor.fetchall()

        return dados

    def mostrar_aba_resumo(self):
        """Dashboard profissional com KPIs, filtros e graficos"""
        self.limpar_conteudo()

        # Titulo da aba
        tk.Label(self.conteudo, text="Dashboard Geral - Paixao e Filhos",
                 font=("Helvetica", 20, "bold"), fg="#FFFFFF", bg=self.COR_BG).pack(anchor="w", pady=(0, 10))

        # --- BARRA DE FILTROS ---
        frame_filtros = tk.Frame(self.conteudo, bg=self.COR_CARD, padx=15, pady=10)
        frame_filtros.pack(fill="x", pady=(0, 10))

        tk.Label(frame_filtros, text="Ano:", font=("Helvetica", 11, "bold"),
                 fg=self.COR_TEXTO, bg=self.COR_CARD).pack(side="left", padx=(0, 5))

        anos_disponiveis = self._buscar_anos_disponiveis()
        self.cb_filtro_ano = ttk.Combobox(frame_filtros, values=anos_disponiveis,
                                          state="readonly", font=("Helvetica", 11), width=8)
        self.cb_filtro_ano.set(str(datetime.now().year))
        self.cb_filtro_ano.pack(side="left", padx=(0, 15))

        tk.Label(frame_filtros, text="Mes:", font=("Helvetica", 11, "bold"),
                 fg=self.COR_TEXTO, bg=self.COR_CARD).pack(side="left", padx=(0, 5))

        meses_filtro = ["Todos", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.cb_filtro_mes = ttk.Combobox(frame_filtros, values=meses_filtro,
                                          state="readonly", font=("Helvetica", 11), width=12)
        self.cb_filtro_mes.set("Todos")
        self.cb_filtro_mes.pack(side="left", padx=(0, 15))

        self._criar_botao(frame_filtros, "Atualizar", self._atualizar_dashboard,
                          bg=self.COR_MAGENTA, hover_bg="#C2185B", font_size=10,
                          side="left", padx=5, ipady=4)

        self._criar_botao(frame_filtros, "Exportar PDF", self._exportar_relatorio_filtrado,
                          bg="#64748B", hover_bg="#94A3B8", font_size=10,
                          side="left", padx=5, ipady=4)

        # Frame scrollavel para o conteudo
        self.frame_dashboard_scroll = tk.Frame(self.conteudo, bg=self.COR_BG)
        self.frame_dashboard_scroll.pack(fill="both", expand=True)

        # Carrega e renderiza
        self._renderizar_dashboard()

    def _buscar_anos_disponiveis(self):
        """Retorna lista de anos que existem na base de dados"""
        self.cursor.execute("SELECT DISTINCT substr(data, -4) as ano FROM reservas ORDER BY ano DESC")
        anos = [row[0] for row in self.cursor.fetchall() if row[0]]
        if not anos:
            anos = [str(datetime.now().year)]
        return anos

    def _obter_mes_numero(self, nome_mes):
        """Converte nome do mes para numero"""
        mapa = {"Todos": None, "Janeiro": "01", "Fevereiro": "02", "Marco": "03",
                "Abril": "04", "Maio": "05", "Junho": "06", "Julho": "07",
                "Agosto": "08", "Setembro": "09", "Outubro": "10",
                "Novembro": "11", "Dezembro": "12"}
        return mapa.get(nome_mes, None)

    def _atualizar_dashboard(self):
        """Callback do botao Atualizar - recarrega graficos com filtros"""
        for widget in self.frame_dashboard_scroll.winfo_children():
            widget.destroy()
        self._renderizar_dashboard()

    def _renderizar_dashboard(self):
        """Renderiza KPIs e graficos no frame scrollavel"""
        ano = self.cb_filtro_ano.get()
        mes_nome = self.cb_filtro_mes.get()
        mes_num = self._obter_mes_numero(mes_nome)

        dados = self.carregar_dados_dashboard(ano, mes_num)

        # --- KPI CARDS ---
        frame_kpis = tk.Frame(self.frame_dashboard_scroll, bg=self.COR_BG)
        frame_kpis.pack(fill="x", pady=(0, 10))

        kpis = [
            ("Receita Total", f"{dados['receita_total']:.0f} KZ", self.COR_ROSA_VIVO),
            ("Total Reservas", f"{dados['total_reservas']}", "#A855F7"),
            ("Ticket Medio", f"{dados['ticket_medio']:.0f} KZ", "#3B82F6"),
            ("Total Convidados", f"{dados['total_convidados']}", "#F59E0B"),
            ("Despesas Totais", f"{dados['despesas_totais']:.0f} KZ", "#EF4444"),
            ("Lucro Liquido", f"{dados['lucro_liquido']:.0f} KZ", "#10B981"),
        ]

        for i, (titulo, valor, cor) in enumerate(kpis):
            card = tk.Frame(frame_kpis, bg=self.COR_CARD, highlightbackground=cor,
                            highlightthickness=2, padx=15, pady=12)
            card.grid(row=0, column=i, sticky="nsew", padx=5, ipady=5)
            frame_kpis.grid_columnconfigure(i, weight=1)

            tk.Label(card, text=titulo, font=("Helvetica", 9), fg=self.COR_TEXTO,
                     bg=self.COR_CARD).pack(anchor="w")
            tk.Label(card, text=valor, font=("Helvetica", 15, "bold"), fg=cor,
                     bg=self.COR_CARD).pack(anchor="w", pady=(5, 0))

        # --- GRAFICOS ---
        if MATPLOTLIB_DISPONIVEL:
            frame_graficos = tk.Frame(self.frame_dashboard_scroll, bg=self.COR_BG)
            frame_graficos.pack(fill="both", expand=True, pady=(5, 0))
            frame_graficos.grid_columnconfigure(0, weight=1)
            frame_graficos.grid_columnconfigure(1, weight=1)
            frame_graficos.grid_rowconfigure(0, weight=1)
            frame_graficos.grid_rowconfigure(1, weight=1)

            self._criar_grafico_receita_mensal(frame_graficos, dados)
            self._criar_grafico_eventos(frame_graficos, dados)
            self._criar_grafico_pacotes(frame_graficos, dados)
            self._criar_grafico_fluxo_caixa(frame_graficos, dados)
        else:
            frame_msg = tk.Frame(self.frame_dashboard_scroll, bg=self.COR_CARD, padx=20, pady=20)
            frame_msg.pack(fill="x", pady=20)
            tk.Label(frame_msg, text="Graficos indisponiveis. Instale o matplotlib:",
                     font=("Helvetica", 12, "bold"), fg="#F59E0B", bg=self.COR_CARD).pack()
            tk.Label(frame_msg, text="pip3 install matplotlib",
                     font=("Courier", 11), fg=self.COR_TEXTO, bg=self.COR_CARD).pack(pady=(5, 0))

    def _criar_grafico_receita_mensal(self, parent, dados):
        """Grafico de linha: receita vs despesa mensal"""
        fig = Figure(figsize=(5.5, 3.2), dpi=100, facecolor=self.COR_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.COR_CARD)

        meses = dados["meses_labels"]
        x = range(len(meses))

        ax.plot(x, dados["receita_mensal"], color=self.COR_ROSA_VIVO, linewidth=2.5,
                marker='o', markersize=5, label='Receita', zorder=3)
        ax.fill_between(x, dados["receita_mensal"], alpha=0.15, color=self.COR_ROSA_VIVO)
        ax.plot(x, dados["despesa_mensal"], color="#EF4444", linewidth=2,
                marker='s', markersize=4, label='Despesa', linestyle='--', zorder=3)

        ax.set_xticks(list(x))
        ax.set_xticklabels(meses, fontsize=7, color=self.COR_TEXTO)
        ax.tick_params(axis='y', colors=self.COR_TEXTO, labelsize=7)
        ax.set_title("Receita vs Despesa Mensal", fontsize=11, color="#FFFFFF", fontweight='bold', pad=10)
        ax.legend(fontsize=8, facecolor=self.COR_CARD, edgecolor='#444', labelcolor=self.COR_TEXTO)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1000:.0f}K' if v >= 1000 else f'{v:.0f}'))
        for spine in ax.spines.values():
            spine.set_color('#444')
        ax.grid(axis='y', alpha=0.2, color='#666')

        fig.tight_layout(pad=1.5)
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        canvas.get_tk_widget().configure(bg=self.COR_CARD)

    def _criar_grafico_eventos(self, parent, dados):
        """Grafico de torta: distribuicao por tipo de evento"""
        fig = Figure(figsize=(5.5, 3.2), dpi=100, facecolor=self.COR_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.COR_CARD)

        eventos = dados["eventos_distribuicao"]
        if eventos:
            labels = [e[0] for e in eventos]
            sizes = [e[1] for e in eventos]
            cores = ['#F472B6', '#DB2777', '#A855F7', '#3B82F6', '#F59E0B', '#10B981', '#EF4444', '#64748B']
            explode = [0.03] * len(labels)

            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.0f%%',
                                               colors=cores[:len(labels)], explode=explode,
                                               textprops={'fontsize': 7, 'color': self.COR_TEXTO},
                                               pctdistance=0.75, startangle=90)
            for at in autotexts:
                at.set_fontsize(6)
                at.set_color('#FFFFFF')
        else:
            ax.text(0.5, 0.5, 'Sem dados', ha='center', va='center',
                    fontsize=12, color=self.COR_TEXTO, transform=ax.transAxes)

        ax.set_title("Distribuicao por Tipo de Evento", fontsize=11, color="#FFFFFF", fontweight='bold', pad=10)
        fig.tight_layout(pad=1.5)
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        canvas.get_tk_widget().configure(bg=self.COR_CARD)

    def _criar_grafico_pacotes(self, parent, dados):
        """Grafico de barras: pacotes mais reservados"""
        fig = Figure(figsize=(5.5, 3.2), dpi=100, facecolor=self.COR_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.COR_CARD)

        pacotes = dados["pacotes_popularidade"]
        if pacotes:
            labels = [p[0][:12] for p in pacotes[:8]]
            valores = [p[1] for p in pacotes[:8]]
            cores = ['#DB2777', '#A855F7', '#3B82F6', '#F472B6', '#F59E0B', '#10B981', '#EF4444', '#64748B']

            barras = ax.barh(labels, valores, color=cores[:len(labels)], height=0.6, edgecolor='none')
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels, fontsize=8, color=self.COR_TEXTO)
            ax.tick_params(axis='x', colors=self.COR_TEXTO, labelsize=7)
            ax.invert_yaxis()

            for barra, val in zip(barras, valores):
                ax.text(barra.get_width() + 0.1, barra.get_y() + barra.get_height()/2,
                        str(val), va='center', fontsize=8, color=self.COR_TEXTO, fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'Sem dados', ha='center', va='center',
                    fontsize=12, color=self.COR_TEXTO, transform=ax.transAxes)

        ax.set_title("Pacotes Mais Reservados", fontsize=11, color="#FFFFFF", fontweight='bold', pad=10)
        for spine in ax.spines.values():
            spine.set_color('#444')
        ax.grid(axis='x', alpha=0.2, color='#666')
        fig.tight_layout(pad=1.5)
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        canvas.get_tk_widget().configure(bg=self.COR_CARD)

    def _criar_grafico_fluxo_caixa(self, parent, dados):
        """Grafico de barras empilhado: receita vs despesa por mes"""
        fig = Figure(figsize=(5.5, 3.2), dpi=100, facecolor=self.COR_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.COR_CARD)

        meses = dados["meses_labels"]
        x = range(len(meses))
        largura = 0.35

        ax.bar([i - largura/2 for i in x], dados["receita_mensal"], largura,
               label='Receita', color=self.COR_ROSA_VIVO, edgecolor='none')
        ax.bar([i + largura/2 for i in x], dados["despesa_mensal"], largura,
               label='Despesa', color='#EF4444', edgecolor='none')

        ax.set_xticks(list(x))
        ax.set_xticklabels(meses, fontsize=7, color=self.COR_TEXTO)
        ax.tick_params(axis='y', colors=self.COR_TEXTO, labelsize=7)
        ax.set_title("Fluxo de Caixa Mensal", fontsize=11, color="#FFFFFF", fontweight='bold', pad=10)
        ax.legend(fontsize=8, facecolor=self.COR_CARD, edgecolor='#444', labelcolor=self.COR_TEXTO)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1000:.0f}K' if v >= 1000 else f'{v:.0f}'))
        for spine in ax.spines.values():
            spine.set_color('#444')
        ax.grid(axis='y', alpha=0.2, color='#666')

        fig.tight_layout(pad=1.5)
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        canvas.get_tk_widget().configure(bg=self.COR_CARD)

    def _exportar_relatorio_filtrado(self):
        """Exporta relatorio PDF com os dados filtrados"""
        from fpdf import FPDF

        ano = self.cb_filtro_ano.get()
        mes_nome = self.cb_filtro_mes.get()
        mes_num = self._obter_mes_numero(mes_nome)
        dados = self.carregar_dados_dashboard(ano, mes_num)
        filtro_label = f"{mes_nome}/{ano}" if mes_num else f"Ano {ano}"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_ficheiro = f"Relatorio_Dashboard_{ano}_{mes_num or 'total'}_{timestamp}.pdf"
        pasta = self._obter_pasta_downloads()
        caminho_completo = os.path.join(pasta, nome_ficheiro)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Cabecalho
        pdf.set_fill_color(219, 39, 119)
        pdf.rect(10, 10, 190, 30, "F")
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=12, y=12, w=12, h=12)
            txt_x = 28
            txt_w = 172
        else:
            txt_x = 10
            txt_w = 190
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_xy(txt_x, 12)
        pdf.cell(txt_w, 8, "DASHBOARD - PAIXAO E FILHOS", align="C")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_xy(txt_x, 22)
        pdf.cell(txt_w, 6, f"Periodo: {filtro_label}", align="C")

        # Titulo
        y = 46
        pdf.set_xy(10, y)
        pdf.set_text_color(51, 51, 51)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(190, 10, "Resumo Financeiro", ln=True)
        y += 14

        # KPI Cards
        kpis = [
            ("Receita Total", f"{dados['receita_total']:,.0f} KZ"),
            ("Despesas Totais", f"{dados['despesas_totais']:,.0f} KZ"),
            ("Lucro Liquido", f"{dados['lucro_liquido']:,.0f} KZ"),
            ("Total Reservas", f"{dados['total_reservas']}"),
            ("Ticket Medio", f"{dados['ticket_medio']:,.0f} KZ"),
            ("Total Convidados", f"{dados['total_convidados']}"),
        ]

        pdf.set_font("Helvetica", "", 10)
        for i, (titulo, valor) in enumerate(kpis):
            col = i % 3
            x = 10 + col * 65
            if col == 0 and i > 0:
                y += 16
            pdf.set_xy(x, y)
            pdf.set_fill_color(245, 245, 245)
            pdf.cell(60, 14, "", border=1, fill=True)
            pdf.set_xy(x + 3, y + 2)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(54, 5, titulo)
            pdf.set_xy(x + 3, y + 7)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(51, 51, 51)
            pdf.cell(54, 5, valor)

        y += 22

        # Distribuicao por Evento
        if dados["eventos_distribuicao"]:
            pdf.set_xy(10, y)
            pdf.set_text_color(157, 23, 77)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(190, 8, "Distribuicao por Tipo de Evento", ln=True)
            y += 10
            pdf.set_fill_color(157, 23, 77)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_xy(10, y)
            pdf.cell(100, 7, "  Evento", border=1, fill=True)
            pdf.cell(40, 7, "Reservas", border=1, align="C", fill=True)
            y += 7
            pdf.set_text_color(51, 51, 51)
            pdf.set_font("Helvetica", "", 9)
            for evento, qtd in dados["eventos_distribuicao"]:
                pdf.set_xy(10, y)
                pdf.cell(100, 7, f"  {evento}", border=1)
                pdf.cell(40, 7, str(qtd), border=1, align="C")
                y += 7
            y += 5

        # Pacotes mais reservados
        if dados["pacotes_popularidade"]:
            pdf.set_xy(10, y)
            pdf.set_text_color(157, 23, 77)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(190, 8, "Pacotes Mais Reservados", ln=True)
            y += 10
            pdf.set_fill_color(157, 23, 77)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_xy(10, y)
            pdf.cell(100, 7, "  Pacote", border=1, fill=True)
            pdf.cell(40, 7, "Reservas", border=1, align="C", fill=True)
            y += 7
            pdf.set_text_color(51, 51, 51)
            pdf.set_font("Helvetica", "", 9)
            for pacote, qtd in dados["pacotes_popularidade"]:
                pdf.set_xy(10, y)
                pdf.cell(100, 7, f"  {pacote}", border=1)
                pdf.cell(40, 7, str(qtd), border=1, align="C")
                y += 7
            y += 5

        # Rodape
        y += 5
        pdf.set_xy(10, y)
        pdf.set_draw_color(157, 23, 77)
        pdf.line(10, y, 200, y)
        y += 3
        pdf.set_xy(10, y)
        pdf.set_text_color(102, 102, 102)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(190, 5, f"Relatorio gerado em {datetime.now().strftime('%d/%m/%Y as %H:%M')}", align="C")

        pdf.output(caminho_completo)

        # Perguntar se quer imprimir
        if messagebox.askyesno("PDF Exportado", f"Relatorio guardado em:\n{caminho_completo}\n\nDeseja imprimir?"):
            self._enviar_para_impressora(caminho_completo)
    # =====================================================================
    # ABA 2: CADASTRAMENTO E GESTAO DE UTILIZADORES (APENAS ADMIN)
    # =====================================================================
    def mostrar_aba_utilizadores(self):
        """Interface gráfica para cadastramento e listagem de colaboradores internos"""
        self.limpar_conteudo()
        self._user_editando_id = None
        
        # Título da Aba
        tk.Label(self.conteudo, text="Registo de Utilizadores & Cargos", 
                 font=("Helvetica", 18, "bold"), fg="#FFFFFF", bg=self.COR_BG).pack(anchor="w", pady=(0,15))
        
        # Formulário de Cadastro
        form = tk.Frame(self.conteudo, bg=self.COR_CARD, padx=15, pady=15)
        form.pack(fill="x", pady=10)
        
        # Campo: Nome de Utilizador
        tk.Label(form, text="Nome de Utilizador:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.ent_novo_user = tk.Entry(form, font=("Helvetica", 11), bg=self.COR_BG, fg="white", bd=0, width=18)
        self.ent_novo_user.grid(row=0, column=1, padx=10, ipady=4)
        
        # Campo: Palavra-passe
        tk.Label(form, text="Palavra-passe:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=5, sticky="w")
        self.ent_nova_pass = tk.Entry(form, font=("Helvetica", 11), show="*", bg=self.COR_BG, fg="white", bd=0, width=18)
        self.ent_nova_pass.grid(row=0, column=3, padx=10, ipady=4)
        
        # Campo: Cargo (Dropdown)
        tk.Label(form, text="Cargo Atribuído:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=0, column=4, padx=5, sticky="w")
        self.cb_novo_cargo = ttk.Combobox(form, values=["Administrador", "Gerente", "Secretária", "Funcionário"], state="readonly", font=("Helvetica", 11), width=15)
        self.cb_novo_cargo.grid(row=0, column=5, padx=10, ipady=2)
        
        # Botoes de Acao - segunda linha
        frame_botoes = tk.Frame(form, bg=self.COR_CARD)
        frame_botoes.grid(row=1, column=0, columnspan=7, pady=(10, 0), sticky="w")
        
        # Botao Registar / Guardar
        self.frame_registar = tk.Frame(frame_botoes, bg=self.COR_MAGENTA, cursor="hand2")
        self.frame_registar.pack(side="left", padx=5)
        self.lbl_registar = tk.Label(self.frame_registar, text="Registar", font=("Helvetica", 10, "bold"),
                                fg="white", bg=self.COR_MAGENTA, padx=15)
        self.lbl_registar.pack()
        for w in [self.frame_registar, self.lbl_registar]:
            w.bind("<Enter>", lambda e: (self.frame_registar.configure(bg="#C2185B"), self.lbl_registar.configure(bg="#C2185B")))
            w.bind("<Leave>", lambda e: (self.frame_registar.configure(bg=self.COR_MAGENTA), self.lbl_registar.configure(bg=self.COR_MAGENTA)))
            w.bind("<Button-1>", lambda e: self.guardar_utilizador())
        
        # Botao Editar
        frame_editar = tk.Frame(frame_botoes, bg="#F59E0B", cursor="hand2")
        frame_editar.pack(side="left", padx=5)
        lbl_editar = tk.Label(frame_editar, text="Editar", font=("Helvetica", 10, "bold"),
                              fg="white", bg="#F59E0B", padx=15)
        lbl_editar.pack()
        for w in [frame_editar, lbl_editar]:
            w.bind("<Enter>", lambda e: (frame_editar.configure(bg="#D97706"), lbl_editar.configure(bg="#D97706")))
            w.bind("<Leave>", lambda e: (frame_editar.configure(bg="#F59E0B"), lbl_editar.configure(bg="#F59E0B")))
            w.bind("<Button-1>", lambda e: self._editar_utilizador_selecionado())
        
        # Botao Eliminar
        frame_eliminar = tk.Frame(frame_botoes, bg="#EF4444", cursor="hand2")
        frame_eliminar.pack(side="left", padx=5)
        lbl_eliminar = tk.Label(frame_eliminar, text="Eliminar", font=("Helvetica", 10, "bold"),
                                fg="white", bg="#EF4444", padx=15)
        lbl_eliminar.pack()
        for w in [frame_eliminar, lbl_eliminar]:
            w.bind("<Enter>", lambda e: (frame_eliminar.configure(bg="#DC2626"), lbl_eliminar.configure(bg="#DC2626")))
            w.bind("<Leave>", lambda e: (frame_eliminar.configure(bg="#EF4444"), lbl_eliminar.configure(bg="#EF4444")))
            w.bind("<Button-1>", lambda e: self._eliminar_utilizador_selecionado())
        
        # Tabela Visual de Utilizadores Cadastrados
        self.tv_users = ttk.Treeview(self.conteudo, columns=("ID", "Nome de Utilizador", "Cargo"), show="headings")
        for col in self.tv_users["columns"]:
            self.tv_users.heading(col, text=col)
            self.tv_users.column(col, anchor="center")
        self.tv_users.pack(fill="both", expand=True, pady=15)
        self.tv_users.bind("<<TreeviewSelect>>", lambda e: self._selecionar_utilizador())
        
        self.atualizar_tabela_utilizadores()

    def guardar_utilizador(self):
        """Valida e grava o novo utilizador ou atualiza existente"""
        u = self.ent_novo_user.get()
        p = self.ent_nova_pass.get()
        c = self.cb_novo_cargo.get()
        
        if not u or not c:
            messagebox.showwarning("Aviso", "Preencha todos os campos obrigatorios.")
            return
        
        if self._user_editando_id:
            # Modo edicao
            if p:
                pwd_hash = hashlib.sha256(p.encode()).hexdigest()
                self.cursor.execute("UPDATE utilizadores SET username=?, password=?, cargo=? WHERE id=?",
                                    (u, pwd_hash, c, self._user_editando_id))
            else:
                self.cursor.execute("UPDATE utilizadores SET username=?, cargo=? WHERE id=?",
                                    (u, c, self._user_editando_id))
            self.conn.commit()
            messagebox.showinfo("Sucesso", f"Utilizador '{u}' atualizado com sucesso!")
            self.mostrar_aba_utilizadores()
        else:
            # Modo insercao
            if not p:
                messagebox.showwarning("Aviso", "Indique a palavra-passe para novo utilizador.")
                return
            try:
                pwd_hash = hashlib.sha256(p.encode()).hexdigest()
                self.cursor.execute("INSERT INTO utilizadores (username, password, cargo) VALUES (?, ?, ?)", (u, pwd_hash, c))
                self.conn.commit()
                messagebox.showinfo("Sucesso", f"Utilizador '{u}' cadastrado com sucesso como {c}!")
                self.mostrar_aba_utilizadores()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Esse nome de utilizador ja se encontra registado!")

    def _selecionar_utilizador(self):
        """Carrega dados do utilizador selecionado nos campos do formulario"""
        sel = self.tv_users.selection()
        if not sel:
            return
        valores = self.tv_users.item(sel[0], "values")
        user_id, username, cargo = valores
        self._user_editando_id = int(user_id)
        self.ent_novo_user.delete(0, "end")
        self.ent_novo_user.insert(0, username)
        self.ent_nova_pass.delete(0, "end")
        self.cb_novo_cargo.set(cargo)
        self.lbl_registar.config(text="Guardar")

    def _editar_utilizador_selecionado(self):
        """Edita o utilizador selecionado na tabela"""
        sel = self.tv_users.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um utilizador na tabela para editar.")
            return
        valores = self.tv_users.item(sel[0], "values")
        user_id = int(valores[0])
        # Nao permitir editar a si proprio (admin logado)
        if user_id == self.utilizador_atual_id:
            messagebox.showwarning("Aviso", "Nao pode editar o proprio utilizador logged in.")
            return
        self._user_editando_id = user_id
        self.ent_novo_user.delete(0, "end")
        self.ent_novo_user.insert(0, valores[1])
        self.ent_nova_pass.delete(0, "end")
        self.cb_novo_cargo.set(valores[2])
        self.lbl_registar.config(text="Guardar")
        self.ent_novo_user.focus_set()

    def _eliminar_utilizador_selecionado(self):
        """Elimina o utilizador selecionado na tabela"""
        sel = self.tv_users.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um utilizador na tabela para eliminar.")
            return
        valores = self.tv_users.item(sel[0], "values")
        user_id = int(valores[0])
        username = valores[1]
        # Nao permitir eliminar a si proprio
        if user_id == self.utilizador_atual_id:
            messagebox.showwarning("Aviso", "Nao pode eliminar o proprio utilizador logged in.")
            return
        if not messagebox.askyesno("Confirmar", f"Deseja eliminar o utilizador '{username}'?"):
            return
        self.cursor.execute("DELETE FROM utilizadores WHERE id=?", (user_id,))
        self.conn.commit()
        messagebox.showinfo("Sucesso", f"Utilizador '{username}' eliminado com sucesso!")
        self.mostrar_aba_utilizadores()

    def atualizar_tabela_utilizadores(self):
        """Atualiza a Treeview de utilizadores buscando dados do SQLite"""
        self.tv_users.delete(*self.tv_users.get_children())
        for row in self.cursor.execute("SELECT id, username, cargo FROM utilizadores"):
            self.tv_users.insert("", "end", values=row)

    # =====================================================================
    # ABA 3: CONFIGURACAO DE SERVICOS & PACOTES
    # =====================================================================
    def mostrar_aba_servicos(self):
        """Interface gráfica para a Configuração de Serviços & Pacotes do Salão"""
        self.limpar_conteudo()
        tk.Label(self.conteudo, text="Configuração de Serviços & Pacotes", font=("Helvetica", 18, "bold"), fg="#FFFFFF", bg=self.COR_BG).pack(anchor="w", pady=(0,15))
        
        form = tk.Frame(self.conteudo, bg=self.COR_CARD, padx=15, pady=15)
        form.pack(fill="x", pady=10)
        
        fields = [("Nome do Pacote:", "nome"), ("Descrição Curta:", "desc"), ("Preço Base (KZ):", "preco")]
        self.inputs_servico = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form, text=label, fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=0, column=i*2, padx=5, sticky="w")
            ent = tk.Entry(form, font=("Helvetica", 11), bg=self.COR_BG, fg="white", bd=0, width=18)
            ent.grid(row=0, column=i*2+1, padx=10, ipady=4)
            self.inputs_servico[key] = ent
            
        frame_adicionar = tk.Frame(form, bg=self.COR_MAGENTA, cursor="hand2")
        frame_adicionar.grid(row=0, column=6, padx=15, ipady=4)
        lbl_adicionar = tk.Label(frame_adicionar, text="Adicionar", font=("Helvetica", 10, "bold"),
                                 fg="white", bg=self.COR_MAGENTA, padx=15)
        lbl_adicionar.pack()
        for w in [frame_adicionar, lbl_adicionar]:
            w.bind("<Enter>", lambda e: (frame_adicionar.configure(bg="#C2185B"), lbl_adicionar.configure(bg="#C2185B")))
            w.bind("<Leave>", lambda e: (frame_adicionar.configure(bg=self.COR_MAGENTA), lbl_adicionar.configure(bg=self.COR_MAGENTA)))
            w.bind("<Button-1>", lambda e: self.guardar_servico())
        
        self.tv_ser = ttk.Treeview(self.conteudo, columns=("ID", "Nome do Pacote", "Descrição", "Preço Base"), show="headings")
        for col in self.tv_ser["columns"]:
            self.tv_ser.heading(col, text=col)
            self.tv_ser.column(col, anchor="center")
        self.tv_ser.pack(fill="both", expand=True, pady=15)
        
        self.atualizar_tabela_servicos()

    def guardar_servico(self):
        """Valida e grava o novo pacote de serviço na base de dados SQLite"""
        n = self.inputs_servico["nome"].get()
        d = self.inputs_servico["desc"].get()
        p = self.inputs_servico["preco"].get()
        if n and d and p:
            try:
                self.cursor.execute("INSERT INTO servicos (nome, descricao, preco_base) VALUES (?, ?, ?)", (n, d, float(p)))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Pacote/Serviço adicionado com sucesso!")
                self.mostrar_aba_servicos()
            except ValueError:
                messagebox.showerror("Erro", "O preço deve ser um valor numérico.")
        else:
            messagebox.showwarning("Aviso", "Preencha todos os campos antes de guardar.")

    def atualizar_tabela_servicos(self):
        """Limpa a tabela visual e recarrega os registos a partir da BD"""
        self.tv_ser.delete(*self.tv_ser.get_children())
        for row in self.cursor.execute("SELECT * FROM servicos"):
            self.tv_ser.insert("", "end", values=row)

    def puxar_lista_pacotes(self):
        """Busca na base de dados apenas os nomes dos pacotes para preencher a Combobox das reservas"""
        self.cursor.execute("SELECT nome FROM servicos")
        return [row[0] for row in self.cursor.fetchall()]

    def preencher_dados_do_pacote(self, event):
        """Preenche automaticamente os campos de Descrição e Preço do formulário ao selecionar um pacote"""
        pacote_selecionado = self.inputs_reserva["pacote"].get()
        if pacote_selecionado:
            self.cursor.execute("SELECT descricao, preco_base FROM servicos WHERE nome = ?", (pacote_selecionado,))
            resultado = self.cursor.fetchone()
            if resultado:
                descricao, preco = resultado
                
                self.inputs_reserva["desc_pacote"].config(state="normal")
                self.inputs_reserva["desc_pacote"].delete(0, tk.END)
                self.inputs_reserva["desc_pacote"].insert(0, str(descricao))
                self.inputs_reserva["desc_pacote"].config(state="readonly")
                
                self.inputs_reserva["valor"].delete(0, tk.END)
                self.inputs_reserva["valor"].insert(0, str(preco))
    # =====================================================================
    # ABA 4: AGENDAMENTO, MARCACAO E CONTROLO DE FESTAS
    # =====================================================================
    def mostrar_aba_reservas(self):
        """Interface gráfica para marcação de festas com suporte a Número de Registo Único e Convidados"""
        self.limpar_conteudo()
        self.reserva_id_selecionado = None
        
        tk.Label(self.conteudo, text="Agendamento & Marcação de Festas", font=("Helvetica", 18, "bold"), fg="#FFFFFF", bg=self.COR_BG).pack(anchor="w", pady=(0,15))
        form = tk.Frame(self.conteudo, bg=self.COR_CARD, padx=15, pady=15)
        form.pack(fill="x", pady=10)
        
        self.inputs_reserva = {}
        
        # Linha 1: Registo, Cliente, Tipo Festa
        tk.Label(form, text="Nº Registo:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ent_registo = tk.Entry(form, font=("Helvetica", 11, "bold"), bg=self.COR_CARD, fg=self.COR_ROSA_VIVO, bd=1, width=20, state="readonly")
        ent_registo.grid(row=0, column=1, padx=10, pady=5, ipady=4)
        self.inputs_reserva["numero_registo"] = ent_registo

        tk.Label(form, text="Nome do Cliente:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ent_cliente = tk.Entry(form, font=("Helvetica", 11), bg=self.COR_BG, fg="white", bd=0, width=20)
        ent_cliente.grid(row=0, column=3, padx=10, pady=5, ipady=4)
        self.inputs_reserva["cliente"] = ent_cliente

        tk.Label(form, text="Tipo de Festa:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        cb_evento = ttk.Combobox(form, values=["Casamento", "Baptismo", "Aniversário", "Pedido", "Apresentação"], state="readonly", font=("Helvetica", 11), width=18)
        cb_evento.grid(row=0, column=5, padx=10, pady=5, ipady=2)
        self.inputs_reserva["evento"] = cb_evento

        # Linha 2: Pacote, Descrição, Data
        tk.Label(form, text="Escolha o Pacote:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        cb_pacote = ttk.Combobox(form, values=self.puxar_lista_pacotes(), state="readonly", font=("Helvetica", 11), width=18)
        cb_pacote.grid(row=1, column=1, padx=10, pady=5, ipady=2)
        cb_pacote.bind("<<ComboboxSelected>>", self.preencher_dados_do_pacote)
        self.inputs_reserva["pacote"] = cb_pacote

        tk.Label(form, text="Descrição/Pacote:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ent_desc = tk.Entry(form, font=("Helvetica", 11), bg=self.COR_CARD, fg=self.COR_ROSA_VIVO, bd=1, width=20, state="readonly")
        ent_desc.grid(row=1, column=3, padx=10, pady=5, ipady=4)
        self.inputs_reserva["desc_pacote"] = ent_desc

        tk.Label(form, text="Data (DD/MM/AAAA):", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=1, column=4, padx=5, pady=5, sticky="w")
        ent_data = tk.Entry(form, font=("Helvetica", 11), bg=self.COR_BG, fg="white", bd=0, width=18)
        ent_data.grid(row=1, column=5, padx=10, pady=5, ipady=4)
        self.inputs_reserva["data"] = ent_data

        # Linha 3: Valor, Responsável, Nº Convidados
        tk.Label(form, text="Valor Acordado (KZ):", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ent_valor = tk.Entry(form, font=("Helvetica", 11), bg=self.COR_BG, fg="white", bd=0, width=20)
        ent_valor.grid(row=2, column=1, padx=10, pady=5, ipady=4)
        self.inputs_reserva["valor"] = ent_valor

        tk.Label(form, text="Funcionário Resp.:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=2, column=2, padx=5, pady=5, sticky="w")
        ent_resp = tk.Entry(form, font=("Helvetica", 11), bg=self.COR_BG, fg="white", bd=0, width=20)
        ent_resp.grid(row=2, column=3, padx=10, pady=5, ipady=4)
        self.inputs_reserva["resp"] = ent_resp

        tk.Label(form, text="Nº Convidados:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).grid(row=2, column=4, padx=5, pady=5, sticky="w")
        ent_convidados = tk.Entry(form, font=("Helvetica", 11), bg=self.COR_BG, fg="white", bd=0, width=18)
        ent_convidados.grid(row=2, column=5, padx=10, pady=5, ipady=4)
        self.inputs_reserva["num_convidados"] = ent_convidados
            
        # Linha de Botões Operacionais
        frame_botoes = tk.Frame(form, bg=self.COR_CARD)
        frame_botoes.grid(row=3, column=0, columnspan=6, pady=15, sticky="ew")
        
        self._criar_botao(frame_botoes, "Registar Reserva", self.guardar_reserva,
                          bg="#10B981", hover_bg="#34D399", font_size=10,
                          side="left", padx=3, ipady=6, fill=None)
        self._criar_botao(frame_botoes, "Gravar Alteracoes", self.editar_reserva_confirmar,
                          bg="#F59E0B", hover_bg="#FBBF24", font_size=10,
                          side="left", padx=3, ipady=6, fill=None)
        self._criar_botao(frame_botoes, "Eliminar Registo", self.eliminar_reserva,
                          bg="#EF4444", hover_bg="#F87171", font_size=10,
                          side="left", padx=3, ipady=6, fill=None)
        self._criar_botao(frame_botoes, "Visualizar Recibo", self.visualizar_recibo_a5,
                          bg=self.COR_MAGENTA, hover_bg="#C2185B", font_size=10,
                          side="left", padx=3, ipady=6, fill=None)
        self._criar_botao(frame_botoes, "Imprimir Recibo", self.imprimir_recibo_selecionado,
                          bg="#0EA5E9", hover_bg="#38BDF8", font_size=10,
                          side="left", padx=3, ipady=6, fill=None)
        self._criar_botao(frame_botoes, "Limpar Campos", self.limpar_campos_reserva,
                          bg="#64748B", hover_bg="#94A3B8", font_size=10,
                          side="left", padx=3, ipady=6, fill=None)
        
        # Tabela Grid de Visualização das Reservas
        self.tv_res = ttk.Treeview(self.conteudo, columns=("ID", "Nº Registo", "Cliente", "Festa", "Pacote", "Descrição", "Data", "Valor (KZ)", "Responsável", "Convidados"), show="headings")
        for col in self.tv_res["columns"]:
            self.tv_res.heading(col, text=col)
            self.tv_res.column(col, anchor="center", width=110)
        self.tv_res.pack(fill="both", expand=True, pady=15)
        
        self.tv_res.bind("<<TreeviewSelect>>", self.carregar_reserva_selecionada)
        self.atualizar_tabela_reservas()

    def carregar_reserva_selecionada(self, event):
        """Preenche o formulário ao clicar numa linha da tabela de reservas com índices de tuplos corrigidos"""
        selecao = self.tv_res.selection()
        if not selecao:
            return
        valores = self.tv_res.item(selecao)["values"]
        
        # Correção Crítica: extrai apenas o ID inteiro para evitar falhas em cascata no SQLite
        self.reserva_id_selecionado = valores[0]
        
        self.inputs_reserva["numero_registo"].config(state="normal")
        self.inputs_reserva["numero_registo"].delete(0, tk.END)
        self.inputs_reserva["numero_registo"].insert(0, valores[1])
        self.inputs_reserva["numero_registo"].config(state="readonly")
        
        self.inputs_reserva["cliente"].delete(0, tk.END)
        self.inputs_reserva["cliente"].insert(0, valores[2])
        self.inputs_reserva["evento"].set(valores[3])
        self.inputs_reserva["pacote"].set(valores[4])
        
        self.inputs_reserva["desc_pacote"].config(state="normal")
        self.inputs_reserva["desc_pacote"].delete(0, tk.END)
        self.inputs_reserva["desc_pacote"].insert(0, valores[5])
        self.inputs_reserva["desc_pacote"].config(state="readonly")
        
        self.inputs_reserva["data"].delete(0, tk.END)
        self.inputs_reserva["data"].insert(0, valores[6])
        self.inputs_reserva["valor"].delete(0, tk.END)
        self.inputs_reserva["valor"].insert(0, str(valores[7]).replace(",", ""))
        self.inputs_reserva["resp"].delete(0, tk.END)
        self.inputs_reserva["resp"].insert(0, valores[8])
        self.inputs_reserva["num_convidados"].delete(0, tk.END)
        self.inputs_reserva["num_convidados"].insert(0, valores[9])

    def limpar_campos_reserva(self):
        """Limpa e redefine as Comboboxes e as caixas de texto"""
        self.reserva_id_selecionado = None
        for key in self.inputs_reserva:
            if isinstance(self.inputs_reserva[key], ttk.Combobox):
                self.inputs_reserva[key].set("")
            else:
                self.inputs_reserva[key].config(state="normal")
                self.inputs_reserva[key].delete(0, tk.END)
                if key in ["desc_pacote", "numero_registo"]:
                    self.inputs_reserva[key].config(state="readonly")
    def guardar_reserva(self):
        """Grava o agendamento com validação estrita de choque de datas e faturamento automático"""
        c = self.inputs_reserva["cliente"].get()
        e = self.inputs_reserva["evento"].get()
        pac = self.inputs_reserva["pacote"].get()
        desc = self.inputs_reserva["desc_pacote"].get()
        d = self.inputs_reserva["data"].get()
        v_str = self.inputs_reserva["valor"].get()
        r = self.inputs_reserva["resp"].get()
        nc_str = self.inputs_reserva["num_convidados"].get()
        
        if c and e and pac and d and v_str and r and nc_str:
            self.cursor.execute("SELECT cliente, evento FROM reservas WHERE data = ?", (d,))
            conflito = self.cursor.fetchone()
            if conflito:
                messagebox.showerror(
                    "Conflito de Agenda", 
                    f"[SMS ALERTA]: Já tem um evento marcado nesta data!\n\nCliente: {conflito[0]}\nFesta: {conflito[1]}\n\nPor favor, escolha outro dia."
                )
                return
                
            try:
                datetime.strptime(d, "%d/%m/%Y")
                v = float(v_str)
                nc = int(nc_str)
                
                num_registo = f"REG-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                data_criacao = datetime.now().strftime("%d/%m/%Y")
                
                self.cursor.execute(
                    "INSERT INTO reservas (numero_registo, cliente, evento, pacote, descricao_pacote, data, valor_total, responsavel, num_convidados, data_criacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (num_registo, c, e, pac, desc, d, v, r, nc, data_criacao)
                )
                reserva_id = self.cursor.lastrowid
                
                if v > 0:
                    self.cursor.execute(
                        "INSERT INTO financeiro (reserva_id, tipo, descricao, valor, data, data_criacao) VALUES (?, 'ENTRADA', ?, ?, ?, ?)",
                        (reserva_id, f"Faturamento Total - {c} ({e})", v, d, data_criacao)
                    )
                    
                self.conn.commit()
                
                if messagebox.askyesno("Sucesso", f"Agendamento concluido com sucesso!\nRegisto Gerado: {num_registo}\n\nDeseja emitir a fatura?"):
                    self.imprimir_factura(num_registo, c, e, pac, d, v, r, nc)
                else:
                    self.mostrar_aba_reservas()
            except ValueError:
                messagebox.showerror("Erro de Validação", "O Valor e Convidados devem ser numéricos. Formato da data: DD/MM/AAAA.")
        else:
            messagebox.showwarning("Aviso", "Preencha todos os campos do formulário para registar.")

    def editar_reserva_confirmar(self):
        """Regra de Segurança: Exige obrigatoriamente a senha de administrador (admin123) para alterar dados"""
        if not self.reserva_id_selecionado:
            messagebox.showwarning("Aviso", "Por favor, selecione primeiro uma reserva na tabela para editar.")
            return
        
        senha_admin = simpledialog.askstring("Autenticação Requerida", "Insira a senha do Administrador para autorizar alterações:", show="*")
        
        if senha_admin != "admin123":
            messagebox.showerror("Acesso Negado", "Palavra-passe do Administrador inválida! A gravação foi bloqueada.")
            return

        c = self.inputs_reserva["cliente"].get()
        e = self.inputs_reserva["evento"].get()
        pac = self.inputs_reserva["pacote"].get()
        desc = self.inputs_reserva["desc_pacote"].get()
        d = self.inputs_reserva["data"].get()
        v_str = self.inputs_reserva["valor"].get()
        r = self.inputs_reserva["resp"].get()
        nc_str = self.inputs_reserva["num_convidados"].get()
        
        if c and e and pac and d and v_str and r and nc_str:
            self.cursor.execute("SELECT cliente, evento FROM reservas WHERE data = ? AND id != ?", (d, self.reserva_id_selecionado))
            conflito = self.cursor.fetchone()
            if conflito:
                messagebox.showerror("Conflito de Agenda", f"Impossível alterar! A data escolhida já está reservada para o evento de {conflito[0]}.")
                return
                
            try:
                datetime.strptime(d, "%d/%m/%Y")
                v = float(v_str)
                nc = int(nc_str)
                
                self.cursor.execute(
                    "UPDATE reservas SET cliente=?, evento=?, pacote=?, descricao_pacote=?, data=?, valor_total=?, responsavel=?, num_convidados=? WHERE id=?",
                    (c, e, pac, desc, d, v, r, nc, self.reserva_id_selecionado)
                )
                self.cursor.execute(
                    "UPDATE financeiro SET valor=?, data=? WHERE reserva_id=? AND tipo='ENTRADA'",
                    (v, d, self.reserva_id_selecionado)
                )
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Registo alterado com sucesso mediante verificação de Administrador!")
                self.mostrar_aba_reservas()
            except ValueError:
                messagebox.showerror("Erro de Validação", "Verifique os campos numéricos e a data.")
        else:
            messagebox.showwarning("Aviso", "Preencha todos os campos para salvar.")

    def eliminar_reserva(self):
        """Elimina permanentemente a atividade e limpa em cascata os registos de fluxo de caixa"""
        if not self.reserva_id_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma reserva na tabela para poder eliminar.")
            return
        if messagebox.askyesno("Confirmar", "Tem a certeza que deseja eliminar permanentemente esta atividade e as suas faturas de gastos?"):
            self.cursor.execute("DELETE FROM reservas WHERE id=?", (self.reserva_id_selecionado,))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Agendamento e histórico financeiro removidos.")
            self.mostrar_aba_reservas()

    def atualizar_tabela_reservas(self):
        """Recarrega a tabela visual de agendamentos contendo todas as 10 colunas estruturadas"""
        self.tv_res.delete(*self.tv_res.get_children())
        for row in self.cursor.execute("SELECT id, numero_registo, cliente, evento, pacote, descricao_pacote, data, valor_total, responsavel, num_convidados FROM reservas"):
            self.tv_res.insert("", "end", values=row)

    def visualizar_recibo_a5(self):
        """Abre uma folha gráfica simulando perfeitamente as dimensões do formato profissional A5"""
        nr = self.inputs_reserva["numero_registo"].get()
        c = self.inputs_reserva["cliente"].get()
        e = self.inputs_reserva["evento"].get()
        pac = self.inputs_reserva["pacote"].get()
        d = self.inputs_reserva["data"].get()
        v_str = self.inputs_reserva["valor"].get()
        r = self.inputs_reserva["resp"].get()
        nc = self.inputs_reserva["num_convidados"].get()
        
        if not (c and e and d and v_str):
            messagebox.showwarning("Aviso", "Selecione ou preencha uma reserva válida para visualizar.")
            return
            
        janela_a5 = tk.Toplevel(self.root)
        janela_a5.title("Recibo A5 - Pré-visualização Profissional")
        janela_a5.geometry("520x720") 
        janela_a5.configure(bg="#FFFFFF")
        janela_a5.resizable(False, False)
        
        frame_header = tk.Frame(janela_a5, bg="#FFFFFF")
        frame_header.pack(fill="x", pady=(25, 5))
            
        tk.Label(frame_header, text="SALÃO DE FESTAS PAIXÃO E FILHOS", font=("Courier", 14, "bold"), fg="#000000", bg="#FFFFFF").pack(pady=6)
        tk.Label(frame_header, text="Zona de Eventos Premium, Luanda, Angola", font=("Courier", 10), fg="#333333", bg="#FFFFFF").pack()
        tk.Label(frame_header, text=f"Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}", font=("Courier", 10), fg="#333333", bg="#FFFFFF").pack()
        
        tk.Label(janela_a5, text="----------------------------------------------------------", font=("Courier", 11), bg="#FFFFFF", fg="#000000").pack()
        tk.Label(janela_a5, text="RECIBO COMPROVATIVO DE RESERVA (FORMATO A5)", font=("Courier", 11, "bold"), bg="#FFFFFF", fg="#000000").pack()
        tk.Label(janela_a5, text="----------------------------------------------------------", font=("Courier", 11), bg="#FFFFFF", fg="#000000").pack()
        
        frame_corpo = tk.Frame(janela_a5, bg="#FFFFFF")
        frame_corpo.pack(fill="both", expand=True, padx=40, pady=15)
        
        dados = [
            ("Nº Ficha Registo:", nr if nr else "Novo"),
            ("Cliente:", c),
            ("Tipo de Festa:", e),
            ("Pacote Escolhido:", pac),
            ("Data do Evento:", d),
            ("Nº Convidados:", nc),
            ("Operador Resp:", r)
        ]
        
        for label, val in dados:
            row = tk.Frame(frame_corpo, bg="#FFFFFF")
            row.pack(fill="x", pady=6)
            tk.Label(row, text=f"{label:<20}", font=("Courier", 11, "bold"), bg="#FFFFFF", fg="#000000", anchor="w").pack(side="left")
            tk.Label(row, text=str(val), font=("Courier", 11), bg="#FFFFFF", fg="#000000", anchor="w").pack(side="left")
            
        tk.Label(janela_a5, text="----------------------------------------------------------", font=("Courier", 11), bg="#FFFFFF", fg="#000000").pack()
        
        frame_total = tk.Frame(janela_a5, bg="#FFFFFF")
        frame_total.pack(fill="x", padx=40, pady=10)
        tk.Label(frame_total, text="VALOR TOTAL BRUTO:", font=("Courier", 12, "bold"), bg="#FFFFFF", fg="#000000", anchor="w").pack(side="left")
        tk.Label(frame_total, text=f"{float(v_str):,.2f} KZ", font=("Courier", 13, "bold"), bg="#FFFFFF", fg="#10B981", anchor="e").pack(side="right")
        
        tk.Label(janela_a5, text="==========================================================", font=("Courier", 11), bg="#FFFFFF", fg="#000000").pack()
        # Continuado de: tk.Label(janela_a5, text="----------------------------------------------------------", font=("Courier", 11), bg="#FFFFFF", fg="#000000").pack()
        
        frame_total = tk.Frame(janela_a5, bg="#FFFFFF")
        frame_total.pack(fill="x", padx=40, pady=10)
        tk.Label(frame_total, text="VALOR TOTAL BRUTO:", font=("Courier", 12, "bold"), bg="#FFFFFF", fg="#000000", anchor="w").pack(side="left")
        tk.Label(frame_total, text=f"{float(v_str):,.2f} KZ", font=("Courier", 13, "bold"), bg="#FFFFFF", fg="#10B981", anchor="e").pack(side="right")
        
        tk.Label(janela_a5, text="==========================================================", font=("Courier", 11), bg="#FFFFFF", fg="#000000").pack()
        tk.Label(janela_a5, text="Agradecemos a preferência!\nSalão Paixão e Filhos, celebrando consigo.", font=("Courier", 10, "italic"), bg="#FFFFFF", fg="#444444", justify="center").pack(pady=(10, 25))

    def imprimir_recibo_selecionado(self):
        """Abre dialog de impressao de fatura para a reserva selecionada"""
        nr = self.inputs_reserva["numero_registo"].get()
        c = self.inputs_reserva["cliente"].get()
        e = self.inputs_reserva["evento"].get()
        pac = self.inputs_reserva["pacote"].get()
        d = self.inputs_reserva["data"].get()
        v_str = self.inputs_reserva["valor"].get()
        r = self.inputs_reserva["resp"].get()
        nc = self.inputs_reserva["num_convidados"].get()
        if c and e and d and v_str and r:
            try:
                v = float(v_str)
                nc_int = int(nc) if nc else 0
                self.imprimir_factura(nr, c, e, pac, d, v, r, nc_int)
            except ValueError:
                messagebox.showerror("Erro", "O valor no formulario e invalido.")
        else:
            messagebox.showwarning("Aviso", "Selecione uma reserva valida na tabela.")

    def puxar_lista_reservas_combobox(self):
        """Busca todas as reservas ativas para abastecer a seleção do fluxo de caixa"""
        self.cursor.execute("SELECT id, numero_registo, cliente FROM reservas")
        return [f"{row[0]} | {row[1]} | {row[2]}" for row in self.cursor.fetchall()]

    # =====================================================================
    # ABA 5: FLUXO DE CAIXA, DESPESAS E CALCULO DE DIFERENCA REAL
    # =====================================================================
    def mostrar_aba_financeiro(self):
        """Interface de Fluxo de Caixa para registar saidas com painel de resultado diferencial"""
        self.limpar_conteudo()
        tk.Label(self.conteudo, text="Fluxo de Caixa & Registo de Despesas de Atividades", font=("Helvetica", 18, "bold"), fg="#FFFFFF", bg=self.COR_BG).pack(anchor="w", pady=(0,15))
        
        # CONSULTAS SQL PARA O BALANCO DE CAIXA EM TEMPO REAL
        self.cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'ENTRADA'")
        r_ent = self.cursor.fetchone()
        entradas = r_ent[0] if r_ent and r_ent[0] is not None else 0.0
        
        self.cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'SAIDA'")
        r_sai = self.cursor.fetchone()
        saidas = r_sai[0] if r_sai and r_sai[0] is not None else 0.0
        
        resultado_diferenca = entradas - saidas
        
        # Painel Informativo Superior
        frame_balanco_caixa = tk.Frame(self.conteudo, bg=self.COR_CARD, padx=15, pady=12, highlightbackground=self.COR_MUTED, highlightthickness=1)
        frame_balanco_caixa.pack(fill="x", pady=(0, 15))
        
        tk.Label(frame_balanco_caixa, text=f"Total de Entradas: {entradas:.2f} KZ", font=("Helvetica", 11, "bold"), fg="#10B981", bg=self.COR_CARD).pack(side="left", padx=15)
        tk.Label(frame_balanco_caixa, text=f"Despesas Totais: {saidas:.2f} KZ", font=("Helvetica", 11, "bold"), fg="#F43F5E", bg=self.COR_CARD).pack(side="left", padx=15)
        
        cor_resultado = "#10B981" if resultado_diferenca >= 0 else "#EF4444"
        tk.Label(frame_balanco_caixa, text=f"Lucro / Diferenca Real: {resultado_diferenca:.2f} KZ", font=("Helvetica", 12, "bold"), fg=cor_resultado, bg=self.COR_CARD).pack(side="right", padx=15)

        # Formulario de registo de despesas - Linha 1: campos
        form_fin = tk.Frame(self.conteudo, bg=self.COR_CARD, padx=15, pady=15)
        form_fin.pack(fill="x", pady=10)
        
        self.inputs_fin = {}
        
        # Linha 1: Vincular Atividade + Descricao + Valor
        linha1 = tk.Frame(form_fin, bg=self.COR_CARD)
        linha1.pack(fill="x", pady=(0, 10))
        
        tk.Label(linha1, text="Vincular Atividade:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).pack(side="left", padx=(0, 5))
        self.cb_vinculo = ttk.Combobox(linha1, values=self.puxar_lista_reservas_combobox(), state="readonly", font=("Helvetica", 11), width=28)
        self.cb_vinculo.pack(side="left", padx=(0, 15))
        
        tk.Label(linha1, text="Descricao Gasto:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).pack(side="left", padx=(0, 5))
        ent_fin_desc = tk.Entry(linha1, font=("Helvetica", 11), bg=self.COR_BG, fg="white", bd=0, width=22)
        ent_fin_desc.pack(side="left", padx=(0, 15))
        self.inputs_fin["desc"] = ent_fin_desc
        
        tk.Label(linha1, text="Valor Saida (KZ):", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 10, "bold")).pack(side="left", padx=(0, 5))
        ent_fin_val = tk.Entry(linha1, font=("Helvetica", 11), bg=self.COR_BG, fg="white", bd=0, width=15)
        ent_fin_val.pack(side="left", padx=(0, 15))
        self.inputs_fin["valor"] = ent_fin_val
        
        # Linha 2: Botao centralizado
        linha2 = tk.Frame(form_fin, bg=self.COR_CARD)
        linha2.pack(fill="x")
        
        frame_saida = tk.Frame(linha2, bg=self.COR_MAGENTA, cursor="hand2")
        frame_saida.pack(ipady=4, padx=10)
        lbl_saida = tk.Label(frame_saida, text="   Registar Saida   ", font=("Helvetica", 11, "bold"),
                             fg="white", bg=self.COR_MAGENTA, padx=20)
        lbl_saida.pack()
        for w in [frame_saida, lbl_saida]:
            w.bind("<Enter>", lambda e: (frame_saida.configure(bg="#C2185B"), lbl_saida.configure(bg="#C2185B")))
            w.bind("<Leave>", lambda e: (frame_saida.configure(bg=self.COR_MAGENTA), lbl_saida.configure(bg=self.COR_MAGENTA)))
            w.bind("<Button-1>", lambda e: self.guardar_despesa_financeira())
        
        # Tabela do extrato com scroll
        frame_tabela = tk.Frame(self.conteudo, bg=self.COR_BG)
        frame_tabela.pack(fill="both", expand=True, pady=(10, 0))
        
        self.tv_fin = ttk.Treeview(frame_tabela, columns=("ID", "ID Reserva", "Tipo", "Descricao", "Valor (KZ)", "Data"), show="headings", height=12)
        
        self.tv_fin.heading("ID", text="ID")
        self.tv_fin.heading("ID Reserva", text="ID Reserva")
        self.tv_fin.heading("Tipo", text="Tipo")
        self.tv_fin.heading("Descricao", text="Descricao")
        self.tv_fin.heading("Valor (KZ)", text="Valor (KZ)")
        self.tv_fin.heading("Data", text="Data")
        
        self.tv_fin.column("ID", width=50, minwidth=50, anchor="center")
        self.tv_fin.column("ID Reserva", width=80, minwidth=80, anchor="center")
        self.tv_fin.column("Tipo", width=80, minwidth=80, anchor="center")
        self.tv_fin.column("Descricao", width=280, minwidth=150, anchor="w")
        self.tv_fin.column("Valor (KZ)", width=120, minwidth=100, anchor="e")
        self.tv_fin.column("Data", width=100, minwidth=90, anchor="center")
        
        scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tv_fin.yview)
        self.tv_fin.configure(yscrollcommand=scroll_y.set)
        
        self.tv_fin.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        
        self.atualizar_tabela_financeiro()
    def guardar_despesa_financeira(self):
        """Vincula o gasto variável a uma atividade, grava no BD e emite a fatura física da despesa"""
        vinculo = self.cb_vinculo.get()
        desc = self.inputs_fin["desc"].get()
        val_str = self.inputs_fin["valor"].get()
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        if vinculo and desc and val_str:
            try:
                partes = vinculo.split(" | ")
                reserva_id = int(partes[0])
                num_registo_ref = partes[1]
                val = float(val_str)
                
                # Grava a saída na tabela financeira
                self.cursor.execute(
                    "INSERT INTO financeiro (reserva_id, tipo, descricao, valor, data, data_criacao) VALUES (?, 'SAIDA', ?, ?, ?, ?)",
                    (reserva_id, f"Gasto Variável ({num_registo_ref}) - {desc}", val, data_atual, data_atual)
                )
                self.conn.commit()
                
                # Emitir a Factura Física de Saída em ficheiro TXT individual
                nome_factura_despesa = f"factura_despesa_{reserva_id}_{random.randint(100,999)}.txt"
                with open(nome_factura_despesa, "w", encoding="utf-8") as f:
                    f.write("==================================================\n")
                    f.write("       FACTURA DE CUSTOS & DESPESAS OPERACIONAIS  \n")
                    f.write("          SALÃO DE FESTAS PAIXÃO E FILHOS         \n")
                    f.write("==================================================\n")
                    f.write(f"Data de Lançamento: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                    f.write(f"Atividade Ref:       {num_registo_ref}\n")
                    f.write("--------------------------------------------------\n")
                    f.write(f"Descrição Custo:     {desc}\n")
                    f.write(f"Valor Pago:          {val:,.2f} KZ\n")
                    f.write("==================================================\n")
                    f.write("Armazenada com sucesso no controlo interno.\n")
                
                messagebox.showinfo("Sucesso", f"Despesa variável vinculada e fatura '{nome_factura_despesa}' emitida!")
                self.mostrar_aba_financeiro()
            except ValueError:
                messagebox.showerror("Erro", "O valor do gasto deve ser estritamente numérico.")
        else:
            messagebox.showwarning("Aviso", "Selecione a atividade vinculada e preencha a descrição e o valor.")

    def atualizar_tabela_financeiro(self):
        """Carrega todo o extrato na tabela"""
        self.tv_fin.delete(*self.tv_fin.get_children())
        for row in self.cursor.execute("SELECT id, reserva_id, tipo, descricao, valor, data FROM financeiro"):
            self.tv_fin.insert("", "end", values=row)

    def imprimir_factura(self, nr, cliente, evento, pacote, data_evento, valor, responsavel, convidados):
        """Janela de pre-visualizacao da factura com opcao de salvar PDF ou imprimir"""
        data_emissao = datetime.now().strftime("%d/%m/%Y")
        hora_emissao = datetime.now().strftime("%H:%M")

        # Calcular IVA (14%)
        taxa_iva = 0.14
        valor_sem_iva = valor / (1 + taxa_iva)
        valor_iva = valor - valor_sem_iva

        # Janela principal
        janela = tk.Toplevel(self.root)
        janela.title(f"Pre-visualizacao - Factura {nr}")
        janela.geometry("600x780")
        janela.configure(bg="#FFFFFF")
        janela.resizable(True, True)
        janela.transient(self.root)
        janela.grab_set()

        # === BOTOES DE ACAO (pack PRIMEIRO com side=bottom para ficar sempre visivel) ===
        frame_acao = tk.Frame(janela, bg="#F3F4F6", padx=15, pady=8)
        frame_acao.pack(fill="x", side="bottom")

        def _salvar():
            caminho = self._gerar_factura_pdf(nr, cliente, evento, pacote, data_evento, valor, responsavel, convidados)
            if caminho:
                janela.destroy()
                messagebox.showinfo("PDF Guardado", f"Factura guardada em:\n{caminho}")

        def _imprimir():
            caminho = self._gerar_factura_pdf(nr, cliente, evento, pacote, data_evento, valor, responsavel, convidados)
            if caminho:
                janela.destroy()
                self._enviar_para_impressora(caminho)

        def _fechar():
            canvas.unbind_all("<MouseWheel>")
            janela.destroy()

        # Botoes
        f1 = tk.Frame(frame_acao, bg="#3B82F6", cursor="hand2")
        f1.pack(side="left", padx=5, ipady=6, ipadx=15)
        l1 = tk.Label(f1, text="  Salvar PDF  ", font=("Helvetica", 10, "bold"), fg="white", bg="#3B82F6")
        l1.pack()
        for w in [f1, l1]:
            w.bind("<Enter>", lambda e: (f1.configure(bg="#60A5FA"), l1.configure(bg="#60A5FA")))
            w.bind("<Leave>", lambda e: (f1.configure(bg="#3B82F6"), l1.configure(bg="#3B82F6")))
            w.bind("<Button-1>", lambda e: _salvar())

        f2 = tk.Frame(frame_acao, bg="#10B981", cursor="hand2")
        f2.pack(side="left", padx=5, ipady=6, ipadx=15)
        l2 = tk.Label(f2, text="  Imprimir  ", font=("Helvetica", 10, "bold"), fg="white", bg="#10B981")
        l2.pack()
        for w in [f2, l2]:
            w.bind("<Enter>", lambda e: (f2.configure(bg="#34D399"), l2.configure(bg="#34D399")))
            w.bind("<Leave>", lambda e: (f2.configure(bg="#10B981"), l2.configure(bg="#10B981")))
            w.bind("<Button-1>", lambda e: _imprimir())

        f3 = tk.Frame(frame_acao, bg="#64748B", cursor="hand2")
        f3.pack(side="right", padx=5, ipady=6, ipadx=15)
        l3 = tk.Label(f3, text="  Fechar  ", font=("Helvetica", 10, "bold"), fg="white", bg="#64748B")
        l3.pack()
        for w in [f3, l3]:
            w.bind("<Enter>", lambda e: (f3.configure(bg="#94A3B8"), l3.configure(bg="#94A3B8")))
            w.bind("<Leave>", lambda e: (f3.configure(bg="#64748B"), l3.configure(bg="#64748B")))
            w.bind("<Button-1>", lambda e: _fechar())

        # === CONTEUDO SCROLLAVEL (pack DEPOIS dos botoes) ===
        canvas = tk.Canvas(janela, bg="#FFFFFF", highlightthickness=0)
        scrollbar = ttk.Scrollbar(janela, orient="vertical", command=canvas.yview)
        frame_pdf = tk.Frame(canvas, bg="#FFFFFF", padx=25, pady=15)

        frame_pdf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_pdf, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # === CABECALHO EMPRESA COM LOGO ===
        header_frame = tk.Frame(frame_pdf, bg="#DB2777", padx=15, pady=12)
        header_frame.pack(fill="x", pady=(0, 10))

        # Linha com logo + texto
        header_top = tk.Frame(header_frame, bg="#DB2777")
        header_top.pack(fill="x")

        if self.logo_img_login:
            logo_preview = self.logo_img_login.subsample(2, 2) if self.logo_img_login.width() > 60 else self.logo_img_login
            lbl_logo = tk.Label(header_top, image=logo_preview, bg="#DB2777")
            lbl_logo.pack(side="left", padx=(0, 10))
            # Manter referencia
            janela._logo_ref = logo_preview

        header_texto = tk.Frame(header_top, bg="#DB2777")
        header_texto.pack(side="left", fill="x", expand=True)

        tk.Label(header_texto, text="PAIXAO E FILHOS", font=("Helvetica", 18, "bold"),
                 fg="#FFFFFF", bg="#DB2777").pack(anchor="w")
        tk.Label(header_texto, text="Salao de Festas & Eventos", font=("Helvetica", 9),
                 fg="#FCE7F3", bg="#DB2777").pack(anchor="w")
        tk.Label(header_texto, text="Luanda, Angola", font=("Helvetica", 8),
                 fg="#FCE7F3", bg="#DB2777").pack(anchor="w")
        tk.Label(header_texto, text="NIF: 5419573961 | Tel: +244 923 456 789", font=("Helvetica", 7),
                 fg="#FCE7F3", bg="#DB2777").pack(anchor="w")

        # === DADOS DOCUMENTO ===
        doc_frame = tk.Frame(frame_pdf, bg="#FFFFFF", padx=10, pady=8)
        doc_frame.pack(fill="x", pady=(0, 8))

        # Linha com Nr. Factura + DOCUMENTO VALIDO
        doc_row1 = tk.Frame(doc_frame, bg="#FFFFFF")
        doc_row1.pack(fill="x")
        tk.Label(doc_row1, text="Nr. Factura:", font=("Helvetica", 9, "bold"), fg="#555555",
                 bg="#FFFFFF", width=14, anchor="w").pack(side="left")
        tk.Label(doc_row1, text=nr, font=("Helvetica", 9), fg="#1A1519",
                 bg="#FFFFFF").pack(side="left")
        tk.Label(doc_row1, text="DOCUMENTO VALIDO PARA FINS FISCAIS", font=("Helvetica", 7, "bold"),
                 fg="#9D174D", bg="#FFFFFF").pack(side="right")

        # Linha com Data Emissao
        doc_row2 = tk.Frame(doc_frame, bg="#FFFFFF")
        doc_row2.pack(fill="x")
        tk.Label(doc_row2, text="Data Emissao:", font=("Helvetica", 9, "bold"), fg="#555555",
                 bg="#FFFFFF", width=14, anchor="w").pack(side="left")
        tk.Label(doc_row2, text=data_emissao, font=("Helvetica", 9), fg="#1A1519",
                 bg="#FFFFFF").pack(side="left")

        # Linha com Hora
        doc_row3 = tk.Frame(doc_frame, bg="#FFFFFF")
        doc_row3.pack(fill="x")
        tk.Label(doc_row3, text="Hora:", font=("Helvetica", 9, "bold"), fg="#555555",
                 bg="#FFFFFF", width=14, anchor="w").pack(side="left")
        tk.Label(doc_row3, text=hora_emissao, font=("Helvetica", 9), fg="#1A1519",
                 bg="#FFFFFF").pack(side="left")

        # === TIPO DOCUMENTO ===
        tipo_frame = tk.Frame(frame_pdf, bg="#9D174D", padx=10, pady=6)
        tipo_frame.pack(fill="x", pady=(0, 10))
        tk.Label(tipo_frame, text="FACTURA", font=("Helvetica", 14, "bold"),
                 fg="#FFFFFF", bg="#9D174D").pack()

        # Separador
        tk.Frame(frame_pdf, bg="#9D174D", height=2).pack(fill="x", pady=5)

        # === DADOS CLIENTE ===
        tk.Label(frame_pdf, text="  DADOS DO CLIENTE", font=("Helvetica", 10, "bold"),
                 fg="#FFFFFF", bg="#FCE7F3", anchor="w").pack(fill="x", pady=(8, 3))

        cliente_frame = tk.Frame(frame_pdf, bg="#FFFFFF", padx=10, pady=5)
        cliente_frame.pack(fill="x", pady=(0, 8))

        for lbl, val in [("Nome:", cliente), ("Evento:", evento), ("Pacote:", pacote),
                         ("Data do Evento:", data_evento), ("Nr. Convidados:", convidados),
                         ("Func. Responsavel:", responsavel)]:
            row = tk.Frame(cliente_frame, bg="#FFFFFF")
            row.pack(fill="x", pady=1)
            tk.Label(row, text=lbl, font=("Helvetica", 9, "bold"), fg="#555555",
                     bg="#FFFFFF", width=18, anchor="w").pack(side="left")
            tk.Label(row, text=str(val), font=("Helvetica", 9), fg="#1A1519",
                     bg="#FFFFFF").pack(side="left")

        # Separador
        tk.Frame(frame_pdf, bg="#9D174D", height=2).pack(fill="x", pady=5)

        # === TABELA SERVICOS ===
        tk.Label(frame_pdf, text="  DETALHES DO SERVICO", font=("Helvetica", 10, "bold"),
                 fg="#FFFFFF", bg="#FCE7F3", anchor="w").pack(fill="x", pady=(8, 3))

        tbl_header = tk.Frame(frame_pdf, bg="#9D174D")
        tbl_header.pack(fill="x")
        for txt, w in [("Descricao", 220), ("Qtd", 50), ("Preco Unit.", 100), ("Total", 100)]:
            tk.Label(tbl_header, text=txt, font=("Helvetica", 9, "bold"),
                     fg="#FFFFFF", bg="#9D174D", width=w // 8, anchor="center").pack(side="left", padx=1)

        tbl_row = tk.Frame(frame_pdf, bg="#FFFFFF", highlightbackground="#E5E7EB", highlightthickness=1)
        tbl_row.pack(fill="x")
        for txt, w, al in [("Pacote: " + pacote, 220, "w"), ("1", 50, "center"),
                           (f"{valor_sem_iva:,.0f}", 100, "center"), (f"{valor_sem_iva:,.0f}", 100, "center")]:
            tk.Label(tbl_row, text=txt, font=("Helvetica", 9), fg="#1A1519",
                     bg="#FFFFFF", width=w // 8, anchor=al, padx=3).pack(side="left", padx=1)

        tbl_empty = tk.Frame(frame_pdf, bg="#FFFFFF", highlightbackground="#E5E7EB", highlightthickness=1)
        tbl_empty.pack(fill="x")
        for w in [220, 50, 100, 100]:
            tk.Label(tbl_empty, text="", width=w // 8, bg="#FFFFFF").pack(side="left", padx=1)

        # Separador
        tk.Frame(frame_pdf, bg="#9D174D", height=1).pack(fill="x", pady=8)

        # === TOTAIS ===
        totais_frame = tk.Frame(frame_pdf, bg="#FFFFFF")
        totais_frame.pack(fill="x", padx=10)

        for lbl, val, is_total in [("Sub-Total:", f"{valor_sem_iva:,.0f} KZ", False),
                                    ("IVA (14%):", f"{valor_iva:,.0f} KZ", False),
                                    ("TOTAL:", f"{valor:,.0f} KZ", True)]:
            row = tk.Frame(totais_frame, bg="#FFFFFF")
            row.pack(fill="x", pady=1)
            tk.Label(row, text=lbl, font=("Helvetica", 10, "bold" if is_total else ""),
                     fg="#DB2777" if is_total else "#555555", bg="#FFFFFF",
                     anchor="e").pack(side="right", padx=(0, 10))
            if is_total:
                tk.Frame(row, bg="#DB2777", height=25, width=130).pack(side="right")
                tk.Label(row, text=val, font=("Helvetica", 12, "bold"),
                         fg="#FFFFFF", bg="#DB2777", width=15, anchor="center").pack(side="right")
            else:
                tk.Label(row, text=val, font=("Helvetica", 10), fg="#1A1519",
                         bg="#FFFFFF", anchor="e").pack(side="right")

        # Separador
        tk.Frame(frame_pdf, bg="#9D174D", height=1).pack(fill="x", pady=10)

        # === NOTAS LEGAIS ===
        notas_frame = tk.Frame(frame_pdf, bg="#FFFFFF", padx=10)
        notas_frame.pack(fill="x")
        tk.Label(notas_frame, text="Conforme a Lei Geral Tributaria de Angola e o Codigo do IVA,",
                 font=("Helvetica", 7, "italic"), fg="#888888", bg="#FFFFFF").pack(anchor="w")
        tk.Label(notas_frame, text="este documento serve como comprovativo de prestacao de servicos.",
                 font=("Helvetica", 7, "italic"), fg="#888888", bg="#FFFFFF").pack(anchor="w")
        tk.Label(notas_frame, text="O IVA e liquidado a taxa de 14% conforme legislacao vigente.",
                 font=("Helvetica", 7, "italic"), fg="#888888", bg="#FFFFFF").pack(anchor="w")

        # === RODAPE ===
        tk.Frame(frame_pdf, bg="#9D174D", height=2).pack(fill="x", pady=(15, 5))
        tk.Label(frame_pdf, text="Obrigado pela preferencia!", font=("Helvetica", 10, "bold"),
                 fg="#9D174D", bg="#FFFFFF").pack()
        tk.Label(frame_pdf, text="Salao Paixao e Filhos - celebrando consigo.",
                 font=("Helvetica", 8), fg="#888888", bg="#FFFFFF").pack()

    def _obter_pasta_downloads(self):
        """Retorna o caminho da pasta Downloads do utilizador"""
        home = os.path.expanduser("~")
        pasta = os.path.join(home, "Downloads")
        if not os.path.exists(pasta):
            os.makedirs(pasta)
        return pasta

    def _gerar_factura_pdf(self, nr, cliente, evento, pacote, data_evento, valor, responsavel, convidados):
        """Gera factura em PDF conforme legislacao angolana"""
        from fpdf import FPDF

        data_emissao = datetime.now().strftime("%d/%m/%Y")
        hora_emissao = datetime.now().strftime("%H:%M")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Calcular IVA (14% em Angola)
        taxa_iva = 0.14
        valor_sem_iva = valor / (1 + taxa_iva)
        valor_iva = valor - valor_sem_iva

        # Pasta Downloads
        pasta = self._obter_pasta_downloads()
        nome_ficheiro = f"Factura_{nr}_{timestamp}.pdf"
        caminho_completo = os.path.join(pasta, nome_ficheiro)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Usar fonte Helvetica (suporta caracteres basicos)
        pdf.set_font("Helvetica", "B", 10)

        # --- CABECALHO DA EMPRESA ---
        pdf.set_fill_color(219, 39, 119)  # Magenta
        pdf.rect(10, 10, 190, 35, "F")
        
        # Logo no cabecalho
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=12, y=12, w=15, h=15)
            txt_x = 30
            txt_w = 170
        else:
            txt_x = 10
            txt_w = 190

        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_xy(txt_x, 12)
        pdf.cell(txt_w, 10, "PAIXAO E FILHOS", align="C")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_xy(txt_x, 23)
        pdf.cell(txt_w, 5, "Salao de Festas & Eventos", align="C")
        pdf.set_xy(txt_x, 29)
        pdf.cell(txt_w, 5, "Luanda, Angola", align="C")
        pdf.set_xy(txt_x, 35)
        pdf.cell(txt_w, 5, "NIF: 5419573961 | Tel: +244 923 456 789", align="C")

        # Posicao Y apos cabecalho
        y_apos_cabecalho = 48

        # --- DADOS DO DOCUMENTO (coluna esquerda + direita) ---
        pdf.set_xy(10, y_apos_cabecalho)
        pdf.set_text_color(51, 51, 51)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(95, 6, f"Nr. Factura: {nr}")
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(157, 23, 77)
        pdf.set_xy(110, y_apos_cabecalho)
        pdf.cell(90, 6, "DOCUMENTO VALIDO", align="R")
        pdf.set_xy(110, y_apos_cabecalho + 6)
        pdf.cell(90, 6, "PARA FINS FISCAIS", align="R")

        pdf.set_xy(10, y_apos_cabecalho + 6)
        pdf.set_text_color(51, 51, 51)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(95, 6, f"Data Emissao: {data_emissao}")

        pdf.set_xy(10, y_apos_cabecalho + 12)
        pdf.cell(95, 6, f"Hora: {hora_emissao}")

        # --- TIPO DE DOCUMENTO ---
        y_documento = y_apos_cabecalho + 22
        pdf.set_xy(10, y_documento)
        pdf.set_fill_color(157, 23, 77)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(190, 10, "FACTURA", align="C", fill=True)

        # --- DADOS DO CLIENTE ---
        y_cliente = y_documento + 14
        pdf.set_xy(10, y_cliente)
        pdf.set_fill_color(252, 231, 243)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(51, 51, 51)
        pdf.cell(190, 7, "  DADOS DO CLIENTE", fill=True)
        
        y_valores = y_cliente + 9
        pdf.set_font("Helvetica", "", 10)
        pdf.set_xy(10, y_valores)
        pdf.cell(95, 6, f"  Nome: {cliente}")
        pdf.set_xy(10, y_valores + 6)
        pdf.cell(95, 6, f"  Evento: {evento}")
        pdf.set_xy(10, y_valores + 12)
        pdf.cell(95, 6, f"  Data do Evento: {data_evento}")
        pdf.set_xy(10, y_valores + 18)
        pdf.cell(95, 6, f"  Nr. Convidados: {convidados}")
        pdf.set_xy(10, y_valores + 24)
        pdf.cell(95, 6, f"  Func. Responsavel: {responsavel}")

        # --- DETALHES DO SERVICO ---
        y_servico = y_valores + 34
        pdf.set_xy(10, y_servico)
        pdf.set_fill_color(252, 231, 243)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 7, "  DETALHES DO SERVICO", fill=True)

        # Cabecalho da tabela
        y_tabela = y_servico + 9
        pdf.set_xy(10, y_tabela)
        pdf.set_fill_color(157, 23, 77)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(80, 7, "  Descricao", border=1, fill=True)
        pdf.cell(30, 7, "Qtd", border=1, align="C", fill=True)
        pdf.cell(40, 7, "Preco Unit. (KZ)", border=1, align="C", fill=True)
        pdf.cell(40, 7, "Total (KZ)", border=1, align="C", fill=True)

        # Linha do servico
        y_linha = y_tabela + 7
        pdf.set_xy(10, y_linha)
        pdf.set_text_color(51, 51, 51)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(80, 7, f"  Pacote: {pacote}", border=1)
        pdf.cell(30, 7, "1", border=1, align="C")
        pdf.cell(40, 7, f"{valor_sem_iva:,.2f}", border=1, align="C")
        pdf.cell(40, 7, f"{valor_sem_iva:,.2f}", border=1, align="C")

        # Linha vazia
        y_vazia = y_linha + 7
        pdf.set_xy(10, y_vazia)
        pdf.cell(80, 7, "", border=1)
        pdf.cell(30, 7, "", border=1)
        pdf.cell(40, 7, "", border=1)
        pdf.cell(40, 7, "", border=1)

        # --- TOTAIS ---
        y_totais = y_vazia + 14
        pdf.set_xy(110, y_totais)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(51, 51, 51)
        pdf.cell(40, 6, "Sub-Total:", align="R")
        pdf.cell(40, 6, f"{valor_sem_iva:,.2f} KZ", align="R")

        pdf.set_xy(110, y_totais + 7)
        pdf.cell(40, 6, "IVA (14%):", align="R")
        pdf.cell(40, 6, f"{valor_iva:,.2f} KZ", align="R")

        pdf.set_xy(110, y_totais + 16)
        pdf.set_fill_color(219, 39, 119)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(40, 8, "TOTAL:", align="R", fill=True)
        pdf.cell(40, 8, f"{valor:,.0f} KZ", align="R", fill=True)

        # --- NOTAS LEGAIS ---
        y_notas = y_totais + 32
        pdf.set_xy(10, y_notas)
        pdf.set_text_color(102, 102, 102)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(190, 5, "Conforme a Lei Geral Tributaria de Angola e o Codigo do IVA,")
        pdf.set_xy(10, y_notas + 5)
        pdf.cell(190, 5, "este documento serve como comprovativo de prestacao de servicos.")
        pdf.set_xy(10, y_notas + 10)
        pdf.cell(190, 5, "O IVA e liquidado a taxa de 14% conforme legislacao vigente.")

        # --- RODAPE ---
        y_rodape = y_notas + 22
        pdf.set_xy(10, y_rodape)
        pdf.set_draw_color(157, 23, 77)
        pdf.line(10, y_rodape, 200, y_rodape)
        pdf.set_xy(10, y_rodape + 3)
        pdf.set_text_color(157, 23, 77)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(190, 5, "Obrigado pela preferencia!", align="C")
        pdf.set_xy(10, y_rodape + 9)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(102, 102, 102)
        pdf.cell(190, 5, "Salao Paixao e Filhos - celebrando consigo.", align="C")
        pdf.set_xy(10, y_rodape + 14)
        pdf.cell(190, 5, f"Documento gerado em {data_emissao} as {hora_emissao}", align="C")

        # Guardar PDF
        pdf.output(caminho_completo)
        return caminho_completo

    def _enviar_para_impressora(self, caminho_pdf):
        """Envia o PDF para a impressora padrao do sistema"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(caminho_pdf, "print")
            elif os.name == 'posix':  # macOS
                subprocess.Popen(['lpr', caminho_pdf])
            messagebox.showinfo("Impressao", "Documento enviado para a impressora!")
        except Exception as e:
            messagebox.showerror("Erro de Impressao",
                                 f"Nao foi possivel enviar para a impressora.\nO PDF foi guardado em:\n{caminho_pdf}")

    # =====================================================================
    # MODULO DE PATRIMONIO
    # =====================================================================
    def _gerar_codigo_patrimonio(self):
        """Gera codigo unico PAT-XXXX"""
        self.cursor.execute("SELECT COUNT(*) FROM patrimonio")
        total = self.cursor.fetchone()[0] + 1
        return f"PAT-{total:04d}"

    def _gerar_codigo_aluguer(self):
        """Gera codigo unico ALU-XXXXX"""
        self.cursor.execute("SELECT COUNT(*) FROM aluguer_patrimonio")
        total = self.cursor.fetchone()[0] + 1
        return f"ALU-{total:05d}"

    def _registrar_historico(self, patrimonio_id, operacao, estado_ant=None, estado_novo=None,
                             sit_ant=None, sit_nova=None, qtd_ant=None, qtd_nova=None,
                             desc=None, resp=None):
        """Registra uma entrada no historico do patrimonio"""
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cursor.execute(
            "INSERT INTO patrimonio_historico (patrimonio_id, operacao, estado_anterior, estado_novo, "
            "situacao_anterior, situacao_nova, quantidade_anterior, quantidade_nova, descricao, "
            "responsavel, data_operacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (patrimonio_id, operacao, estado_ant, estado_novo, sit_ant, sit_nova,
             qtd_ant, qtd_nova, desc, resp or self.utilizador_atual, agora)
        )

    def _obter_categorias(self):
        """Retorna lista de categorias"""
        return [(r[0], r[1]) for r in self.cursor.execute("SELECT id, nome FROM patrimonio_categorias ORDER BY nome")]

    def _calcular_situacao_patrimonio(self, pat_id):
        """Calcula a situacao operacional correta baseada nas quantidades"""
        r = self.cursor.execute(
            "SELECT quantidade_total, quantidade_disponivel, quantidade_alugada, quantidade_manutencao "
            "FROM patrimonio WHERE id=?", (pat_id,)).fetchone()
        if not r:
            return "INDISPONIVEL"
        total, disp, alug, manut = r
        if disp <= 0 and alug > 0 and manut <= 0:
            return "ALUGADO"
        elif disp <= 0 and manut > 0 and alug <= 0:
            return "EM_MANUTENCAO"
        elif disp <= 0 and alug > 0 and manut > 0:
            return "EM_USO"
        elif manut > 0 and disp > 0:
            return "EM_MANUTENCAO"
        elif alug > 0 and disp > 0:
            return "EM_USO"
        elif disp > 0:
            return "DISPONIVEL"
        else:
            return "INDISPONIVEL"

    # --- ABA PATRIMONIO ---
    def mostrar_aba_patrimonio(self):
        """Interface de gestao de patrimonio"""
        self.limpar_conteudo()
        self._patrimonio_editando_id = None

        tk.Label(self.conteudo, text="Gestao de Patrimonio",
                 font=("Helvetica", 18, "bold"), fg="#FFFFFF", bg=self.COR_BG).pack(anchor="w", pady=(0, 10))

        # Formulario
        form = tk.Frame(self.conteudo, bg=self.COR_CARD, padx=15, pady=15)
        form.pack(fill="x", pady=5)

        tk.Label(form, text="Nome:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=0, column=0, padx=3, sticky="w")
        self.ent_pat_nome = tk.Entry(form, font=("Helvetica", 10), bg=self.COR_BG, fg="white", bd=0, width=20)
        self.ent_pat_nome.grid(row=0, column=1, padx=5, ipady=3)

        tk.Label(form, text="Categoria:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=0, column=2, padx=3, sticky="w")
        cats = [c[1] for c in self._obter_categorias()]
        self.cb_pat_categoria = ttk.Combobox(form, values=cats, state="readonly", font=("Helvetica", 10), width=14)
        self.cb_pat_categoria.grid(row=0, column=3, padx=5, ipady=2)

        tk.Label(form, text="Quantidade:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=0, column=4, padx=3, sticky="w")
        self.ent_pat_qtd = tk.Entry(form, font=("Helvetica", 10), bg=self.COR_BG, fg="white", bd=0, width=6)
        self.ent_pat_qtd.grid(row=0, column=5, padx=5, ipady=3)
        self.ent_pat_qtd.insert(0, "1")

        tk.Label(form, text="Valor (KZ):", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=1, column=0, padx=3, sticky="w", pady=(5,0))
        self.ent_pat_valor = tk.Entry(form, font=("Helvetica", 10), bg=self.COR_BG, fg="white", bd=0, width=12)
        self.ent_pat_valor.grid(row=1, column=1, padx=5, ipady=3, pady=(5,0))

        tk.Label(form, text="Estado Fisico:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=1, column=2, padx=3, sticky="w", pady=(5,0))
        self.cb_pat_estado = ttk.Combobox(form, values=["NOVO", "BOM", "REGULAR", "DANIFICADO", "EM_MANUTENCAO", "INSERVIVEL"],
                                           state="readonly", font=("Helvetica", 10), width=14)
        self.cb_pat_estado.grid(row=1, column=3, padx=5, ipady=2, pady=(5,0))
        self.cb_pat_estado.set("NOVO")

        tk.Label(form, text="Situacao:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=1, column=4, padx=3, sticky="w", pady=(5,0))
        self.cb_pat_situacao = ttk.Combobox(form, values=["DISPONIVEL", "EM_USO", "ALUGADO", "EM_MANUTENCAO", "INDISPONIVEL"],
                                             state="readonly", font=("Helvetica", 10), width=14)
        self.cb_pat_situacao.grid(row=1, column=5, padx=5, ipady=2, pady=(5,0))
        self.cb_pat_situacao.set("DISPONIVEL")

        tk.Label(form, text="Descricao:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=2, column=0, padx=3, sticky="w", pady=(5,0))
        self.ent_pat_desc = tk.Entry(form, font=("Helvetica", 10), bg=self.COR_BG, fg="white", bd=0, width=40)
        self.ent_pat_desc.grid(row=2, column=1, columnspan=3, padx=5, ipady=3, pady=(5,0), sticky="w")

        tk.Label(form, text="Localizacao:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=2, column=4, padx=3, sticky="w", pady=(5,0))
        self.ent_pat_local = tk.Entry(form, font=("Helvetica", 10), bg=self.COR_BG, fg="white", bd=0, width=14)
        self.ent_pat_local.grid(row=2, column=5, padx=5, ipady=3, pady=(5,0))

        # Botoes
        frame_botoes = tk.Frame(form, bg=self.COR_CARD)
        frame_botoes.grid(row=3, column=0, columnspan=6, pady=(10, 0), sticky="w")

        self.frame_pat_registar = tk.Frame(frame_botoes, bg=self.COR_MAGENTA, cursor="hand2")
        self.frame_pat_registar.pack(side="left", padx=5)
        self.lbl_pat_registar = tk.Label(self.frame_pat_registar, text="Registar", font=("Helvetica", 9, "bold"), fg="white", bg=self.COR_MAGENTA, padx=12)
        self.lbl_pat_registar.pack()
        for w in [self.frame_pat_registar, self.lbl_pat_registar]:
            w.bind("<Enter>", lambda e: (self.frame_pat_registar.configure(bg="#C2185B"), self.lbl_pat_registar.configure(bg="#C2185B")))
            w.bind("<Leave>", lambda e: (self.frame_pat_registar.configure(bg=self.COR_MAGENTA), self.lbl_pat_registar.configure(bg=self.COR_MAGENTA)))
            w.bind("<Button-1>", lambda e: self._guardar_patrimonio())

        f_edit = tk.Frame(frame_botoes, bg="#F59E0B", cursor="hand2")
        f_edit.pack(side="left", padx=5)
        l_edit = tk.Label(f_edit, text="Editar", font=("Helvetica", 9, "bold"), fg="white", bg="#F59E0B", padx=12)
        l_edit.pack()
        for w in [f_edit, l_edit]:
            w.bind("<Enter>", lambda e: (f_edit.configure(bg="#D97706"), l_edit.configure(bg="#D97706")))
            w.bind("<Leave>", lambda e: (f_edit.configure(bg="#F59E0B"), l_edit.configure(bg="#F59E0B")))
            w.bind("<Button-1>", lambda e: self._editar_patrimonio_selecionado())

        f_del = tk.Frame(frame_botoes, bg="#EF4444", cursor="hand2")
        f_del.pack(side="left", padx=5)
        l_del = tk.Label(f_del, text="Inativar", font=("Helvetica", 9, "bold"), fg="white", bg="#EF4444", padx=12)
        l_del.pack()
        for w in [f_del, l_del]:
            w.bind("<Enter>", lambda e: (f_del.configure(bg="#DC2626"), l_del.configure(bg="#DC2626")))
            w.bind("<Leave>", lambda e: (f_del.configure(bg="#EF4444"), l_del.configure(bg="#EF4444")))
            w.bind("<Button-1>", lambda e: self._inativar_patrimonio())

        f_hist = tk.Frame(frame_botoes, bg="#3B82F6", cursor="hand2")
        f_hist.pack(side="left", padx=5)
        l_hist = tk.Label(f_hist, text="Historico", font=("Helvetica", 9, "bold"), fg="white", bg="#3B82F6", padx=12)
        l_hist.pack()
        for w in [f_hist, l_hist]:
            w.bind("<Enter>", lambda e: (f_hist.configure(bg="#60A5FA"), l_hist.configure(bg="#60A5FA")))
            w.bind("<Leave>", lambda e: (f_hist.configure(bg="#3B82F6"), l_hist.configure(bg="#3B82F6")))
            w.bind("<Button-1>", lambda e: self._ver_historico_patrimonio())

        f_limpar = tk.Frame(frame_botoes, bg="#64748B", cursor="hand2")
        f_limpar.pack(side="left", padx=5)
        l_limpar = tk.Label(f_limpar, text="Limpar", font=("Helvetica", 9, "bold"), fg="white", bg="#64748B", padx=12)
        l_limpar.pack()
        for w in [f_limpar, l_limpar]:
            w.bind("<Enter>", lambda e: (f_limpar.configure(bg="#94A3B8"), l_limpar.configure(bg="#94A3B8")))
            w.bind("<Leave>", lambda e: (f_limpar.configure(bg="#64748B"), l_limpar.configure(bg="#64748B")))
            w.bind("<Button-1>", lambda e: self._limpar_form_patrimonio())

        # Tabela
        self.tv_pat = ttk.Treeview(self.conteudo, columns=("Codigo", "Nome", "Categoria", "Qtd Total", "Qtd Disp", "Qtd Alug", "Estado", "Situacao"), show="headings")
        for col in self.tv_pat["columns"]:
            self.tv_pat.heading(col, text=col)
            self.tv_pat.column(col, anchor="center", width=90)
        self.tv_pat.column("Nome", width=150)
        self.tv_pat.pack(fill="both", expand=True, pady=10)
        self.tv_pat.bind("<<TreeviewSelect>>", lambda e: self._selecionar_patrimonio())
        self._atualizar_tabela_patrimonio()

    def _limpar_form_patrimonio(self):
        """Limpa o formulario de patrimonio"""
        self._patrimonio_editando_id = None
        for ent in [self.ent_pat_nome, self.ent_pat_desc, self.ent_pat_local, self.ent_pat_valor]:
            ent.delete(0, "end")
        self.ent_pat_qtd.delete(0, "end")
        self.ent_pat_qtd.insert(0, "1")
        self.cb_pat_estado.set("NOVO")
        self.cb_pat_situacao.set("DISPONIVEL")
        if self._obter_categorias():
            self.cb_pat_categoria.set(self._obter_categorias()[0][1])
        self.lbl_pat_registar.config(text="Registar")

    def _guardar_patrimonio(self):
        """Guarda novo patrimonio ou atualiza existente"""
        nome = self.ent_pat_nome.get().strip()
        cat_nome = self.cb_pat_categoria.get()
        qtd_str = self.ent_pat_qtd.get().strip()
        valor_str = self.ent_pat_valor.get().strip()
        estado = self.cb_pat_estado.get()
        situacao = self.cb_pat_situacao.get()
        desc = self.ent_pat_desc.get().strip()
        local = self.ent_pat_local.get().strip()

        if not nome:
            messagebox.showwarning("Aviso", "Indique o nome do patrimonio.")
            return
        try:
            qtd = int(qtd_str) if qtd_str else 1
            valor = float(valor_str) if valor_str else 0
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e valor devem ser numericos.")
            return
        if qtd < 1:
            messagebox.showwarning("Aviso", "Quantidade deve ser >= 1.")
            return

        cat_id = None
        for cid, cnome in self._obter_categorias():
            if cnome == cat_nome:
                cat_id = cid
                break

        agora = datetime.now().strftime("%d/%m/%Y %H:%M")

        if self._patrimonio_editando_id:
            # Editar
            pid = self._patrimonio_editando_id
            self.cursor.execute("SELECT quantidade_total, quantidade_alugada, quantidade_manutencao, estado_fisico, situacao_operacional FROM patrimonio WHERE id=?", (pid,))
            ant = self.cursor.fetchone()
            qtd_total_ant, qtd_alug_ant, qtd_manut_ant, est_ant, sit_ant = ant

            nova_disp = qtd - qtd_alug_ant - qtd_manut_ant
            if nova_disp < 0:
                messagebox.showerror("Erro", f"Quantidade invalida. Ha {qtd_alug_ant} alugadas + {qtd_manut_ant} em manutencao.")
                return

            self.cursor.execute(
                "UPDATE patrimonio SET nome=?, descricao=?, categoria_id=?, quantidade_total=?, "
                "quantidade_disponivel=?, estado_fisico=?, situacao_operacional=?, valor_aquisicao=?, "
                "localizacao=?, updated_at=? WHERE id=?",
                (nome, desc, cat_id, qtd, nova_disp, estado, situacao, valor, local, agora, pid)
            )
            self._registrar_historico(pid, "EDICAO", est_ant, estado, sit_ant, situacao, qtd_total_ant, qtd, "Patrimonio editado")
            msg = f"Patrimonio '{nome}' atualizado!"
        else:
            # Novo
            if qtd < 1:
                messagebox.showwarning("Aviso", "Quantidade deve ser >= 1.")
                return
            codigo = self._gerar_codigo_patrimonio()
            self.cursor.execute(
                "INSERT INTO patrimonio (codigo, nome, descricao, categoria_id, quantidade_total, "
                "quantidade_disponivel, estado_fisico, situacao_operacional, valor_aquisicao, "
                "data_aquisicao, localizacao, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (codigo, nome, desc, cat_id, qtd, qtd, estado, situacao, valor, agora.split(" ")[0], local, agora, agora)
            )
            pid = self.cursor.lastrowid
            self._registrar_historico(pid, "CADASTRO", None, estado, None, situacao, None, qtd, "Patrimonio cadastrado")
            msg = f"Patrimonio '{nome}' cadastrado como {codigo}!"

        self.conn.commit()
        messagebox.showinfo("Sucesso", msg)
        self._limpar_form_patrimonio()
        self._atualizar_tabela_patrimonio()

    def _selecionar_patrimonio(self):
        """Carrega patrimonio selecionado no formulario"""
        sel = self.tv_pat.selection()
        if not sel:
            return
        vals = self.tv_pat.item(sel[0], "values")
        codigo = vals[0]
        self.cursor.execute("SELECT id, nome, descricao, categoria_id, quantidade_total, estado_fisico, "
                           "situacao_operacional, valor_aquisicao, localizacao FROM patrimonio WHERE codigo=?", (codigo,))
        p = self.cursor.fetchone()
        if not p:
            return
        self._patrimonio_editando_id = p[0]
        self._limpar_form_patrimonio()
        self._patrimonio_editando_id = p[0]
        self.ent_pat_nome.insert(0, p[1])
        if p[3]:
            for cid, cnome in self._obter_categorias():
                if cid == p[3]:
                    self.cb_pat_categoria.set(cnome)
                    break
        self.ent_pat_qtd.delete(0, "end")
        self.ent_pat_qtd.insert(0, str(p[4]))
        self.ent_pat_valor.delete(0, "end")
        self.ent_pat_valor.insert(0, str(p[7] or 0))
        self.cb_pat_estado.set(p[5])
        self.cb_pat_situacao.set(p[6])
        self.ent_pat_desc.insert(0, p[2] or "")
        self.ent_pat_local.insert(0, p[8] or "")
        self.lbl_pat_registar.config(text="Guardar")

    def _editar_patrimonio_selecionado(self):
        """Ativa modo edicao"""
        sel = self.tv_pat.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um patrimonio na tabela.")
            return
        self._selecionar_patrimonio()

    def _inativar_patrimonio(self):
        """Inativa patrimonio selecionado"""
        sel = self.tv_pat.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um patrimonio na tabela.")
            return
        vals = self.tv_pat.item(sel[0], "values")
        codigo, nome = vals[0], vals[1]
        qtd_alug = int(vals[5]) if vals[5] else 0
        if qtd_alug > 0:
            messagebox.showwarning("Aviso", f"Nao e possivel inativar '{nome}' — tem {qtd_alug} unidades alugadas.")
            return
        if not messagebox.askyesno("Confirmar", f"Inativar o patrimonio '{nome}' ({codigo})?"):
            return
        self.cursor.execute("UPDATE patrimonio SET ativo=0, updated_at=? WHERE codigo=?",
                           (datetime.now().strftime("%d/%m/%Y %H:%M"), codigo))
        pid = self.cursor.execute("SELECT id FROM patrimonio WHERE codigo=?", (codigo,)).fetchone()[0]
        self._registrar_historico(pid, "INATIVACAO", desc="Patrimonio inativado")
        self.conn.commit()
        messagebox.showinfo("Sucesso", f"Patrimonio '{nome}' inativado.")
        self._limpar_form_patrimonio()
        self._atualizar_tabela_patrimonio()

    def _ver_historico_patrimonio(self):
        """Abre janela com historico do patrimonio selecionado"""
        sel = self.tv_pat.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um patrimonio na tabela.")
            return
        vals = self.tv_pat.item(sel[0], "values")
        codigo, nome = vals[0], vals[1]
        pid = self.cursor.execute("SELECT id FROM patrimonio WHERE codigo=?", (codigo,)).fetchone()[0]

        janela = tk.Toplevel(self.root)
        janela.title(f"Historico - {nome}")
        janela.geometry("700x400")
        janela.configure(bg=self.COR_BG)

        tk.Label(janela, text=f"Historico de {codigo} - {nome}", font=("Helvetica", 14, "bold"),
                 fg="#FFFFFF", bg=self.COR_BG).pack(pady=10)

        tv = ttk.Treeview(janela, columns=("Data", "Operacao", "Est. Anterior", "Est. Novo", "Sit. Anterior", "Sit. Nova", "Qtd Ant", "Qtd Nova", "Resp"), show="headings")
        for col in tv["columns"]:
            tv.heading(col, text=col)
            tv.column(col, anchor="center", width=70)
        tv.column("Operacao", width=100)
        tv.pack(fill="both", expand=True, padx=10, pady=5)

        for h in self.cursor.execute(
            "SELECT data_operacao, operacao, estado_anterior, estado_novo, situacao_anterior, "
            "situacao_nova, quantidade_anterior, quantidade_nova, responsavel "
            "FROM patrimonio_historico WHERE patrimonio_id=? ORDER BY id DESC", (pid,)):
            tv.insert("", "end", values=h)

        tk.Button(janela, text="Fechar", command=janela.destroy, bg="#64748B", fg="white").pack(pady=5)

    def _atualizar_tabela_patrimonio(self):
        """Atualiza tabela de patrimonios"""
        self.tv_pat.delete(*self.tv_pat.get_children())
        for r in self.cursor.execute(
            "SELECT p.codigo, p.nome, c.nome, p.quantidade_total, p.quantidade_disponivel, "
            "p.quantidade_alugada, p.estado_fisico, p.situacao_operacional "
            "FROM patrimonio p LEFT JOIN patrimonio_categorias c ON p.categoria_id=c.id "
            "WHERE p.ativo=1 ORDER BY p.codigo"):
            self.tv_pat.insert("", "end", values=r)

    # --- ABA ALUGUER PATRIMONIO ---
    def mostrar_aba_aluguer_patrimonio(self):
        """Interface de gestao de alugueres de patrimonio"""
        self.limpar_conteudo()
        self._aluguer_editando_id = None
        self._aluguer_itens = []  # [(patrimonio_id, nome, qtd, valor_unit, estado_saida)]

        tk.Label(self.conteudo, text="Aluguer de Patrimonio",
                 font=("Helvetica", 18, "bold"), fg="#FFFFFF", bg=self.COR_BG).pack(anchor="w", pady=(0, 10))

        # Formulario principal
        form = tk.Frame(self.conteudo, bg=self.COR_CARD, padx=15, pady=15)
        form.pack(fill="x", pady=5)

        tk.Label(form, text="Cliente:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=0, column=0, padx=3, sticky="w")
        self.ent_alug_cliente = tk.Entry(form, font=("Helvetica", 10), bg=self.COR_BG, fg="white", bd=0, width=25)
        self.ent_alug_cliente.grid(row=0, column=1, padx=5, ipady=3)

        tk.Label(form, text="Inicio:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=0, column=2, padx=3, sticky="w")
        self.ent_alug_inicio = tk.Entry(form, font=("Helvetica", 10), bg=self.COR_BG, fg="white", bd=0, width=12)
        self.ent_alug_inicio.grid(row=0, column=3, padx=5, ipady=3)
        self.ent_alug_inicio.insert(0, datetime.now().strftime("%d/%m/%Y"))

        tk.Label(form, text="Devolucao:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=0, column=4, padx=3, sticky="w")
        self.ent_alug_devolucao = tk.Entry(form, font=("Helvetica", 10), bg=self.COR_BG, fg="white", bd=0, width=12)
        self.ent_alug_devolucao.grid(row=0, column=5, padx=(5,2), ipady=3)

        # Botoes de calendario
        f_cal_dev = tk.Frame(form, bg="#3B82F6", cursor="hand2")
        f_cal_dev.grid(row=0, column=6, padx=2)
        l_cal_dev = tk.Label(f_cal_dev, text="...", font=("Helvetica", 10, "bold"), fg="white", bg="#3B82F6", padx=4)
        l_cal_dev.pack()
        for w in [f_cal_dev, l_cal_dev]:
            w.bind("<Enter>", lambda e: (f_cal_dev.configure(bg="#60A5FA"), l_cal_dev.configure(bg="#60A5FA")))
            w.bind("<Leave>", lambda e: (f_cal_dev.configure(bg="#3B82F6"), l_cal_dev.configure(bg="#3B82F6")))
            w.bind("<Button-1>", lambda e: self._criar_calendario(self.root, self.ent_alug_devolucao))

        tk.Label(form, text="Observacoes:", fg=self.COR_TEXTO, bg=self.COR_CARD, font=("Helvetica", 9, "bold")).grid(row=1, column=0, padx=3, sticky="w", pady=(5,0))
        self.ent_alug_obs = tk.Entry(form, font=("Helvetica", 10), bg=self.COR_BG, fg="white", bd=0, width=40)
        self.ent_alug_obs.grid(row=1, column=1, columnspan=3, padx=5, ipady=3, pady=(5,0), sticky="w")

        # Seccao de adicionar itens
        frame_itens_add = tk.Frame(form, bg="#3D2E36", padx=10, pady=10)
        frame_itens_add.grid(row=2, column=0, columnspan=6, pady=(10,0), sticky="ew")

        tk.Label(frame_itens_add, text="Adicionar Item:", font=("Helvetica", 10, "bold"), fg="#FFFFFF", bg="#3D2E36").pack(anchor="w")

        linha_item = tk.Frame(frame_itens_add, bg="#3D2E36")
        linha_item.pack(fill="x", pady=3)

        tk.Label(linha_item, text="Patrimonio:", fg=self.COR_TEXTO, bg="#3D2E36", font=("Helvetica", 9)).pack(side="left", padx=3)
        pat_nomes = [(r[0], f"{r[1]} ({r[2]} - Disp: {r[3]})") for r in self.cursor.execute(
            "SELECT id, codigo, nome, quantidade_disponivel FROM patrimonio WHERE ativo=1 AND quantidade_disponivel>0 ORDER BY nome")]
        self._alug_pat_map = {f"{c} ({n} - Disp: {d})": pid for pid, c, n, d in self.cursor.execute(
            "SELECT id, codigo, nome, quantidade_disponivel FROM patrimonio WHERE ativo=1 AND quantidade_disponivel>0 ORDER BY nome")}
        self.cb_alug_pat = ttk.Combobox(linha_item, values=list(self._alug_pat_map.keys()), state="readonly", font=("Helvetica", 9), width=35)
        self.cb_alug_pat.pack(side="left", padx=3)

        tk.Label(linha_item, text="Qtd:", fg=self.COR_TEXTO, bg="#3D2E36", font=("Helvetica", 9)).pack(side="left", padx=3)
        self.ent_alug_item_qtd = tk.Entry(linha_item, font=("Helvetica", 9), bg=self.COR_BG, fg="white", bd=0, width=5)
        self.ent_alug_item_qtd.pack(side="left", padx=3, ipady=2)
        self.ent_alug_item_qtd.insert(0, "1")

        tk.Label(linha_item, text="Valor Unit:", fg=self.COR_TEXTO, bg="#3D2E36", font=("Helvetica", 9)).pack(side="left", padx=3)
        self.ent_alug_item_valor = tk.Entry(linha_item, font=("Helvetica", 9), bg=self.COR_BG, fg="white", bd=0, width=10)
        self.ent_alug_item_valor.pack(side="left", padx=3, ipady=2)

        tk.Label(linha_item, text="Estado:", fg=self.COR_TEXTO, bg="#3D2E36", font=("Helvetica", 9)).pack(side="left", padx=3)
        self.cb_alug_item_estado = ttk.Combobox(linha_item, values=["NOVO", "BOM", "REGULAR", "DANIFICADO"],
                                                 state="readonly", font=("Helvetica", 9), width=10)
        self.cb_alug_item_estado.pack(side="left", padx=3)
        self.cb_alug_item_estado.set("BOM")

        f_add = tk.Frame(linha_item, bg="#10B981", cursor="hand2")
        f_add.pack(side="left", padx=8)
        l_add = tk.Label(f_add, text=" + Adicionar ", font=("Helvetica", 9, "bold"), fg="white", bg="#10B981")
        l_add.pack()
        for w in [f_add, l_add]:
            w.bind("<Enter>", lambda e: (f_add.configure(bg="#34D399"), l_add.configure(bg="#34D399")))
            w.bind("<Leave>", lambda e: (f_add.configure(bg="#10B981"), l_add.configure(bg="#10B981")))
            w.bind("<Button-1>", lambda e: self._adicionar_item_aluguer())

        # Lista de itens adicionados
        frame_itens_lista = tk.Frame(self.conteudo, bg=self.COR_CARD, padx=10, pady=10)
        frame_itens_lista.pack(fill="x", pady=5)

        tk.Label(frame_itens_lista, text="Itens do Aluguer:", font=("Helvetica", 10, "bold"),
                 fg="#FFFFFF", bg=self.COR_CARD).pack(anchor="w")

        self.tv_alug_itens = ttk.Treeview(frame_itens_lista, columns=("Patrimonio", "Qtd", "Valor Unit.", "Total", "Estado Saida"), show="headings", height=4)
        for col in self.tv_alug_itens["columns"]:
            self.tv_alug_itens.heading(col, text=col)
            self.tv_alug_itens.column(col, anchor="center", width=100)
        self.tv_alug_itens.column("Patrimonio", width=200)
        self.tv_alug_itens.pack(fill="x")

        f_rem = tk.Frame(frame_itens_lista, bg="#EF4444", cursor="hand2")
        f_rem.pack(anchor="w", pady=3)
        l_rem = tk.Label(f_rem, text=" Remover Item ", font=("Helvetica", 8, "bold"), fg="white", bg="#EF4444")
        l_rem.pack()
        for w in [f_rem, l_rem]:
            w.bind("<Enter>", lambda e: (f_rem.configure(bg="#DC2626"), l_rem.configure(bg="#DC2626")))
            w.bind("<Leave>", lambda e: (f_rem.configure(bg="#EF4444"), l_rem.configure(bg="#EF4444")))
            w.bind("<Button-1>", lambda e: self._remover_item_aluguer())

        # Resumo e botoes
        frame_resumo = tk.Frame(self.conteudo, bg=self.COR_CARD, padx=15, pady=10)
        frame_resumo.pack(fill="x", pady=5)

        self.lbl_alug_total = tk.Label(frame_resumo, text="Total: 0 KZ", font=("Helvetica", 14, "bold"),
                                        fg=self.COR_ROSA_VIVO, bg=self.COR_CARD)
        self.lbl_alug_total.pack(side="left")

        frame_b_alug = tk.Frame(frame_resumo, bg=self.COR_CARD)
        frame_b_alug.pack(side="right")

        self._criar_botao(frame_b_alug, "Confirmar Aluguer", self._confirmar_aluguer_patrimonio, bg="#10B981")
        self._criar_botao(frame_b_alug, "Limpar", self._limpar_form_aluguer, bg="#64748B")

        # Tabela de alugueres existentes
        tk.Label(self.conteudo, text="Alugueres Registados", font=("Helvetica", 12, "bold"),
                 fg="#FFFFFF", bg=self.COR_BG).pack(anchor="w", pady=(10, 5))

        self.tv_alug = ttk.Treeview(self.conteudo, columns=("Nr", "Cliente", "Data", "Prev. Dev.", "Valor", "Pago", "Pendente", "Estado"), show="headings")
        for col in self.tv_alug["columns"]:
            self.tv_alug.heading(col, text=col)
            self.tv_alug.column(col, anchor="center", width=90)
        self.tv_alug.column("Nr", width=100)
        self.tv_alug.column("Cliente", width=130)
        self.tv_alug.pack(fill="both", expand=True, pady=5)
        self.tv_alug.bind("<<TreeviewSelect>>", lambda e: self._selecionar_aluguer())

        # Botoes de acao para alugueres
        frame_b_alug_acao = tk.Frame(self.conteudo, bg=self.COR_BG)
        frame_b_alug_acao.pack(fill="x", pady=3)
        self._criar_botao(frame_b_alug_acao, "Registar Devolucao", self._abrir_devolucao_aluguer, bg="#F59E0B")
        self._criar_botao(frame_b_alug_acao, "Registar Pagamento", self._abrir_pagamento_aluguer, bg="#10B981")
        self._criar_botao(frame_b_alug_acao, "Cancelar Aluguer", self._cancelar_aluguer, bg="#EF4444")
        self._criar_botao(frame_b_alug_acao, "Atualizar", self._atualizar_tabela_alugueres, bg="#64748B")

        self._atualizar_tabela_alugueres()

    def _adicionar_item_aluguer(self):
        """Adiciona item a lista do aluguer"""
        pat_sel = self.cb_alug_pat.get()
        if not pat_sel or pat_sel not in self._alug_pat_map:
            messagebox.showwarning("Aviso", "Selecione um patrimonio.")
            return
        pat_id = self._alug_pat_map[pat_sel]
        try:
            qtd = int(self.ent_alug_item_qtd.get().strip())
            valor = float(self.ent_alug_item_valor.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e valor devem ser numericos.")
            return
        if qtd < 1:
            messagebox.showwarning("Aviso", "Quantidade deve ser >= 1.")
            return

        # Verificar disponibilidade
        disp = self.cursor.execute("SELECT quantidade_disponivel, nome FROM patrimonio WHERE id=?", (pat_id,)).fetchone()
        if qtd > disp[0]:
            messagebox.showerror("Erro", f"Disponivel: {disp[0]} unidades de '{disp[1]}'.")
            return

        estado = self.cb_alug_item_estado.get()
        self._aluguer_itens.append((pat_id, disp[1], qtd, valor, estado))
        self._atualizar_lista_itens_aluguer()

    def _remover_item_aluguer(self):
        """Remove item selecionado da lista"""
        sel = self.tv_alug_itens.selection()
        if not sel:
            return
        idx = self.tv_alug_itens.index(sel[0])
        if idx < len(self._aluguer_itens):
            self._aluguer_itens.pop(idx)
        self._atualizar_lista_itens_aluguer()

    def _atualizar_lista_itens_aluguer(self):
        """Atualiza a lista visual de itens"""
        self.tv_alug_itens.delete(*self.tv_alug_itens.get_children())
        total = 0
        for pid, nome, qtd, valor_unit, estado in self._aluguer_itens:
            subtotal = qtd * valor_unit
            total += subtotal
            self.tv_alug_itens.insert("", "end", values=(nome, qtd, f"{valor_unit:,.0f}", f"{subtotal:,.0f}", estado))
        self.lbl_alug_total.config(text=f"Total: {total:,.0f} KZ")

    def _confirmar_aluguer_patrimonio(self):
        """Confirma e cria o aluguer"""
        cliente = self.ent_alug_cliente.get().strip()
        inicio = self.ent_alug_inicio.get().strip()
        devolucao = self.ent_alug_devolucao.get().strip()
        obs = self.ent_alug_obs.get().strip()

        if not cliente:
            messagebox.showwarning("Aviso", "Indique o cliente.")
            return
        if not self._aluguer_itens:
            messagebox.showwarning("Aviso", "Adicione pelo menos um item.")
            return
        try:
            datetime.strptime(inicio, "%d/%m/%Y")
            if devolucao:
                datetime.strptime(devolucao, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data invalido. Use DD/MM/AAAA.")
            return

        numero = self._gerar_codigo_aluguer()
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        total = sum(q * v for _, _, q, v, _ in self._aluguer_itens)

        # Criar aluguer
        self.cursor.execute(
            "INSERT INTO aluguer_patrimonio (numero_aluguer, cliente, data_aluguer, data_inicio, "
            "data_devolucao_prevista, estado, valor_total, valor_pago, valor_pendente, observacoes, "
            "responsavel, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'ATIVO', ?, 0, ?, ?, ?, ?, ?)",
            (numero, cliente, agora.split(" ")[0], inicio, devolucao or None, total, total, obs,
             self.utilizador_atual, agora, agora)
        )
        aluguer_id = self.cursor.lastrowid

        # Entrada financeira do aluguer
        self.cursor.execute(
            "INSERT INTO financeiro (reserva_id, tipo, descricao, valor, data, data_criacao) "
            "VALUES (NULL, 'ENTRADA', ?, ?, ?, ?)",
            (f"Aluguer Patrimonio {numero} - {cliente}", total, agora.split(" ")[0], agora.split(" ")[0])
        )

        # Criar itens e atualizar quantidades
        for pat_id, nome, qtd, valor_unit, estado_saida in self._aluguer_itens:
            valor_total_item = qtd * valor_unit
            self.cursor.execute(
                "INSERT INTO aluguer_patrimonio_itens (aluguer_id, patrimonio_id, quantidade, "
                "valor_unitario, valor_total, estado_saida) VALUES (?, ?, ?, ?, ?, ?)",
                (aluguer_id, pat_id, qtd, valor_unit, valor_total_item, estado_saida)
            )
            # Atualizar disponibilidade
            nova_sit = self._calcular_situacao_patrimonio(pat_id)
            self.cursor.execute(
                "UPDATE patrimonio SET quantidade_disponivel = quantidade_disponivel - ?, "
                "quantidade_alugada = quantidade_alugada + ?, situacao_operacional = ?, "
                "updated_at = ? WHERE id = ?",
                (qtd, qtd, nova_sit, agora, pat_id)
            )
            self._registrar_historico(pat_id, "ALUGUER", None, None, None, nova_sit, None, qtd,
                                       f"Aluguer {numero} - {cliente}")

        self.conn.commit()
        messagebox.showinfo("Sucesso", f"Aluguer {numero} criado com sucesso!\nTotal: {total:,.0f} KZ")
        self._limpar_form_aluguer()
        self._atualizar_tabela_alugueres()

    def _limpar_form_aluguer(self):
        """Limpa formulario de aluguer"""
        self._aluguer_itens = []
        self._aluguer_editando_id = None
        for ent in [self.ent_alug_cliente, self.ent_alug_obs]:
            ent.delete(0, "end")
        self.ent_alug_inicio.delete(0, "end")
        self.ent_alug_inicio.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ent_alug_devolucao.delete(0, "end")
        self.lbl_alug_total.config(text="Total: 0 KZ")
        self._atualizar_lista_itens_aluguer()

    def _selecionar_aluguer(self):
        """Seleciona aluguer na tabela"""
        pass  # Acao opcional

    def _atualizar_tabela_alugueres(self):
        """Atualiza tabela de alugueres"""
        self.tv_alug.delete(*self.tv_alug.get_children())
        for r in self.cursor.execute(
            "SELECT numero_aluguer, cliente, data_aluguer, data_devolucao_prevista, "
            "valor_total, valor_pago, valor_pendente, estado FROM aluguer_patrimonio ORDER BY id DESC"):
            self.tv_alug.insert("", "end", values=r)

    def _abrir_devolucao_aluguer(self):
        """Abre janela de devolucao"""
        sel = self.tv_alug.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um aluguer na tabela.")
            return
        vals = self.tv_alug.item(sel[0], "values")
        numero = vals[0]
        estado = vals[7]
        if estado in ("DEVOLVIDO", "CANCELADO"):
            messagebox.showwarning("Aviso", f"Aluguer {numero} ja esta {estado}.")
            return

        alug_id = self.cursor.execute("SELECT id FROM aluguer_patrimonio WHERE numero_aluguer=?", (numero,)).fetchone()[0]

        janela = tk.Toplevel(self.root)
        janela.title(f"Devolucao - {numero}")
        janela.geometry("600x450")
        janela.configure(bg=self.COR_BG)
        janela.transient(self.root)
        janela.grab_set()

        tk.Label(janela, text=f"Devolucao - {numero}", font=("Helvetica", 14, "bold"),
                 fg="#FFFFFF", bg=self.COR_BG).pack(pady=10)

        tk.Label(janela, text=f"Cliente: {vals[1]}", font=("Helvetica", 10),
                 fg=self.COR_TEXTO, bg=self.COR_BG).pack(anchor="w", padx=15)

        # Itens do aluguer
        tv = ttk.Treeview(janela, columns=("Patrimonio", "Qtd Alugada", "Qtd Devolvida", "Estado Devolucao", "Observacoes"), show="headings", height=6)
        for col in tv["columns"]:
            tv.heading(col, text=col)
            tv.column(col, anchor="center", width=90)
        tv.column("Patrimonio", width=150)
        tv.pack(fill="x", padx=15, pady=5)

        itens = self.cursor.execute(
            "SELECT ai.id, p.nome, ai.quantidade, ai.quantidade_devolvida, ai.estado_saida "
            "FROM aluguer_patrimonio_itens ai JOIN patrimonio p ON ai.patrimonio_id=p.id "
            "WHERE ai.aluguer_id=?", (alug_id,)).fetchall()

        for item in itens:
            restante = item[2] - item[3]
            tv.insert("", "end", values=(item[1], item[2], item[3], item[4], ""), iid=str(item[0]))

        # Formulario de devolucao por item
        frame_dev = tk.Frame(janela, bg=self.COR_CARD, padx=10, pady=10)
        frame_dev.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_dev, text="Qtd a devolver:", fg=self.COR_TEXTO, bg=self.COR_CARD).grid(row=0, column=0, padx=3)
        ent_qtd_dev = tk.Entry(frame_dev, font=("Helvetica", 10), bg=self.COR_BG, fg="white", bd=0, width=6)
        ent_qtd_dev.grid(row=0, column=1, padx=3, ipady=2)
        ent_qtd_dev.insert(0, "0")

        tk.Label(frame_dev, text="Estado:", fg=self.COR_TEXTO, bg=self.COR_CARD).grid(row=0, column=2, padx=3)
        cb_estado_dev = ttk.Combobox(frame_dev, values=["BOM", "REGULAR", "DANIFICADO"], state="readonly", font=("Helvetica", 10), width=12)
        cb_estado_dev.grid(row=0, column=3, padx=3)
        cb_estado_dev.set("BOM")

        tk.Label(frame_dev, text="Obs:", fg=self.COR_TEXTO, bg=self.COR_CARD).grid(row=0, column=4, padx=3)
        ent_obs_dev = tk.Entry(frame_dev, font=("Helvetica", 10), bg=self.COR_BG, fg="white", bd=0, width=15)
        ent_obs_dev.grid(row=0, column=5, padx=3, ipady=2)

        def _registrar_devolucao():
            sel_item = tv.selection()
            if not sel_item:
                messagebox.showwarning("Aviso", "Selecione um item na tabela.")
                return
            item_id = int(sel_item[0])
            try:
                qtd_dev = int(ent_qtd_dev.get().strip())
            except ValueError:
                messagebox.showerror("Erro", "Quantidade invalida.")
                return

            item_info = self.cursor.execute(
                "SELECT ai.quantidade, ai.quantidade_devolvida, ai.patrimonio_id, ai.estado_saida "
                "FROM aluguer_patrimonio_itens ai WHERE ai.id=?", (item_id,)).fetchone()

            qtd_total = item_info[0]
            qtd_ja_dev = item_info[1]
            pat_id = item_info[2]
            restante = qtd_total - qtd_ja_dev

            if qtd_dev < 0 or qtd_dev > restante:
                messagebox.showerror("Erro", f"Quantidade invalida. Maximo: {restante}")
                return

            estado_dev = cb_estado_dev.get()
            agora = datetime.now().strftime("%d/%m/%Y %H:%M")

            # Atualizar item
            nova_qtd_dev = qtd_ja_dev + qtd_dev
            self.cursor.execute("UPDATE aluguer_patrimonio_itens SET quantidade_devolvida=?, estado_devolucao=?, observacoes=? WHERE id=?",
                               (nova_qtd_dev, estado_dev, ent_obs_dev.get().strip(), item_id))

            # Atualizar patrimonio
            nova_sit = self._calcular_situacao_patrimonio(pat_id)
            self.cursor.execute("UPDATE patrimonio SET quantidade_alugada = quantidade_alugada - ?, "
                               "quantidade_disponivel = quantidade_disponivel + ?, situacao_operacional=?, updated_at=? WHERE id=?",
                               (qtd_dev, qtd_dev, nova_sit, agora, pat_id))

            if estado_dev == "DANIFICADO":
                self.cursor.execute("UPDATE patrimonio SET estado_fisico='DANIFICADO', quantidade_manutencao = quantidade_manutencao + ?, "
                                   "quantidade_disponivel = quantidade_disponivel - ? WHERE id=?", (qtd_dev, qtd_dev, pat_id))
                nova_sit2 = self._calcular_situacao_patrimonio(pat_id)
                self.cursor.execute("UPDATE patrimonio SET situacao_operacional=? WHERE id=?", (nova_sit2, pat_id))
                self._registrar_historico(pat_id, "DEVOLUCAO_DANIFICADO", None, "DANIFICADO", None, nova_sit2, None, qtd_dev, f"Devolucao {numero} - {qtd_dev} danificadas")
            else:
                self._registrar_historico(pat_id, "DEVOLUCAO", None, estado_dev, None, nova_sit, None, qtd_dev, f"Devolucao {numero} - {qtd_dev} unidades")

            self.conn.commit()

            # Verificar se todos os itens foram devolvidos
            todos_dev = self.cursor.execute(
                "SELECT SUM(quantidade), SUM(quantidade_devolvida) FROM aluguer_patrimonio_itens WHERE aluguer_id=?", (alug_id,)).fetchone()
            if todos_dev[0] == todos_dev[1]:
                self.cursor.execute("UPDATE aluguer_patrimonio SET estado='DEVOLVIDO', data_devolucao_efetiva=?, updated_at=? WHERE id=?",
                                   (agora.split(" ")[0], agora, alug_id))
                self.conn.commit()

            messagebox.showinfo("Sucesso", f"{qtd_dev} unidades devolvidas com sucesso!")
            janela.destroy()
            self._atualizar_tabela_alugueres()
            self._atualizar_tabela_patrimonio()

        self._criar_botao(frame_dev, "Registar Devolucao", _registrar_devolucao, bg="#10B981")
        self._criar_botao(frame_dev, "Fechar", janela.destroy, bg="#64748B")

    def _abrir_pagamento_aluguer(self):
        """Abre janela de pagamento"""
        sel = self.tv_alug.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um aluguer na tabela.")
            return
        vals = self.tv_alug.item(sel[0], "values")
        numero = vals[0]
        pendente = float(str(vals[6]).replace(",", ""))

        if pendente <= 0:
            messagebox.showinfo("Info", "Este aluguer ja esta totalmente pago.")
            return

        janela = tk.Toplevel(self.root)
        janela.title(f"Pagamento - {numero}")
        janela.geometry("400x250")
        janela.configure(bg=self.COR_BG)
        janela.transient(self.root)
        janela.grab_set()

        tk.Label(janela, text=f"Pagamento - {numero}", font=("Helvetica", 14, "bold"),
                 fg="#FFFFFF", bg=self.COR_BG).pack(pady=10)
        tk.Label(janela, text=f"Pendente: {pendente:,.0f} KZ", font=("Helvetica", 11),
                 fg="#F59E0B", bg=self.COR_BG).pack()

        frame = tk.Frame(janela, bg=self.COR_CARD, padx=15, pady=15)
        frame.pack(fill="x", padx=15, pady=10)

        tk.Label(frame, text="Valor (KZ):", fg=self.COR_TEXTO, bg=self.COR_CARD).grid(row=0, column=0, padx=5)
        ent_valor = tk.Entry(frame, font=("Helvetica", 11), bg=self.COR_BG, fg="white", bd=0, width=15)
        ent_valor.grid(row=0, column=1, padx=5, ipady=3)

        tk.Label(frame, text="Forma:", fg=self.COR_TEXTO, bg=self.COR_CARD).grid(row=1, column=0, padx=5, pady=(5,0))
        cb_forma = ttk.Combobox(frame, values=["Dinheiro", "Transferencia", "Multicaixa", "Outro"], state="readonly", font=("Helvetica", 10), width=13)
        cb_forma.grid(row=1, column=1, padx=5, pady=(5,0))
        cb_forma.set("Dinheiro")

        def _efetuar_pagamento():
            try:
                valor = float(ent_valor.get().strip())
            except ValueError:
                messagebox.showerror("Erro", "Valor invalido.")
                return
            if valor <= 0:
                messagebox.showwarning("Aviso", "Valor deve ser > 0.")
                return
            if valor > pendente:
                if not messagebox.askyesno("Aviso", f"Valor ({valor:,.0f}) excede o pendente ({pendente:,.0f}). Confirmar?"):
                    return

            agora = datetime.now().strftime("%d/%m/%Y %H:%M")
            alug_id = self.cursor.execute("SELECT id FROM aluguer_patrimonio WHERE numero_aluguer=?", (numero,)).fetchone()[0]

            # Registar pagamento
            self.cursor.execute(
                "INSERT INTO aluguer_patrimonio_pagamentos (aluguer_id, valor, data_pagamento, forma_pagamento, responsavel, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (alug_id, valor, agora.split(" ")[0], cb_forma.get(), self.utilizador_atual, agora)
            )

            # Atualizar aluguer
            novo_pago = float(vals[5]) + valor
            novo_pendente = max(0, float(str(vals[4]).replace(",", "")) - novo_pago)
            self.cursor.execute("UPDATE aluguer_patrimonio SET valor_pago=?, valor_pendente=?, updated_at=? WHERE id=?",
                               (novo_pago, novo_pendente, agora, alug_id))

            # Entrada financeira
            self.cursor.execute(
                "INSERT INTO financeiro (reserva_id, tipo, descricao, valor, data, data_criacao) "
                "VALUES (NULL, 'ENTRADA', ?, ?, ?, ?)",
                (f"Pagamento Aluguer {numero} - {vals[1]}", valor, agora.split(" ")[0], agora.split(" ")[0])
            )

            self.conn.commit()
            messagebox.showinfo("Sucesso", f"Pagamento de {valor:,.0f} KZ registado!")
            janela.destroy()
            self._atualizar_tabela_alugueres()

        self._criar_botao(frame, "Efetuar Pagamento", _efetuar_pagamento, bg="#10B981")

    def _cancelar_aluguer(self):
        """Cancela um aluguer"""
        sel = self.tv_alug.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um aluguer na tabela.")
            return
        vals = self.tv_alug.item(sel[0], "values")
        numero = vals[0]
        estado = vals[7]
        if estado in ("DEVOLVIDO", "CANCELADO"):
            messagebox.showwarning("Aviso", f"Aluguer {numero} ja esta {estado}.")
            return
        if not messagebox.askyesno("Confirmar", f"Cancelar aluguer {numero}?"):
            return

        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        alug_id = self.cursor.execute("SELECT id FROM aluguer_patrimonio WHERE numero_aluguer=?", (numero,)).fetchone()[0]

        # Devolver quantidades
        for pat_id, qtd in self.cursor.execute(
            "SELECT patrimonio_id, quantidade FROM aluguer_patrimonio_itens WHERE aluguer_id=?", (alug_id,)):
            nova_sit = self._calcular_situacao_patrimonio(pat_id)
            self.cursor.execute("UPDATE patrimonio SET quantidade_disponivel = quantidade_disponivel + ?, "
                               "quantidade_alugada = quantidade_alugada - ?, situacao_operacional = ?, "
                               "updated_at = ? WHERE id = ?",
                               (qtd, qtd, nova_sit, agora, pat_id))
            self._registrar_historico(pat_id, "CANCELAMENTO_ALUGUER", None, None, None, nova_sit, None, qtd, f"Cancelamento {numero}")

        self.cursor.execute("UPDATE aluguer_patrimonio SET estado='CANCELADO', updated_at=? WHERE id=?", (agora, alug_id))
        self.conn.commit()
        messagebox.showinfo("Sucesso", f"Aluguer {numero} cancelado.")
        self._atualizar_tabela_alugueres()
        self._atualizar_tabela_patrimonio()

    # --- DASHBOARD PATRIMONIO ---
    def mostrar_aba_dashboard_patrimonio(self):
        """Dashboard de visao geral do patrimonio"""
        self.limpar_conteudo()

        tk.Label(self.conteudo, text="Dashboard Patrimonio",
                 font=("Helvetica", 18, "bold"), fg="#FFFFFF", bg=self.COR_BG).pack(anchor="w", pady=(0, 15))

        # KPI Cards
        frame_kpis = tk.Frame(self.conteudo, bg=self.COR_BG)
        frame_kpis.pack(fill="x", pady=(0, 10))

        # Dados do patrimonio
        tot = self.cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE ativo=1").fetchone()[0]
        disp = self.cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE ativo=1 AND situacao_operacional='DISPONIVEL'").fetchone()[0]
        alug = self.cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE ativo=1 AND situacao_operacional='ALUGADO'").fetchone()[0]
        manut = self.cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE ativo=1 AND situacao_operacional='EM_MANUTENCAO'").fetchone()[0]
        danif = self.cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE ativo=1 AND estado_fisico='DANIFICADO'").fetchone()[0]
        indisp = self.cursor.execute("SELECT COUNT(*) FROM patrimonio WHERE ativo=1 AND situacao_operacional='INDISPONIVEL'").fetchone()[0]

        # Dados de alugueres
        alug_ativos = self.cursor.execute("SELECT COUNT(*) FROM aluguer_patrimonio WHERE estado='ATIVO'").fetchone()[0]
        alug_atrasados = self.cursor.execute(
            "SELECT COUNT(*) FROM aluguer_patrimonio WHERE estado='ATIVO' AND data_devolucao_prevista < ?",
            (datetime.now().strftime("%d/%m/%Y"),)).fetchone()[0]
        alug_pendentes = self.cursor.execute("SELECT COUNT(*) FROM aluguer_patrimonio WHERE estado='DEVOLUCAO_PENDENTE'").fetchone()[0]
        valor_pendente = self.cursor.execute("SELECT SUM(valor_pendente) FROM aluguer_patrimonio WHERE estado IN ('ATIVO','DEVOLUCAO_PENDENTE','ATRASADO')").fetchone()[0] or 0
        receita_aluguer = self.cursor.execute("SELECT SUM(valor_pago) FROM aluguer_patrimonio").fetchone()[0] or 0

        kpis = [
            ("Total Patrimonios", str(tot), "#A855F7"),
            ("Disponiveis", str(disp), "#10B981"),
            ("Alugados", str(alug), "#F59E0B"),
            ("Em Manutencao", str(manut), "#3B82F6"),
            ("Danificados", str(danif), "#EF4444"),
            ("Indisponiveis", str(indisp), "#64748B"),
        ]

        for i, (titulo, valor, cor) in enumerate(kpis):
            card = tk.Frame(frame_kpis, bg=self.COR_CARD, highlightbackground=cor, highlightthickness=2, padx=12, pady=10)
            card.grid(row=0, column=i, sticky="nsew", padx=4, ipady=3)
            frame_kpis.grid_columnconfigure(i, weight=1)
            tk.Label(card, text=titulo, font=("Helvetica", 8), fg=self.COR_TEXTO, bg=self.COR_CARD).pack(anchor="w")
            tk.Label(card, text=valor, font=("Helvetica", 16, "bold"), fg=cor, bg=self.COR_CARD).pack(anchor="w", pady=(3, 0))

        # KPIs de alugueres
        frame_kpis2 = tk.Frame(self.conteudo, bg=self.COR_BG)
        frame_kpis2.pack(fill="x", pady=(0, 10))

        kpis2 = [
            ("Alugueres Ativos", str(alug_ativos), "#F59E0B"),
            ("Alugueres Atrasados", str(alug_atrasados), "#EF4444"),
            ("Devolucoes Pendentes", str(alug_pendentes), "#3B82F6"),
            ("Valor Pendente", f"{valor_pendente:,.0f} KZ", "#F59E0B"),
            ("Receita de Alugueres", f"{receita_aluguer:,.0f} KZ", "#10B981"),
        ]

        for i, (titulo, valor, cor) in enumerate(kpis2):
            card = tk.Frame(frame_kpis2, bg=self.COR_CARD, highlightbackground=cor, highlightthickness=2, padx=12, pady=10)
            card.grid(row=0, column=i, sticky="nsew", padx=4, ipady=3)
            frame_kpis2.grid_columnconfigure(i, weight=1)
            tk.Label(card, text=titulo, font=("Helvetica", 8), fg=self.COR_TEXTO, bg=self.COR_CARD).pack(anchor="w")
            tk.Label(card, text=valor, font=("Helvetica", 13, "bold"), fg=cor, bg=self.COR_CARD).pack(anchor="w", pady=(3, 0))

        # Tabela: Alugueres Atrasados
        if alug_atrasados > 0:
            tk.Label(self.conteudo, text="Alugueres Atrasados", font=("Helvetica", 12, "bold"),
                     fg="#EF4444", bg=self.COR_BG).pack(anchor="w", pady=(10, 5))
            tv_atrasados = ttk.Treeview(self.conteudo, columns=("Nr", "Cliente", "Prev. Devolucao", "Valor Pendente"), show="headings", height=4)
            for col in tv_atrasados["columns"]:
                tv_atrasados.heading(col, text=col)
                tv_atrasados.column(col, anchor="center", width=120)
            tv_atrasados.pack(fill="x")
            for r in self.cursor.execute(
                "SELECT numero_aluguer, cliente, data_devolucao_prevista, valor_pendente "
                "FROM aluguer_patrimonio WHERE estado='ATIVO' AND data_devolucao_prevista < ? "
                "ORDER BY data_devolucao_prevista",
                (datetime.now().strftime("%d/%m/%Y"),)):
                tv_atrasados.insert("", "end", values=r)

        # Tabela: Patrimonio com estado critico
        tk.Label(self.conteudo, text="Patrimonio com Problemas", font=("Helvetica", 12, "bold"),
                 fg="#F59E0B", bg=self.COR_BG).pack(anchor="w", pady=(15, 5))
        tv_problemas = ttk.Treeview(self.conteudo, columns=("Codigo", "Nome", "Estado", "Situacao", "Qtd Manutencao"), show="headings", height=4)
        for col in tv_problemas["columns"]:
            tv_problemas.heading(col, text=col)
            tv_problemas.column(col, anchor="center", width=100)
        tv_problemas.column("Nome", width=150)
        tv_problemas.pack(fill="x")
        for r in self.cursor.execute(
            "SELECT codigo, nome, estado_fisico, situacao_operacional, quantidade_manutencao "
            "FROM patrimonio WHERE ativo=1 AND (estado_fisico IN ('DANIFICADO','INSERVIVEL') OR "
            "situacao_operacional='EM_MANUTENCAO') ORDER BY nome"):
            tv_problemas.insert("", "end", values=r)

    def emitir_relatorio_mensal_txt(self):
        """Filtra o livro de caixa e exporta o balanco contabilistico detalhado da empresa"""
        try:
            mes_ano = self.ent_mes_ano.get()
        except AttributeError:
            messagebox.showwarning("Aviso", "Use a aba Dashboard para filtrar e exportar relatorios.")
            return
        if not mes_ano or "/" not in mes_ano:
            messagebox.showerror("Erro", "Formato invalido. Use MM/AAAA.")
            return
            
        self.cursor.execute("SELECT tipo, descricao, valor, data FROM financeiro")
        todas_transacoes = self.cursor.fetchall()
        transacoes_filtradas = [t for t in todas_transacoes if t[3].endswith(mes_ano)]
        
        if not transacoes_filtradas:
            messagebox.showwarning("Aviso", f"Nenhum registo de caixa encontrado para {mes_ano}.")
            return
            
        t_entradas = sum(t[2] for t in transacoes_filtradas if t[0] == 'ENTRADA')
        t_saidas = sum(t[2] for t in transacoes_filtradas if t[0] == 'SAIDA')
        balanco = t_entradas - t_saidas
        
        nome_ficheiro = f"relatorio_mensal_{mes_ano.replace('/', '_')}.txt"
        with open(nome_ficheiro, "w", encoding="utf-8") as f:
            f.write("==================================================\n")
            f.write(f"  BALANÇO FINANCEIRO MENSAL - PAIXÃO E FILHOS    \n")
            f.write(f"                  MÊS: {mes_ano}                  \n")
            f.write("==================================================\n")
            f.write(f"Total de Entradas: {t_entradas:,.2f} KZ\n")
            f.write(f"Total de Saídas:   {t_saidas:,.2f} KZ\n")
            f.write(f"Balanço Final:     {balanco:,.2f} KZ\n")
            f.write("==================================================\n")
            
        messagebox.showinfo("Sucesso", f"Relatório mensal exportado como: '{nome_ficheiro}'")

# =====================================================================
# BLOCO DE EXECUÇÃO PRINCIPAL DO PROGRAMA
# =====================================================================
if __name__ == "__main__":
    # Inicializa a janela principal do Tkinter
    root = tk.Tk()
    
    # Instancia a classe do sistema aplicando o novo layout
    app = SistemaSalaoPaixaoFilhos(root)
    
    # Inicia o loop para capturar cliques e comandos das utilizadoras
    root.mainloop()
