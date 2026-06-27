import discord
from discord import app_commands
from discord.ext import tasks
from datetime import datetime, timedelta
from collections import defaultdict
import random
import re
import unicodedata
import asyncio

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
AUTO_ROLE_ID       = None   # cargo dado automaticamente após verificação

COR_CLEAN = 0x1a1a1a
COR_RED   = 0xe03030
COR_DIM   = 0x444444

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
    "silencioso"      : False,  # age sem avisar no canal
    "shadow_mute"     : False,  # silencia sem o usuário saber
    # modos
    "lockdown"        : False,
    "emergencia"      : False,
    "quarentena"      : False,
    "captcha"         : False,
    "ai_mode"         : True,
    # limites
    "quarentena_tempo": 10,
    "max_joins"       : 5,
    "join_window"     : 10,
    "max_messages"    : 6,
    "msg_window"      : 5,
    "max_mentions"    : 5,
    "max_channel_ops" : 3,
    "channel_op_window": 10,
    "max_mass_ban"    : 3,
    "mass_ban_window" : 10,
    # listas
    "whitelist"       : set(),
    "banned_words"    : [],
    "shadow_muted"    : set(),   # usuários em shadow mute
    # stats
    "raid_score"      : 0,
    "total_raids"     : 0,
    "total_bans"      : 0,
    "total_warns"     : 0,
    "historico"       : [],
    # perfis de config salvos
    "perfis"          : {},
}

# trackers
join_tracker        = []
msg_tracker         = defaultdict(list)
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

# rastrear nomes anteriores para detectar imitação
nomes_anteriores    = defaultdict(list)
# rastrear horários de entrada para detectar alts
entrada_horarios    = []   # [(datetime, member_id)]

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
FRASES_RAID  = ["tentaram. nao conseguiram.","bloqueado antes de comecar.","o servidor nao e de brincadeira.","raid detectado. eliminado."]
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


# ============================================================
#  EMBEDS
# ============================================================

def E(desc, cor=COR_CLEAN):
    e = discord.Embed(description=desc, color=cor)
    e.set_footer(text="aegis")
    return e

def embed_ban(m, motivo, mod):
    e = discord.Embed(color=COR_RED)
    e.set_author(name=f"ban — {m}", icon_url=m.display_avatar.url)
    e.description = f"```{motivo}```\n*{random.choice(FRASES_BAN)}*"
    e.add_field(name="mod",  value=f"`{mod}`",    inline=True)
    e.add_field(name="id",   value=f"`{m.id}`",   inline=True)
    e.add_field(name="data", value=f"<t:{ts()}:R>",inline=True)
    e.set_footer(text="aegis")
    return e

def embed_kick(m, motivo, mod):
    e = discord.Embed(color=COR_DIM)
    e.set_author(name=f"kick — {m}", icon_url=m.display_avatar.url)
    e.description = f"```{motivo}```\n*{random.choice(FRASES_KICK)}*"
    e.add_field(name="mod",  value=f"`{mod}`",    inline=True)
    e.add_field(name="id",   value=f"`{m.id}`",   inline=True)
    e.add_field(name="data", value=f"<t:{ts()}:R>",inline=True)
    e.set_footer(text="aegis")
    return e

def embed_warn(m, motivo, mod, nivel):
    barra = "▰" * nivel + "▱" * (5 - nivel)
    e = discord.Embed(color=COR_CLEAN)
    e.set_author(name=f"warn — {m}", icon_url=m.display_avatar.url)
    e.description = f"```{motivo}```\n*{random.choice(FRASES_WARN)}*"
    e.add_field(name="mod",       value=f"`{mod}`",     inline=True)
    e.add_field(name="nivel",     value=f"`{nivel}/5`", inline=True)
    e.add_field(name="progresso", value=f"`{barra}`",   inline=True)
    e.set_footer(text="aegis")
    return e

def embed_auto(acao, motivo, usuario, nivel=None):
    cores = {1: COR_CLEAN, 2: COR_DIM, 3: COR_RED}
    e = discord.Embed(color=cores.get(nivel, COR_CLEAN))
    e.set_author(name=f"aegis — {acao}")
    e.description = f"`{usuario}`\n> {motivo}"
    if nivel:
        e.add_field(name="infra", value=f"`{'▰'*nivel+'▱'*(5-nivel)}` {nivel}/5", inline=True)
    e.set_footer(text=f"aegis • {datetime.utcnow().strftime('%H:%M:%S')}")
    return e

