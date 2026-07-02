import discord
from discord import app_commands
from discord.ext import tasks
from datetime import datetime, timedelta
from collections import defaultdict, deque
import random
import re
import unicodedata
import asyncio
import sqlite3
import json
import os
import aiohttp
from difflib import SequenceMatcher

# ============================================================
#   █████╗ ███████╗ ██████╗ ██╗███████╗
#  ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝
#  ███████║█████╗  ██║  ███╗██║███████╗
#  ██╔══██║██╔══╝  ██║   ██║██║╚════██║
#  ██║  ██║███████╗╚██████╔╝██║███████║
#  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝
#          Aegis — Bot de Proteção
#                  by Gon
# ============================================================

TOKEN              = "SEU_TOKEN_AQUI"
LOG_CHANNEL_ID     = None
STAFF_ROLE_ID      = None
QUARENTENA_ROLE_ID = None
HONEYPOT_CHANNEL_ID = None   # ID do canal honeypot (invisivel pra membros normais)
WEBHOOK_EXTERNO     = None   # URL do webhook backup externo para logs criticos
VPN_API_KEY         = None   # chave da vpnapi.io (gratis em vpnapi.io)
AUTO_ROLE_ID       = None   # cargo dado automaticamente após verificação

COR_CLEAN = 0x2ECC71   # verde mint — info/ok
COR_RED   = 0xE74C3C   # vermelho escuro — perigo/ban
COR_DIM   = 0x1ABC9C   # verde água — neutro/log
COR_WARN  = 0xF39C12   # laranja — aviso/warning

intents = discord.Intents.all()
client  = discord.Client(intents=intents)
tree    = app_commands.CommandTree(client)

config = {
    # proteções
    "antiraid"        : True,
    "antispam"        : True,
    "antiphishing"    : True,
    "anti_zalgo"      : True,
    "anti_invite"     : True,
    "anti_repeated"   : True,
    "anti_nuke"       : True,
    "anti_alt"        : True,
    "log_edits"       : True,
    "log_deletes"     : True,
    "silencioso"      : False,
    "shadow_mute"     : False,
    # modos
    "lockdown"        : False,
    "lockdown_mode"   : "hard",   # soft | medium | hard
    "emergencia"      : False,
    "quarentena"      : False,
    "captcha"         : False,
    "ai_mode"         : True,
    # threat level: normal | warning | critical
    "threat_level"    : "normal",
    # limites
    "quarentena_tempo": 10,
    "max_joins"       : 5,
    "join_window"     : 10,
    "max_messages"    : 8,
    "msg_window"      : 6,
    "max_mentions"    : 5,
    "max_channel_ops" : 3,
    "channel_op_window": 10,
    "max_mass_ban"    : 3,
    "mass_ban_window" : 10,
    "reset_infracoes_dias": 14,
    "aviso_janela_min": 10,
    # listas
    "whitelist"         : set(),
    "banned_words_leve" : [],
    "banned_words_grave": [],
    "canais_livres"     : set(),
    "shadow_muted"      : set(),
    # stats globais
    "raid_score"      : 0,
    "total_raids"     : 0,
    "total_bans"      : 0,
    "total_warns"     : 0,
    "historico"       : [],
    # stats diários (resetam meia-noite UTC)
    "daily_joins"     : 0,
    "daily_raids"     : 0,
    "daily_warns"     : 0,
    "daily_date"      : datetime.utcnow().date().isoformat(),
    # perfis de config salvos
    "perfis"          : {},
}

DB_PATH = "aegis.db"

# trackers
join_tracker        = deque()
msg_tracker         = defaultdict(lambda: deque(maxlen=100))
repeated_tracker    = defaultdict(list)
infra_tracker       = defaultdict(int)
reputacao           = defaultdict(int)    # score de reputação (+/-)
comportamento       = defaultdict(list)   # histórico de ações por usuário
raid_log            = []
channel_del_tracker = []
channel_cre_tracker = []
ban_tracker         = defaultdict(list)
quarentena_members  = {}
captcha_pendente    = {}
backup_data         = {"roles": [], "channels": [], "timestamp": None}

# aviso antes de punir: uid -> {motivo_tipo: datetime do ultimo aviso}
aviso_recente       = defaultdict(dict)
# data da ultima infracao de cada usuario, pra resetar ficha com o tempo
ultima_infracao     = defaultdict(lambda: None)

# rastrear nomes anteriores para detectar imitação
nomes_anteriores    = defaultdict(list)
# rastrear horários de entrada para detectar alts
entrada_horarios    = []   # [(datetime, member_id)]

# joins por minuto (sliding window 60s) para /security
joins_por_minuto    = deque()

# raid pattern fingerprint — historico de raids pra comparacao
raid_fingerprints   = []   # lista de dicts {hora, quantidade, conta_nova_pct}

# message similarity — historico recente por uid pra calcular ratio
similarity_tracker  = defaultdict(lambda: deque(maxlen=10))

# auto-nuke recovery — flag de restauracao em andamento
nuke_recovery_ativo = False


# ============================================================
#  SQLITE — PERSISTÊNCIA
# ============================================================

def _db():
    """Retorna uma conexão com row_factory=sqlite3.Row."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def db_init():
    """Cria as tabelas se não existirem."""
    with _db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS config_kv (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS usuarios (
            uid             INTEGER PRIMARY KEY,
            reputacao       INTEGER DEFAULT 0,
            infracoes       INTEGER DEFAULT 0,
            ultima_infracao TEXT
        );
        CREATE TABLE IF NOT EXISTS punicoes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            uid       INTEGER,
            nome      TEXT,
            tipo      TEXT,
            motivo    TEXT,
            ts        TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS alertas (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo  TEXT,
            dado  TEXT,
            ts    TEXT DEFAULT (datetime('now'))
        );
        """)

def db_save():
    """Persiste config, whitelist, banned words, reputação e infrações."""
    serializavel = {}
    for k, v in config.items():
        if k in ("historico", "perfis"):
            serializavel[k] = json.dumps(v, default=str)
        elif isinstance(v, set):
            serializavel[k] = json.dumps(list(v))
        elif isinstance(v, (bool, int, float, str, list)):
            serializavel[k] = json.dumps(v)
        # ignora tipos não serializáveis direto

    with _db() as conn:
        conn.executemany(
            "INSERT OR REPLACE INTO config_kv (key, value) VALUES (?, ?)",
            [(k, v) for k, v in serializavel.items()]
        )
        conn.executemany(
            """INSERT INTO usuarios (uid, reputacao, infracoes, ultima_infracao)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(uid) DO UPDATE SET
                 reputacao=excluded.reputacao,
                 infracoes=excluded.infracoes,
                 ultima_infracao=excluded.ultima_infracao""",
            [
                (uid, reputacao[uid], infra_tracker[uid],
                 ultima_infracao[uid].isoformat() if ultima_infracao[uid] else None)
                for uid in set(list(reputacao.keys()) + list(infra_tracker.keys()))
            ]
        )

def db_load():
    """Carrega config e usuários do banco."""
    global config
    with _db() as conn:
        rows = conn.execute("SELECT key, value FROM config_kv").fetchall()
    for row in rows:
        k, v = row["key"], row["value"]
        try:
            parsed = json.loads(v)
        except Exception:
            continue
        # restaura sets
        if k in ("whitelist", "shadow_muted", "canais_livres"):
            config[k] = set(parsed)
        elif k in config:
            config[k] = parsed

    with _db() as conn:
        rows = conn.execute("SELECT * FROM usuarios").fetchall()
    for row in rows:
        uid = row["uid"]
        reputacao[uid]    = row["reputacao"]
        infra_tracker[uid] = row["infracoes"]
        if row["ultima_infracao"]:
            ultima_infracao[uid] = datetime.fromisoformat(row["ultima_infracao"])

def db_log_punicao(uid: int, nome: str, tipo: str, motivo: str):
    with _db() as conn:
        conn.execute(
            "INSERT INTO punicoes (uid, nome, tipo, motivo) VALUES (?, ?, ?, ?)",
            (uid, nome, tipo, motivo)
        )

def db_log_alerta(tipo: str, dado: str):
    with _db() as conn:
        conn.execute("INSERT INTO alertas (tipo, dado) VALUES (?, ?)", (tipo, dado))


# ============================================================
#  FEATURE 1 — HONEYPOT
# ============================================================

async def checar_honeypot(message: discord.Message) -> bool:
    """Retorna True se a mensagem veio do canal honeypot e baniu o autor."""
    if not HONEYPOT_CHANNEL_ID: return False
    if message.channel.id != HONEYPOT_CHANNEL_ID: return False
    try:
        await message.author.ban(reason="[aegis] honeypot triggered — auto-ban")
        db_log_alerta("honeypot", str(message.author))
        await _log_t(message.guild,
            f"```\n[aegis@server ~]$ honeypot --trigger\n"
            f"> uid    : {message.author.id}\n"
            f"> user   : {message.author}\n"
            f"> action : banned\n```", COR_RED)
    except Exception: pass
    return True


# ============================================================
#  FEATURE 2 — VPN / PROXY CHECK
# ============================================================

async def checar_vpn(member: discord.Member) -> bool:
    """
    Checa VPN/proxy via vpnapi.io.
    Sem key: 100 req/dia gratis.
    Com key (VPN_API_KEY): 1000 req/dia.
    Discord nao expoe IP — usa o IP do audit log se disponivel,
    senao faz check por padrao de conta (fallback).
    """
    try:
        # tenta pegar IP real via audit log
        ip = None
        async for entry in member.guild.audit_logs(
            action=discord.AuditLogAction.member_update, limit=5
        ):
            if hasattr(entry, "ip_address"):
                ip = entry.ip_address
                break

        if ip:
            url = f"https://vpnapi.io/api/{ip}"
            if VPN_API_KEY:
                url += f"?key={VPN_API_KEY}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as r:
                    if r.status != 200: return False
                    data = await r.json()
                    sec = data.get("security", {})
                    return sec.get("vpn") or sec.get("proxy") or sec.get("tor") or sec.get("relay")

        # fallback: conta nova + sem avatar = alto risco, trata como suspeito
        idade = (datetime.utcnow() - member.created_at.replace(tzinfo=None)).days
        return idade < 7 and member.avatar is None

    except Exception:
        return False


# ============================================================
#  FEATURE 3 — MESSAGE SIMILARITY SCORING
# ============================================================

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def checar_similarity(uid: int, content: str) -> bool:
    """
    Compara a mensagem atual com as ultimas 10 do usuario.
    Se 3+ tiverem ratio > 0.85, e spam disfarçado.
    """
    historico = similarity_tracker[uid]
    hits = sum(1 for msg in historico if similarity(content, msg) > 0.85)
    historico.append(content)
    return hits >= 3


# ============================================================
#  FEATURE 4 — RAID PATTERN FINGERPRINT
# ============================================================

def salvar_fingerprint():
    """Salva o padrao do raid atual pra comparacao futura."""
    agora = datetime.utcnow()
    pct_novas = 0
    for _, mid in entrada_horarios[-20:]:
        guild = next((g for g in client.guilds), None)
        if guild:
            m = guild.get_member(mid)
            if m and (agora - m.created_at.replace(tzinfo=None)).days < 30:
                pct_novas += 1
    fingerprint = {
        "hora"       : agora.hour,
        "quantidade" : len(join_tracker),
        "pct_nova"   : pct_novas,
        "ts"         : agora.isoformat(),
    }
    raid_fingerprints.append(fingerprint)
    if len(raid_fingerprints) > 50:
        raid_fingerprints.pop(0)

def parece_raid_por_padrao() -> bool:
    """
    Compara o padrao de joins atual com fingerprints de raids anteriores.
    Se bater em 2+ raids passados, eleva ameaca antes de atingir o limite.
    """
    if len(raid_fingerprints) < 2: return False
    agora = datetime.utcnow()
    joins_agora = len(join_tracker)
    hora_agora  = agora.hour
    hits = 0
    for fp in raid_fingerprints[-20:]:
        if (abs(fp["hora"] - hora_agora) <= 2 and
            abs(fp["quantidade"] - joins_agora) <= 3):
            hits += 1
    return hits >= 2


# ============================================================
#  FEATURE 5 — AUTO-NUKE RECOVERY
# ============================================================

async def auto_nuke_recovery(guild: discord.Guild):
    """
    Detectou nuke (multiplos canais deletados em sequencia)?
    Restaura do backup automaticamente, sem precisar de comando.
    """
    global nuke_recovery_ativo
    if nuke_recovery_ativo: return
    if not backup_data["channels"]: return
    nuke_recovery_ativo = True
    await _log_t(guild,
        "```\n[aegis@server ~]$ nuke-recovery --auto\n"
        "> channels deleted threshold hit\n"
        "> restoring from last backup...\n```", COR_RED)
    restaurados = 0
    for ch_data in backup_data["channels"]:
        if guild.get_channel(ch_data["id"]): continue
        try:
            cat = guild.get_channel(ch_data.get("category_id"))
            await guild.create_text_channel(
                name=ch_data["name"],
                topic=ch_data.get("topic", ""),
                category=cat,
                reason="[aegis] auto-nuke-recovery"
            )
            restaurados += 1
        except Exception: pass
    await _log_t(guild,
        f"```\n[aegis@server ~]$ nuke-recovery --done\n"
        f"> restored : {restaurados} channels\n```", COR_CLEAN)
    nuke_recovery_ativo = False


