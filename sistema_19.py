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
