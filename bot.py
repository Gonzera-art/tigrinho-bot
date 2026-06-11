import discord
import json
import random
import asyncio
import aiohttp
from datetime import date
from discord.ext import commands
from discord.ui import View

TOKEN = "SEU_TOKEN_AQUI"
PREFIX = "!"
DONO_ID = 1277801876523454547
CANAL_BOT = 1513290347973967962
OPENAI_KEY = ""

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

async def gerar_pergunta():
    categorias = ["história", "matemática", "geografia", "ciências", "cultura geral", "esportes", "tecnologia"]
    dificuldades = ["fácil", "médio", "difícil"]
    categoria = random.choice(categorias)
    dif = random.choice(dificuldades)
    prompt = f"""Crie uma pergunta de quiz de {categoria} com dificuldade {dif}.
Responda APENAS em JSON neste formato exato sem nenhum texto adicional:
{{"p": "pergunta aqui", "ops": ["A) opcao1", "B) opcao2", "C) opcao3", "D) opcao4"], "r": "A", "dif": "{dif}"}}
A resposta correta deve variar entre A B C e D."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 300,
                    "messages": [{"role": "user", "content": prompt}]
                }
            ) as r:
                data = await r.json()
                texto = data["choices"][0]["message"]["content"].strip()
                inicio = texto.find("{")
                fim = texto.rfind("}") + 1
                texto = texto[inicio:fim]
                pergunta = json.loads(texto)
                return pergunta
    except Exception as e:
        print(f"Erro quiz: {e}")
        return None

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
            "wins": 0, "minigames": {"data": hoje, "pescar": 0, "cacar": 0, "minerar": 0, "roubar": 0}
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
    return u

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
    salvar(dados)
    nome_vencedor = lutas[luta_id]["jogadores"][vencedor_id]["nome"]
    del lutas[luta_id]
    await canal.send(f"🏆 **{nome_vencedor} venceu a luta** e roubou **{premio} fichas!**")

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
        if escolha == correta:
            u["fichas"] += self.fichas_ganho
            u["total"] += self.fichas_ganho
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
            dados = carregar()
            u = get_usuario(dados, self.user_id)
            u["fichas"] = max(0, u["fichas"] - self.fichas_perda)
            salvar(dados)
            if self.user_id in quizzes_ativos:
                msg = quizzes_ativos[self.user_id]
                del quizzes_ativos[self.user_id]
                try:
                    await msg.edit(
                        content=f"⏰ **Tempo esgotado!** A resposta era **{self.pergunta['r']}**!\n💸 Você perdeu **{self.fichas_perda} fichas!**",
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
    u["cooldowns"]["pescar"] = agora + get_cooldown(u, "pescar")
    restantes = LIMITE_DIARIO - u["minigames"]["pescar"]
    salvar(dados)
    await ctx.send(f"🎣 {ctx.author.mention} pescou e ganhou **{ganho} fichas!** 💰 (**{restantes}/3** restantes hoje)")
    await verificar_patente(ctx, u, dados)

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
    u["cooldowns"]["cacar"] = agora + get_cooldown(u, "cacar")
    restantes = LIMITE_DIARIO - u["minigames"]["cacar"]
    salvar(dados)
    await ctx.send(f"🏹 {ctx.author.mention} caçou e ganhou **{ganho} fichas!** 💰 (**{restantes}/3** restantes hoje)")
    await verificar_patente(ctx, u, dados)

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
    u["cooldowns"]["minerar"] = agora + get_cooldown(u, "minerar")
    restantes = LIMITE_DIARIO - u["minigames"]["minerar"]
    salvar(dados)
    await ctx.send(f"⛏️ {ctx.author.mention} minerou e ganhou **{ganho} fichas!** 💰 (**{restantes}/3** restantes hoje)")
    await verificar_patente(ctx, u, dados)

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
    if random.random() > 0.5:
        u["fichas"] += valor
        u["total"] += valor
        await ctx.send(f"🎰 {ctx.author.mention} ganhou **{valor} fichas!** 💰")
        await verificar_patente(ctx, u, dados)
    else:
        u["fichas"] -= valor
        await ctx.send(f"🎰 {ctx.author.mention} perdeu **{valor} fichas!** 😢")
    salvar(dados)

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
    if random.random() > 0.5:
        ganho = random.randint(50, min(300, alvo["fichas"]))
        u["fichas"] += ganho
        u["total"] += ganho
        alvo["fichas"] -= ganho
         await ctx.send(f"🦹 {ctx.author.mention} roubou **{ganho} fichas** de {membro.mention}! (**{restantes}/3** restantes hoje)")
         await verificar_patente(ctx, u, dados) 
    else:
        multa = random.randint(50, 150)
        u["fichas"] = max(0, u["fichas"] - multa)
        await ctx.send(f"🚔 {ctx.author.mention} foi pego e pagou **{multa} fichas** de multa! (**{restantes}/3** restantes hoje)")
    u["cooldowns"]["roubar"] = agora + get_cooldown(u, "roubar")
    salvar(dados)

@bot.command(name="quiz")
async def quiz(ctx):
    if ctx.author.id in quizzes_ativos:
        await ctx.send("❌ Você já tem um quiz ativo!")
        return
    await ctx.send("🧠 Gerando pergunta...")
    pergunta = await gerar_pergunta()
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
    else:
        ganho, perda = 120, 80
        emoji = "🔴"
    ops = "\n".join(pergunta["ops"])
    msg_texto = f"""🧠 **QUIZ** {emoji} **{dif.upper()}**

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

📅 **Tentativas hoje**
🎣 Pescar: **{mg.get('pescar', 0)}/3**
🏹 Caçar: **{mg.get('cacar', 0)}/3**
⛏️ Minerar: **{mg.get('minerar', 0)}/3**
🦹 Roubar: **{mg.get('roubar', 0)}/3**"""
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

@bot.command(name="loja")
async def loja(ctx):
    msg = "🛒 **Loja da Irmandade**\n\n"
    for key, item in LOJA.items():
        msg += f"{item['nome']} → **{item['preco']} fichas** | `!comprar {key}`\n"
    await ctx.send(msg)

@bot.command(name="comprar")
async def comprar(ctx, item: str):
    item = item.lower()
    if item not in LOJA:
        await ctx.send("❌ Item inválido! Use `!loja` para ver os itens.")
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
    except discord.Forbidden
        await ctx.send("❌ O bot não tem permissão para gerenciar cargos!")
       
        ("@bot.command(name="lutar")
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
`!quiz` — Responda perguntas e ganhe fichas

💰 **Economia**
`!saldo` — Ver suas fichas e patente
`!perfil [@pessoa]` — Ver perfil completo
`!top` — Ranking dos mais ricos
`!loja` — Ver a loja de cargos
`!comprar [item]` — Comprar um cargo

🏅 **Patentes**
🧢 Pobre → 10.000 fichas
💵 Rico → 50.000 fichas
💎 Milionário → 100.000 fichas
🏦 Bilionário → 500.000 fichas

⚔️ **Lutas**
`!lutar @pessoa` — Desafiar alguém
Use os botões para lutar!"""
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