# ============================================================
#  FEATURE 6 — LOG EXTERNO (WEBHOOK BACKUP)
# ============================================================

async def log_externo(evento: str, cor: int = None, detalhes: str = ""):
    """Envia log critico para webhook externo. Fallback se o servidor for nukado."""
    if not WEBHOOK_EXTERNO: return
    payload = {
        "embeds": [{
            "description": f"```\n{evento}\n{detalhes}\n```",
            "color": cor or 0xE74C3C,
            "footer": {"text": f"[aegis] {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"}
        }]
    }
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(WEBHOOK_EXTERNO, json=payload,
                               timeout=aiohttp.ClientTimeout(total=5))
    except Exception: pass


# ============================================================
#  FEATURE 7 — ML LEVE (SPAM SCORE)
# ============================================================

SPAM_TOKENS = [
    # padroes que ML treinado em spam real identificaria
    r'(bit\.ly|tinyurl|discord\.gift|nitro|free\s*nitro)',
    r'(\$\d+|\d+\s*usd|\d+\s*reais).{0,30}(clica|acessa|entra|ganh)',
    r'(compra|vend[ae]|seguidores|views|likes).{0,50}(barato|promo|oferta)',
    r'(ganhe|gratis|free).{0,30}(nitro|robux|v-?bucks|steam)',
    r'(@everyone|@here).{0,20}(clica|acessa|vem|entra)',
    r'discord\.(gg|com/invite)/[a-zA-Z0-9]+',
]

SPAM_PESOS = [3, 4, 3, 4, 3, 5]  # peso de cada pattern

def spam_score(content: str) -> int:
    """
    Calcula score de spam 0-10.
    >= 5 = suspeito. >= 8 = certamente spam.
    """
    score = 0
    lower = content.lower()
    for pattern, peso in zip(SPAM_TOKENS, SPAM_PESOS):
        if re.search(pattern, lower, re.I):
            score += peso
    # bonus por caps excessivo
    if len(content) > 10:
        caps = sum(1 for c in content if c.isupper())
        if caps / len(content) > 0.6: score += 2
    # bonus por links multiplos
    links = re.findall(r'https?://', content)
    if len(links) >= 3: score += 3
    return min(score, 10)




PHISHING_PATTERNS = [
    r"discord[\.\-]?gift", r"free[\s\-]?nitro",
    r"steamcommunity\.(?!com)", r"discordapp\.(?!com)",
    r"bit\.ly", r"tinyurl", r"grabify",
]
INVITE_PATTERN   = r"(discord\.gg|discord\.com\/invite)\/\w+"
RAID_KEYWORDS    = ["raid","raidar","invadindo","todos entrem","join fast","nuker","nuke"]
ADMIN_NAMES      = ["admin","administrador","mod","moderador","staff","dono","owner","suporte"]

PUNICOES = {
    1: ("warn",    "aviso"),
    2: ("timeout", "10 minutos de silencio"),
    3: ("timeout", "1 hora de silencio"),
    4: ("kick",    "tchau"),
    5: ("ban",     "banido. fim."),
}

FRASES_BAN   = ["a porta e ali. ou era.","nao era bem-vindo de qualquer forma.","saiu pela porta dos fundos.","deletado com sucesso.","o servidor agradece.","era so uma questao de tempo."]
FRASES_KICK  = ["pode ir, a saudade nao vai apertar.","foi com gentileza. por enquanto.","um convite pra sair.","ate logo. ou nao.","expulso. educadamente."]
FRASES_WARN  = ["ta de bobeira ne.","to de olho.","isso nao vai passar em branco.","ultima vez que aviso com simpatia.","voce ta empurrando a sorte."]
FRASES_RAID  = [
    "$ aegis --block  →  access denied.",
    "$ intrusion detected. payload dropped.",
    "$ firewall triggered. 0 nodes compromised.",
    "$ raid neutralized. threat level escalated.",
]
FRASES_EMERG = ["modo emergencia. ninguem entra, ninguem sai.","servidor em alerta maximo.","protocolo de emergencia ativado.","blindado."]


# ============================================================
#  UTILIDADES
# ============================================================

def ts(): return int(datetime.utcnow().timestamp())

def parse_duracao(texto: str) -> timedelta:
    match = re.match(r'^(\d+)(s|m|h|d)$', texto.lower())
    if not match: return timedelta(minutes=10)
    v, u = int(match.group(1)), match.group(2)
    return {"s": timedelta(seconds=v), "m": timedelta(minutes=v),
            "h": timedelta(hours=v),   "d": timedelta(days=v)}[u]

def registrar(tipo: str, detalhe: str):
    config["historico"].append({"tipo": tipo, "detalhe": detalhe, "time": datetime.utcnow().isoformat()})
    if len(config["historico"]) > 1000:
        config["historico"] = config["historico"][-1000:]

def gerar_captcha() -> str:
    return "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=5))

def reputacao_str(uid: int) -> str:
    r = reputacao[uid]
    if r >= 10:  return "excelente"
    if r >= 5:   return "boa"
    if r >= 0:   return "neutra"
    if r >= -5:  return "ruim"
    return "pessima"

def caps_threshold(uid: int) -> float:
    """Quanto melhor a reputacao, mais tolerante com mensagem em caps."""
    r = reputacao[uid]
    if r >= 10:  return 0.9
    if r >= 5:   return 0.8
    if r >= 0:   return 0.7
    if r >= -5:  return 0.6
    return 0.5

def repeated_minimo(uid: int) -> int:
    """Quantas mensagens identicas em seguida pra contar como spam, por reputacao."""
    r = reputacao[uid]
    if r >= 10: return 6
    if r >= 5:  return 5
    if r >= 0:  return 4
    return 3

def limite_spam(uid: int) -> int:
    """Limite de mensagens na janela de tempo, por reputacao."""
    base = config["max_messages"]
    r = reputacao[uid]
    if r >= 10: return base + 5
    if r >= 5:  return base + 3
    if r >= 0:  return base
    if r >= -5: return max(base - 1, 3)
    return max(base - 3, 2)

def eh_canal_livre(channel_id: int) -> bool:
    return channel_id in config["canais_livres"]

async def aviso_ou_punir(member: discord.Member, motivo_tipo: str, motivo_completo: str,
                          guild: discord.Guild, message: discord.Message):
    """Infracao leve: 1a vez so deleta e avisa por DM. Se repetir o mesmo
    tipo de infracao dentro da janela de tempo, ai pune de verdade."""
    agora = datetime.utcnow()
    janela = timedelta(minutes=config["aviso_janela_min"])
    historico = aviso_recente[member.id]
    ultimo = historico.get(motivo_tipo)

    try: await message.delete()
    except Exception: pass

    if ultimo and agora - ultimo <= janela:
        await punir(member, motivo_completo, guild)
    else:
        historico[motivo_tipo] = agora
        if not config["silencioso"]:
            try:
                dm = discord.Embed(
                    description=f"```\n[aegis@{guild.name} ~]$ warn\n> {motivo_completo}\n> status: WARNING — proximo = punicao\n```",
                    color=COR_WARN)
                dm.set_footer(text="[aegis@server ~]$")
                await member.send(embed=dm)
            except Exception: pass
            await _log_t(guild, f"aviso (sem punicao): `{member}` — {motivo_completo}", COR_DIM)


# ============================================================
#  EMBEDS
# ============================================================

def E(desc, cor=COR_CLEAN):
    e = discord.Embed(description=desc, color=cor)
    e.set_footer(text="[aegis@server ~]$")
    return e

def embed_ban(m, motivo, mod):
    e = discord.Embed(color=COR_RED)
    e.set_author(name=f"[aegis@server ~]$ ban {m}", icon_url=m.display_avatar.url)
    e.description = f"```{motivo}```\n*{random.choice(FRASES_BAN)}*"
    e.add_field(name="mod",  value=f"`{mod}`",    inline=True)
    e.add_field(name="id",   value=f"`{m.id}`",   inline=True)
    e.add_field(name="data", value=f"<t:{ts()}:R>",inline=True)
    e.set_footer(text="[aegis@server ~]$")
    return e

def embed_kick(m, motivo, mod):
    e = discord.Embed(color=COR_DIM)
    e.set_author(name=f"[aegis@server ~]$ kick {m}", icon_url=m.display_avatar.url)
    e.description = f"```{motivo}```\n*{random.choice(FRASES_KICK)}*"
    e.add_field(name="mod",  value=f"`{mod}`",    inline=True)
    e.add_field(name="id",   value=f"`{m.id}`",   inline=True)
    e.add_field(name="data", value=f"<t:{ts()}:R>",inline=True)
    e.set_footer(text="[aegis@server ~]$")
    return e

def embed_warn(m, motivo, mod, nivel):
    barra = "▰" * nivel + "▱" * (5 - nivel)
    e = discord.Embed(color=COR_CLEAN)
    e.set_author(name=f"[aegis@server ~]$ warn {m}", icon_url=m.display_avatar.url)
    e.description = f"```{motivo}```\n*{random.choice(FRASES_WARN)}*"
    e.add_field(name="mod",       value=f"`{mod}`",     inline=True)
    e.add_field(name="nivel",     value=f"`{nivel}/5`", inline=True)
    e.add_field(name="progresso", value=f"`{barra}`",   inline=True)
    e.set_footer(text="[aegis@server ~]$")
    return e

def embed_auto(acao, motivo, usuario, nivel=None):
    icones = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "💀"}
    cores  = {1: COR_CLEAN, 2: COR_WARN, 3: COR_WARN, 4: COR_RED, 5: COR_RED}
    barra  = ("▰" * (nivel or 1) + "▱" * (5 - (nivel or 1))) if nivel else ""
    cor    = cores.get(nivel, COR_CLEAN)
    e = discord.Embed(color=cor)
    e.description = (
        f"```ansi\n"
        f"[aegis@server ~]$ enforce\n"
        f"\n"
        f"  user   : {usuario}\n"
        f"  action : {acao}\n"
        f"  reason : {motivo}\n"
        f"  level  : {barra} {nivel or 0}/5  {icones.get(nivel, '')}\n"
        f"```"
    )
    e.set_footer(text=f"[aegis@server ~]$  •  {datetime.utcnow().strftime('%H:%M:%S UTC')}")
    return e

def embed_status():
    def s(v): return "[ ON ]" if v else "[ -- ]"
    tl = config["threat_level"]
    tl_cor = {"normal": COR_CLEAN, "warning": COR_WARN, "critical": COR_RED}.get(tl, COR_CLEAN)
    e = discord.Embed(color=tl_cor)
    e.set_author(name="[aegis@server ~]$ status --all")
    e.description = (
        "```ansi\n"
        f"  anti-raid      {s(config['antiraid'])}\n"
        f"  anti-spam      {s(config['antispam'])}\n"
        f"  anti-phish     {s(config['antiphishing'])}\n"
        f"  anti-zalgo     {s(config['anti_zalgo'])}\n"
        f"  anti-invite    {s(config['anti_invite'])}\n"
        f"  anti-repeated  {s(config['anti_repeated'])}\n"
        f"  anti-nuke      {s(config['anti_nuke'])}\n"
        f"  anti-alt       {s(config['anti_alt'])}\n"
        f"  ia mode        {s(config['ai_mode'])}\n"
        f"  lockdown       {s(config['lockdown'])} {config['lockdown_mode'] if config['lockdown'] else ''}\n"
        f"  emergencia     {s(config['emergencia'])}\n"
        f"  quarentena     {s(config['quarentena'])}\n"
        f"  captcha        {s(config['captcha'])}\n"
        f"  silencioso     {s(config['silencioso'])}\n"
        f"  shadow mute    {s(config['shadow_mute'])}\n"
        f"  log edits      {s(config['log_edits'])}\n"
        f"  log deletes    {s(config['log_deletes'])}\n"
        f"  threat level   {tl.upper()}\n"
        "```"
    )
    e.add_field(name="bans",         value=f"`{config['total_bans']}`",            inline=True)
    e.add_field(name="warns",        value=f"`{config['total_warns']}`",           inline=True)
    e.add_field(name="raids",        value=f"`{config['total_raids']}`",           inline=True)
    e.add_field(name="wl",           value=f"`{len(config['whitelist'])}` users",  inline=True)
    e.add_field(name="shadow",       value=f"`{len(config['shadow_muted'])}` muted", inline=True)
    e.add_field(name="ia risk",      value=f"`{config['raid_score']}/10`",         inline=True)
    e.add_field(name="canais livres",value=f"`{len(config['canais_livres'])}`",    inline=True)
    e.add_field(name="bw leve/grave",value=f"`{len(config['banned_words_leve'])}`/`{len(config['banned_words_grave'])}`", inline=True)
    e.set_footer(text=f"[aegis@server ~]$  •  {datetime.utcnow().strftime('%H:%M:%S UTC')}")
    return e