def embed_status():
    def s(v): return "on" if v else "off"
    e = discord.Embed(color=COR_CLEAN)
    e.set_author(name="aegis — painel")
    e.description = (
        "```\n"
        f"  anti-raid      {s(config['antiraid'])}\n"
        f"  anti-spam      {s(config['antispam'])}\n"
        f"  anti-phish     {s(config['antiphishing'])}\n"
        f"  anti-zalgo     {s(config['anti_zalgo'])}\n"
        f"  anti-invite    {s(config['anti_invite'])}\n"
        f"  anti-repeated  {s(config['anti_repeated'])}\n"
        f"  anti-nuke      {s(config['anti_nuke'])}\n"
        f"  anti-alt       {s(config['anti_alt'])}\n"
        f"  ia mode        {s(config['ai_mode'])}\n"
        f"  lockdown       {s(config['lockdown'])}\n"
        f"  emergencia     {s(config['emergencia'])}\n"
        f"  quarentena     {s(config['quarentena'])}\n"
        f"  captcha        {s(config['captcha'])}\n"
        f"  silencioso     {s(config['silencioso'])}\n"
        f"  shadow mute    {s(config['shadow_mute'])}\n"
        f"  log edits      {s(config['log_edits'])}\n"
        f"  log deletes    {s(config['log_deletes'])}\n"
        "```"
    )
    e.add_field(name="bans",   value=f"`{config['total_bans']}`",            inline=True)
    e.add_field(name="warns",  value=f"`{config['total_warns']}`",           inline=True)
    e.add_field(name="raids",  value=f"`{config['total_raids']}`",           inline=True)
    e.add_field(name="wl",     value=f"`{len(config['whitelist'])}` users",  inline=True)
    e.add_field(name="shadow", value=f"`{len(config['shadow_muted'])}` muted",inline=True)
    e.add_field(name="ia risk",value=f"`{config['raid_score']}/10`",         inline=True)
    e.set_footer(text="aegis")
    return e

def embed_ajuda():
    e = discord.Embed(color=COR_CLEAN)
    e.set_author(name="aegis — comandos")
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
        "  /lock        lockdown on/off\n"
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
        "  /bw  palavra banir palavra\n"
        "  /ubw palavra remover\n"
        "  /backup      salvar servidor\n"
        "```"
    ), inline=False)
    e.add_field(name="info", value=(
        "```\n"
        "  /s       painel de status\n"
        "  /ver @u  analise de risco\n"
        "  /rl      log de raids\n"
        "  /resumo  atividade semanal\n"
        "  /ajuda   esta mensagem\n"
        "```"
    ), inline=False)
    e.set_footer(text="aegis • duracao: 10s 5m 2h 1d")
    return e

def embed_varredura(resultado):
    suspeitos = resultado["suspeitos"]
    e = discord.Embed(color=COR_RED if suspeitos else COR_CLEAN)
    e.set_author(name="aegis — varredura")
    e.description = f"`{resultado['total']}` membros · `{len(suspeitos)}` suspeitos"
    if suspeitos:
        lista = "\n".join(f"  [{s['score']}/10] {s['nome']} — {s['motivo']}" for s in suspeitos[:15])
        if len(suspeitos) > 15: lista += f"\n  ...e mais {len(suspeitos)-15}"
        e.add_field(name="lista", value=f"```{lista}```", inline=False)
    else:
        e.add_field(name="resultado", value="`nenhum suspeito.`", inline=False)
    e.set_footer(text="aegis")
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

def analisar_mensagem(content: str):
    lower = content.lower()
    for kw in RAID_KEYWORDS:
        if kw in lower: return True, f"palavra: {kw}"
    for p in PHISHING_PATTERNS:
        if re.search(p, lower): return True, "link suspeito"
    if len(content) > 10:
        caps = sum(1 for c in content if c.isupper())
        if caps / len(content) > 0.7: return True, "caps excessivo"
    emojis = re.findall(r'[\U00010000-\U0010ffff]|[\u2600-\u27BF]', content)
    if len(emojis) > 15: return True, "flood de emojis"
    return False, ""


