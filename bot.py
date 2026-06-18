import discord
import json
import random
import asyncio
from datetime import date
from discord.ext import commands
from discord.ui import View

TOKEN = "TOKEN_DO_DISCORD"
PREFIX = "!"
DONO_ID = 1277801876523454547
CANAL_BOT = 1513290347973967962

# Banco de perguntas fixas do quiz.
# "r" é a letra da resposta correta (A, B, C ou D).
# "dif" pode ser "fácil", "médio" ou "difícil" (isso define o quanto vale a pergunta).
PERGUNTAS = [
    {
        "p": 'Qual é a capital do Brasil?',
        "ops": ['A) São Paulo', 'B) Rio de Janeiro', 'C) Brasília', 'D) Salvador'],
        "r": 'C',
        "dif": 'fácil',
        "categoria": 'geografia'
    },
    {
        "p": 'Quantos lados tem um hexágono?',
        "ops": ['A) 5', 'B) 6', 'C) 7', 'D) 8'],
        "r": 'B',
        "dif": 'fácil',
        "categoria": 'matematica'
    },
    {
        "p": "Quem escreveu 'Dom Casmurro'?",
        "ops": ['A) Machado de Assis', 'B) José de Alencar', 'C) Clarice Lispector', 'D) Graciliano Ramos'],
        "r": 'A',
        "dif": 'médio',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Qual planeta é conhecido como o 'Planeta Vermelho'?",
        "ops": ['A) Júpiter', 'B) Vênus', 'C) Marte', 'D) Saturno'],
        "r": 'C',
        "dif": 'fácil',
        "categoria": 'ciencias'
    },
    {
        "p": 'Em que ano começou a Segunda Guerra Mundial?',
        "ops": ['A) 1935', 'B) 1939', 'C) 1941', 'D) 1945'],
        "r": 'B',
        "dif": 'médio',
        "categoria": 'historia'
    },
    {
        "p": 'Qual é o maior oceano do mundo?',
        "ops": ['A) Atlântico', 'B) Índico', 'C) Ártico', 'D) Pacífico'],
        "r": 'D',
        "dif": 'fácil',
        "categoria": 'geografia'
    },
    {
        "p": 'Quantos ossos tem o corpo humano adulto?',
        "ops": ['A) 186', 'B) 206', 'C) 226', 'D) 246'],
        "r": 'B',
        "dif": 'difícil',
        "categoria": 'ciencias'
    },
    {
        "p": "Qual desses elementos químicos tem o símbolo 'Au'?",
        "ops": ['A) Prata', 'B) Alumínio', 'C) Ouro', 'D) Argônio'],
        "r": 'C',
        "dif": 'médio',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quantos dias tem uma semana?',
        "ops": ['A) 5', 'B) 6', 'C) 7', 'D) 8'],
        "r": 'C',
        "dif": 'fácil',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Qual é a cor do céu em um dia claro?',
        "ops": ['A) Verde', 'B) Azul', 'C) Vermelho', 'D) Roxo'],
        "r": 'B',
        "dif": 'fácil',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quantas patas tem um cachorro?',
        "ops": ['A) 2', 'B) 4', 'C) 6', 'D) 8'],
        "r": 'B',
        "dif": 'fácil',
        "categoria": 'ciencias'
    },
    {
        "p": "Qual é o animal conhecido como 'rei da selva'?",
        "ops": ['A) Tigre', 'B) Leão', 'C) Elefante', 'D) Urso'],
        "r": 'B',
        "dif": 'fácil',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quantos meses tem um ano?',
        "ops": ['A) 10', 'B) 11', 'C) 12', 'D) 13'],
        "r": 'C',
        "dif": 'fácil',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Qual cor é formada pela mistura de azul e amarelo?',
        "ops": ['A) Verde', 'B) Roxo', 'C) Laranja', 'D) Rosa'],
        "r": 'A',
        "dif": 'fácil',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quantos dedos tem uma mão humana?',
        "ops": ['A) 4', 'B) 5', 'C) 6', 'D) 7'],
        "r": 'B',
        "dif": 'fácil',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Qual é o maior planeta do sistema solar?',
        "ops": ['A) Terra', 'B) Marte', 'C) Júpiter', 'D) Vênus'],
        "r": 'C',
        "dif": 'fácil',
        "categoria": 'ciencias'
    },
    {
        "p": 'Em que continente está o Brasil?',
        "ops": ['A) África', 'B) Ásia', 'C) América do Sul', 'D) Europa'],
        "r": 'C',
        "dif": 'fácil',
        "categoria": 'geografia'
    },
    {
        "p": "Qual é o oposto de 'quente'?",
        "ops": ['A) Frio', 'B) Seco', 'C) Molhado', 'D) Claro'],
        "r": 'A',
        "dif": 'fácil',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Quantos lados tem um triângulo?',
        "ops": ['A) 2', 'B) 3', 'C) 4', 'D) 5'],
        "r": 'B',
        "dif": 'fácil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual desses é uma fruta?',
        "ops": ['A) Cenoura', 'B) Batata', 'C) Maçã', 'D) Alface'],
        "r": 'C',
        "dif": 'fácil',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Quantas horas tem um dia?',
        "ops": ['A) 12', 'B) 20', 'C) 24', 'D) 30'],
        "r": 'C',
        "dif": 'fácil',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Qual é a capital da França?',
        "ops": ['A) Londres', 'B) Paris', 'C) Madrid', 'D) Roma'],
        "r": 'B',
        "dif": 'fácil',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual desses animais sabe voar?',
        "ops": ['A) Cachorro', 'B) Gato', 'C) Pássaro', 'D) Peixe'],
        "r": 'C',
        "dif": 'fácil',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é o nome do menor osso do corpo humano?',
        "ops": ['A) Estribo', 'B) Fêmur', 'C) Tíbia', 'D) Rádio'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Em que ano foi fundada a Organização das Nações Unidas (ONU)?',
        "ops": ['A) 1942', 'B) 1945', 'C) 1948', 'D) 1950'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Qual é a velocidade aproximada da luz no vácuo?',
        "ops": ['A) 150.000 km/s', 'B) 300.000 km/s', 'C) 450.000 km/s', 'D) 600.000 km/s'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quem foi o primeiro imperador do Brasil?',
        "ops": ['A) Dom Pedro I', 'B) Dom Pedro II', 'C) Dom João VI', 'D) Marechal Deodoro'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Qual tratado encerrou oficialmente a Primeira Guerra Mundial?',
        "ops": ['A) Tratado de Versalhes', 'B) Tratado de Paris', 'C) Tratado de Roma', 'D) Tratado de Tordesilhas'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Qual é o elemento químico mais abundante no universo?',
        "ops": ['A) Oxigênio', 'B) Carbono', 'C) Hidrogênio', 'D) Hélio'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Em que ano o ser humano pisou na Lua pela primeira vez?',
        "ops": ['A) 1965', 'B) 1969', 'C) 1972', 'D) 1975'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": "Qual filósofo escreveu a obra 'O Príncipe'?",
        "ops": ['A) Maquiavel', 'B) Sócrates', 'C) Aristóteles', 'D) Platão'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Qual é a capital da Mongólia?',
        "ops": ['A) Ulan Bator', 'B) Astana', 'C) Bishkek', 'D) Tashkent'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o nome do processo de divisão celular que forma os gametas (células reprodutivas)?',
        "ops": ['A) Mitose', 'B) Meiose', 'C) Fagocitose', 'D) Osmose'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": "Quem pintou a obra 'A Noite Estrelada'?",
        "ops": ['A) Pablo Picasso', 'B) Vincent van Gogh', 'C) Claude Monet', 'D) Salvador Dalí'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Qual é a unidade de medida da resistência elétrica?',
        "ops": ['A) Volt', 'B) Watt', 'C) Ampère', 'D) Ohm'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Em que ano caiu o Muro de Berlim?',
        "ops": ['A) 1985', 'B) 1989', 'C) 1991', 'D) 1993'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Qual foi o primeiro satélite artificial lançado ao espaço?',
        "ops": ['A) Sputnik 1', 'B) Apollo 11', 'C) Voyager 1', 'D) Explorer 1'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Quem é considerado o pai da genética moderna por seus estudos com ervilhas?',
        "ops": ['A) Charles Darwin', 'B) Gregor Mendel', 'C) Louis Pasteur', 'D) Isaac Newton'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
]

CARGOS_LOJA = {
    "soldado": 1513239906246332638,
    "guerreiro": 1513240476960948396,
    "assassino": 1513240751100919949,
    "elite": 1513241133529039040,
    "lenda": 1513241599490920628,
}

LOJA = {
    "soldado":  {"nome": "🗡️ Soldado", "preco": 500, "cargo": "soldado"},
    "guerreiro": {"nome": "⚔️ Guerreiro", "preco": 1500, "cargo": "guerreiro"},
    "assassino": {"nome": "🏹 Assassino", "preco": 3000, "cargo": "assassino"},
    "elite":    {"nome": "👑 Elite da Irmandade", "preco": 6000, "cargo": "elite"},
    "lenda":    {"nome": "🌟 Lenda da Irmandade", "preco": 12000, "cargo": "lenda"},
}

ITENS = {
    "pocao_tempo": {"nome": "⏳ Poção do Tempo", "preco": 300, "desc": "Zera todos os seus cooldowns de minigames na hora"},
    "escudo": {"nome": "🛡️ Escudo Anti-Roubo", "preco": 400, "desc": "Bloqueia a próxima tentativa de roubo contra você"},
    "amuleto": {"nome": "🍀 Amuleto da Sorte", "preco": 500, "desc": "Dobra o ganho da próxima aposta vencedora"},
}

PRECO_BILHETE = 100

def get_loteria(dados):
    if "_loteria" not in dados:
        dados["_loteria"] = {"bilhetes": {}, "pote": 0}
    return dados["_loteria"]

PATENTES = [
    {"nome": "🧢 Pobre", "minimo": 10000},
    {"nome": "💵 Rico", "minimo": 50000},
    {"nome": "💎 Milionário", "minimo": 100000},
    {"nome": "🏦 Bilionário", "minimo": 500000},
]

COOLDOWNS = {
    "pescar": 30,
    "cacar": 45,
    "minerar": 60,
    "roubar": 60,
}

LIMITE_DIARIO = 3

MISSOES_POOL = [
    {"acao": "pescar", "meta": 2, "desc": "🎣 Pescar 2 vezes", "recompensa": 100},
    {"acao": "cacar", "meta": 2, "desc": "🏹 Caçar 2 vezes", "recompensa": 100},
    {"acao": "minerar", "meta": 2, "desc": "⛏️ Minerar 2 vezes", "recompensa": 100},
    {"acao": "roubar", "meta": 1, "desc": "🦹 Tentar roubar alguém 1 vez", "recompensa": 80},
    {"acao": "apostar", "meta": 1, "desc": "🎰 Fazer 1 aposta", "recompensa": 80},
    {"acao": "quiz", "meta": 1, "desc": "🧠 Responder 1 pergunta do quiz", "recompensa": 80},
    {"acao": "quiz_acerto", "meta": 1, "desc": "✅ Acertar 1 pergunta do quiz", "recompensa": 120},
    {"acao": "lutar_vencer", "meta": 1, "desc": "⚔️ Vencer 1 luta", "recompensa": 150},
]

CONQUISTAS = [
    {"id": "primeira_vitoria", "nome": "🥊 Primeira Vitória", "desc": "Venceu sua primeira luta", "recompensa": 100,
     "check": lambda u: u.get("wins", 0) >= 1},
    {"id": "veterano", "nome": "⚔️ Veterano de Guerra", "desc": "Venceu 10 lutas", "recompensa": 500,
     "check": lambda u: u.get("wins", 0) >= 10},
    {"id": "sequencia_7", "nome": "🔥 Disciplinado", "desc": "Coletou o diário por 7 dias seguidos", "recompensa": 300,
     "check": lambda u: u.get("streak_diario", 0) >= 7},
    {"id": "milionario_ach", "nome": "💎 Milionário", "desc": "Acumulou 100.000 fichas no total", "recompensa": 1000,
     "check": lambda u: u.get("total", 0) >= 100000},
    {"id": "bilionario_ach", "nome": "🏦 Bilionário", "desc": "Acumulou 500.000 fichas no total", "recompensa": 3000,
     "check": lambda u: u.get("total", 0) >= 500000},
    {"id": "mestre_quiz", "nome": "🧠 Mestre do Quiz", "desc": "Acertou 20 perguntas do quiz", "recompensa": 400,
     "check": lambda u: u.get("estatisticas", {}).get("quiz_acertos", 0) >= 20},
    {"id": "ladrao_pro", "nome": "🦹 Ladrão Profissional", "desc": "Realizou 10 roubos bem-sucedidos", "recompensa": 400,
     "check": lambda u: u.get("estatisticas", {}).get("roubos_sucesso", 0) >= 10},
    {"id": "pescador_lendario", "nome": "🎣 Pescador Lendário", "desc": "Pescou 50 vezes no total", "recompensa": 300,
     "check": lambda u: u.get("estatisticas", {}).get("pescar_total", 0) >= 50},
]

GOLPES_ESPECIAIS = [
    "🔥 Hadouken", "⚡ Shoryuken", "🌀 Tatsumaki",
    "💨 Sonic Boom", "⚡ Flash Kick", "🔥 Shinku Hadouken",
    "💀 Messatsu Gou Hadou", "🔥 Shoryu Reppa", "✨ Kikosho",
    "🔥 Yoga Inferno", "⚡ Shinryuken", "💥 Metsu Hadouken",
    "🔥 Metsu Shoryuken", "👹 Raging Demon", "💫 Omega Drive"
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
lutas = {}
quizzes_ativos = {}

CATEGORIA_NOMES = {
    "geografia": "🌍 Geografia",
    "historia": "📜 História",
    "ciencias": "🔬 Ciências",
    "cultura_geral": "🎭 Cultura Geral",
    "matematica": "🔢 Matemática",
}

async def gerar_pergunta(categoria=None):
    # Sorteia uma pergunta pré-programada da lista PERGUNTAS, opcionalmente filtrando por categoria.
    if categoria:
        filtradas = [p for p in PERGUNTAS if p.get("categoria") == categoria]
        if not filtradas:
            return None
        return random.choice(filtradas)
    return random.choice(PERGUNTAS)

def carregar():
    try:
        with open("dados.json", "r") as f:
            return json.load(f)
    except:
        return {}

def salvar(dados):
    with open("dados.json", "w") as f:
        json.dump(dados, f)

def get_usuario(dados, uid):
    uid = str(uid)
    hoje = str(date.today())
    if uid not in dados:
        dados[uid] = {
            "fichas": 0, "total": 0, "cooldowns": {}, "patente": -1,
            "wins": 0, "minigames": {"data": hoje, "pescar": 0, "cacar": 0, "minerar": 0, "roubar": 0},
            "inventario": {}, "protegido": False, "sorte_ativa": False,
            "ultimo_diario": None, "streak_diario": 0,
            "estatisticas": {"pescar_total": 0, "cacar_total": 0, "minerar_total": 0, "roubos_sucesso": 0, "quiz_acertos": 0},
            "conquistas": [],
            "missoes": {"data": None, "lista": []},
            "semana_id": None, "semana_total_inicio": 0
        }
    u = dados[uid]
    if "wins" not in u:
        u["wins"] = 0
    if "total" not in u:
        u["total"] = u["fichas"]
    if "minigames" not in u:
        u["minigames"] = {"data": hoje, "pescar": 0, "cacar": 0, "minerar": 0, "roubar": 0}
    if u["minigames"]["data"] != hoje:
        u["minigames"] = {"data": hoje, "pescar": 0, "cacar": 0, "minerar": 0, "roubar": 0}
    if "inventario" not in u:
        u["inventario"] = {}
    if "protegido" not in u:
        u["protegido"] = False
    if "sorte_ativa" not in u:
        u["sorte_ativa"] = False
    if "ultimo_diario" not in u:
        u["ultimo_diario"] = None
    if "streak_diario" not in u:
        u["streak_diario"] = 0
    if "estatisticas" not in u:
        u["estatisticas"] = {"pescar_total": 0, "cacar_total": 0, "minerar_total": 0, "roubos_sucesso": 0, "quiz_acertos": 0}
    if "conquistas" not in u:
        u["conquistas"] = []
    if "missoes" not in u:
        u["missoes"] = {"data": None, "lista": []}
    semana_id = semana_atual()
    if u.get("semana_id") != semana_id:
        u["semana_id"] = semana_id
        u["semana_total_inicio"] = u.get("total", 0)
    return u

def semana_atual():
    iso = date.today().isocalendar()
    return f"{iso[0]}-W{iso[1]}"

def garantir_missoes(u):
    hoje = str(date.today())
    if u.get("missoes", {}).get("data") != hoje:
        escolhidas = random.sample(MISSOES_POOL, 3)
        u["missoes"] = {
            "data": hoje,
            "lista": [dict(m, progresso=0, completa=False) for m in escolhidas]
        }
    return u["missoes"]

def registrar_missao(u, acao):
    """Atualiza o progresso de missões pra essa ação. Retorna mensagens de missões concluídas agora."""
    missoes = garantir_missoes(u)
    mensagens = []
    for m in missoes["lista"]:
        if m["acao"] == acao and not m["completa"]:
            m["progresso"] += 1
            if m["progresso"] >= m["meta"]:
                m["completa"] = True
                u["fichas"] += m["recompensa"]
                u["total"] += m["recompensa"]
                mensagens.append(f"🎯 Missão concluída: **{m['desc']}** (+{m['recompensa']} fichas)")
    return mensagens

def verificar_conquistas(u):
    """Verifica se alguma conquista nova foi desbloqueada. Retorna lista das conquistas novas."""
    if "conquistas" not in u:
        u["conquistas"] = []
    novas = []
    for c in CONQUISTAS:
        if c["id"] not in u["conquistas"] and c["check"](u):
            u["conquistas"].append(c["id"])
            u["fichas"] += c["recompensa"]
            u["total"] += c["recompensa"]
            novas.append(c)
    return novas

def check_limite(u, acao):
    return u["minigames"].get(acao, 0) < LIMITE_DIARIO

def add_minigame(u, acao):
    u["minigames"][acao] = u["minigames"].get(acao, 0) + 1

def get_cooldown(u, acao):
    patente = u.get("patente", -1)
    reducao = (patente + 1) if patente >= 0 else 0
    return max(5, COOLDOWNS[acao] - reducao)

async def verificar_patente(ctx, u, dados):
    total = u.get("total", 0)
    patente_atual = u.get("patente", -1)
    nova_patente = patente_atual
    for i, p in enumerate(PATENTES):
        if total >= p["minimo"] and i > patente_atual:
            nova_patente = i
    if nova_patente > patente_atual:
        u["patente"] = nova_patente
        salvar(dados)
        patente = PATENTES[nova_patente]
        await ctx.send(f"🎉 {ctx.author.mention} alcançou a patente **{patente['nome']}**! Cooldowns reduzidos!")

def get_luta(user_id, canal_id):
    for lid, l in lutas.items():
        if user_id in lid and l["canal"] == canal_id:
            return lid, l
    return None, None

async def fim_de_luta(canal, luta_id, vencedor_id, perdedor_id):
    dados = carregar()
    u_vencedor = get_usuario(dados, vencedor_id)
    u_perdedor = get_usuario(dados, perdedor_id)
    premio = int(u_perdedor["fichas"] * 0.1)
    u_vencedor["fichas"] += premio
    u_vencedor["wins"] = u_vencedor.get("wins", 0) + 1
    u_perdedor["fichas"] = max(0, u_perdedor["fichas"] - premio)
    mensagens_extra = registrar_missao(u_vencedor, "lutar_vencer")
    novas_conquistas = verificar_conquistas(u_vencedor)
    salvar(dados)
    nome_vencedor = lutas[luta_id]["jogadores"][vencedor_id]["nome"]
    del lutas[luta_id]
    await canal.send(f"🏆 **{nome_vencedor} venceu a luta** e roubou **{premio} fichas!**")
    for m in mensagens_extra:
        await canal.send(m)
    for c in novas_conquistas:
        await canal.send(f"🏆 **Conquista desbloqueada por {nome_vencedor}:** {c['nome']} (+{c['recompensa']} fichas)")

class LutaView(View):
    def __init__(self, luta_id, turno_id):
        super().__init__(timeout=120)
        self.luta_id = luta_id
        self.turno_id = turno_id

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.turno_id:
            await interaction.response.send_message("❌ Não é seu turno!", ephemeral=True)
            return False
        return True

    async def processar_acao(self, interaction, acao):
        luta = lutas.get(self.luta_id)
        if not luta:
            await interaction.response.send_message("❌ Luta não encontrada!", ephemeral=True)
            return

        jogadores = luta["jogadores"]
        atacante_id = interaction.user.id
        adversario_id = [i for i in self.luta_id if i != atacante_id][0]
        atacante = jogadores[atacante_id]
        defensor = jogadores[adversario_id]
        luta["rodada"] += 1
        msg = ""
        multiplicador = 2 if atacante.get("dano2x", False) else 1

        if acao == "atacar":
            if defensor["esquivando"]:
                defensor["esquivando"] = False
                if random.random() < 0.6:
                    dano = random.randint(10, 25) * multiplicador
                    atacante["hp"] = max(0, atacante["hp"] - dano)
                    msg = f"🌀 **{defensor['nome']}** esquivou e contra-atacou causando **{dano} de dano!**\n❤️ HP de {atacante['nome']}: **{atacante['hp']}/250**"
                    if atacante["hp"] <= 0:
                        self.stop()
                        await interaction.response.edit_message(content=msg, view=None)
                        await fim_de_luta(interaction.channel, self.luta_id, adversario_id, atacante_id)
                        return
                else:
                    msg = f"🌀 **{defensor['nome']}** tentou esquivar mas falhou!\n"

            if defensor["contra"]:
                defensor["contra"] = False
                dano1 = random.randint(10, 25) * multiplicador
                dano2 = random.randint(10, 25) * multiplicador
                total = dano1 + dano2
                atacante["hp"] = max(0, atacante["hp"] - total)
                msg = f"🔄 **{defensor['nome']}** usou CONTRA-ATAQUE! Causou **{total} de dano!**\n❤️ HP de {atacante['nome']}: **{atacante['hp']}/250**"
                if atacante["hp"] <= 0:
                    self.stop()
                    await interaction.response.edit_message(content=msg, view=None)
                    await fim_de_luta(interaction.channel, self.luta_id, adversario_id, atacante_id)
                    return
            else:
                critico = random.random() < 0.2
                dano = (random.randint(30, 50) if critico else random.randint(10, 25)) * multiplicador
                prefixo = "💥 **CRÍTICO!**" if critico else "⚔️"
                if defensor["defendendo"]:
                    dano = dano // 2
                    defensor["defendendo"] = False
                    msg += f"🛡️ {defensor['nome']} estava defendendo! Dano reduzido!\n"
                defensor["hp"] = max(0, defensor["hp"] - dano)
                msg += f"{prefixo} {atacante['nome']} causou **{dano} de dano!**\n❤️ HP de {defensor['nome']}: **{defensor['hp']}/250**"

        elif acao == "especial":
            cd = atacante.get("especial_cooldown", 0)
            if luta["rodada"] <= cd:
                resto = cd - luta["rodada"] + 1
                await interaction.response.send_message(f"❌ Especial disponível em **{resto} rodadas!**", ephemeral=True)
                return
            golpe = random.choice(GOLPES_ESPECIAIS)
            dano = random.randint(60, 100) * multiplicador
            atacante["especial_cooldown"] = luta["rodada"] + 5
            if defensor["defendendo"]:
                dano = dano // 2
                defensor["defendendo"] = False
                msg += f"⚠️ {defensor['nome']} estava defendendo! Dano reduzido!\n"
            defensor["hp"] = max(0, defensor["hp"] - dano)
            msg = f"💫 **{golpe}!** {atacante['nome']} causou **{dano} de dano DEVASTADOR!**\n❤️ HP de {defensor['nome']}: **{defensor['hp']}/250**"

        elif acao == "contra":
            atacante["contra"] = True
            msg = f"🔄 **{atacante['nome']}** está preparando CONTRA-ATAQUE!"

        elif acao == "esquivar":
            atacante["esquivando"] = True
            msg = f"🌀 **{atacante['nome']}** está em posição de esquiva!"

        elif acao == "defender":
            atacante["defendendo"] = True
            msg = f"🛡️ **{atacante['nome']}** assumiu posição de defesa!"

        elif acao == "desistir":
            self.stop()
            await interaction.response.edit_message(content=f"🏳️ **{atacante['nome']}** desistiu!", view=None)
            await fim_de_luta(interaction.channel, self.luta_id, adversario_id, atacante_id)
            return

        if acao in ["atacar", "especial"] and defensor["hp"] <= 0:
            self.stop()
            await interaction.response.edit_message(content=msg, view=None)
            await fim_de_luta(interaction.channel, self.luta_id, atacante_id, adversario_id)
            return

        luta["turno"] = adversario_id
        novo_view = LutaView(self.luta_id, adversario_id)
        msg += f"\n➡️ Turno de **{defensor['nome']}**!"
        await interaction.response.edit_message(content=msg, view=novo_view)

    @discord.ui.button(label="⚔️ Atacar", style=discord.ButtonStyle.primary)
    async def btn_atacar(self, interaction, button):
        await self.processar_acao(interaction, "atacar")

    @discord.ui.button(label="💫 Especial", style=discord.ButtonStyle.danger)
    async def btn_especial(self, interaction, button):
        await self.processar_acao(interaction, "especial")

    @discord.ui.button(label="🔄 Contra", style=discord.ButtonStyle.secondary)
    async def btn_contra(self, interaction, button):
        await self.processar_acao(interaction, "contra")

    @discord.ui.button(label="🌀 Esquivar", style=discord.ButtonStyle.secondary)
    async def btn_esquivar(self, interaction, button):
        await self.processar_acao(interaction, "esquivar")

    @discord.ui.button(label="🛡️ Defender", style=discord.ButtonStyle.secondary)
    async def btn_defender(self, interaction, button):
        await self.processar_acao(interaction, "defender")

    @discord.ui.button(label="🏳️ Desistir", style=discord.ButtonStyle.danger)
    async def btn_desistir(self, interaction, button):
        await self.processar_acao(interaction, "desistir")

class QuizView(View):
    def __init__(self, user_id, pergunta, fichas_ganho, fichas_perda):
        super().__init__(timeout=20)
        self.user_id = user_id
        self.pergunta = pergunta
        self.fichas_ganho = fichas_ganho
        self.fichas_perda = fichas_perda
        self.respondido = False

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esse quiz não é seu!", ephemeral=True)
            return False
        return True

    async def responder(self, interaction, escolha):
        if self.respondido:
            return
        self.respondido = True
        self.stop()
        dados = carregar()
        u = get_usuario(dados, self.user_id)
        correta = self.pergunta["r"]
        mensagens_extra = registrar_missao(u, "quiz")
        novas_conquistas = []
        if escolha == correta:
            u["fichas"] += self.fichas_ganho
            u["total"] += self.fichas_ganho
            u["estatisticas"]["quiz_acertos"] = u["estatisticas"].get("quiz_acertos", 0) + 1
            mensagens_extra += registrar_missao(u, "quiz_acerto")
            novas_conquistas = verificar_conquistas(u)
            salvar(dados)
            await interaction.response.edit_message(
                content=f"✅ **Correto!** A resposta era **{correta}**!\n💰 Você ganhou **{self.fichas_ganho} fichas!**",
                view=None
            )
        else:
            u["fichas"] = max(0, u["fichas"] - self.fichas_perda)
            salvar(dados)
            await interaction.response.edit_message(
                content=f"❌ **Errado!** A resposta correta era **{correta}**!\n💸 Você perdeu **{self.fichas_perda} fichas!**",
                view=None
            )
        for m in mensagens_extra:
            await interaction.followup.send(m)
        for c in novas_conquistas:
            await interaction.followup.send(f"🏆 **Conquista desbloqueada:** {c['nome']} (+{c['recompensa']} fichas)")
        if self.user_id in quizzes_ativos:
            del quizzes_ativos[self.user_id]

    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def btn_a(self, interaction, button):
        await self.responder(interaction, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def btn_b(self, interaction, button):
        await self.responder(interaction, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def btn_c(self, interaction, button):
        await self.responder(interaction, "C")

    @discord.ui.button(label="D", style=discord.ButtonStyle.primary)
    async def btn_d(self, interaction, button):
        await self.responder(interaction, "D")

    async def on_timeout(self):
        if not self.respondido:
            self.respondido = True
            perda_tempo = 50  # perda fixa quando o tempo esgota, independente da dificuldade
            dados = carregar()
            u = get_usuario(dados, self.user_id)
            u["fichas"] = max(0, u["fichas"] - perda_tempo)
            salvar(dados)
            if self.user_id in quizzes_ativos:
                msg = quizzes_ativos[self.user_id]
                del quizzes_ativos[self.user_id]
                try:
                    await msg.edit(
                        content=f"⏰ **Tempo esgotado!** A resposta era **{self.pergunta['r']}**!\n💸 Você perdeu **{perda_tempo} fichas** por não responder a tempo!",
                        view=None
                    )
                except:
                    pass

@bot.event
async def on_ready():
    print(f"Bot ligado como {bot.user}")

@bot.check
async def apenas_canal_bot(ctx):
    if ctx.channel.id != CANAL_BOT:
        await ctx.send(f"❌ Use os comandos no canal <#{CANAL_BOT}>!")
        return False
    return True

@bot.command(name="pescar")
async def pescar(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if not check_limite(u, "pescar"):
        await ctx.send(f"❌ {ctx.author.mention} você já pescou **3/3** vezes hoje! Volte amanhã.")
        return
    cd = u["cooldowns"].get("pescar", 0)
    agora = asyncio.get_event_loop().time()
    if agora < cd:
        await ctx.send(f"🎣 Aguarde **{int(cd - agora)}s** para pescar de novo!")
        return
    ganho = random.randint(50, 200)
    u["fichas"] += ganho
    u["total"] += ganho
    add_minigame(u, "pescar")
    u["estatisticas"]["pescar_total"] = u["estatisticas"].get("pescar_total", 0) + 1
    mensagens_extra = registrar_missao(u, "pescar")
    novas_conquistas = verificar_conquistas(u)
    u["cooldowns"]["pescar"] = agora + get_cooldown(u, "pescar")
    restantes = LIMITE_DIARIO - u["minigames"]["pescar"]
    salvar(dados)
    await ctx.send(f"🎣 {ctx.author.mention} pescou e ganhou **{ganho} fichas!** 💰 (**{restantes}/3** restantes hoje)")
    await verificar_patente(ctx, u, dados)
    for m in mensagens_extra:
        await ctx.send(m)
    for c in novas_conquistas:
        await ctx.send(f"🏆 **Conquista desbloqueada:** {c['nome']} (+{c['recompensa']} fichas)")

@bot.command(name="caçar")
async def cacar(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if not check_limite(u, "cacar"):
        await ctx.send(f"❌ {ctx.author.mention} você já caçou **3/3** vezes hoje! Volte amanhã.")
        return
    cd = u["cooldowns"].get("cacar", 0)
    agora = asyncio.get_event_loop().time()
    if agora < cd:
        await ctx.send(f"🏹 Aguarde **{int(cd - agora)}s** para caçar de novo!")
        return
    ganho = random.randint(80, 300)
    u["fichas"] += ganho
    u["total"] += ganho
    add_minigame(u, "cacar")
    u["estatisticas"]["cacar_total"] = u["estatisticas"].get("cacar_total", 0) + 1
    mensagens_extra = registrar_missao(u, "cacar")
    novas_conquistas = verificar_conquistas(u)
    u["cooldowns"]["cacar"] = agora + get_cooldown(u, "cacar")
    restantes = LIMITE_DIARIO - u["minigames"]["cacar"]
    salvar(dados)
    await ctx.send(f"🏹 {ctx.author.mention} caçou e ganhou **{ganho} fichas!** 💰 (**{restantes}/3** restantes hoje)")
    await verificar_patente(ctx, u, dados)
    for m in mensagens_extra:
        await ctx.send(m)
    for c in novas_conquistas:
        await ctx.send(f"🏆 **Conquista desbloqueada:** {c['nome']} (+{c['recompensa']} fichas)")

@bot.command(name="minerar")
async def minerar(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if not check_limite(u, "minerar"):
        await ctx.send(f"❌ {ctx.author.mention} você já minerou **3/3** vezes hoje! Volte amanhã.")
        return
    cd = u["cooldowns"].get("minerar", 0)
    agora = asyncio.get_event_loop().time()
    if agora < cd:
        await ctx.send(f"⛏️ Aguarde **{int(cd - agora)}s** para minerar de novo!")
        return
    ganho = random.randint(100, 400)
    u["fichas"] += ganho
    u["total"] += ganho
    add_minigame(u, "minerar")
    u["estatisticas"]["minerar_total"] = u["estatisticas"].get("minerar_total", 0) + 1
    mensagens_extra = registrar_missao(u, "minerar")
    novas_conquistas = verificar_conquistas(u)
    u["cooldowns"]["minerar"] = agora + get_cooldown(u, "minerar")
    restantes = LIMITE_DIARIO - u["minigames"]["minerar"]
    salvar(dados)
    await ctx.send(f"⛏️ {ctx.author.mention} minerou e ganhou **{ganho} fichas!** 💰 (**{restantes}/3** restantes hoje)")
    await verificar_patente(ctx, u, dados)
    for m in mensagens_extra:
        await ctx.send(m)
    for c in novas_conquistas:
        await ctx.send(f"🏆 **Conquista desbloqueada:** {c['nome']} (+{c['recompensa']} fichas)")

@bot.command(name="bilhete")
async def bilhete(ctx, quantidade: int = 1):
    if quantidade <= 0:
        await ctx.send("❌ A quantidade deve ser maior que zero!")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    custo = PRECO_BILHETE * quantidade
    if u["fichas"] < custo:
        await ctx.send(f"❌ Você precisa de **{custo} fichas** para comprar {quantidade} bilhete(s). Você tem **{u['fichas']}**.")
        return
    u["fichas"] -= custo
    loteria = get_loteria(dados)
    uid = str(ctx.author.id)
    loteria["bilhetes"][uid] = loteria["bilhetes"].get(uid, 0) + quantidade
    loteria["pote"] += custo
    salvar(dados)
    total_bilhetes = loteria["bilhetes"][uid]
    await ctx.send(f"🎫 {ctx.author.mention} comprou **{quantidade} bilhete(s)** da loteria por **{custo} fichas**! Você tem **{total_bilhetes}** bilhete(s) essa rodada.\n💰 Pote atual: **{loteria['pote']} fichas**")

@bot.command(name="loteria")
async def loteria_status(ctx):
    dados = carregar()
    loteria = get_loteria(dados)
    total_bilhetes = sum(loteria["bilhetes"].values())
    msg = f"""🎰 **Loteria Semanal**

🎫 Preço do bilhete: **{PRECO_BILHETE} fichas**
💰 Pote atual: **{loteria['pote']} fichas**
🎟️ Total de bilhetes vendidos: **{total_bilhetes}**

Compre com `!bilhete [quantidade]`!"""
    await ctx.send(msg)

@bot.command(name="apostar")
async def apostar(ctx, valor: int):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if valor < 50:
        await ctx.send("❌ Aposta mínima é de **50 fichas!**")
        return
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} fichas!**")
        return
    mensagens_extra = registrar_missao(u, "apostar")
    if random.random() > 0.5:
        ganho = valor
        bonus_msg = ""
        if u.get("sorte_ativa"):
            ganho *= 2
            u["sorte_ativa"] = False
            bonus_msg = " 🍀 **(Amuleto da Sorte dobrou o ganho!)**"
        u["fichas"] += ganho
        u["total"] += ganho
        await ctx.send(f"🎰 {ctx.author.mention} ganhou **{ganho} fichas!** 💰{bonus_msg}")
        await verificar_patente(ctx, u, dados)
    else:
        u["fichas"] -= valor
        await ctx.send(f"🎰 {ctx.author.mention} perdeu **{valor} fichas!** 😢")
    salvar(dados)
    for m in mensagens_extra:
        await ctx.send(m)

@bot.command(name="roubar")
async def roubar(ctx, membro: discord.Member):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if not check_limite(u, "roubar"):
        await ctx.send(f"❌ {ctx.author.mention} você já tentou roubar **3/3** vezes hoje! Volte amanhã.")
        return
    alvo = get_usuario(dados, membro.id)
    cd = u["cooldowns"].get("roubar", 0)
    agora = asyncio.get_event_loop().time()
    if agora < cd:
        await ctx.send(f"🦹 Aguarde **{int(cd - agora)}s** para roubar de novo!")
        return
    if alvo["fichas"] < 50:
        await ctx.send(f"❌ {membro.mention} não tem fichas suficientes!")
        return
    add_minigame(u, "roubar")
    restantes = LIMITE_DIARIO - u["minigames"]["roubar"]
    mensagens_extra = registrar_missao(u, "roubar")
    novas_conquistas = []
    if alvo.get("protegido"):
        alvo["protegido"] = False
        u["cooldowns"]["roubar"] = agora + get_cooldown(u, "roubar")
        salvar(dados)
        await ctx.send(f"🛡️ {membro.mention} estava protegido por um **Escudo Anti-Roubo** e bloqueou a tentativa de {ctx.author.mention}! (**{restantes}/3** restantes hoje)")
        for m in mensagens_extra:
            await ctx.send(m)
        return
    if random.random() > 0.5:
        ganho = random.randint(50, min(300, alvo["fichas"]))
        u["fichas"] += ganho
        u["total"] += ganho
        alvo["fichas"] -= ganho
        u["estatisticas"]["roubos_sucesso"] = u["estatisticas"].get("roubos_sucesso", 0) + 1
        novas_conquistas = verificar_conquistas(u)
        await ctx.send(f"🦹 {ctx.author.mention} roubou **{ganho} fichas** de {membro.mention}! (**{restantes}/3** restantes hoje)")
        await verificar_patente(ctx, u, dados)
    else:
        multa = random.randint(50, 150)
        u["fichas"] = max(0, u["fichas"] - multa)
        await ctx.send(f"🚔 {ctx.author.mention} foi pego e pagou **{multa} fichas** de multa! (**{restantes}/3** restantes hoje)")
    u["cooldowns"]["roubar"] = agora + get_cooldown(u, "roubar")
    salvar(dados)
    for m in mensagens_extra:
        await ctx.send(m)
    for c in novas_conquistas:
        await ctx.send(f"🏆 **Conquista desbloqueada:** {c['nome']} (+{c['recompensa']} fichas)")

@bot.command(name="diario")
async def diario(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    hoje = date.today()
    ultimo = u.get("ultimo_diario")
    if ultimo == str(hoje):
        await ctx.send(f"❌ {ctx.author.mention} você já coletou a recompensa diária hoje! Volte amanhã.")
        return
    streak = u.get("streak_diario", 0)
    if ultimo:
        dias_diff = (hoje - date.fromisoformat(ultimo)).days
        streak = streak + 1 if dias_diff == 1 else 1
    else:
        streak = 1
    bonus_streak = min(streak, 7) * 20
    recompensa = 100 + bonus_streak
    u["fichas"] += recompensa
    u["total"] += recompensa
    u["ultimo_diario"] = str(hoje)
    u["streak_diario"] = streak
    novas_conquistas = verificar_conquistas(u)
    salvar(dados)
    await ctx.send(f"📅 {ctx.author.mention} coletou a recompensa diária!\n💰 **+{recompensa} fichas** (sequência: **{streak} dia(s)**)")
    await verificar_patente(ctx, u, dados)
    for c in novas_conquistas:
        await ctx.send(f"🏆 **Conquista desbloqueada:** {c['nome']} (+{c['recompensa']} fichas)")

@bot.command(name="pagar")
async def pagar(ctx, membro: discord.Member, valor: int):
    if valor <= 0:
        await ctx.send("❌ O valor deve ser maior que zero!")
        return
    if membro.id == ctx.author.id:
        await ctx.send("❌ Você não pode pagar para si mesmo!")
        return
    if membro.bot:
        await ctx.send("❌ Você não pode pagar para um bot!")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} fichas!**")
        return
    destino = get_usuario(dados, membro.id)
    u["fichas"] -= valor
    destino["fichas"] += valor
    destino["total"] += valor
    salvar(dados)
    await ctx.send(f"💸 {ctx.author.mention} transferiu **{valor} fichas** para {membro.mention}!")
    await verificar_patente(ctx, destino, dados)

@bot.command(name="itens")
async def itens(ctx):
    msg = "🎁 **Loja de Itens**\n\n"
    for key, item in ITENS.items():
        msg += f"{item['nome']} → **{item['preco']} fichas**\n_{item['desc']}_\n`!comprar {key}`\n\n"
    msg += "Use `!usar [item]` para ativar um item do seu inventário."
    await ctx.send(msg)

@bot.command(name="usar")
async def usar(ctx, item: str):
    item = item.lower()
    if item not in ITENS:
        await ctx.send("❌ Item inválido! Use `!itens` para ver os itens disponíveis.")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if u["inventario"].get(item, 0) <= 0:
        await ctx.send(f"❌ Você não tem **{ITENS[item]['nome']}** no inventário! Compre com `!comprar {item}`.")
        return
    if item == "pocao_tempo":
        u["cooldowns"] = {}
        msg = "⏳ **Poção do Tempo** usada! Todos os seus cooldowns foram zerados."
    elif item == "escudo":
        if u.get("protegido"):
            await ctx.send("❌ Você já está protegido por um escudo ativo!")
            return
        u["protegido"] = True
        msg = "🛡️ **Escudo Anti-Roubo** ativado! A próxima tentativa de roubo contra você será bloqueada."
    elif item == "amuleto":
        if u.get("sorte_ativa"):
            await ctx.send("❌ Você já está com o Amuleto da Sorte ativo!")
            return
        u["sorte_ativa"] = True
        msg = "🍀 **Amuleto da Sorte** ativado! Sua próxima aposta vencedora terá o ganho dobrado."
    u["inventario"][item] -= 1
    salvar(dados)
    await ctx.send(f"{ctx.author.mention} {msg}")
@bot.command(name="quiz")
async def quiz(ctx, categoria: str = None):
    if ctx.author.id in quizzes_ativos:
        await ctx.send("❌ Você já tem um quiz ativo!")
        return
    if categoria:
        categoria = categoria.lower()
        if categoria not in CATEGORIA_NOMES:
            opcoes = ", ".join(f"`{k}`" for k in CATEGORIA_NOMES)
            await ctx.send(f"❌ Categoria inválida! Opções: {opcoes}")
            return
    await ctx.send("🧠 Gerando pergunta...")
    pergunta = await gerar_pergunta(categoria)
    if not pergunta:
        await ctx.send("❌ Erro ao gerar pergunta! Tente novamente.")
        return
    dif = pergunta.get("dif", "médio")
    if dif == "fácil":
        ganho, perda = 40, 30
        emoji = "🟢"
    elif dif == "médio":
        ganho, perda = 70, 50
        emoji = "🟡"
    elif dif == "difícil":
        ganho, perda = 120, 80
        emoji = "🔴"
    else:  # extremo
        ganho, perda = 300, 250
        emoji = "💀"
    nome_categoria = CATEGORIA_NOMES.get(pergunta.get("categoria"), "")
    ops = "\n".join(pergunta["ops"])
    msg_texto = f"""🧠 **QUIZ** {emoji} **{dif.upper()}** {f"| {nome_categoria}" if nome_categoria else ""}

**{pergunta['p']}**

{ops}

⏰ Você tem **20 segundos** para responder!
✅ Acerto: **+{ganho} fichas** | ❌ Erro: **-{perda} fichas**"""
    view = QuizView(ctx.author.id, pergunta, ganho, perda)
    msg = await ctx.send(msg_texto, view=view)
    quizzes_ativos[ctx.author.id] = msg

@bot.command(name="saldo")
async def saldo(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    patente = PATENTES[u["patente"]]["nome"] if u["patente"] >= 0 else "Sem patente"
    await ctx.send(f"💰 {ctx.author.mention} tem **{u['fichas']} fichas**\n🏅 Patente: **{patente}**\n📊 Total acumulado: **{u['total']} fichas**")

@bot.command(name="perfil")
async def perfil(ctx, membro: discord.Member = None):
    membro = membro or ctx.author
    dados = carregar()
    u = get_usuario(dados, membro.id)
    patente = PATENTES[u["patente"]]["nome"] if u["patente"] >= 0 else "Sem patente"
    mg = u["minigames"]
    msg = f"""👤 **Perfil de {membro.display_name}**

💰 Fichas: **{u['fichas']}**
📊 Total acumulado: **{u['total']}**
🏅 Patente: **{patente}**
🏆 Vitórias em lutas: **{u.get('wins', 0)}**
🏆 Conquistas: **{len(u.get('conquistas', []))}/{len(CONQUISTAS)}**

📅 **Tentativas hoje**
🎣 Pescar: **{mg.get('pescar', 0)}/3**
🏹 Caçar: **{mg.get('cacar', 0)}/3**
⛏️ Minerar: **{mg.get('minerar', 0)}/3**
🦹 Roubar: **{mg.get('roubar', 0)}/3**"""
    await ctx.send(msg)

@bot.command(name="inventario")
async def inventario(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    itens_possuidos = {k: v for k, v in u.get("inventario", {}).items() if v > 0}
    if not itens_possuidos:
        await ctx.send(f"🎒 {ctx.author.mention} seu inventário está vazio! Use `!itens` para ver o que comprar.")
        return
    msg = f"🎒 **Inventário de {ctx.author.display_name}**\n\n"
    for key, qtd in itens_possuidos.items():
        nome = ITENS.get(key, {}).get("nome", key)
        msg += f"{nome} — **x{qtd}** | `!usar {key}`\n"
    await ctx.send(msg)

@bot.command(name="missoes")
async def missoes_cmd(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    missoes = garantir_missoes(u)
    salvar(dados)
    msg = "🎯 **Missões de hoje**\n\n"
    for m in missoes["lista"]:
        status = "✅ Completa" if m["completa"] else f"{m['progresso']}/{m['meta']}"
        msg += f"{m['desc']} — **{status}** | recompensa: **{m['recompensa']} fichas**\n"
    await ctx.send(msg)

@bot.command(name="conquistas")
async def conquistas_cmd(ctx, membro: discord.Member = None):
    membro = membro or ctx.author
    dados = carregar()
    u = get_usuario(dados, membro.id)
    desbloqueadas = set(u.get("conquistas", []))
    msg = f"🏆 **Conquistas de {membro.display_name}** ({len(desbloqueadas)}/{len(CONQUISTAS)})\n\n"
    for c in CONQUISTAS:
        check = "✅" if c["id"] in desbloqueadas else "🔒"
        msg += f"{check} **{c['nome']}** — {c['desc']} _(+{c['recompensa']} fichas)_\n"
    await ctx.send(msg)

@bot.command(name="top")
async def top(ctx):
    dados = carregar()
    ranking = []
    for uid, u in dados.items():
        try:
            membro = ctx.guild.get_member(int(uid))
            if membro:
                ranking.append((membro.display_name, u.get("fichas", 0), u.get("wins", 0)))
        except:
            continue
    ranking.sort(key=lambda x: x[1], reverse=True)
    msg = "🏆 **Ranking da Irmandade**\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (nome, fichas, wins) in enumerate(ranking[:10]):
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        msg += f"{medal} {nome} — **{fichas} fichas** | {wins} wins\n"
    await ctx.send(msg)

@bot.command(name="topsemana")
async def topsemana(ctx):
    dados = carregar()
    ranking = []
    for uid in list(dados.keys()):
        try:
            membro = ctx.guild.get_member(int(uid))
            if not membro:
                continue
            u = get_usuario(dados, uid)
            ganho_semana = max(0, u.get("total", 0) - u.get("semana_total_inicio", 0))
            ranking.append((membro.display_name, ganho_semana))
        except:
            continue
    salvar(dados)
    ranking.sort(key=lambda x: x[1], reverse=True)
    msg = "📅 **Ranking Semanal** (fichas ganhas essa semana)\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (nome, ganho) in enumerate(ranking[:10]):
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        msg += f"{medal} {nome} — **{ganho} fichas ganhas**\n"
    msg += "\nA semana reseta automaticamente toda segunda-feira."
    await ctx.send(msg)

@bot.command(name="loja")
async def loja(ctx):
    msg = "🛒 **Loja de Cargos**\n\n"
    for key, item in LOJA.items():
        msg += f"{item['nome']} → **{item['preco']} fichas** | `!comprar {key}`\n"
    msg += "\n🎁 Veja também a `!itens` para itens consumíveis com efeitos especiais."
    await ctx.send(msg)

@bot.command(name="comprar")
async def comprar(ctx, item: str):
    item = item.lower()
    if item in ITENS:
        dados = carregar()
        u = get_usuario(dados, ctx.author.id)
        produto = ITENS[item]
        if u["fichas"] < produto["preco"]:
            await ctx.send(f"❌ Você precisa de **{produto['preco']} fichas!** Você tem **{u['fichas']}**.")
            return
        u["fichas"] -= produto["preco"]
        u["inventario"][item] = u["inventario"].get(item, 0) + 1
        salvar(dados)
        await ctx.send(f"✅ {ctx.author.mention} comprou **{produto['nome']}**! Use `!usar {item}` para ativar.")
        return
    if item not in LOJA:
        await ctx.send("❌ Item inválido! Use `!loja` ou `!itens` para ver as opções.")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    produto = LOJA[item]
    if u["fichas"] < produto["preco"]:
        await ctx.send(f"❌ Você precisa de **{produto['preco']} fichas!** Você tem **{u['fichas']}**.")
        return
    cargo_id = CARGOS_LOJA[produto["cargo"]]
    cargo = ctx.guild.get_role(cargo_id)
    if cargo is None:
        await ctx.send("❌ Erro ao encontrar o cargo! Avise o admin.")
        return
    if cargo in ctx.author.roles:
        await ctx.send(f"❌ Você já tem o cargo **{produto['nome']}**!")
        return
    try:
        await ctx.author.add_roles(cargo)
        u["fichas"] -= produto["preco"]
        salvar(dados)
        await ctx.send(f"✅ {ctx.author.mention} comprou **{produto['nome']}** e recebeu o cargo!")
    except discord.Forbidden:
        await ctx.send("❌ O bot não tem permissão para gerenciar cargos!")

@bot.command(name="lutar")
async def lutar(ctx, membro: discord.Member):
    if membro.id == ctx.author.id:
        await ctx.send("❌ Você não pode lutar contra si mesmo!")
        return
    luta_id = tuple(sorted([ctx.author.id, membro.id]))
    if luta_id in lutas:
        await ctx.send("❌ Já existe uma luta em andamento entre vocês!")
        return
    lutas[luta_id] = {
        "jogadores": {
            ctx.author.id: {"nome": ctx.author.display_name, "hp": 250, "defendendo": False, "contra": False, "esquivando": False, "especial_cooldown": 0, "dano2x": False},
            membro.id: {"nome": membro.display_name, "hp": 250, "defendendo": False, "contra": False, "esquivando": False, "especial_cooldown": 0, "dano2x": False}
        },
        "turno": ctx.author.id,
        "canal": ctx.channel.id,
        "rodada": 0
    }
    view = LutaView(luta_id, ctx.author.id)
    await ctx.send(
        f"⚔️ **{ctx.author.display_name}** VS **{membro.display_name}**\n"
        f"❤️ HP: **250/250** cada\n"
        f"➡️ Turno de **{ctx.author.display_name}**!",
        view=view
    )

@bot.command(name="ajuda")
async def ajuda(ctx):
    msg = """🤖 **Comandos do Tigrinho**

🎮 **Minigames** (3x por dia cada)
`!pescar` — Pesca e ganha fichas (30s)
`!caçar` — Caça e ganha fichas (45s)
`!minerar` — Minera e ganha fichas (60s)
`!apostar [valor]` — Aposta suas fichas (mín. 50)
`!roubar @pessoa` — Tenta roubar alguém (3x/dia)
`!quiz [categoria]` — Responda perguntas e ganhe fichas
`!diario` — Recompensa diária com bônus por sequência

🎯 **Progresso**
`!missoes` — Ver suas missões diárias
`!conquistas [@pessoa]` — Ver conquistas desbloqueadas
`!topsemana` — Ranking de quem mais ganhou fichas na semana

🎰 **Loteria Semanal**
`!bilhete [quantidade]` — Comprar bilhete(s) (100 fichas cada)
`!loteria` — Ver o pote atual e bilhetes vendidos

💰 **Economia**
`!saldo` — Ver suas fichas e patente
`!perfil [@pessoa]` — Ver perfil completo
`!inventario` — Ver seus itens guardados
`!top` — Ranking dos mais ricos
`!pagar @pessoa [valor]` — Transferir fichas para alguém
`!loja` — Ver a loja de cargos
`!comprar [item]` — Comprar um cargo ou item
`!itens` — Ver a loja de itens consumíveis
`!usar [item]` — Usar um item do seu inventário

🏅 **Patentes**
🧢 Pobre → 10.000 fichas
💵 Rico → 50.000 fichas
💎 Milionário → 100.000 fichas
🏦 Bilionário → 500.000 fichas

⚔️ **Lutas**
`!lutar @pessoa` — Desafiar alguém
Use os botões para lutar!"""
    categorias_str = ", ".join(f"`{k}`" for k in CATEGORIA_NOMES)
    msg += f"\n\n🧠 Categorias do quiz: {categorias_str}"
    await ctx.send(msg)

@bot.command(name="ego")
async def ego(ctx):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    await ctx.send("""```fix
╔════════════════════════════════╗
║      ⚙️  PAINEL DO EGO         ║
╚════════════════════════════════╝
+ 💰 ECONOMIA
+ !darfichas @p [v]  → Adicionar fichas
+ !tirfichas @p [v]  → Remover fichas
+ !setfichas @p [v]  → Definir fichas
+ !godmode @p        → 999999 fichas
+ !zerarfichas @p    → Zerar fichas
🎮 MINIGAMES
!resetlimite @p  → Resetar limites diários
!resetquiz       → Resetar quiz travado
- ⚔️ LUTA
- !dano2x @p      → Ativar dano 2x na luta
- !cancelluta @p  → Cancelar luta
📅 SEMANAL E LOTERIA
!premiarsemana    → Premia o top 1 semanal e reseta a semana
!sortearloteria   → Sorteia o vencedor da loteria e zera o pote
```""")

@bot.command(name="darfichas")
async def darfichas(ctx, membro: discord.Member, valor: int):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    dados = carregar()
    u = get_usuario(dados, membro.id)
    u["fichas"] += valor
    u["total"] += valor
    salvar(dados)
    await ctx.send(f"✅ **{valor} fichas** adicionadas para {membro.mention}!")
    await verificar_patente(ctx, u, dados)

@bot.command(name="tirfichas")
async def tirfichas(ctx, membro: discord.Member, valor: int):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    dados = carregar()
    u = get_usuario(dados, membro.id)
    u["fichas"] = max(0, u["fichas"] - valor)
    salvar(dados)
    await ctx.send(f"✅ **{valor} fichas** removidas de {membro.mention}!")

@bot.command(name="setfichas")
async def setfichas(ctx, membro: discord.Member, valor: int):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    dados = carregar()
    u = get_usuario(dados, membro.id)
    u["fichas"] = valor
    salvar(dados)
    await ctx.send(f"✅ Fichas de {membro.mention} definidas para **{valor}**!")

@bot.command(name="godmode")
async def godmode(ctx, membro: discord.Member):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    dados = carregar()
    u = get_usuario(dados, membro.id)
    u["fichas"] = 999999
    u["total"] = 999999
    salvar(dados)
    await ctx.send(f"✅ **GOD MODE** ativado para {membro.mention}! 999999 fichas!")
    await verificar_patente(ctx, u, dados)

@bot.command(name="zerarfichas")
async def zerarfichas(ctx, membro: discord.Member):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    dados = carregar()
    u = get_usuario(dados, membro.id)
    u["fichas"] = 0
    salvar(dados)
    await ctx.send(f"✅ Fichas de {membro.mention} zeradas!")

@bot.command(name="resetlimite")
async def resetlimite(ctx, membro: discord.Member):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    dados = carregar()
    u = get_usuario(dados, membro.id)
    hoje = str(date.today())
    u["minigames"] = {"data": hoje, "pescar": 0, "cacar": 0, "minerar": 0, "roubar": 0}
    salvar(dados)
    await ctx.send(f"✅ Limites diários de {membro.mention} resetados!")

@bot.command(name="resetquiz")
async def resetquiz(ctx):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    quizzes_ativos.clear()
    await ctx.send("✅ Todos os quizzes ativos foram resetados!")

@bot.command(name="premiarsemana")
async def premiarsemana(ctx):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    dados = carregar()
    ranking = []
    for uid in list(dados.keys()):
        try:
            membro = ctx.guild.get_member(int(uid))
            if not membro:
                continue
            u = get_usuario(dados, uid)
            ganho_semana = max(0, u.get("total", 0) - u.get("semana_total_inicio", 0))
            ranking.append((uid, membro, ganho_semana))
        except:
            continue
    if not ranking:
        await ctx.send("❌ Ninguém pra premiar ainda!")
        return
    ranking.sort(key=lambda x: x[2], reverse=True)
    uid_top, membro_top, ganho_top = ranking[0]
    premio = 1000
    u_top = get_usuario(dados, uid_top)
    u_top["fichas"] += premio
    u_top["total"] += premio
    nova_semana = semana_atual()
    for uid in dados:
        if uid == uid_top or "fichas" in dados[uid]:
            dados[uid]["semana_id"] = nova_semana
            dados[uid]["semana_total_inicio"] = dados[uid].get("total", 0)
    salvar(dados)
    await ctx.send(f"🏆 **{membro_top.display_name}** venceu o ranking semanal com **{ganho_top} fichas ganhas** e recebeu **{premio} fichas** de prêmio!\n📅 Uma nova semana de ranking começou para todos!")

@bot.command(name="sortearloteria")
async def sortearloteria(ctx):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    dados = carregar()
    loteria = get_loteria(dados)
    if not loteria["bilhetes"]:
        await ctx.send("❌ Nenhum bilhete foi vendido ainda!")
        return
    pool = []
    for uid, qtd in loteria["bilhetes"].items():
        pool.extend([uid] * qtd)
    vencedor_id = random.choice(pool)
    premio = loteria["pote"]
    u_vencedor = get_usuario(dados, vencedor_id)
    u_vencedor["fichas"] += premio
    u_vencedor["total"] += premio
    membro = ctx.guild.get_member(int(vencedor_id))
    nome = membro.display_name if membro else f"<@{vencedor_id}>"
    dados["_loteria"] = {"bilhetes": {}, "pote": 0}
    salvar(dados)
    await ctx.send(f"🎉🎰 **{nome}** ganhou a loteria semanal e levou **{premio} fichas**! Uma nova rodada começou.")

@bot.command(name="dano2x")
async def dano2x(ctx, membro: discord.Member):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    for luta_id, luta in lutas.items():
        if membro.id in luta_id:
            luta["jogadores"][membro.id]["dano2x"] = True
            await ctx.send(f"✅ **Dano 2x** ativado para {membro.mention} na luta!")
            return
    await ctx.send(f"❌ {membro.mention} não está em nenhuma luta!")

@bot.command(name="cancelluta")
async def cancelluta(ctx, membro: discord.Member):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    for luta_id in list(lutas.keys()):
        if membro.id in luta_id:
            del lutas[luta_id]
            await ctx.send(f"✅ Luta de {membro.mention} cancelada!")
            return
    await ctx.send(f"❌ {membro.mention} não está em nenhuma luta!")

bot.run(TOKEN)