def embed_ajuda():
    e = discord.Embed(color=COR_CLEAN)
    e.set_author(name="[aegis@server ~]$ help --full")
    e.add_field(name="moderacao", value=(
        "```\n"
        "  /ban    @u motivo\n"
        "  /kick   @u motivo\n"
        "  /warn   @u motivo\n"
        "  /unban  <id> motivo\n"
        "  /mute   @u duracao motivo\n"
        "  /unmute @u\n"
        "  /smute  @u   shadow mute\n"
        "  /sunmute @u  remover shadow\n"
        "  /limpar <n> [@u]\n"
        "  /inf    @u\n"
        "  /reset  @u\n"
        "  /rep    @u\n"
        "  /apelação lista/aceitar/rejeitar\n"
        "```"
    ), inline=False)
    e.add_field(name="protecao", value=(
        "```\n"
        "  /lock [soft|medium|hard]\n"
        "  /unlock\n"
        "  /emergencia  on/off\n"
        "  /quarentena  on/off [tempo]\n"
        "  /captcha     on/off\n"
        "  /ai          toggle ia\n"
        "  /scan        varredura [listar/kickar/banir]\n"
        "  /simular     teste de raid\n"
        "  /silencioso  toggle modo silencioso\n"
        "```"
    ), inline=False)
    e.add_field(name="config", value=(
        "```\n"
        "  /setup       configuracao automatica\n"
        "  /cfg         ajustar limites\n"
        "  /perfil salvar/carregar/lista <nome>\n"
        "  /wl  @u      whitelist\n"
        "  /bw  palavra [leve|grave]\n"
        "  /ubw palavra remover\n"
        "  /cl  [#canal]  marcar canal livre\n"
        "  /ucl [#canal]  remover canal livre\n"
        "  /backup      salvar servidor\n"
        "```"
    ), inline=False)
    e.add_field(name="info", value=(
        "```\n"
        "  /s        painel de status\n"
        "  /security dashboard ao vivo\n"
        "  /ver @u   analise de risco\n"
        "  /rl       log de raids\n"
        "  /resumo   atividade semanal\n"
        "  /ajuda    esta mensagem\n"
        "```"
    ), inline=False)
    e.add_field(name="📖 tutorial do bot Aegis - by gon  [1/2]", value=(
        "```\n"
        "  1. PRIMEIRO USO\n"
        "     /setup → cria cargos e canais automaticamente\n"
        "     defina LOG_CHANNEL_ID e STAFF_ROLE_ID no topo\n"
        "\n"
        "  2. RAID ACONTECENDO AGORA\n"
        "     /lock hard  → trava tudo\n"
        "     /emergencia → expulsa entrantes\n"
        "     /security   → dashboard ao vivo\n"
        "     /unlock     → reabre quando acabar\n"
        "\n"
        "  3. LOCKDOWN MODES\n"
        "     soft   → slowmode 2s\n"
        "     medium → bloqueia envio do @everyone\n"
        "     hard   → bloqueia tudo, so staff acessa\n"
        "\n"
        "  4. HONEYPOT\n"
        "     /honeypot #canal → canal armadilha\n"
        "     msg no canal = ban automatico\n"
        "\n"
        "  5. VPN / PROXY\n"
        "     VPN_API_KEY no topo (vpnapi.io)\n"
        "     VPN detectada = quarentena automatica\n"
        "\n"
        "  6. ML SPAM SCORE\n"
        "     score 0-10 por mensagem\n"
        "     5-7 = aviso | 8+ = delete + punicao\n"
        "     /spamscore <texto> pra testar\n"
        "```"
    ), inline=False)
    e.add_field(name="📖 tutorial do bot Aegis - by gon  [2/2]", value=(
        "```\n"
        "  7. SIMILARITY SPAM\n"
        "     detecta spam disfarçado (c0mpr4 = compra)\n"
        "     3+ msgs com 85% similar = punido\n"
        "\n"
        "  8. RAID FINGERPRINT\n"
        "     aprende padrao dos raids anteriores\n"
        "     eleva threat antes de atingir o limite\n"
        "\n"
        "  9. AUTO NUKE RECOVERY\n"
        "     canais deletados em massa = restaura sozinho\n"
        "\n"
        " 10. LOG EXTERNO\n"
        "     WEBHOOK_EXTERNO no topo do arquivo\n"
        "     servidor nukado? log continua em outro lugar\n"
        "\n"
        " 11. PALAVRAS BANIDAS\n"
        "     /bw palavra leve  → avisa 1a vez\n"
        "     /bw palavra grave → pune sempre\n"
        "\n"
        " 12. DADOS SALVOS\n"
        "     aegis.db — autosave a cada 2min\n"
        "     reiniciar o bot nao perde nada\n"
        "```"
    ), inline=False)
    e.set_footer(text="[aegis@server ~]$ help  |  duracao: 10s 5m 2h 1d")
    return e

def embed_varredura(resultado):
    suspeitos = resultado["suspeitos"]
    e = discord.Embed(color=COR_RED if suspeitos else COR_CLEAN)
    e.set_author(name="[aegis@server ~]$ scan --members")
    e.description = f"`{resultado['total']}` membros · `{len(suspeitos)}` suspeitos"
    if suspeitos:
        lista = "\n".join(f"  [{s['score']}/10] {s['nome']} — {s['motivo']}" for s in suspeitos[:15])
        if len(suspeitos) > 15: lista += f"\n  ...e mais {len(suspeitos)-15}"
        e.add_field(name="lista", value=f"```{lista}```", inline=False)
    else:
        e.add_field(name="resultado", value="`nenhum suspeito.`", inline=False)
    e.set_footer(text="[aegis@server ~]$")
    return e


# ============================================================
#  IA DE DETECCAO AVANCADA
# ============================================================

def calcular_risco(member: discord.Member):
    score, motivos = 0, []
    idade = (datetime.utcnow() - member.created_at.replace(tzinfo=None)).days

    if idade < 1:    score += 4; motivos.append("conta de hoje")
    elif idade < 7:  score += 3; motivos.append(f"{idade}d de vida")
    elif idade < 30: score += 1; motivos.append("conta nova")

    if member.avatar is None:
        score += 2; motivos.append("sem avatar")
    if re.search(r'\d{4,}', member.name):
        score += 1; motivos.append("nome com numeros")
    if re.search(r'(raid|nuke|bot|spam|hack)', member.name, re.I):
        score += 4; motivos.append("nome suspeito")
    if re.match(r'^[a-z]{6,10}\d{3,}$', member.name.lower()):
        score += 2; motivos.append("nome gerado")

    # reputacao negativa aumenta risco
    rep = reputacao[member.id]
    if rep <= -5: score += 3; motivos.append("reputacao pessima")
    elif rep <= -2: score += 1; motivos.append("reputacao ruim")

    # comportamento historico
    infras = infra_tracker[member.id]
    if infras >= 3: score += 2; motivos.append(f"{infras} infracoes")

    return min(score, 10), motivos

def detectar_bot_comportamento(uid: int, content: str) -> bool:
    """Detecta mensagens muito uniformes típicas de bots."""
    hist = comportamento[uid]
    hist.append(content.lower().strip())
    comportamento[uid] = hist[-10:]
    if len(hist) < 5: return False
    # verificar uniformidade: comprimentos muito parecidos
    lens = [len(m) for m in hist[-5:]]
    variacao = max(lens) - min(lens)
    if variacao <= 3 and len(set(hist[-5:])) >= 3:
        return True  # mensagens diferentes mas de tamanho idêntico = bot
    return False

def detectar_imitacao_admin(name: str) -> bool:
    """Detecta se o nome tenta imitar um admin/staff."""
    name_lower = name.lower()
    for admin_word in ADMIN_NAMES:
        if admin_word in name_lower:
            return True
    # Detectar caracteres lookalike (ex: 'аdmin' com 'а' cirílico)
    normalizado = unicodedata.normalize('NFKD', name_lower)
    normalizado = ''.join(c for c in normalizado if unicodedata.category(c) != 'Mn')
    for admin_word in ADMIN_NAMES:
        if admin_word in normalizado:
            return True
    return False

def detectar_alt(member: discord.Member) -> bool:
    """Detecta possível conta alternativa pelo padrão de entrada."""
    agora = datetime.utcnow()
    entrada_horarios.append((agora, member.id))
    # manter últimas 20 entradas
    while len(entrada_horarios) > 20:
        entrada_horarios.pop(0)
    # contas novas entrando no mesmo minuto = possível alt
    recentes = [uid for t, uid in entrada_horarios
                if agora - t <= timedelta(minutes=2) and uid != member.id]
    if len(recentes) >= 3:
        return True
    return False

def tem_zalgo(text: str) -> bool:
    return sum(1 for c in text if unicodedata.combining(c)) > 5

def tem_invisivel(text: str) -> bool:
    return any(c in text for c in ['\u200b','\u200c','\u200d','\u200e','\u200f','\u00ad','\u2060','\ufeff'])

def eh_risada(texto: str) -> bool:
    """Detecta se a mensagem e so uma risada (kkkk, HAHAHA, rsrs, ksksks, ahsuhsuah etc.),
    pra nao confundir com flood/caps abusivo."""
    t = texto.strip().lower()
    if not t:
        return False
    apenas_letras = re.sub(r'[^a-z]', '', t)
    if len(apenas_letras) < 4:
        return False
    letras_risada = set('krsahe')
    proporcao = sum(1 for c in apenas_letras if c in letras_risada) / len(apenas_letras)
    return proporcao >= 0.85

def tem_tom_de_brincadeira(texto: str) -> bool:
    """Detecta indicios de tom amigavel/brincadeira (risada, emoji, giria afetuosa),
    usado para nao punir xingamento jocoso entre amigos."""
    t = texto.lower()
    if eh_risada(t):
        return True
    marcadores = [
        r'k{3,}', r'(?:rs){2,}', r'(?:ha){2,}', r'(?:he){2,}', r'(?:ks){2,}',
        r'[😂🤣😆😜😝🤪😏👊🤝❤️🫂💀]',
        r'\bmano\b', r'\bman\b', r'\bpar[çc]a\b', r'\bparceiro\b', r'\bbrother\b',
        r'\birm[ãa]o\b', r'\bbro\b', r'\bcausa\b', r'\blol\b', r'\bkk+\b',
    ]
    return any(re.search(p, t) for p in marcadores)

def analisar_mensagem(content: str, uid: int = None, livre: bool = False):
    if eh_risada(content):
        return False, ""
    lower = content.lower()
    for kw in RAID_KEYWORDS:
        if kw in lower: return True, f"palavra: {kw}"
    for p in PHISHING_PATTERNS:
        if re.search(p, lower): return True, "link suspeito"
    if not livre and len(content) > 10:
        limite = caps_threshold(uid) if uid is not None else 0.7
        caps = sum(1 for c in content if c.isupper())
        if caps / len(content) > limite: return True, "caps excessivo"
    if not livre:
        emojis = re.findall(r'[\U00010000-\U0010ffff]|[\u2600-\u27BF]', content)
        if len(emojis) > 15: return True, "flood de emojis"
    return False, ""


# ============================================================
#  PUNICOES E REPUTACAO
# ============================================================

async def punir(member: discord.Member, motivo: str, guild: discord.Guild):
    if member.id in config["whitelist"]: return

    agora = datetime.utcnow()
    reset_apos = timedelta(days=config["reset_infracoes_dias"])
    anterior = ultima_infracao[member.id]
    if anterior and agora - anterior > reset_apos:
        infra_tracker[member.id] = 0  # ficha limpa: faz tempo que nao aprontava
    ultima_infracao[member.id] = agora

    infra_tracker[member.id] += 1
    reputacao[member.id] -= 2
    nivel = min(infra_tracker[member.id], 5)
    tipo, desc = PUNICOES[nivel]
    config["total_warns"] += 1
    config["daily_warns"] += 1
    registrar("punicao", f"{member} — {desc} — {motivo}")
    comportamento[member.id].append(f"[PUNICAO:{tipo}]")
    db_log_punicao(member.id, str(member), tipo, motivo)
    _atualizar_threat_level()

    if not config["silencioso"]:
        e = embed_auto(desc, motivo, str(member), nivel)
        await _log(guild, e)

    # DM terminal completo
    labels = {1: "WARN", 2: "TIMEOUT  10m", 3: "TIMEOUT  1h", 4: "KICK", 5: "BAN"}
    cor_dm = COR_RED if tipo in ("ban", "kick") else COR_WARN
    try:
        dm = discord.Embed(color=cor_dm)
        dm.description = (
            f"```ansi\n"
            f"[aegis@{guild.name} ~]$ punish {member.name}\n"
            f"\n"
            f"  action  : {labels.get(nivel, desc)}\n"
            f"  reason  : {motivo}\n"
            f"  server  : {guild.name}\n"
            f"  time    : {agora.strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"\n"
            f"  acha injusto? use /apelacao no servidor.\n"
            f"```"
        )
        dm.set_footer(text="[aegis@server ~]$ -- session closed")
        await member.send(embed=dm)
    except Exception: pass

    if tipo == "timeout":
        dur = timedelta(minutes=10) if nivel == 2 else timedelta(hours=1)
        try: await member.timeout(dur, reason=f"aegis: {motivo}")
        except Exception: pass
    elif tipo == "kick":
        config["total_bans"] += 1
        try: await member.kick(reason=f"aegis: {motivo}")
        except Exception: pass
    elif tipo == "ban":
        config["total_bans"] += 1
        try: await member.ban(reason=f"aegis: {motivo}", delete_message_days=1)
        except Exception: pass