# ============================================================
#  PUNICOES E REPUTACAO
# ============================================================

async def punir(member: discord.Member, motivo: str, guild: discord.Guild):
    if member.id in config["whitelist"]: return
    infra_tracker[member.id] += 1
    reputacao[member.id] -= 2
    nivel = min(infra_tracker[member.id], 5)
    tipo, desc = PUNICOES[nivel]
    config["total_warns"] += 1
    registrar("punicao", f"{member} — {desc} — {motivo}")
    comportamento[member.id].append(f"[PUNICAO:{tipo}]")

    if not config["silencioso"]:
        e = embed_auto(desc, motivo, str(member), min(nivel, 3))
        await _log(guild, e)

    try:
        dm = discord.Embed(description=f"> **{guild.name}** — {desc}\n> motivo: {motivo}", color=COR_RED)
        dm.set_footer(text="aegis")
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

async def ativar_lockdown(guild: discord.Guild, auto=False):
    config["lockdown"] = True
    config["total_raids"] += 1
    raid_log.append({"time": datetime.utcnow().isoformat(), "auto": auto})
    registrar("raid", f"lockdown {'auto' if auto else 'manual'}")
    for ch in guild.text_channels:
        try: await ch.set_permissions(guild.default_role, send_messages=False)
        except Exception: pass
    await _log_t(guild, f"**raid detectado. lockdown ativado.**\n> {random.choice(FRASES_RAID)}\n> use `/lock` para restaurar.", COR_RED)

async def desativar_lockdown(guild: discord.Guild):
    config["lockdown"] = False
    for ch in guild.text_channels:
        try: await ch.set_permissions(guild.default_role, send_messages=None)
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
    e.set_footer(text="aegis • verificacao automatica")
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
    await tree.sync()
    print(f"\n  aegis — online como {client.user}")
    print(f"  {len(client.guilds)} servidor(es)\n")
    loop_status.start()
    checar_quarentena.start()
    checar_captcha.start()
    resumo_semanal.start()

@tasks.loop(minutes=5)
async def loop_status():
    ops = ["o servidor", f"{sum(g.member_count for g in client.guilds)} membros",
           f"{config['total_bans']} eliminados", "por raids"]
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=random.choice(ops)
    ))

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
        join_tracker.pop(0)

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

    uid, guild, now = message.author.id, message.guild, datetime.utcnow()
    content = message.content

    # Anti-spam
    if config["antispam"]:
        msg_tracker[uid].append(now)
        msg_tracker[uid] = [t for t in msg_tracker[uid] if now - t <= timedelta(seconds=config["msg_window"])]
        if len(msg_tracker[uid]) >= config["max_messages"]:
            try: await message.delete()
            except Exception: pass
            await punir(message.author, "spam", guild); return

    # Anti-repeated
    if config["anti_repeated"]:
        repeated_tracker[uid].append(content.lower().strip())
        repeated_tracker[uid] = repeated_tracker[uid][-5:]
        if len(repeated_tracker[uid]) >= 3 and len(set(repeated_tracker[uid][-3:])) == 1:
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

    # Palavras banidas
    lower = content.lower()
    for word in config["banned_words"]:
        if word in lower:
            try: await message.delete()
            except Exception: pass
            await punir(message.author, f"palavra banida: {word}", guild); return

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

    # IA geral
    if config["ai_mode"]:
        suspeita, motivo = analisar_mensagem(content)
        if suspeita:
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
    e.set_author(name=f"mensagem editada — {before.author}", icon_url=before.author.display_avatar.url)
    e.add_field(name="antes", value=f"```{before.content[:500] if before.content else 'vazio'}```", inline=False)
    e.add_field(name="depois",value=f"```{after.content[:500]  if after.content  else 'vazio'}```", inline=False)
    e.add_field(name="canal", value=before.channel.mention, inline=True)
    e.add_field(name="data",  value=f"<t:{ts()}:R>",        inline=True)
    e.set_footer(text="aegis")
    await _log(before.guild, e)