async def _log(guild, embed):
    if LOG_CHANNEL_ID:
        ch = guild.get_channel(LOG_CHANNEL_ID)
        if ch:
            try: await ch.send(embed=embed)
            except Exception: pass

async def _log_t(guild, texto, cor=COR_DIM):
    await _log(guild, E(texto, cor))

async def _dm_dono(guild_name: str, texto: str):
    # Avisar owner do servidor
    pass  # pode conectar webhook aqui se quiser


# ============================================================
#  SISTEMA DE APELAÇÃO
# ============================================================

apelacoes = {}  # {user_id: {"motivo": str, "status": str, "time": str}}

async def registrar_apelação(user: discord.User, motivo: str):
    apelacoes[user.id] = {
        "user"  : str(user),
        "motivo": motivo,
        "status": "pendente",
        "time"  : datetime.utcnow().isoformat(),
    }


# ============================================================
#  LOCKDOWN E EMERGENCIA
# ============================================================

def _atualizar_threat_level():
    """Recalcula o threat level com base em raids e warns diários."""
    if config["daily_raids"] >= 2 or config["daily_warns"] >= 20:
        config["threat_level"] = "critical"
    elif config["daily_raids"] >= 1 or config["daily_warns"] >= 8:
        config["threat_level"] = "warning"
    else:
        config["threat_level"] = "normal"

# ============================================================
#  LOCKDOWN E EMERGENCIA
# ============================================================

async def ativar_lockdown(guild: discord.Guild, auto=False, modo: str = None):
    """
    soft   → só ativa slowmode (2s) nos canais de texto
    medium → bloqueia @everyone de enviar mensagens
    hard   → bloqueia @everyone + lê mensagens só pra staff
    """
    modo = modo or config.get("lockdown_mode", "hard")
    config["lockdown"]      = True
    config["lockdown_mode"] = modo
    config["total_raids"]   += 1
    config["daily_raids"]   += 1
    raid_log.append({"time": datetime.utcnow().isoformat(), "auto": auto, "modo": modo})
    registrar("raid", f"lockdown {modo} {'auto' if auto else 'manual'}")
    _atualizar_threat_level()
    db_log_alerta("raid", f"lockdown {modo}")
    salvar_fingerprint()
    await log_externo(
        f"[aegis] RAID — lockdown {modo} triggered",
        cor=0xE74C3C,
        detalhes=f"auto={auto} joins={len(join_tracker)} threat={config['threat_level']}"
    )

    everyone = guild.default_role
    for ch in guild.text_channels:
        try:
            if modo == "soft":
                await ch.edit(slowmode_delay=2)
            elif modo == "medium":
                await ch.set_permissions(everyone, send_messages=False)
            else:  # hard
                await ch.set_permissions(everyone, send_messages=False, read_messages=False)
                if STAFF_ROLE_ID:
                    staff = guild.get_role(STAFF_ROLE_ID)
                    if staff:
                        await ch.set_permissions(staff, send_messages=True, read_messages=True)
        except Exception: pass

    labels = {"soft": "🟡 soft — slowmode", "medium": "🟠 medium — sem envio", "hard": "🔴 hard — bloqueio total"}
    await _log_t(guild,
        f"**raid detectado. lockdown {labels.get(modo, modo)} ativado.**\n"
        f"> {random.choice(FRASES_RAID)}\n> use `/lock` para restaurar.",
        COR_RED)

async def desativar_lockdown(guild: discord.Guild):
    modo = config.get("lockdown_mode", "hard")
    config["lockdown"]      = False
    config["threat_level"]  = "normal"
    everyone = guild.default_role
    for ch in guild.text_channels:
        try:
            if modo == "soft":
                await ch.edit(slowmode_delay=0)
            else:
                await ch.set_permissions(everyone, send_messages=None, read_messages=None)
                if STAFF_ROLE_ID:
                    staff = guild.get_role(STAFF_ROLE_ID)
                    if staff:
                        await ch.set_permissions(staff, overwrite=None)
        except Exception: pass

async def ativar_emergencia(guild: discord.Guild, motivo: str):
    if config["emergencia"]: return
    config["emergencia"] = True
    config["lockdown"]   = True
    config["total_raids"] += 1
    raid_log.append({"time": datetime.utcnow().isoformat(), "auto": True})
    registrar("emergencia", motivo)
    for ch in guild.text_channels:
        try: await ch.set_permissions(guild.default_role, send_messages=False)
        except Exception: pass
    try:
        invites = await guild.invites()
        for inv in invites:
            try: await inv.delete(reason="aegis: emergencia")
            except Exception: pass
    except Exception: pass
    if STAFF_ROLE_ID:
        role = guild.get_role(STAFF_ROLE_ID)
        if role:
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    try:
                        await ch.send(
                            content=role.mention,
                            embed=E(f"**emergencia ativada.**\n> motivo: {motivo}\n> {random.choice(FRASES_EMERG)}\n> `/emergencia off` para restaurar.", COR_RED)
                        )
                    except Exception: pass
                    break

async def desativar_emergencia(guild: discord.Guild):
    config["emergencia"] = False
    config["lockdown"]   = False
    for ch in guild.text_channels:
        try: await ch.set_permissions(guild.default_role, send_messages=None)
        except Exception: pass


# ============================================================
#  ANTI-NUKE (restaurar dano automaticamente)
# ============================================================

async def restaurar_canais(guild: discord.Guild):
    """Tenta restaurar canais deletados a partir do backup."""
    if not backup_data["channels"]:
        await _log_t(guild, "anti-nuke: sem backup para restaurar. use `/backup` antes.", COR_RED)
        return 0

    canais_atuais = {c.name for c in guild.channels}
    restaurados = 0
    for ch_data in backup_data["channels"]:
        if ch_data["name"] not in canais_atuais and ch_data["type"] == "text":
            try:
                categoria = discord.utils.get(guild.categories, name=ch_data["category"]) if ch_data["category"] else None
                await guild.create_text_channel(
                    ch_data["name"],
                    category=categoria,
                    topic=ch_data["topic"] or "",
                    reason="aegis: anti-nuke restauracao"
                )
                restaurados += 1
            except Exception: pass
    return restaurados


# ============================================================
#  CAPTCHA
# ============================================================

async def enviar_captcha(member: discord.Member, guild: discord.Guild):
    codigo = gerar_captcha()
    captcha_pendente[member.id] = {
        "codigo": codigo,
        "guild" : guild.id,
        "expira": datetime.utcnow() + timedelta(minutes=5),
    }
    e = discord.Embed(color=COR_CLEAN)
    e.set_author(name=f"verificacao — {guild.name}")
    e.description = f"para acessar o servidor, responda com o codigo:\n\n```\n  {codigo}\n```\n> voce tem 5 minutos."
    e.set_footer(text="[aegis@server ~]$ captcha --verify")
    try:
        await member.send(embed=e)
    except Exception:
        await _log_t(guild, f"nao consegui enviar captcha para {member.mention}. DM fechada.", COR_DIM)
        try: await member.kick(reason="aegis: DM fechada — captcha nao enviado")
        except Exception: pass


# ============================================================
#  BACKUP
# ============================================================

async def fazer_backup(guild: discord.Guild):
    backup_data["roles"] = [
        {"name": r.name, "color": r.color.value, "permissions": r.permissions.value,
         "hoist": r.hoist, "mentionable": r.mentionable, "position": r.position}
        for r in guild.roles if not r.managed and r.name != "@everyone"
    ]
    backup_data["channels"] = [
        {"name": c.name, "type": str(c.type), "position": c.position,
         "topic": getattr(c, "topic", None), "category": c.category.name if c.category else None}
        for c in guild.channels
    ]
    backup_data["timestamp"] = datetime.utcnow().isoformat()
    return len(backup_data["roles"]), len(backup_data["channels"])


# ============================================================
#  EVENTOS
# ============================================================

@client.event
async def on_ready():
    db_init()
    db_load()
    await tree.sync()
    print(f"\n  aegis — online como {client.user}")
    print(f"  {len(client.guilds)} servidor(es)\n")
    loop_status.start()
    checar_quarentena.start()
    checar_captcha.start()
    resumo_semanal.start()
    autosave.start()
    reset_daily.start()

@tasks.loop(minutes=5)
async def loop_status():
    tl = config["threat_level"]
    ops = [
        f"$ threat: {tl.upper()}",
        f"$ bans: {config['total_bans']} | raids: {config['total_raids']}",
        f"$ monitoring {sum(g.member_count for g in client.guilds)} nodes",
        f"$ aegis --active | uptime ok",
        f"$ daily_joins={config['daily_joins']} daily_warns={config['daily_warns']}",
    ]
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=random.choice(ops)
    ))

@tasks.loop(minutes=2)
async def autosave():
    """Persiste tudo no SQLite a cada 2 minutos."""
    try:
        db_save()
    except Exception as e:
        print(f"[aegis] autosave erro: {e}")

@tasks.loop(minutes=1)
async def reset_daily():
    """Reseta stats diários à meia-noite UTC."""
    hoje = datetime.utcnow().date().isoformat()
    if config["daily_date"] != hoje:
        config["daily_date"]  = hoje
        config["daily_joins"] = 0
        config["daily_raids"] = 0
        config["daily_warns"] = 0

@tasks.loop(minutes=1)
async def checar_quarentena():
    if not config["quarentena"] or not QUARENTENA_ROLE_ID: return
    agora = datetime.utcnow()
    expirados = [uid for uid, t in quarentena_members.items()
                 if agora - t >= timedelta(minutes=config["quarentena_tempo"])]
    for uid in expirados:
        del quarentena_members[uid]
        for guild in client.guilds:
            member = guild.get_member(uid)
            if member:
                role = guild.get_role(QUARENTENA_ROLE_ID)
                if role:
                    try: await member.remove_roles(role, reason="aegis: quarentena expirada")
                    except Exception: pass
                if AUTO_ROLE_ID:
                    ar = guild.get_role(AUTO_ROLE_ID)
                    if ar:
                        try: await member.add_roles(ar, reason="aegis: verificado")
                        except Exception: pass

@tasks.loop(minutes=1)
async def checar_captcha():
    agora = datetime.utcnow()
    expirados = [uid for uid, d in captcha_pendente.items() if agora > d["expira"]]
    for uid in expirados:
        dados = captcha_pendente.pop(uid)
        guild = client.get_guild(dados["guild"])
        if guild:
            member = guild.get_member(uid)
            if member:
                try:
                    await member.kick(reason="aegis: captcha nao respondido")
                    await _log_t(guild, f"`{member}` kickado — captcha expirado.", COR_DIM)
                except Exception: pass

@tasks.loop(hours=168)
async def resumo_semanal():
    await asyncio.sleep(10)
    for guild in client.guilds:
        hist = [h for h in config["historico"]
                if datetime.utcnow() - datetime.fromisoformat(h["time"]) <= timedelta(days=7)]
        raids    = sum(1 for h in hist if h["tipo"] == "raid")
        punicoes = sum(1 for h in hist if h["tipo"] == "punicao")
        emerg    = sum(1 for h in hist if h["tipo"] == "emergencia")
        texto = (
            f"**resumo semanal — {guild.name}**\n"
            f"```\n"
            f"  raids       {raids}\n"
            f"  punicoes    {punicoes}\n"
            f"  emergencias {emerg}\n"
            f"  bans totais {config['total_bans']}\n"
            f"  warns totais {config['total_warns']}\n"
            f"```"
        )
        await _log_t(guild, texto, COR_DIM)

@client.event
async def on_member_join(member: discord.Member):
    if not config["antiraid"] or member.id in config["whitelist"]: return
    now = datetime.utcnow()
    join_tracker.append(now)
    while join_tracker and now - join_tracker[0] > timedelta(seconds=config["join_window"]):
        join_tracker.popleft()

    # tracking pra /security (janela de 60s)
    joins_por_minuto.append(now)
    while joins_por_minuto and now - joins_por_minuto[0] > timedelta(seconds=60):
        joins_por_minuto.popleft()

    config["daily_joins"] += 1

    # VPN / PROXY CHECK
    if VPN_API_KEY:
        is_vpn = await checar_vpn(member)
        if is_vpn:
            await _log_t(member.guild,
                f"```\n[aegis@server ~]$ vpn-check --flag\n"
                f"> uid  : {member.id}\n"
                f"> user : {member}\n"
                f"> result: VPN/PROXY detected — quarantine\n```", COR_WARN)
            quarentena_members[member.id] = now
            if QUARENTENA_ROLE_ID:
                role = member.guild.get_role(QUARENTENA_ROLE_ID)
                if role:
                    try: await member.add_roles(role, reason="vpn detected")
                    except Exception: pass

    # RAID FINGERPRINT — bate com padrao de raids anteriores?
    if parece_raid_por_padrao():
        config["threat_level"] = "warning"
        await _log_t(member.guild,
            "```\n[aegis@server ~]$ fingerprint --match\n"
            "> pattern matches previous raid signature\n"
            "> threat escalated to WARNING\n```", COR_WARN)
        await log_externo("fingerprint match — possible raid incoming",
                          detalhes=f"joins={len(join_tracker)} hora={now.hour}")

    risco, motivos = calcular_risco(member)
    config["raid_score"] = risco

    if config["emergencia"]:
        try: await member.kick(reason="aegis: emergencia ativa")
        except Exception: pass
        return

    # Detectar imitacao de admin no nome
    if detectar_imitacao_admin(member.name):
        await punir(member, "nome imitando admin/staff", member.guild)
        await _log_t(member.guild, f"imitacao de admin detectada: `{member}` (`{member.name}`)", COR_RED)
        return

    # Detectar alt
    if config["anti_alt"] and detectar_alt(member):
        await _log_t(member.guild, f"possivel alt detectado: `{member}` (risco: {risco}/10 — {', '.join(motivos)})", COR_RED)

    # IA: conta suspeita
    if config["ai_mode"] and risco >= 7:
        await punir(member, f"conta suspeita — ia: {risco}/10", member.guild)
        return

    # Raid por volume
    if len(join_tracker) >= config["max_joins"]:
        await ativar_lockdown(member.guild, auto=True)
        try: await member.kick(reason="aegis: raid")
        except Exception: pass
        return

    # Captcha
    if config["captcha"]:
        await enviar_captcha(member, member.guild)
        return

    # Quarentena
    if config["quarentena"] and QUARENTENA_ROLE_ID:
        role = member.guild.get_role(QUARENTENA_ROLE_ID)
        if role:
            try:
                await member.add_roles(role, reason="aegis: quarentena")
                quarentena_members[member.id] = now
            except Exception: pass
        return

    # Auto-role para membros normais
    if AUTO_ROLE_ID:
        ar = member.guild.get_role(AUTO_ROLE_ID)
        if ar:
            try: await member.add_roles(ar, reason="aegis: auto-role")
            except Exception: pass

    # Guardar horário de entrada para detectar alts futuros
    nomes_anteriores[member.id].append(member.name)

@client.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild: return

    # Resposta de captcha via DM
    if isinstance(message.channel, discord.DMChannel):
        uid = message.author.id
        if uid in captcha_pendente:
            dados = captcha_pendente[uid]
            if datetime.utcnow() > dados["expira"]:
                del captcha_pendente[uid]
                await message.channel.send(embed=E("codigo expirado. voce sera removido.", COR_RED))
                return
            if message.content.upper().strip() == dados["codigo"]:
                del captcha_pendente[uid]
                guild = client.get_guild(dados["guild"])
                if guild:
                    member = guild.get_member(uid)
                    if member:
                        if QUARENTENA_ROLE_ID:
                            role = guild.get_role(QUARENTENA_ROLE_ID)
                            if role:
                                try: await member.remove_roles(role, reason="aegis: captcha ok")
                                except Exception: pass
                        if AUTO_ROLE_ID:
                            ar = guild.get_role(AUTO_ROLE_ID)
                            if ar:
                                try: await member.add_roles(ar, reason="aegis: verificado")
                                except Exception: pass
                reputacao[uid] += 1
                await message.channel.send(embed=E("verificado. bem-vindo ao servidor."))
            else:
                reputacao[uid] -= 1
                await message.channel.send(embed=E("codigo incorreto. tente novamente.", COR_RED))

        # Sistema de apelação via DM
        elif message.content.lower().startswith("apelar:"):
            motivo = message.content[7:].strip()
            if motivo:
                await registrar_apelação(message.author, motivo)
                await message.channel.send(embed=E("apelação registrada. aguarde revisao da staff."))
        return

    if message.author.id in config["whitelist"]: return

    # Shadow mute: deletar silenciosamente
    if message.author.id in config["shadow_muted"]:
        try: await message.delete()
        except Exception: pass
        return

    # HONEYPOT — ban imediato se mandou mensagem no canal armadilha
    if await checar_honeypot(message): return

    uid, guild, now = message.author.id, message.guild, datetime.utcnow()
    content = message.content
    livre = eh_canal_livre(message.channel.id)

    # ML LEVE — spam score
    if config["ai_mode"] and not livre:
        score = spam_score(content)
        if score >= 8:
            try: await message.delete()
            except Exception: pass
            await punir(message.author, f"ml-spam score={score}/10", guild)
            await log_externo(f"ml-spam detected", detalhes=f"uid={uid} score={score} msg={content[:80]}")
            return
        elif score >= 5:
            await aviso_ou_punir(message.author, "ml_spam", f"ml-spam suspeito score={score}/10", guild, message)
            return

    # SIMILARITY — spam disfarçado (c0mpr4 s3guid0res etc)
    if config["antispam"] and not livre and not eh_risada(content):
        if checar_similarity(uid, content):
            try: await message.delete()
            except Exception: pass
            await punir(message.author, "similarity-spam (msgs parecidas)", guild); return

    # Anti-spam (limite mais folgado pra quem tem boa reputacao)
    if config["antispam"]:
        msg_tracker[uid].append(now)
        while msg_tracker[uid] and now - msg_tracker[uid][0] > timedelta(seconds=config["msg_window"]):
            msg_tracker[uid].popleft()
        if len(msg_tracker[uid]) >= limite_spam(uid):
            try: await message.delete()
            except Exception: pass
            await punir(message.author, "spam", guild); return

    # Anti-repeated (risada repetida tipo "kkkk" "kkkk" "kkkk" nao conta, e em canal livre nao se aplica)
    if config["anti_repeated"] and not eh_risada(content) and not livre:
        minimo = repeated_minimo(uid)
        repeated_tracker[uid].append(content.lower().strip())
        repeated_tracker[uid] = repeated_tracker[uid][-10:]
        if len(repeated_tracker[uid]) >= minimo and len(set(repeated_tracker[uid][-minimo:])) == 1:
            try: await message.delete()
            except Exception: pass
            await punir(message.author, "mensagem repetida", guild); return

    # Detectar comportamento de bot
    if config["ai_mode"] and detectar_bot_comportamento(uid, content):
        reputacao[uid] -= 1
        await _log_t(guild, f"comportamento de bot detectado: `{message.author}`", COR_DIM)

    # Anti-mention
    if len(message.mentions) >= config["max_mentions"]:
        try: await message.delete()
        except Exception: pass
        await punir(message.author, f"mention flood ({len(message.mentions)})", guild); return

    # Anti-invite
    if config["anti_invite"] and re.search(INVITE_PATTERN, content, re.I):
        try: await message.delete()
        except Exception: pass
        await punir(message.author, "spam de convite", guild); return

    # Palavras banidas graves (odio/slur): sempre pune, mesmo com tom de brincadeira ou em canal livre
    lower = content.lower()
    for word in config["banned_words_grave"]:
        if word in lower:
            try: await message.delete()
            except Exception: pass
            await punir(message.author, f"palavra grave: {word}", guild); return

    # Palavras banidas leves: nao pune se for brincadeira/risada entre amigos ou canal livre;
    # senao, so avisa na 1a vez e pune de fato se a pessoa repetir.
    if not livre and not tem_tom_de_brincadeira(content):
        for word in config["banned_words_leve"]:
            if word in lower:
                await aviso_ou_punir(message.author, f"palavra:{word}", f"palavra banida: {word}", guild, message)
                return

    # Anti-phishing
    if config["antiphishing"]:
        for p in PHISHING_PATTERNS:
            if re.search(p, lower):
                try: await message.delete()
                except Exception: pass
                await punir(message.author, "phishing", guild); return

    # Anti-zalgo
    if config["anti_zalgo"]:
        if tem_zalgo(content):
            try: await message.delete()
            except Exception: pass
            await punir(message.author, "texto zalgo", guild); return
        if tem_invisivel(content):
            try: await message.delete()
            except Exception: pass
            await punir(message.author, "caracteres invisiveis", guild); return

    # IA geral (caps/flood de emoji ficam de boa em canal livre)
    if config["ai_mode"]:
        suspeita, motivo = analisar_mensagem(content, uid=uid, livre=livre)
        if suspeita:
            if motivo == "caps excessivo":
                await aviso_ou_punir(message.author, "caps", f"ia: {motivo}", guild, message)
                return
            try: await message.delete()
            except Exception: pass
            await punir(message.author, f"ia: {motivo}", guild); return

    # Reputacao positiva por mensagem normal
    if len(content) > 10:
        reputacao[uid] = min(reputacao[uid] + 0, 20)  # não aumentar infinitamente

@client.event
async def on_message_edit(before, after):
    if before.author.bot or not before.guild: return
    if not config["log_edits"]: return
    if before.content == after.content: return
    e = discord.Embed(color=COR_DIM)
    e.set_author(name=f"[aegis@server ~]$ log --edit {before.author}", icon_url=before.author.display_avatar.url)
    e.add_field(name="antes", value=f"```{before.content[:500] if before.content else 'vazio'}```", inline=False)
    e.add_field(name="depois",value=f"```{after.content[:500]  if after.content  else 'vazio'}```", inline=False)
    e.add_field(name="canal", value=before.channel.mention, inline=True)
    e.add_field(name="data",  value=f"<t:{ts()}:R>",        inline=True)
    e.set_footer(text="[aegis@server ~]$")
    await _log(before.guild, e)

@client.event
async def on_message_delete(message):
    if message.author.bot or not message.guild: return
    if not config["log_deletes"]: return
    e = discord.Embed(color=COR_DIM)
    e.set_author(name=f"[aegis@server ~]$ log --delete {message.author}", icon_url=message.author.display_avatar.url)
    e.description = f"```{message.content[:800] if message.content else 'vazio'}```"
    e.add_field(name="canal", value=message.channel.mention, inline=True)
    e.add_field(name="data",  value=f"<t:{ts()}:R>",         inline=True)
    e.set_footer(text="[aegis@server ~]$")
    await _log(message.guild, e)

@client.event
async def on_guild_channel_delete(channel):
    now = datetime.utcnow()
    channel_del_tracker.append(now)
    while channel_del_tracker and now - channel_del_tracker[0] > timedelta(seconds=config["channel_op_window"]):
        channel_del_tracker.pop(0)
    if len(channel_del_tracker) >= config["max_channel_ops"] and config["anti_nuke"]:
        await log_externo(
            "[aegis] NUKE DETECTED",
            cor=0xE74C3C,
            detalhes=f"guild={channel.guild.name} channels_deleted={len(channel_del_tracker)}"
        )
        await _log_t(channel.guild,
            f"```\n[aegis@server ~]$ nuke-detect --alert\n"
            f"> {len(channel_del_tracker)} canais deletados em {config['channel_op_window']}s\n"
            f"> iniciando auto-recovery...\n```", COR_RED)
        await ativar_emergencia(channel.guild, "exclusao em massa de canais (nuke)")
        await auto_nuke_recovery(channel.guild)

@client.event
async def on_guild_channel_create(channel):
    now = datetime.utcnow()
    channel_cre_tracker.append(now)
    while channel_cre_tracker and now - channel_cre_tracker[0] > timedelta(seconds=config["channel_op_window"]):
        channel_cre_tracker.pop(0)
    if len(channel_cre_tracker) >= config["max_channel_ops"]:
        await _log_t(channel.guild, f"criacao em massa de canais!\n> {len(channel_cre_tracker)} canais em {config['channel_op_window']}s", COR_RED)

@client.event
async def on_member_ban(guild, user):
    now = datetime.utcnow()
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
        mod_id = entry.user.id
        if mod_id == client.user.id or mod_id in config["whitelist"]: return
        ban_tracker[mod_id].append(now)
        ban_tracker[mod_id] = [t for t in ban_tracker[mod_id] if now - t <= timedelta(seconds=config["mass_ban_window"])]
        if len(ban_tracker[mod_id]) >= config["max_mass_ban"]:
            await _log_t(guild, f"**ban em massa!**\n> `{entry.user}` baniu {len(ban_tracker[mod_id])} usuarios em {config['mass_ban_window']}s", COR_RED)

@client.event
async def on_member_remove(member):
    registrar("saida", str(member))
    if LOG_CHANNEL_ID:
        ch = member.guild.get_channel(LOG_CHANNEL_ID)
        if ch:
            try: await ch.send(embed=E(f"`{member}` saiu.", COR_DIM))
            except Exception: pass

@client.event
async def on_member_update(before, after):
    # Detectar mudança de nome suspeita
    if before.display_name != after.display_name:
        nomes_anteriores[after.id].append(after.display_name)
        if detectar_imitacao_admin(after.display_name):
            await _log_t(after.guild, f"mudanca de nome suspeita: `{before.display_name}` -> `{after.display_name}` (`{after}`)", COR_RED)
            try: await after.edit(nick=before.display_name, reason="aegis: nome imitando admin")
            except Exception: pass

    # Detectar cargo admin concedido
    novos = set(after.roles) - set(before.roles)
    for role in novos:
        if role.permissions.administrator or role.permissions.manage_guild:
            await _log_t(after.guild, f"cargo admin concedido:\n> `{after}` recebeu `{role.name}`", COR_RED)

@client.event
async def on_guild_update(before, after):
    changes = []
    if before.name != after.name: changes.append(f"nome: `{before.name}` -> `{after.name}`")
    if before.icon != after.icon: changes.append("icone alterado")
    if before.banner != after.banner: changes.append("banner alterado")
    if changes:
        await _log_t(after, "servidor alterado:\n> " + "\n> ".join(changes), COR_DIM)

@client.event
async def on_guild_role_create(role):
    await _log_t(role.guild, f"cargo criado: `{role.name}`", COR_DIM)

@client.event
async def on_guild_role_delete(role):
    await _log_t(role.guild, f"cargo deletado: `{role.name}`", COR_RED)


# ============================================================
#  COMANDOS
# ============================================================