@client.event
async def on_message_delete(message):
    if message.author.bot or not message.guild: return
    if not config["log_deletes"]: return
    e = discord.Embed(color=COR_DIM)
    e.set_author(name=f"mensagem deletada — {message.author}", icon_url=message.author.display_avatar.url)
    e.description = f"```{message.content[:800] if message.content else 'vazio'}```"
    e.add_field(name="canal", value=message.channel.mention, inline=True)
    e.add_field(name="data",  value=f"<t:{ts()}:R>",         inline=True)
    e.set_footer(text="aegis")
    await _log(message.guild, e)

@client.event
async def on_guild_channel_delete(channel):
    now = datetime.utcnow()
    channel_del_tracker.append(now)
    while channel_del_tracker and now - channel_del_tracker[0] > timedelta(seconds=config["channel_op_window"]):
        channel_del_tracker.pop(0)
    if len(channel_del_tracker) >= config["max_channel_ops"] and config["anti_nuke"]:
        await _log_t(channel.guild, f"**nuke detectado!** {len(channel_del_tracker)} canais deletados em {config['channel_op_window']}s\n> ativando emergencia e restaurando...", COR_RED)
        await ativar_emergencia(channel.guild, "exclusao em massa de canais (nuke)")
        restaurados = await restaurar_canais(channel.guild)
        await _log_t(channel.guild, f"anti-nuke: `{restaurados}` canais restaurados do backup.", COR_DIM)

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
    e.set_author(name=f"inf — {usuario}", icon_url=usuario.display_avatar.url)
    e.description = f"`{barra}` {nivel}/5\n> proximo: {proxima}\n> reputacao: {reputacao_str(usuario.id)}"
    e.set_footer(text="aegis")
    await interaction.response.send_message(embed=e, ephemeral=True)

@tree.command(name="reset", description="reseta infracoes")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_reset(interaction: discord.Interaction, usuario: discord.Member):
    infra_tracker[usuario.id] = 0
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

@tree.command(name="lock", description="lockdown on/off")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_lock(interaction: discord.Interaction):
    if config["lockdown"]:
        await desativar_lockdown(interaction.guild)
        await interaction.response.send_message(embed=E("lockdown desativado. canais abertos."), ephemeral=True)
    else:
        await ativar_lockdown(interaction.guild)
        await interaction.response.send_message(embed=E("lockdown ativado. tudo fechado.", COR_RED), ephemeral=True)

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

@tree.command(name="bw", description="bane uma palavra")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_bw(interaction: discord.Interaction, palavra: str):
    if palavra.lower() not in config["banned_words"]:
        config["banned_words"].append(palavra.lower())
        await interaction.response.send_message(embed=E(f"`{palavra}` banida."), ephemeral=True)
    else:
        await interaction.response.send_message(embed=E("ja estava banida."), ephemeral=True)

@tree.command(name="ubw", description="remove palavra banida")
@app_commands.checks.has_permissions(administrator=True)
async def cmd_ubw(interaction: discord.Interaction, palavra: str):
    if palavra.lower() in config["banned_words"]:
        config["banned_words"].remove(palavra.lower())
        await interaction.response.send_message(embed=E(f"`{palavra}` removida."), ephemeral=True)
    else:
        await interaction.response.send_message(embed=E("nao estava banida."), ephemeral=True)

@tree.command(name="backup", description="faz backup dos cargos e canais")
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
        e.set_footer(text="aegis - use /sunmute para remover")
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
        e.set_footer(text="aegis - /apelacao aceitar/rejeitar <id>")
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
        e.set_footer(text="aegis - /rep @user para ajustar")
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
    e.set_author(name=f"ia — {usuario}", icon_url=usuario.display_avatar.url)
    e.description = (
        f"```\n  score      {risco}/10\n  risco      {nivel}\n  conta      {idade} dias\n"
        f"  avatar     {'sim' if usuario.avatar else 'nao'}\n"
        f"  infras     {infra_tracker[usuario.id]}/5\n"
        f"  reputacao  {reputacao_str(usuario.id)} ({reputacao[usuario.id]})\n"
        f"  shadow     {'sim' if usuario.id in config['shadow_muted'] else 'nao'}\n```"
        + (f"> {', '.join(motivos)}" if motivos else "")
    )
    e.set_footer(text="aegis")
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