# ── MODERACAO ────────────────────────────────────────────────

@tree.command(name="ban", description="bane um usuario")
@app_commands.checks.has_permissions(ban_members=True)
async def cmd_ban(interaction: discord.Interaction, usuario: discord.Member, motivo: str = "sem motivo"):
    if usuario.top_role >= interaction.user.top_role:
        await interaction.response.send_message(embed=E("cargo igual ou superior. nao posso.", COR_RED), ephemeral=True); return
    try:
        try: await usuario.send(embed=E(f"> banido de **{interaction.guild.name}**\n> motivo: {motivo}", COR_RED))
        except Exception: pass
        await usuario.ban(reason=f"[aegis] {motivo} | {interaction.user}", delete_message_days=1)
        config["total_bans"] += 1
        reputacao[usuario.id] -= 5
        registrar("ban", f"{usuario} por {interaction.user} — {motivo}")
        e = embed_ban(usuario, motivo, interaction.user)
        await interaction.response.send_message(embed=e)
        await _log(interaction.guild, e)
    except Exception as ex:
        await interaction.response.send_message(embed=E(str(ex), COR_RED), ephemeral=True)

@tree.command(name="unban", description="desbane um usuario pelo ID")
@app_commands.checks.has_permissions(ban_members=True)
async def cmd_unban(interaction: discord.Interaction, user_id: str, motivo: str = "sem motivo"):
    try:
        user = await client.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=f"[aegis] {motivo} | {interaction.user}")
        reputacao[user.id] += 2
        await interaction.response.send_message(embed=E(f"`{user}` desbanido.\n> motivo: {motivo}"), ephemeral=True)
    except Exception as ex:
        await interaction.response.send_message(embed=E(str(ex), COR_RED), ephemeral=True)

@tree.command(name="kick", description="expulsa um usuario")
@app_commands.checks.has_permissions(kick_members=True)
async def cmd_kick(interaction: discord.Interaction, usuario: discord.Member, motivo: str = "sem motivo"):
    if usuario.top_role >= interaction.user.top_role:
        await interaction.response.send_message(embed=E("cargo igual ou superior. nao posso.", COR_RED), ephemeral=True); return
    try:
        try: await usuario.send(embed=E(f"> expulso de **{interaction.guild.name}**\n> motivo: {motivo}", COR_DIM))
        except Exception: pass
        await usuario.kick(reason=f"[aegis] {motivo} | {interaction.user}")
        reputacao[usuario.id] -= 3
        registrar("kick", f"{usuario} por {interaction.user} — {motivo}")
        e = embed_kick(usuario, motivo, interaction.user)
        await interaction.response.send_message(embed=e)
        await _log(interaction.guild, e)
    except Exception as ex:
        await interaction.response.send_message(embed=E(str(ex), COR_RED), ephemeral=True)

@tree.command(name="warn", description="avisa um usuario")
@app_commands.checks.has_permissions(manage_messages=True)
async def cmd_warn(interaction: discord.Interaction, usuario: discord.Member, motivo: str = "sem motivo"):
    infra_tracker[usuario.id] += 1
    nivel = min(infra_tracker[usuario.id], 5)
    config["total_warns"] += 1
    reputacao[usuario.id] -= 1
    registrar("warn", f"{usuario} por {interaction.user} — {motivo}")
    try: await usuario.send(embed=E(f"> aviso em **{interaction.guild.name}**\n> motivo: {motivo}\n> {nivel}/5", COR_DIM))
    except Exception: pass
    e = embed_warn(usuario, motivo, interaction.user, nivel)
    await interaction.response.send_message(embed=e)
    await _log(interaction.guild, e)

@tree.command(name="mute", description="silencia usuario (10s, 5m, 2h, 1d)")
@app_commands.checks.has_permissions(moderate_members=True)
async def cmd_mute(interaction: discord.Interaction, usuario: discord.Member, duracao: str = "10m", motivo: str = "sem motivo"):
    if usuario.top_role >= interaction.user.top_role:
        await interaction.response.send_message(embed=E("cargo igual ou superior.", COR_RED), ephemeral=True); return
    dur = parse_duracao(duracao)
    try:
        await usuario.timeout(dur, reason=f"[aegis] {motivo} | {interaction.user}")
        await interaction.response.send_message(embed=E(f"`{usuario}` silenciado por `{duracao}`.\n> motivo: {motivo}", COR_DIM))
    except Exception as ex:
        await interaction.response.send_message(embed=E(str(ex), COR_RED), ephemeral=True)

@tree.command(name="unmute", description="remove silencio de usuario")
@app_commands.checks.has_permissions(moderate_members=True)
async def cmd_unmute(interaction: discord.Interaction, usuario: discord.Member):
    try:
        await usuario.timeout(None, reason=f"[aegis] unmute por {interaction.user}")
        await interaction.response.send_message(embed=E(f"`{usuario}` desmutado."), ephemeral=True)
    except Exception as ex:
        await interaction.response.send_message(embed=E(str(ex), COR_RED), ephemeral=True)

@tree.command(name="smute", description="shadow mute — usuario nao sabe que foi silenciado")
@app_commands.checks.has_permissions(manage_messages=True)
async def cmd_smute(interaction: discord.Interaction, usuario: discord.Member):
    config["shadow_muted"].add(usuario.id)
    await interaction.response.send_message(embed=E(f"`{usuario}` em shadow mute. ele nao sabe."), ephemeral=True)
    await _log_t(interaction.guild, f"shadow mute: `{usuario}` por `{interaction.user}`", COR_DIM)

@tree.command(name="sunmute", description="remove shadow mute")
@app_commands.checks.has_permissions(manage_messages=True)
async def cmd_sunmute(interaction: discord.Interaction, usuario: discord.Member):
    config["shadow_muted"].discard(usuario.id)
    await interaction.response.send_message(embed=E(f"shadow mute removido de `{usuario}`."), ephemeral=True)

@tree.command(name="limpar", description="deleta mensagens do canal (max 100)")
@app_commands.checks.has_permissions(manage_messages=True)
async def cmd_limpar(interaction: discord.Interaction, quantidade: int, usuario: discord.Member = None):
    if quantidade < 1 or quantidade > 100:
        await interaction.response.send_message(embed=E("entre 1 e 100.", COR_RED), ephemeral=True); return
    await interaction.response.defer(ephemeral=True)
    def check(m): return usuario is None or m.author == usuario
    deletadas = await interaction.channel.purge(limit=quantidade, check=check)
    await interaction.followup.send(embed=E(f"`{len(deletadas)}` mensagens deletadas.", COR_DIM), ephemeral=True)

@tree.command(name="inf", description="infracoes de um usuario")
@app_commands.checks.has_permissions(manage_messages=True)
async def cmd_inf(interaction: discord.Interaction, usuario: discord.Member):
    nivel = infra_tracker[usuario.id]
    proxima = PUNICOES.get(min(nivel + 1, 5), ("", "ja era"))[1]
    barra = "▰" * nivel + "▱" * (5 - nivel)
    e = discord.Embed(color=COR_RED if nivel >= 3 else COR_DIM)
    e.set_author(name=f"[aegis@server ~]$ inf {usuario}", icon_url=usuario.display_avatar.url)
    e.description = f"`{barra}` {nivel}/5\n> proximo: {proxima}\n> reputacao: {reputacao_str(usuario.id)}"
    e.set_footer(text="[aegis@server ~]$")
    await interaction.response.send_message(embed=e, ephemeral=True)

@tree.command(name="reset", description="reseta infracoes")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_reset(interaction: discord.Interaction, usuario: discord.Member):
    infra_tracker[usuario.id] = 0
    ultima_infracao[usuario.id] = None
    aviso_recente[usuario.id] = {}
    await interaction.response.send_message(embed=E(f"`{usuario}` — ficha limpa."), ephemeral=True)

@tree.command(name="rep", description="vê ou ajusta reputacao de um usuario")
@app_commands.checks.has_permissions(manage_messages=True)
async def cmd_rep(interaction: discord.Interaction, usuario: discord.Member, ajuste: int = None):
    if ajuste is not None:
        reputacao[usuario.id] += ajuste
    r = reputacao[usuario.id]
    await interaction.response.send_message(embed=E(
        f"`{usuario}`\n> reputacao: `{r}` — {reputacao_str(usuario.id)}"
    ), ephemeral=True)

@tree.command(name="apelação", description="gerencia apelacoes de usuarios banidos")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_apelação(interaction: discord.Interaction, acao: str, user_id: str = None):
    if acao == "lista":
        if not apelacoes:
            await interaction.response.send_message(embed=E("nenhuma apelação pendente."), ephemeral=True); return
        linhas = ""
        for uid, d in list(apelacoes.items())[:10]:
            linhas += f"  {uid} — {d['user']} — {d['status']} — {d['motivo'][:30]}\n"
        await interaction.response.send_message(embed=E(f"apelacoes:\n```{linhas}```"), ephemeral=True)

    elif acao == "aceitar" and user_id:
        uid = int(user_id)
        if uid in apelacoes:
            apelacoes[uid]["status"] = "aceita"
            try:
                user = await client.fetch_user(uid)
                await interaction.guild.unban(user, reason="aegis: apelação aceita")
                await user.send(embed=E(f"sua apelação em **{interaction.guild.name}** foi aceita. voce foi desbanido."))
            except Exception: pass
            await interaction.response.send_message(embed=E(f"apelação de `{user_id}` aceita."), ephemeral=True)
        else:
            await interaction.response.send_message(embed=E("apelação nao encontrada.", COR_RED), ephemeral=True)

    elif acao == "rejeitar" and user_id:
        uid = int(user_id)
        if uid in apelacoes:
            apelacoes[uid]["status"] = "rejeitada"
            try:
                user = await client.fetch_user(uid)
                await user.send(embed=E(f"sua apelação em **{interaction.guild.name}** foi rejeitada.", COR_RED))
            except Exception: pass
            await interaction.response.send_message(embed=E(f"apelação de `{user_id}` rejeitada."), ephemeral=True)
        else:
            await interaction.response.send_message(embed=E("apelação nao encontrada.", COR_RED), ephemeral=True)
    else:
        await interaction.response.send_message(embed=E("uso:\n```\n  /apelação lista\n  /apelação aceitar <id>\n  /apelação rejeitar <id>\n```"), ephemeral=True)

# ── PROTECAO ─────────────────────────────────────────────────

@tree.command(name="lock", description="ativa lockdown (soft/medium/hard)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(modo=[
    app_commands.Choice(name="soft — slowmode", value="soft"),
    app_commands.Choice(name="medium — bloqueia envio", value="medium"),
    app_commands.Choice(name="hard — bloqueia tudo (default)", value="hard"),
])
async def cmd_lock(interaction: discord.Interaction, modo: app_commands.Choice[str] = None):
    if config["lockdown"]:
        await desativar_lockdown(interaction.guild)
        await interaction.response.send_message(embed=E("lockdown desativado. canais abertos."), ephemeral=True)
    else:
        m = modo.value if modo else "hard"
        await ativar_lockdown(interaction.guild, modo=m)
        await interaction.response.send_message(embed=E(f"lockdown **{m}** ativado.", COR_RED), ephemeral=True)

@tree.command(name="unlock", description="remove lockdown")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_unlock(interaction: discord.Interaction):
    if not config["lockdown"]:
        await interaction.response.send_message(embed=E("nao ha lockdown ativo."), ephemeral=True); return
    await desativar_lockdown(interaction.guild)
    await interaction.response.send_message(embed=E("lockdown removido. canais abertos."), ephemeral=True)

@tree.command(name="security", description="dashboard de segurança ao vivo")
@app_commands.checks.has_permissions(manage_messages=True)
async def cmd_security(interaction: discord.Interaction):
    agora = datetime.utcnow()
    # limpa joins_por_minuto antes de contar
    while joins_por_minuto and agora - joins_por_minuto[0] > timedelta(seconds=60):
        joins_por_minuto.popleft()

    tl = config["threat_level"]
    tl_emoji = {"normal": "🟢", "warning": "🟡", "critical": "🔴"}.get(tl, "⚪")

    alertas_ativos = []
    if config["lockdown"]:     alertas_ativos.append(f"lockdown {config['lockdown_mode']}")
    if config["emergencia"]:   alertas_ativos.append("emergencia")
    if config["quarentena"]:   alertas_ativos.append("quarentena")
    alertas_str = ", ".join(alertas_ativos) if alertas_ativos else "nenhum"

    e = discord.Embed(color=COR_RED if tl == "critical" else (0xffaa00 if tl == "warning" else COR_CLEAN))
    e.set_author(name="[aegis@server ~]$ security --live")
    e.description = (
        f"```\n"
        f"  threat level   {tl_emoji} {tl.upper()}\n"
        f"  joins/min      {len(joins_por_minuto)}\n"
        f"  joins hoje     {config['daily_joins']}\n"
        f"  raids hoje     {config['daily_raids']}\n"
        f"  warns hoje     {config['daily_warns']}\n"
        f"  lockdown       {'on — ' + config['lockdown_mode'] if config['lockdown'] else 'off'}\n"
        f"  alertas        {alertas_str}\n"
        f"  shadow muted   {len(config['shadow_muted'])}\n"
        f"  ia risk score  {config['raid_score']}/10\n"
        f"```"
    )
    e.add_field(name="total raids",  value=f"`{config['total_raids']}`", inline=True)
    e.add_field(name="total bans",   value=f"`{config['total_bans']}`",  inline=True)
    e.add_field(name="total warns",  value=f"`{config['total_warns']}`", inline=True)
    e.set_footer(text=f"[aegis@server ~]$ security --live • {agora.strftime('%H:%M:%S UTC')}")
    await interaction.response.send_message(embed=e, ephemeral=True)

@tree.command(name="emergencia", description="modo emergencia on/off")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_emergencia(interaction: discord.Interaction, acao: str = "on"):
    if acao.lower() == "off":
        await desativar_emergencia(interaction.guild)
        await interaction.response.send_message(embed=E("emergencia desativada."), ephemeral=True)
    else:
        await ativar_emergencia(interaction.guild, "ativado manualmente")
        await interaction.response.send_message(embed=E("emergencia ativada.\n> convites off\n> novos membros bloqueados\n> canais fechados.", COR_RED), ephemeral=True)

@tree.command(name="captcha", description="toggle captcha para novos membros")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_captcha(interaction: discord.Interaction):
    config["captcha"] = not config["captcha"]
    await interaction.response.send_message(embed=E(f"captcha {'ativado.' if config['captcha'] else 'desativado.'}"), ephemeral=True)

@tree.command(name="quarentena", description="toggle quarentena para novos membros")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_quarentena(interaction: discord.Interaction, tempo: int = None):
    if tempo: config["quarentena_tempo"] = tempo
    config["quarentena"] = not config["quarentena"]
    await interaction.response.send_message(embed=E(f"quarentena {'ativada' if config['quarentena'] else 'desativada'}. ({config['quarentena_tempo']} min)"), ephemeral=True)

@tree.command(name="ai", description="toggle ia")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_ai(interaction: discord.Interaction):
    config["ai_mode"] = not config["ai_mode"]
    await interaction.response.send_message(embed=E(f"`ia {'ligada.' if config['ai_mode'] else 'desligada.'}`"), ephemeral=True)

@tree.command(name="silencioso", description="toggle modo silencioso (age sem avisar no canal)")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_silencioso(interaction: discord.Interaction):
    config["silencioso"] = not config["silencioso"]
    s = "ativado. vou agir sem fazer barulho." if config["silencioso"] else "desativado."
    await interaction.response.send_message(embed=E(f"modo silencioso {s}"), ephemeral=True)

@tree.command(name="scan", description="varredura de contas suspeitas")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_scan(interaction: discord.Interaction, acao: str = "listar"):
    await interaction.response.defer(ephemeral=True)
    suspeitos, total = [], 0
    for member in interaction.guild.members:
        if member.bot or member.id in config["whitelist"] or member.id == interaction.user.id: continue
        total += 1
        risco, motivos = calcular_risco(member)
        if risco >= 5:
            suspeitos.append({"member": member, "nome": str(member), "score": risco, "motivo": ", ".join(motivos)})
    e = embed_varredura({"total": total, "suspeitos": suspeitos})
    if acao in ("kickar", "banir") and suspeitos:
        count = 0
        for s in suspeitos:
            try:
                if acao == "kickar": await s["member"].kick(reason="aegis: varredura")
                else: await s["member"].ban(reason="aegis: varredura", delete_message_days=1)
                config["total_bans"] += 1; count += 1
            except Exception: pass
        e.add_field(name="acao", value=f"`{count}` {'expulsos' if acao == 'kickar' else 'banidos'}.", inline=False)
    await interaction.followup.send(embed=e, ephemeral=True)
    await _log(interaction.guild, e)

@tree.command(name="simular", description="simula raid para testar o bot (sem efeito real)")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_simular(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    resultados = []

    # Simula volume de entradas
    now = datetime.utcnow()
    for _ in range(config["max_joins"] + 1):
        join_tracker.append(now)
    resultados.append(f"raid por volume — {'OK' if len(join_tracker) >= config['max_joins'] else 'FALHOU'}")
    join_tracker.clear()

    # IA
    s, m = analisar_mensagem("RAID RAID TODOS ENTREM AGORA")
    resultados.append(f"ia — {'OK: ' + m if s else 'FALHOU'}")

    # Phishing
    s2, _ = analisar_mensagem("discord.gift/freenitro123")
    resultados.append(f"phishing — {'OK' if s2 else 'FALHOU'}")

    # Zalgo
    zalgo_test = "t\u0300\u0301\u0302\u0303\u0304\u0305e\u0300\u0301\u0302xt"
    resultados.append(f"zalgo — {'OK' if tem_zalgo(zalgo_test) else 'FALHOU'}")

    # Anti-nuke
    resultados.append(f"anti-nuke — {'OK (ativo)' if config['anti_nuke'] else 'OFF'}")

    linhas = "\n".join(f"  {r}" for r in resultados)
    await interaction.followup.send(embed=E(f"**resultado da simulacao:**\n```\n{linhas}\n```"), ephemeral=True)

# ── CONFIG ───────────────────────────────────────────────────

@tree.command(name="setup", description="configura o Aegis automaticamente")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_setup(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild  = interaction.guild
    criados = []
    global LOG_CHANNEL_ID, QUARENTENA_ROLE_ID, STAFF_ROLE_ID

    log_ch = discord.utils.get(guild.text_channels, name="aegis-logs")
    if not log_ch:
        try:
            ow = {guild.default_role: discord.PermissionOverwrite(read_messages=False),
                  guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
            log_ch = await guild.create_text_channel("aegis-logs", overwrites=ow, reason="aegis: setup")
            criados.append("canal #aegis-logs")
        except Exception: pass

    q_role = discord.utils.get(guild.roles, name="Quarentena")
    if not q_role:
        try:
            q_role = await guild.create_role(name="Quarentena", color=discord.Color.dark_gray(), reason="aegis: setup")
            for ch in guild.text_channels:
                try: await ch.set_permissions(q_role, send_messages=False, add_reactions=False)
                except Exception: pass
            criados.append("cargo @Quarentena")
        except Exception: pass

    staff_role = discord.utils.get(guild.roles, name="Staff")
    if not staff_role:
        try:
            staff_role = await guild.create_role(name="Staff", color=discord.Color.blue(), reason="aegis: setup")
            criados.append("cargo @Staff")
        except Exception: pass

    if log_ch:     LOG_CHANNEL_ID     = log_ch.id
    if q_role:     QUARENTENA_ROLE_ID = q_role.id
    if staff_role: STAFF_ROLE_ID      = staff_role.id

    roles, canais = await fazer_backup(guild)
    lista = "\n".join(f"  + {c}" for c in criados) if criados else "  tudo ja configurado"
    await interaction.followup.send(embed=E(
        f"**setup concluido.**\n```\n{lista}\n  backup: {roles} cargos, {canais} canais\n```"
    ), ephemeral=True)

@tree.command(name="cfg", description="ajusta limites de deteccao")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_cfg(interaction: discord.Interaction, max_joins: int=None, join_window: int=None,
                  max_messages: int=None, msg_window: int=None, max_mentions: int=None):
    if max_joins:    config["max_joins"]    = max_joins
    if join_window:  config["join_window"]  = join_window
    if max_messages: config["max_messages"] = max_messages
    if msg_window:   config["msg_window"]   = msg_window
    if max_mentions: config["max_mentions"] = max_mentions
    await interaction.response.send_message(embed=E(
        f"```\n  raid    {config['max_joins']}x / {config['join_window']}s\n"
        f"  spam    {config['max_messages']}x / {config['msg_window']}s\n"
        f"  mencoes {config['max_mentions']}\n```"
    ), ephemeral=True)

@tree.command(name="perfil", description="salvar/carregar perfis de configuracao")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_perfil(interaction: discord.Interaction, acao: str, nome: str = None):
    chaves = ["max_joins","join_window","max_messages","msg_window","max_mentions",
              "antiraid","antispam","antiphishing","anti_zalgo","anti_invite","ai_mode"]

    if acao == "salvar" and nome:
        config["perfis"][nome] = {k: config[k] for k in chaves}
        await interaction.response.send_message(embed=E(f"perfil `{nome}` salvo."), ephemeral=True)

    elif acao == "carregar" and nome:
        if nome not in config["perfis"]:
            await interaction.response.send_message(embed=E(f"perfil `{nome}` nao existe.", COR_RED), ephemeral=True); return
        for k, v in config["perfis"][nome].items():
            config[k] = v
        await interaction.response.send_message(embed=E(f"perfil `{nome}` carregado."), ephemeral=True)

    elif acao == "lista":
        if not config["perfis"]:
            await interaction.response.send_message(embed=E("nenhum perfil salvo."), ephemeral=True); return
        lista = "\n".join(f"  {n}" for n in config["perfis"])
        await interaction.response.send_message(embed=E(f"perfis:\n```\n{lista}\n```"), ephemeral=True)

    else:
        await interaction.response.send_message(embed=E(
            "uso:\n```\n  /perfil salvar <nome>\n  /perfil carregar <nome>\n  /perfil lista\n```"
        ), ephemeral=True)

@tree.command(name="wl", description="whitelist add/remove")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_wl(interaction: discord.Interaction, usuario: discord.Member):
    if usuario.id in config["whitelist"]:
        config["whitelist"].discard(usuario.id)
        await interaction.response.send_message(embed=E(f"`{usuario}` removido da whitelist."), ephemeral=True)
    else:
        config["whitelist"].add(usuario.id)
        await interaction.response.send_message(embed=E(f"`{usuario}` adicionado a whitelist."), ephemeral=True)

@tree.command(name="bw", description="bane uma palavra (leve = so avisa antes de punir, grave = pune sempre)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(nivel=[
    app_commands.Choice(name="leve", value="leve"),
    app_commands.Choice(name="grave", value="grave"),
])
async def cmd_bw(interaction: discord.Interaction, palavra: str, nivel: app_commands.Choice[str] = None):
    nivel_v = nivel.value if nivel else "leve"
    chave = "banned_words_grave" if nivel_v == "grave" else "banned_words_leve"
    if palavra.lower() not in config[chave]:
        config[chave].append(palavra.lower())
        await interaction.response.send_message(embed=E(f"`{palavra}` banida ({nivel_v})."), ephemeral=True)
    else:
        await interaction.response.send_message(embed=E("ja estava banida."), ephemeral=True)

@tree.command(name="ubw", description="remove palavra banida")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_ubw(interaction: discord.Interaction, palavra: str):
    p = palavra.lower()
    removida = False
    for chave in ("banned_words_leve", "banned_words_grave"):
        if p in config[chave]:
            config[chave].remove(p)
            removida = True
    if removida:
        await interaction.response.send_message(embed=E(f"`{palavra}` removida."), ephemeral=True)
    else:
        await interaction.response.send_message(embed=E("nao estava banida."), ephemeral=True)

@tree.command(name="cl", description="marca um canal como livre (filtros leves desligados)")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_cl(interaction: discord.Interaction, canal: discord.TextChannel = None):
    canal = canal or interaction.channel
    config["canais_livres"].add(canal.id)
    await interaction.response.send_message(embed=E(
        f"`#{canal.name}` agora e canal livre.\n> caps, mensagem repetida e palavra leve ficam de boa aqui.\n"
        f"> anti-raid, phishing, zalgo e palavra grave continuam ativos."
    ), ephemeral=True)

@tree.command(name="ucl", description="remove um canal da lista de canais livres")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_ucl(interaction: discord.Interaction, canal: discord.TextChannel = None):
    canal = canal or interaction.channel
    if canal.id in config["canais_livres"]:
        config["canais_livres"].discard(canal.id)
        await interaction.response.send_message(embed=E(f"`#{canal.name}` removido dos canais livres."), ephemeral=True)
    else:
        await interaction.response.send_message(embed=E("esse canal nao era livre."), ephemeral=True)

@tree.command(name="honeypot", description="define o canal honeypot (ban imediato em quem mandar msg)")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_honeypot(interaction: discord.Interaction, canal: discord.TextChannel = None):
    global HONEYPOT_CHANNEL_ID
    if canal is None:
        HONEYPOT_CHANNEL_ID = None
        await interaction.response.send_message(embed=E("honeypot desativado."), ephemeral=True)
        return
    HONEYPOT_CHANNEL_ID = canal.id
    # garante que membros normais nao veem o canal
    try:
        await canal.set_permissions(interaction.guild.default_role,
                                    read_messages=False, send_messages=False)
        if STAFF_ROLE_ID:
            staff = interaction.guild.get_role(STAFF_ROLE_ID)
            if staff:
                await canal.set_permissions(staff, read_messages=True, send_messages=True)
    except Exception: pass
    await interaction.response.send_message(embed=E(
        f"```\n[aegis@server ~]$ honeypot --set\n"
        f"> canal  : #{canal.name}\n"
        f"> status : armed\n"
        f"> qualquer membro que mandar msg aqui = ban imediato\n```"
    ), ephemeral=True)

@tree.command(name="spamscore", description="testa o ml-score de uma mensagem")
@app_commands.checks.has_permissions(manage_messages=True)
async def cmd_spamscore(interaction: discord.Interaction, mensagem: str):
    score = spam_score(mensagem)
    nivel = "CLEAN" if score < 5 else ("SUSPEITO" if score < 8 else "SPAM")
    cor   = COR_CLEAN if score < 5 else (COR_WARN if score < 8 else COR_RED)
    e = discord.Embed(color=cor)
    e.description = (
        f"```\n[aegis@server ~]$ ml --score\n"
        f"> input : {mensagem[:60]}\n"
        f"> score : {score}/10\n"
        f"> label : {nivel}\n```"
    )
    e.set_footer(text="[aegis@server ~]$ ml --done")
    await interaction.response.send_message(embed=e, ephemeral=True)


@app_commands.checks.has_permissions(administrator=True)
async def cmd_backup(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    roles, canais = await fazer_backup(interaction.guild)
    await interaction.followup.send(embed=E(
        f"backup concluido.\n```\n  cargos   {roles}\n  canais   {canais}\n  horario  {backup_data['timestamp'][:19]}\n```"
    ), ephemeral=True)

@tree.command(name="mban", description="bane membros sem cargo (emergencia)")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_mban(interaction: discord.Interaction, confirmar: str):
    if confirmar.lower() != "confirmar":
        await interaction.response.send_message(embed=E("use `/mban confirmar`."), ephemeral=True); return
    await interaction.response.defer(ephemeral=True)
    count = 0
    for member in interaction.guild.members:
        if member.bot or member.id == interaction.user.id or member.id in config["whitelist"]: continue
        if len(member.roles) <= 1:
            try: await member.ban(reason="aegis: massban"); config["total_bans"] += 1; count += 1
            except Exception: pass
    await interaction.followup.send(embed=E(f"`{count}` banidos. servidor limpo.", COR_RED), ephemeral=True)

# ── INFO ─────────────────────────────────────────────────────

# ============================================================
#  PAINEL INTERATIVO
# ============================================================

class PainelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.pagina = "status"

    def embed_pagina(self):
        if self.pagina == "status":    return embed_status()
        if self.pagina == "protecoes": return self._embed_protecoes()
        if self.pagina == "shadow":    return self._embed_shadow()
        if self.pagina == "apelacoes": return self._embed_apelacoes()
        if self.pagina == "rep":       return self._embed_reputacao()
        return embed_status()

    def _embed_protecoes(self):
        def s(v): return "on " if v else "off"
        e = discord.Embed(color=COR_CLEAN)
        e.set_author(name="aegis - protecoes")
        linhas = (
            "  anti-raid      " + s(config["antiraid"]) + "\n" +
            "  anti-spam      " + s(config["antispam"]) + "\n" +
            "  anti-phishing  " + s(config["antiphishing"]) + "\n" +
            "  anti-zalgo     " + s(config["anti_zalgo"]) + "\n" +
            "  anti-invite    " + s(config["anti_invite"]) + "\n" +
            "  anti-repeated  " + s(config["anti_repeated"]) + "\n" +
            "  anti-nuke      " + s(config["anti_nuke"]) + "\n" +
            "  anti-alt       " + s(config["anti_alt"]) + "\n" +
            "  ia mode        " + s(config["ai_mode"]) + "\n" +
            "  lockdown       " + s(config["lockdown"]) + "\n" +
            "  emergencia     " + s(config["emergencia"]) + "\n" +
            "  quarentena     " + s(config["quarentena"]) + "\n" +
            "  captcha        " + s(config["captcha"]) + "\n" +
            "  silencioso     " + s(config["silencioso"]) + "\n" +
            "  shadow mute    " + s(config["shadow_mute"]) + "\n" +
            "  log edits      " + s(config["log_edits"]) + "\n" +
            "  log deletes    " + s(config["log_deletes"])
        )
        e.description = "```\n" + linhas + "\n```\n> clique nos botoes para alternar"
        e.set_footer(text="aegis - painel de protecoes")
        return e

    def _embed_shadow(self):
        e = discord.Embed(color=COR_CLEAN)
        e.set_author(name="aegis - shadow mutes ativos")
        if not config["shadow_muted"]:
            e.description = "> nenhum shadow mute ativo."
        else:
            linhas = ""
            for uid in list(config["shadow_muted"])[:20]:
                linhas += "  " + str(uid) + "\n"
            e.description = "**" + str(len(config["shadow_muted"])) + " usuario(s) em shadow mute:**\n```\n" + linhas + "```"
        e.set_footer(text="[aegis@server ~]$ /sunmute @user")
        return e

    def _embed_apelacoes(self):
        e = discord.Embed(color=COR_CLEAN)
        e.set_author(name="aegis - apelacoes")
        pendentes = {uid: d for uid, d in apelacoes.items() if d["status"] == "pendente"}
        if not pendentes:
            e.description = "> nenhuma apelacao pendente."
        else:
            linhas = ""
            for uid, d in list(pendentes.items())[:10]:
                linhas += "  " + str(uid) + " - " + d["user"] + "\n  > " + d["motivo"][:40] + "\n"
            e.description = "**" + str(len(pendentes)) + " apelacao(oes) pendente(s):**\n```\n" + linhas + "```"
        e.set_footer(text="[aegis@server ~]$ /apelacao aceitar|rejeitar <id>")
        return e

    def _embed_reputacao(self):
        e = discord.Embed(color=COR_CLEAN)
        e.set_author(name="aegis - reputacao dos membros")
        if not reputacao:
            e.description = "> nenhum dado de reputacao ainda."
        else:
            ordenado = sorted(reputacao.items(), key=lambda x: x[1])
            piores   = ordenado[:5]
            melhores = ordenado[-5:][::-1]
            linhas = "  -- piores --\n"
            for uid, r in piores:
                linhas += "  " + str(uid) + "  " + ("+" if r >= 0 else "") + str(r) + " (" + reputacao_str(uid) + ")\n"
            linhas += "\n  -- melhores --\n"
            for uid, r in melhores:
                linhas += "  " + str(uid) + "  " + ("+" if r >= 0 else "") + str(r) + " (" + reputacao_str(uid) + ")\n"
            e.description = "```\n" + linhas + "```"
        e.set_footer(text="[aegis@server ~]$ /rep @user +N")
        return e

    # ── BOTOES DE NAVEGACAO ──────────────────────────────────

    @discord.ui.button(label="status", style=discord.ButtonStyle.secondary, row=0)
    async def btn_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pagina = "status"
        self._atualizar_botoes()
        await interaction.response.edit_message(embed=self.embed_pagina(), view=self)

    @discord.ui.button(label="proteções", style=discord.ButtonStyle.secondary, row=0)
    async def btn_protecoes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pagina = "protecoes"
        self._atualizar_botoes()
        await interaction.response.edit_message(embed=self.embed_pagina(), view=self)

    @discord.ui.button(label="shadow mutes", style=discord.ButtonStyle.secondary, row=0)
    async def btn_shadow(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pagina = "shadow"
        self._atualizar_botoes()
        await interaction.response.edit_message(embed=self.embed_pagina(), view=self)

    @discord.ui.button(label="apelacoes", style=discord.ButtonStyle.secondary, row=1)
    async def btn_apelacoes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pagina = "apelacoes"
        self._atualizar_botoes()
        await interaction.response.edit_message(embed=self.embed_pagina(), view=self)

    @discord.ui.button(label="reputação", style=discord.ButtonStyle.secondary, row=1)
    async def btn_rep(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.pagina = "rep"
        self._atualizar_botoes()
        await interaction.response.edit_message(embed=self.embed_pagina(), view=self)

    # ── BOTOES DE TOGGLE RAPIDO ──────────────────────────────

    @discord.ui.button(label="⚡ toggle raid", style=discord.ButtonStyle.danger, row=2)
    async def btn_raid(self, interaction: discord.Interaction, button: discord.ui.Button):
        config["antiraid"] = not config["antiraid"]
        await interaction.response.edit_message(embed=self.embed_pagina(), view=self)

    @discord.ui.button(label="💬 toggle spam", style=discord.ButtonStyle.danger, row=2)
    async def btn_spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        config["antispam"] = not config["antispam"]
        await interaction.response.edit_message(embed=self.embed_pagina(), view=self)

    @discord.ui.button(label="🤖 toggle ia", style=discord.ButtonStyle.danger, row=2)
    async def btn_ia(self, interaction: discord.Interaction, button: discord.ui.Button):
        config["ai_mode"] = not config["ai_mode"]
        await interaction.response.edit_message(embed=self.embed_pagina(), view=self)

    @discord.ui.button(label="🔒 lockdown", style=discord.ButtonStyle.danger, row=3)
    async def btn_lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        if config["lockdown"]:
            await desativar_lockdown(interaction.guild)
        else:
            await ativar_lockdown(interaction.guild)
        await interaction.response.edit_message(embed=self.embed_pagina(), view=self)

    @discord.ui.button(label="🚨 emergência", style=discord.ButtonStyle.danger, row=3)
    async def btn_emerg(self, interaction: discord.Interaction, button: discord.ui.Button):
        if config["emergencia"]:
            await desativar_emergencia(interaction.guild)
        else:
            await ativar_emergencia(interaction.guild, "painel interativo")
        await interaction.response.edit_message(embed=self.embed_pagina(), view=self)

    @discord.ui.button(label="🔇 silencioso", style=discord.ButtonStyle.secondary, row=3)
    async def btn_silencioso(self, interaction: discord.Interaction, button: discord.ui.Button):
        config["silencioso"] = not config["silencioso"]
        await interaction.response.edit_message(embed=self.embed_pagina(), view=self)

    def _atualizar_botoes(self):
        estilos = {
            "status"   : self.btn_status,
            "protecoes": self.btn_protecoes,
            "shadow"   : self.btn_shadow,
            "apelacoes": self.btn_apelacoes,
            "rep"      : self.btn_rep,
        }
        for nome, btn in estilos.items():
            btn.style = discord.ButtonStyle.primary if self.pagina == nome else discord.ButtonStyle.secondary

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


@tree.command(name="s", description="painel interativo do aegis")
@app_commands.checks.has_permissions(manage_messages=True)
async def cmd_s(interaction: discord.Interaction):
    view = PainelView()
    await interaction.response.send_message(embed=view.embed_pagina(), view=view, ephemeral=True)

@tree.command(name="ajuda", description="lista todos os comandos")
async def cmd_ajuda(interaction: discord.Interaction):
    await interaction.response.send_message(embed=embed_ajuda(), ephemeral=True)

@tree.command(name="ver", description="analisa risco de um usuario")
@app_commands.checks.has_permissions(manage_messages=True)
async def cmd_ver(interaction: discord.Interaction, usuario: discord.Member):
    risco, motivos = calcular_risco(usuario)
    nivel = "baixo" if risco <= 3 else "medio" if risco <= 5 else "alto" if risco <= 7 else "critico"
    idade = (datetime.utcnow() - usuario.created_at.replace(tzinfo=None)).days
    e = discord.Embed(color=COR_RED if risco >= 7 else COR_DIM if risco >= 4 else COR_CLEAN)
    e.set_author(name=f"[aegis@server ~]$ ia --risk {usuario}", icon_url=usuario.display_avatar.url)
    e.description = (
        f"```\n  score      {risco}/10\n  risco      {nivel}\n  conta      {idade} dias\n"
        f"  avatar     {'sim' if usuario.avatar else 'nao'}\n"
        f"  infras     {infra_tracker[usuario.id]}/5\n"
        f"  reputacao  {reputacao_str(usuario.id)} ({reputacao[usuario.id]})\n"
        f"  shadow     {'sim' if usuario.id in config['shadow_muted'] else 'nao'}\n```"
        + (f"> {', '.join(motivos)}" if motivos else "")
    )
    e.set_footer(text="[aegis@server ~]$")
    await interaction.response.send_message(embed=e, ephemeral=True)

@tree.command(name="rl", description="log de raids")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_rl(interaction: discord.Interaction):
    if not raid_log:
        await interaction.response.send_message(embed=E("nenhum raid. ate agora."), ephemeral=True); return
    linhas = "".join(f"  {i}. {'auto' if r['auto'] else 'manual'} — {r['time'][:19]}\n" for i, r in enumerate(raid_log[-10:], 1))
    await interaction.response.send_message(embed=E(f"```{linhas}```\n> {len(raid_log)} total.", COR_RED), ephemeral=True)

@tree.command(name="resumo", description="atividade dos ultimos 7 dias")
@app_commands.checks.has_permissions(manage_messages=True)
async def cmd_resumo(interaction: discord.Interaction):
    hist = [h for h in config["historico"]
            if datetime.utcnow() - datetime.fromisoformat(h["time"]) <= timedelta(days=7)]
    tipos = ["raid","punicao","ban","kick","warn","emergencia","saida"]
    contagens = {t: sum(1 for h in hist if h["tipo"] == t) for t in tipos}
    linhas = "\n".join(f"  {k:<12} {v}" for k, v in contagens.items())
    await interaction.response.send_message(embed=E(f"**ultimos 7 dias:**\n```\n{linhas}\n```"), ephemeral=True)


# ============================================================
#  ERROS
# ============================================================

@tree.error
async def on_error(interaction: discord.Interaction, error):
    txt = "sem permissao." if isinstance(error, app_commands.MissingPermissions) else str(error)
    try: await interaction.response.send_message(embed=E(txt, COR_RED), ephemeral=True)
    except Exception: await interaction.followup.send(embed=E(txt, COR_RED), ephemeral=True)


# ============================================================
client.run(TOKEN)
