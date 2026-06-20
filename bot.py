import discord
import json
import random
import asyncio
from datetime import date, datetime, timedelta
from discord.ext import commands, tasks
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
    {
        "p": 'Quanto é 241 × 55 − 8333?',
        "ops": ['A) 5007', 'B) 5163', 'C) 4922', 'D) 4938'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 922 × 88 − 8142?',
        "ops": ['A) 74149', 'B) 75678', 'C) 75497', 'D) 72994'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 748 × 25 − 1914?',
        "ops": ['A) 16535', 'B) 17619', 'C) 16147', 'D) 16786'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 815 × 55 − 3544?',
        "ops": ['A) 41281', 'B) 42065', 'C) 41277', 'D) 42471'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 860 × 58 − 1569?',
        "ops": ['A) 48311', 'B) 48289', 'C) 50462', 'D) 50303'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 780 × 88 − 5162?',
        "ops": ['A) 66128', 'B) 63478', 'C) 60507', 'D) 63326'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 212 × 66 − 8266?',
        "ops": ['A) 5875', 'B) 5559', 'C) 5958', 'D) 5726'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 550 × 87 − 7951?',
        "ops": ['A) 41202', 'B) 39899', 'C) 40006', 'D) 40026'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 904 × 31 − 900?',
        "ops": ['A) 27911', 'B) 28316', 'C) 26188', 'D) 27124'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 613 × 44 − 2099?',
        "ops": ['A) 25552', 'B) 25864', 'C) 24873', 'D) 25501'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 805 × 54 − 8323?',
        "ops": ['A) 35351', 'B) 36250', 'C) 36686', 'D) 35147'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 421 × 49 − 251?',
        "ops": ['A) 19666', 'B) 19427', 'C) 20702', 'D) 20378'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 488 × 40 − 4361?',
        "ops": ['A) 15396', 'B) 15820', 'C) 15357', 'D) 15159'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 971 × 52 − 5288?',
        "ops": ['A) 45204', 'B) 43749', 'C) 46693', 'D) 46535'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 555 × 76 − 1153?',
        "ops": ['A) 41158', 'B) 43059', 'C) 41027', 'D) 42008'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 269 × 72 − 329?',
        "ops": ['A) 18276', 'B) 19039', 'C) 19012', 'D) 18088'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 373 × 30 − 831?',
        "ops": ['A) 10359', 'B) 10391', 'C) 10158', 'D) 10573'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 826 × 32 − 3752?',
        "ops": ['A) 22680', 'B) 23483', 'C) 22083', 'D) 23613'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 804 × 35 − 2317?',
        "ops": ['A) 26932', 'B) 25785', 'C) 26611', 'D) 25823'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 652 × 40 − 6260?',
        "ops": ['A) 18857', 'B) 19046', 'C) 20792', 'D) 19820'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 7x + (-10) = 284, qual é o valor de x?',
        "ops": ['A) 49', 'B) 34', 'C) 42', 'D) 50'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 9x + (-69) = -60, qual é o valor de x?',
        "ops": ['A) 1', 'B) 8', 'C) 7', 'D) -2'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 8x + (-14) = 298, qual é o valor de x?',
        "ops": ['A) 45', 'B) 38', 'C) 33', 'D) 39'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 4x + (65) = -75, qual é o valor de x?',
        "ops": ['A) -42', 'B) -29', 'C) -37', 'D) -35'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 4x + (35) = 203, qual é o valor de x?',
        "ops": ['A) 42', 'B) 40', 'C) 38', 'D) 50'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 8x + (8) = -40, qual é o valor de x?',
        "ops": ['A) -6', 'B) -1', 'C) -12', 'D) -2'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 4x + (18) = -10, qual é o valor de x?',
        "ops": ['A) -2', 'B) -6', 'C) 0', 'D) -7'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 11x + (13) = 244, qual é o valor de x?',
        "ops": ['A) 21', 'B) 29', 'C) 16', 'D) 19'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 9x + (-16) = 362, qual é o valor de x?',
        "ops": ['A) 42', 'B) 39', 'C) 34', 'D) 47'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 11x + (46) = 563, qual é o valor de x?',
        "ops": ['A) 42', 'B) 48', 'C) 47', 'D) 45'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 3x + (-33) = 147, qual é o valor de x?',
        "ops": ['A) 57', 'B) 60', 'C) 55', 'D) 65'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 7x + (-53) = 311, qual é o valor de x?',
        "ops": ['A) 54', 'B) 60', 'C) 52', 'D) 47'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 6x + (-59) = -59, qual é o valor de x?',
        "ops": ['A) 0', 'B) -8', 'C) -6', 'D) 5'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 2x + (-40) = -96, qual é o valor de x?',
        "ops": ['A) -28', 'B) -27', 'C) -33', 'D) -36'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Se 7x + (16) = 429, qual é o valor de x?',
        "ops": ['A) 52', 'B) 59', 'C) 63', 'D) 61'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (-4)x + (-96) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) 16', 'B) 12', 'C) 11', 'D) 14'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (5)x + (-84) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) 7', 'B) 1', 'C) 12', 'D) 5'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (-15)x + (44) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) 5', 'B) 11', 'C) 10', 'D) 14'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (13)x + (40) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) -11', 'B) -5', 'C) -10', 'D) -2'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (10)x + (-56) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) 0', 'B) 7', 'C) 3', 'D) 4'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (-11)x + (0) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) 11', 'B) 15', 'C) 8', 'D) 17'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (-39)x + (380) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) 20', 'B) 26', 'C) 16', 'D) 18'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (-21)x + (38) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) 19', 'B) 17', 'C) 20', 'D) 18'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (-16)x + (-80) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) 24', 'B) 20', 'C) 14', 'D) 22'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (27)x + (180) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) -15', 'B) -11', 'C) -12', 'D) -8'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (-18)x + (80) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) 10', 'B) 16', 'C) 12', 'D) 7'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (-15)x + (56) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) 9', 'B) 10', 'C) 12', 'D) 8'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (8)x + (15) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) -3', 'B) -2', 'C) -7', 'D) 1'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (17)x + (52) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) -5', 'B) -4', 'C) -6', 'D) -9'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'A equação x² + (-5)x + (-266) = 0 tem duas raízes inteiras. Qual é a MAIOR das duas raízes?',
        "ops": ['A) 24', 'B) 16', 'C) 19', 'D) 22'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 62 e 60?',
        "ops": ['A) -1', 'B) 6', 'C) 2', 'D) 0'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 54 e 82?',
        "ops": ['A) 0', 'B) 2', 'C) 1', 'D) -2'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 57 e 29?',
        "ops": ['A) 0', 'B) -3', 'C) 3', 'D) 1'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 80 e 33?',
        "ops": ['A) 5', 'B) -3', 'C) 1', 'D) -1'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 32 e 15?',
        "ops": ['A) 1', 'B) 5', 'C) -3', 'D) -2'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 50 e 39?',
        "ops": ['A) -1', 'B) 1', 'C) 0', 'D) 5'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 74 e 25?',
        "ops": ['A) -2', 'B) 2', 'C) 3', 'D) 1'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 83 e 78?',
        "ops": ['A) 2', 'B) 1', 'C) 0', 'D) 4'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 23 e 75?',
        "ops": ['A) 0', 'B) 2', 'C) -1', 'D) 1'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 53 e 96?',
        "ops": ['A) 4', 'B) 1', 'C) 2', 'D) 3'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 40 e 56?',
        "ops": ['A) 13', 'B) 8', 'C) 11', 'D) 12'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MDC (máximo divisor comum) entre 84 e 96?',
        "ops": ['A) 12', 'B) 4', 'C) 13', 'D) 23'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 26 e 23?',
        "ops": ['A) 598', 'B) 612', 'C) 536', 'D) 566'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 15 e 13?',
        "ops": ['A) 197', 'B) 200', 'C) 221', 'D) 195'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 27 e 32?',
        "ops": ['A) 768', 'B) 973', 'C) 864', 'D) 892'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 27 e 9?',
        "ops": ['A) 17', 'B) 29', 'C) 27', 'D) 22'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 14 e 27?',
        "ops": ['A) 393', 'B) 397', 'C) 389', 'D) 378'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 27 e 6?',
        "ops": ['A) 54', 'B) 51', 'C) 45', 'D) 64'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 26 e 7?',
        "ops": ['A) 201', 'B) 202', 'C) 165', 'D) 182'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 29 e 11?',
        "ops": ['A) 354', 'B) 290', 'C) 319', 'D) 337'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 27 e 20?',
        "ops": ['A) 568', 'B) 540', 'C) 502', 'D) 605'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 11 e 32?',
        "ops": ['A) 352', 'B) 381', 'C) 360', 'D) 385'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 23 e 32?',
        "ops": ['A) 625', 'B) 661', 'C) 736', 'D) 754'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o MMC (mínimo múltiplo comum) entre 27 e 28?',
        "ops": ['A) 752', 'B) 756', 'C) 785', 'D) 711'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De quantas formas diferentes é possível organizar 5 livros distintos em uma estante?',
        "ops": ['A) 102', 'B) 120', 'C) 131', 'D) 116'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De quantas formas diferentes é possível organizar 6 livros distintos em uma estante?',
        "ops": ['A) 712', 'B) 767', 'C) 720', 'D) 741'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De quantas formas diferentes é possível organizar 7 livros distintos em uma estante?',
        "ops": ['A) 5398', 'B) 5060', 'C) 5285', 'D) 5040'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De quantas formas diferentes é possível organizar 8 livros distintos em uma estante?',
        "ops": ['A) 42963', 'B) 41053', 'C) 36731', 'D) 40320'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De quantas formas diferentes é possível organizar 9 livros distintos em uma estante?',
        "ops": ['A) 338482', 'B) 362880', 'C) 393390', 'D) 389846'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 11 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 7 pessoas (sem importar a ordem)?',
        "ops": ['A) 298', 'B) 346', 'C) 330', 'D) 284'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 7 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 6 pessoas (sem importar a ordem)?',
        "ops": ['A) -3', 'B) 7', 'C) 11', 'D) 3'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 14 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 10 pessoas (sem importar a ordem)?',
        "ops": ['A) 1098', 'B) 899', 'C) 1001', 'D) 943'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 8 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 6 pessoas (sem importar a ordem)?',
        "ops": ['A) 28', 'B) 30', 'C) 29', 'D) 38'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 8 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 3 pessoas (sem importar a ordem)?',
        "ops": ['A) 54', 'B) 56', 'C) 64', 'D) 47'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 10 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 7 pessoas (sem importar a ordem)?',
        "ops": ['A) 120', 'B) 129', 'C) 110', 'D) 108'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 8 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 7 pessoas (sem importar a ordem)?',
        "ops": ['A) 2', 'B) 18', 'C) 11', 'D) 8'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 10 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 5 pessoas (sem importar a ordem)?',
        "ops": ['A) 252', 'B) 279', 'C) 275', 'D) 256'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 8 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 4 pessoas (sem importar a ordem)?',
        "ops": ['A) 63', 'B) 70', 'C) 75', 'D) 81'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 6 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 2 pessoas (sem importar a ordem)?',
        "ops": ['A) 13', 'B) 15', 'C) 16', 'D) 23'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 14 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 5 pessoas (sem importar a ordem)?',
        "ops": ['A) 2002', 'B) 2101', 'C) 2112', 'D) 1761'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'De um grupo de 9 pessoas, de quantas formas diferentes pode-se escolher uma comissão de 7 pessoas (sem importar a ordem)?',
        "ops": ['A) 32', 'B) 36', 'C) 37', 'D) 41'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 798?',
        "ops": ['A) 17', 'B) 19', 'C) 16', 'D) 18'],
        "r": 'C',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 632?',
        "ops": ['A) 8', 'B) 7', 'C) 11', 'D) 5'],
        "r": 'A',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 422?',
        "ops": ['A) 3', 'B) 2', 'C) 1', 'D) 4'],
        "r": 'D',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 91?',
        "ops": ['A) 5', 'B) 2', 'C) 8', 'D) 4'],
        "r": 'D',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 593?',
        "ops": ['A) 3', 'B) 5', 'C) 2', 'D) 0'],
        "r": 'C',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 427?',
        "ops": ['A) 4', 'B) 0', 'C) 6', 'D) 7'],
        "r": 'A',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 532?',
        "ops": ['A) 12', 'B) 15', 'C) 13', 'D) 16'],
        "r": 'A',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 98?',
        "ops": ['A) 2', 'B) 10', 'C) 3', 'D) 6'],
        "r": 'D',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 455?',
        "ops": ['A) 4', 'B) 11', 'C) 8', 'D) 12'],
        "r": 'C',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 87?',
        "ops": ['A) 2', 'B) 4', 'C) 1', 'D) 6'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 826?',
        "ops": ['A) 9', 'B) 5', 'C) 8', 'D) 12'],
        "r": 'C',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos divisores positivos tem o número 307?',
        "ops": ['A) 5', 'B) 3', 'C) 1', 'D) 2'],
        "r": 'D',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Considerando a sequência de Fibonacci (1, 1, 2, 3, 5, 8...), qual é o 10º termo?',
        "ops": ['A) 55', 'B) 58', 'C) 46', 'D) 60'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Considerando a sequência de Fibonacci (1, 1, 2, 3, 5, 8...), qual é o 12º termo?',
        "ops": ['A) 154', 'B) 133', 'C) 138', 'D) 144'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Considerando a sequência de Fibonacci (1, 1, 2, 3, 5, 8...), qual é o 14º termo?',
        "ops": ['A) 391', 'B) 397', 'C) 332', 'D) 377'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Considerando a sequência de Fibonacci (1, 1, 2, 3, 5, 8...), qual é o 16º termo?',
        "ops": ['A) 999', 'B) 1050', 'C) 872', 'D) 987'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Considerando a sequência de Fibonacci (1, 1, 2, 3, 5, 8...), qual é o 18º termo?',
        "ops": ['A) 2584', 'B) 2794', 'C) 2507', 'D) 2582'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Considerando a sequência de Fibonacci (1, 1, 2, 3, 5, 8...), qual é o 20º termo?',
        "ops": ['A) 6765', 'B) 6984', 'C) 6643', 'D) 7153'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Considerando a sequência de Fibonacci (1, 1, 2, 3, 5, 8...), qual é o 22º termo?',
        "ops": ['A) 16120', 'B) 18516', 'C) 17711', 'D) 17274'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Considerando a sequência de Fibonacci (1, 1, 2, 3, 5, 8...), qual é o 24º termo?',
        "ops": ['A) 42303', 'B) 42391', 'C) 47386', 'D) 46368'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^9?',
        "ops": ['A) 467', 'B) 512', 'C) 494', 'D) 486'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^10?',
        "ops": ['A) 1024', 'B) 943', 'C) 1017', 'D) 987'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^11?',
        "ops": ['A) 2167', 'B) 2048', 'C) 2205', 'D) 2208'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^12?',
        "ops": ['A) 4397', 'B) 4165', 'C) 4096', 'D) 4051'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^13?',
        "ops": ['A) 8192', 'B) 7969', 'C) 7559', 'D) 7469'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^14?',
        "ops": ['A) 15889', 'B) 15584', 'C) 16384', 'D) 14775'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^15?',
        "ops": ['A) 32768', 'B) 31616', 'C) 30076', 'D) 33353'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^16?',
        "ops": ['A) 65536', 'B) 67857', 'C) 67097', 'D) 59855'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^17?',
        "ops": ['A) 120830', 'B) 133170', 'C) 131072', 'D) 125904'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^18?',
        "ops": ['A) 272360', 'B) 261216', 'C) 241787', 'D) 262144'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^19?',
        "ops": ['A) 493433', 'B) 524288', 'C) 502909', 'D) 494348'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 2^20?',
        "ops": ['A) 1016838', 'B) 1048532', 'C) 1048576', 'D) 1113100'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 3^9?',
        "ops": ['A) 19683', 'B) 17792', 'C) 19125', 'D) 18019'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 3^10?',
        "ops": ['A) 59049', 'B) 64506', 'C) 55585', 'D) 60916'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 3^11?',
        "ops": ['A) 159531', 'B) 166993', 'C) 168521', 'D) 177147'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 3^12?',
        "ops": ['A) 560776', 'B) 566224', 'C) 531441', 'D) 533167'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 3^13?',
        "ops": ['A) 1478522', 'B) 1594323', 'C) 1744881', 'D) 1445907'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quanto é 3^14?',
        "ops": ['A) 4561320', 'B) 5224976', 'C) 4782969', 'D) 4700238'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 250. Ele sofre um aumento de 42% e, depois, um desconto de 5% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 307', 'B) 347', 'C) 326', 'D) 337'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 200. Ele sofre um aumento de 38% e, depois, um desconto de 29% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 187', 'B) 215', 'C) 209', 'D) 196'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 150. Ele sofre um aumento de 8% e, depois, um desconto de 24% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 127', 'B) 120', 'C) 115', 'D) 123'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 500. Ele sofre um aumento de 26% e, depois, um desconto de 35% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 388', 'B) 410', 'C) 450', 'D) 417'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 120. Ele sofre um aumento de 22% e, depois, um desconto de 31% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 105', 'B) 101', 'C) 93', 'D) 103'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 250. Ele sofre um aumento de 24% e, depois, um desconto de 19% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 273', 'B) 265', 'C) 252', 'D) 251'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 150. Ele sofre um aumento de 14% e, depois, um desconto de 24% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 123', 'B) 130', 'C) 134', 'D) 117'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 400. Ele sofre um aumento de 22% e, depois, um desconto de 32% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 311', 'B) 320', 'C) 332', 'D) 340'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 750. Ele sofre um aumento de 29% e, depois, um desconto de 25% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 755', 'B) 707', 'C) 726', 'D) 791'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 250. Ele sofre um aumento de 30% e, depois, um desconto de 32% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 227', 'B) 221', 'C) 210', 'D) 214'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 250. Ele sofre um aumento de 18% e, depois, um desconto de 32% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 208', 'B) 189', 'C) 218', 'D) 201'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 900. Ele sofre um aumento de 11% e, depois, um desconto de 24% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 762', 'B) 693', 'C) 759', 'D) 815'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 400. Ele sofre um aumento de 22% e, depois, um desconto de 27% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 386', 'B) 356', 'C) 357', 'D) 389'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 600. Ele sofre um aumento de 22% e, depois, um desconto de 5% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 760', 'B) 733', 'C) 735', 'D) 695'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Um produto custa R$ 200. Ele sofre um aumento de 43% e, depois, um desconto de 23% sobre o novo preço. Qual é o preço final, em reais (arredondado)?',
        "ops": ['A) 220', 'B) 199', 'C) 204', 'D) 222'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 8536 por 86?',
        "ops": ['A) 46', 'B) 24', 'C) 22', 'D) 19'],
        "r": 'C',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 6627 por 10?',
        "ops": ['A) 5', 'B) 3', 'C) 10', 'D) 7'],
        "r": 'D',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 6185 por 88?',
        "ops": ['A) 36', 'B) 25', 'C) 29', 'D) 52'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 5762 por 46?',
        "ops": ['A) -3', 'B) 12', 'C) 25', 'D) 0'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 8051 por 87?',
        "ops": ['A) 44', 'B) 59', 'C) 47', 'D) 24'],
        "r": 'C',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 6085 por 83?',
        "ops": ['A) 4', 'B) 26', 'C) 10', 'D) 6'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 7764 por 66?',
        "ops": ['A) 42', 'B) 55', 'C) 26', 'D) 47'],
        "r": 'A',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 8098 por 61?',
        "ops": ['A) 46', 'B) 30', 'C) 57', 'D) 54'],
        "r": 'A',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 6259 por 19?',
        "ops": ['A) 12', 'B) 8', 'C) 4', 'D) 2'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 7456 por 20?',
        "ops": ['A) 10', 'B) 16', 'C) 15', 'D) 12'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 4729 por 62?',
        "ops": ['A) 20', 'B) 17', 'C) 3', 'D) 11'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o resto da divisão de 9967 por 86?',
        "ops": ['A) 76', 'B) 77', 'C) 65', 'D) 69'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 441?',
        "ops": ['A) 19', 'B) 15', 'C) 21', 'D) 23'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 484?',
        "ops": ['A) 20', 'B) 27', 'C) 19', 'D) 22'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 529?',
        "ops": ['A) 23', 'B) 21', 'C) 25', 'D) 18'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 576?',
        "ops": ['A) 29', 'B) 27', 'C) 24', 'D) 23'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 625?',
        "ops": ['A) 24', 'B) 28', 'C) 29', 'D) 25'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 676?',
        "ops": ['A) 25', 'B) 21', 'C) 30', 'D) 26'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 729?',
        "ops": ['A) 26', 'B) 27', 'C) 21', 'D) 30'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 784?',
        "ops": ['A) 28', 'B) 29', 'C) 26', 'D) 34'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 841?',
        "ops": ['A) 29', 'B) 30', 'C) 23', 'D) 32'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 900?',
        "ops": ['A) 30', 'B) 36', 'C) 24', 'D) 32'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 961?',
        "ops": ['A) 31', 'B) 29', 'C) 25', 'D) 36'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1024?',
        "ops": ['A) 32', 'B) 28', 'C) 29', 'D) 27'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1089?',
        "ops": ['A) 35', 'B) 33', 'C) 36', 'D) 34'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1156?',
        "ops": ['A) 29', 'B) 30', 'C) 32', 'D) 34'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1225?',
        "ops": ['A) 35', 'B) 41', 'C) 30', 'D) 40'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1296?',
        "ops": ['A) 36', 'B) 30', 'C) 37', 'D) 32'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1369?',
        "ops": ['A) 36', 'B) 39', 'C) 41', 'D) 37'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1444?',
        "ops": ['A) 34', 'B) 38', 'C) 42', 'D) 36'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1521?',
        "ops": ['A) 33', 'B) 34', 'C) 44', 'D) 39'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1600?',
        "ops": ['A) 36', 'B) 40', 'C) 44', 'D) 41'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1681?',
        "ops": ['A) 37', 'B) 38', 'C) 41', 'D) 47'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1764?',
        "ops": ['A) 38', 'B) 44', 'C) 42', 'D) 45'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1849?',
        "ops": ['A) 49', 'B) 41', 'C) 43', 'D) 48'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 1936?',
        "ops": ['A) 45', 'B) 39', 'C) 43', 'D) 44'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 2025?',
        "ops": ['A) 44', 'B) 45', 'C) 49', 'D) 48'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 2116?',
        "ops": ['A) 45', 'B) 46', 'C) 44', 'D) 43'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 2209?',
        "ops": ['A) 49', 'B) 52', 'C) 47', 'D) 42'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 2304?',
        "ops": ['A) 45', 'B) 44', 'C) 48', 'D) 54'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 2401?',
        "ops": ['A) 47', 'B) 52', 'C) 53', 'D) 49'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 2500?',
        "ops": ['A) 50', 'B) 56', 'C) 46', 'D) 47'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 2601?',
        "ops": ['A) 54', 'B) 47', 'C) 51', 'D) 55'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 2704?',
        "ops": ['A) 52', 'B) 49', 'C) 51', 'D) 54'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 2809?',
        "ops": ['A) 51', 'B) 49', 'C) 54', 'D) 53'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 2916?',
        "ops": ['A) 49', 'B) 51', 'C) 54', 'D) 52'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 3025?',
        "ops": ['A) 55', 'B) 56', 'C) 50', 'D) 54'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 3136?',
        "ops": ['A) 56', 'B) 50', 'C) 51', 'D) 61'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 3249?',
        "ops": ['A) 54', 'B) 61', 'C) 57', 'D) 59'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 3364?',
        "ops": ['A) 58', 'B) 62', 'C) 52', 'D) 55'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 3481?',
        "ops": ['A) 61', 'B) 60', 'C) 59', 'D) 63'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 3600?',
        "ops": ['A) 64', 'B) 59', 'C) 54', 'D) 60'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 3721?',
        "ops": ['A) 61', 'B) 65', 'C) 66', 'D) 55'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 3844?',
        "ops": ['A) 62', 'B) 64', 'C) 66', 'D) 60'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 3969?',
        "ops": ['A) 69', 'B) 57', 'C) 67', 'D) 63'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 4096?',
        "ops": ['A) 68', 'B) 67', 'C) 58', 'D) 64'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 4225?',
        "ops": ['A) 65', 'B) 69', 'C) 60', 'D) 70'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 4356?',
        "ops": ['A) 63', 'B) 61', 'C) 66', 'D) 70'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 4489?',
        "ops": ['A) 71', 'B) 61', 'C) 67', 'D) 68'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 4624?',
        "ops": ['A) 67', 'B) 68', 'C) 64', 'D) 74'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a raiz quadrada exata de 4761?',
        "ops": ['A) 65', 'B) 67', 'C) 75', 'D) 69'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 125, 152, 120, 61, 32?',
        "ops": ['A) 105', 'B) 98', 'C) 107', 'D) 106'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 79, 91, 192, 71, 197?',
        "ops": ['A) 117', 'B) 126', 'C) 140', 'D) 110'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 128, 55, 66, 194, 67?',
        "ops": ['A) 111', 'B) 114', 'C) 104', 'D) 102'],
        "r": 'D',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 195, 84, 187, 33, 171?',
        "ops": ['A) 114', 'B) 129', 'C) 134', 'D) 141'],
        "r": 'C',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 111, 144, 140, 120, 200?',
        "ops": ['A) 143', 'B) 140', 'C) 125', 'D) 146'],
        "r": 'A',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 40, 190, 24, 143, 43?',
        "ops": ['A) 88', 'B) 99', 'C) 81', 'D) 84'],
        "r": 'A',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 168, 182, 79, 13, 183?',
        "ops": ['A) 115', 'B) 125', 'C) 123', 'D) 141'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 127, 142, 193, 199, 29?',
        "ops": ['A) 138', 'B) 123', 'C) 132', 'D) 150'],
        "r": 'A',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 55, 110, 33, 168, 104?',
        "ops": ['A) 91', 'B) 94', 'C) 103', 'D) 96'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 29, 24, 14, 193, 20?',
        "ops": ['A) 47', 'B) 56', 'C) 51', 'D) 57'],
        "r": 'B',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 16, 161, 37, 123, 23?',
        "ops": ['A) 79', 'B) 66', 'C) 72', 'D) 84'],
        "r": 'C',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a média aritmética dos números: 68, 19, 105, 125, 18?',
        "ops": ['A) 62', 'B) 65', 'C) 57', 'D) 67'],
        "r": 'D',
        "dif": 'dificil',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 32 (ou seja, log₂(32))?',
        "ops": ['A) 6', 'B) 4', 'C) 1', 'D) 5'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 64 (ou seja, log₂(64))?',
        "ops": ['A) 2', 'B) 3', 'C) 6', 'D) 1'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 128 (ou seja, log₂(128))?',
        "ops": ['A) 7', 'B) 6', 'C) 2', 'D) 12'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 256 (ou seja, log₂(256))?',
        "ops": ['A) 7', 'B) 9', 'C) 8', 'D) 5'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 512 (ou seja, log₂(512))?',
        "ops": ['A) 9', 'B) 10', 'C) 11', 'D) 5'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 1024 (ou seja, log₂(1024))?',
        "ops": ['A) 14', 'B) 5', 'C) 10', 'D) 8'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 2048 (ou seja, log₂(2048))?',
        "ops": ['A) 14', 'B) 6', 'C) 11', 'D) 13'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 4096 (ou seja, log₂(4096))?',
        "ops": ['A) 12', 'B) 16', 'C) 7', 'D) 14'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 8192 (ou seja, log₂(8192))?',
        "ops": ['A) 17', 'B) 13', 'C) 11', 'D) 16'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 16384 (ou seja, log₂(16384))?',
        "ops": ['A) 12', 'B) 16', 'C) 14', 'D) 9'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 32768 (ou seja, log₂(32768))?',
        "ops": ['A) 18', 'B) 16', 'C) 15', 'D) 11'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 65536 (ou seja, log₂(65536))?',
        "ops": ['A) 16', 'B) 12', 'C) 20', 'D) 13'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o logaritmo na base 2 de 131072 (ou seja, log₂(131072))?',
        "ops": ['A) 18', 'B) 17', 'C) 19', 'D) 22'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 200?',
        "ops": ['A) 20157', 'B) 18656', 'C) 20100', 'D) 20044'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 242?',
        "ops": ['A) 31035', 'B) 30351', 'C) 29403', 'D) 31198'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 140?',
        "ops": ['A) 10532', 'B) 10171', 'C) 9870', 'D) 9569'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 100?',
        "ops": ['A) 5096', 'B) 5327', 'C) 5050', 'D) 5330'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 154?',
        "ops": ['A) 12475', 'B) 11773', 'C) 12608', 'D) 11935'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 52?',
        "ops": ['A) 1378', 'B) 1420', 'C) 1432', 'D) 1483'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 198?',
        "ops": ['A) 19701', 'B) 18692', 'C) 20645', 'D) 18693'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 109?',
        "ops": ['A) 5663', 'B) 5909', 'C) 5995', 'D) 6030'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 226?',
        "ops": ['A) 25651', 'B) 26644', 'C) 24007', 'D) 23875'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 45?',
        "ops": ['A) 1029', 'B) 1035', 'C) 980', 'D) 1025'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 93?',
        "ops": ['A) 4647', 'B) 4243', 'C) 4371', 'D) 4245'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a soma de todos os números inteiros de 1 até 236?',
        "ops": ['A) 28621', 'B) 29216', 'C) 27230', 'D) 27966'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 100010000?',
        "ops": ['A) 289', 'B) 272', 'C) 282', 'D) 305'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 100111?',
        "ops": ['A) 32', 'B) 31', 'C) 39', 'D) 30'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 110001000?',
        "ops": ['A) 367', 'B) 398', 'C) 435', 'D) 392'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 101001?',
        "ops": ['A) 41', 'B) 36', 'C) 28', 'D) 39'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 1011001000?',
        "ops": ['A) 783', 'B) 660', 'C) 712', 'D) 629'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 1100100?',
        "ops": ['A) 113', 'B) 100', 'C) 102', 'D) 93'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 110000?',
        "ops": ['A) 45', 'B) 49', 'C) 48', 'D) 56'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 1000010?',
        "ops": ['A) 81', 'B) 79', 'C) 76', 'D) 66'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 101101?',
        "ops": ['A) 45', 'B) 56', 'C) 42', 'D) 46'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 11110011?',
        "ops": ['A) 253', 'B) 229', 'C) 259', 'D) 243'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 110001?',
        "ops": ['A) 49', 'B) 57', 'C) 35', 'D) 55'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 11101011?',
        "ops": ['A) 222', 'B) 235', 'C) 250', 'D) 220'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 11110011111?',
        "ops": ['A) 2014', 'B) 2132', 'C) 1951', 'D) 1864'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 1110011?',
        "ops": ['A) 121', 'B) 100', 'C) 129', 'D) 115'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o número decimal correspondente ao binário 1101101000?',
        "ops": ['A) 806', 'B) 872', 'C) 873', 'D) 909'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[-2, 3], [-5, -8]]?',
        "ops": ['A) 35', 'B) 39', 'C) 31', 'D) 42'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[-15, 9], [3, 1]]?',
        "ops": ['A) -30', 'B) -40', 'C) -36', 'D) -42'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[-15, -10], [9, 1]]?',
        "ops": ['A) 55', 'B) 63', 'C) 65', 'D) 75'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[5, 14], [10, -2]]?',
        "ops": ['A) -150', 'B) -167', 'C) -152', 'D) -119'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[1, -11], [-14, 7]]?',
        "ops": ['A) -133', 'B) -147', 'C) -146', 'D) -162'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[12, -1], [9, -1]]?',
        "ops": ['A) -3', 'B) 1', 'C) -5', 'D) 2'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[-12, -2], [7, 0]]?',
        "ops": ['A) 14', 'B) 11', 'C) 8', 'D) 20'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[11, 15], [-9, 12]]?',
        "ops": ['A) 306', 'B) 246', 'C) 247', 'D) 267'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[-1, -11], [5, -4]]?',
        "ops": ['A) 59', 'B) 47', 'C) 45', 'D) 54'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[-13, -11], [8, -2]]?',
        "ops": ['A) 132', 'B) 112', 'C) 119', 'D) 114'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[13, -10], [-1, 11]]?',
        "ops": ['A) 133', 'B) 135', 'C) 107', 'D) 116'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é o determinante da matriz [[13, 3], [-7, 8]]?',
        "ops": ['A) 100', 'B) 154', 'C) 125', 'D) 126'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos números primos existem entre 34 e 114 (incluindo os extremos)?',
        "ops": ['A) 15', 'B) 17', 'C) 20', 'D) 19'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos números primos existem entre 88 e 152 (incluindo os extremos)?',
        "ops": ['A) 14', 'B) 16', 'C) 13', 'D) 17'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos números primos existem entre 126 e 210 (incluindo os extremos)?',
        "ops": ['A) 15', 'B) 17', 'C) 16', 'D) 18'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos números primos existem entre 111 e 208 (incluindo os extremos)?',
        "ops": ['A) 17', 'B) 14', 'C) 13', 'D) 18'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos números primos existem entre 75 e 141 (incluindo os extremos)?',
        "ops": ['A) 13', 'B) 9', 'C) 14', 'D) 15'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos números primos existem entre 9 e 78 (incluindo os extremos)?',
        "ops": ['A) 21', 'B) 18', 'C) 17', 'D) 14'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos números primos existem entre 2 e 49 (incluindo os extremos)?',
        "ops": ['A) 14', 'B) 12', 'C) 16', 'D) 15'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos números primos existem entre 9 e 84 (incluindo os extremos)?',
        "ops": ['A) 19', 'B) 22', 'C) 23', 'D) 18'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos números primos existem entre 109 e 153 (incluindo os extremos)?',
        "ops": ['A) 9', 'B) 8', 'C) 4', 'D) 5'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Quantos números primos existem entre 98 e 142 (incluindo os extremos)?',
        "ops": ['A) 12', 'B) 10', 'C) 9', 'D) 6'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'matematica'
    },
    {
        "p": 'Qual é a capital do Cazaquistão?',
        "ops": ['A) Tashkent', 'B) Almaty', 'C) Astana', 'D) Bishkek'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o país com a maior extensão de litoral do mundo?',
        "ops": ['A) Rússia', 'B) Indonésia', 'C) Austrália', 'D) Canadá'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o ponto mais baixo da superfície terrestre (sem contar o fundo do oceano)?',
        "ops": ['A) Vale da Morte', 'B) Mar Morto', 'C) Lago Assal', 'D) Mar Cáspio'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é a capital da Nova Zelândia?',
        "ops": ['A) Hamilton', 'B) Christchurch', 'C) Wellington', 'D) Auckland'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o maior país sem litoral (sem acesso ao mar) do mundo?',
        "ops": ['A) Bolívia', 'B) Cazaquistão', 'C) Mongólia', 'D) Chade'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o menor país do mundo em área territorial?',
        "ops": ['A) San Marino', 'B) Liechtenstein', 'C) Vaticano', 'D) Mônaco'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o rio mais longo da Ásia?',
        "ops": ['A) Mekong', 'B) Indo', 'C) Ganges', 'D) Yangtzé'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é a capital da Austrália?',
        "ops": ['A) Brisbane', 'B) Camberra', 'C) Melbourne', 'D) Sydney'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Quantos países fazem fronteira terrestre com o Brasil?',
        "ops": ['A) 8', 'B) 9', 'C) 10', 'D) 12'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é a capital da Etiópia?',
        "ops": ['A) Nairóbi', 'B) Cabul', 'C) Cartum', 'D) Adis Abeba'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual estreito separa a parte europeia e a parte asiática da Turquia?',
        "ops": ['A) Bering', 'B) Bósforo', 'C) Gibraltar', 'D) Dardanelos'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o lago mais profundo do mundo?',
        "ops": ['A) Lago Titicaca', 'B) Lago Victoria', 'C) Lago Superior', 'D) Lago Baikal'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é a montanha mais alta da América do Sul?',
        "ops": ['A) Huascarán', 'B) Pico Bolívar', 'C) Aconcágua', 'D) Chimborazo'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é a capital de Myanmar (antiga Birmânia)?',
        "ops": ['A) Yangon', 'B) Bangkok', 'C) Naypyidaw', 'D) Mandalay'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o maior arquipélago do mundo em número de ilhas?',
        "ops": ['A) Filipinas', 'B) Maldivas', 'C) Japão', 'D) Indonésia'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual canal liga o Mar Mediterrâneo ao Mar Vermelho?',
        "ops": ['A) Canal de Suez', 'B) Canal do Panamá', 'C) Canal da Mancha', 'D) Canal de Kiel'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é a capital do Canadá?',
        "ops": ['A) Ottawa', 'B) Montreal', 'C) Toronto', 'D) Vancouver'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o ponto mais alto do continente africano?',
        "ops": ['A) Monte Stanley', 'B) Monte Kilimanjaro', 'C) Monte Quênia', 'D) Monte Camarões'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Quantos fusos horários oficiais tem a Rússia?',
        "ops": ['A) 7', 'B) 11', 'C) 13', 'D) 9'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o segundo maior país do mundo em área territorial?',
        "ops": ['A) Brasil', 'B) Estados Unidos', 'C) China', 'D) Canadá'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é a capital da Suíça?',
        "ops": ['A) Berna', 'B) Genebra', 'C) Zurique', 'D) Basileia'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual estreito separa a Ásia da América, entre Rússia e o Alasca?',
        "ops": ['A) Estreito de Bósforo', 'B) Estreito de Bering', 'C) Estreito de Ormuz', 'D) Estreito de Magalhães'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o país mais populoso do continente africano?',
        "ops": ['A) República Democrática do Congo', 'B) Egito', 'C) Etiópia', 'D) Nigéria'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é a capital da Turquia?',
        "ops": ['A) Izmir', 'B) Ancara', 'C) Antália', 'D) Istambul'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o maior lago de água doce do mundo em área de superfície?',
        "ops": ['A) Lago Baikal', 'B) Lago Superior', 'C) Lago Victoria', 'D) Mar Cáspio'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é a capital oficial dos Países Baixos (Holanda)?',
        "ops": ['A) Utrecht', 'B) Haia', 'C) Roterdã', 'D) Amsterdã'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o menor oceano do mundo em área?',
        "ops": ['A) Oceano Ártico', 'B) Oceano Índico', 'C) Oceano Antártico', 'D) Oceano Atlântico'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é o nome da cordilheira que percorre toda a costa oeste da América do Sul?',
        "ops": ['A) Cordilheira dos Andes', 'B) Cordilheira do Himalaia', 'C) Montanhas Rocosas', 'D) Alpes'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual é a capital do Quênia?',
        "ops": ['A) Adis Abeba', 'B) Mombaça', 'C) Kampala', 'D) Nairóbi'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Qual deserto é considerado o maior deserto quente do mundo?',
        "ops": ['A) Gobi', 'B) Saara', 'C) Atacama', 'D) Kalahari'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'geografia'
    },
    {
        "p": 'Em que ano começou a Revolução Francesa?',
        "ops": ['A) 1804', 'B) 1776', 'C) 1799', 'D) 1789'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Quem foi o primeiro presidente dos Estados Unidos?',
        "ops": ['A) George Washington', 'B) Abraham Lincoln', 'C) Thomas Jefferson', 'D) John Adams'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano o Brasil se tornou independente de Portugal?',
        "ops": ['A) 1824', 'B) 1808', 'C) 1822', 'D) 1889'],
        "r": 'C',
        "dif": 'dificil',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano a Segunda Guerra Mundial terminou?',
        "ops": ['A) 1943', 'B) 1946', 'C) 1945', 'D) 1944'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano caiu o Império Romano do Ocidente?',
        "ops": ['A) 410 d.C.', 'B) 527 d.C.', 'C) 476 d.C.', 'D) 395 d.C.'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano ocorreu a Revolução Russa que levou os bolcheviques ao poder?',
        "ops": ['A) 1905', 'B) 1914', 'C) 1917', 'D) 1921'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Qual foi o nome do navio que levou os peregrinos puritanos à América do Norte em 1620?',
        "ops": ['A) Mayflower', 'B) Endeavour', 'C) Santa Maria', 'D) Beagle'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano foi assinada a Magna Carta na Inglaterra?',
        "ops": ['A) 1314', 'B) 1066', 'C) 1492', 'D) 1215'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano começou a Guerra Civil Americana?',
        "ops": ['A) 1861', 'B) 1850', 'C) 1865', 'D) 1845'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Quem foi o líder da Revolução Cubana de 1959?',
        "ops": ['A) Fidel Castro', 'B) Raúl Castro', 'C) Hugo Chávez', 'D) Che Guevara'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano Napoleão foi derrotado na Batalha de Waterloo?',
        "ops": ['A) 1815', 'B) 1821', 'C) 1812', 'D) 1805'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Qual tratado de 1494 dividiu as terras recém-descobertas das Américas entre Portugal e Espanha?',
        "ops": ['A) Tratado de Versalhes', 'B) Tratado de Madrid', 'C) Tratado de Tordesilhas', 'D) Tratado de Utrecht'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano o Muro de Berlim foi construído?',
        "ops": ['A) 1949', 'B) 1968', 'C) 1961', 'D) 1955'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Qual faraó egípcio teve seu túmulo descoberto quase intacto em 1922?',
        "ops": ['A) Akhenaton', 'B) Quéops', 'C) Tutancâmon', 'D) Ramsés II'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano Mao Zedong proclamou a República Popular da China?',
        "ops": ['A) 1949', 'B) 1953', 'C) 1937', 'D) 1945'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Como ficou conhecida a pandemia que matou cerca de um terço da população europeia no século XIV?',
        "ops": ['A) Cólera', 'B) Gripe Espanhola', 'C) Febre Amarela', 'D) Peste Negra'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano ocorreu a queda de Constantinopla, encerrando o Império Bizantino?',
        "ops": ['A) 1453', 'B) 1402', 'C) 1481', 'D) 1492'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Qual navegador português chegou à Índia contornando a África em 1498?',
        "ops": ['A) Bartolomeu Dias', 'B) Vasco da Gama', 'C) Fernão de Magalhães', 'D) Pedro Álvares Cabral'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano foi proclamada a República no Brasil?',
        "ops": ['A) 1889', 'B) 1888', 'C) 1891', 'D) 1822'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Como ficou conhecida a revolta de escravizados no Haiti que resultou na primeira república negra independente, em 1804?',
        "ops": ['A) Revolução Haitiana', 'B) Conjuração Baiana', 'C) Revolta dos Malês', 'D) Revolta da Chibata'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano teve início a Primeira Guerra Mundial?',
        "ops": ['A) 1918', 'B) 1916', 'C) 1912', 'D) 1914'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Quem liderou o movimento de resistência pacífica contra o domínio britânico na Índia?',
        "ops": ['A) Jawaharlal Nehru', 'B) Subhas Chandra Bose', 'C) Muhammad Ali Jinnah', 'D) Mahatma Gandhi'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano a União Soviética foi oficialmente dissolvida?',
        "ops": ['A) 1985', 'B) 1991', 'C) 1993', 'D) 1989'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Qual acordo, assinado em 1973, encerrou oficialmente a participação militar dos EUA na Guerra do Vietnã?',
        "ops": ['A) Acordo de Camp David', 'B) Tratado de Versalhes', 'C) Tratado de Genebra', 'D) Acordos de Paz de Paris'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano a expedição de Cristóvão Colombo chegou à América?',
        "ops": ['A) 1488', 'B) 1500', 'C) 1498', 'D) 1492'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Qual general cartaginês atravessou os Alpes com elefantes para atacar Roma?',
        "ops": ['A) Pompeu', 'B) Júlio César', 'C) Cipião Africano', 'D) Aníbal'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Em que ano foi assinada a Lei Áurea, que aboliu a escravidão no Brasil?',
        "ops": ['A) 1871', 'B) 1850', 'C) 1889', 'D) 1888'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Após a morte de qual imperador romano o império foi definitivamente dividido entre Oriente e Ocidente?',
        "ops": ['A) Teodósio I', 'B) Marco Aurélio', 'C) Diocleciano', 'D) Constantino'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'historia'
    },
    {
        "p": 'Qual é a unidade de medida de força no Sistema Internacional?',
        "ops": ['A) Newton', 'B) Joule', 'C) Watt', 'D) Pascal'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quem propôs a Teoria da Relatividade Geral?',
        "ops": ['A) Isaac Newton', 'B) Niels Bohr', 'C) Albert Einstein', 'D) Max Planck'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é o gás mais abundante na atmosfera terrestre?',
        "ops": ['A) Nitrogênio', 'B) Dióxido de carbono', 'C) Oxigênio', 'D) Argônio'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é o número atômico do hidrogênio?',
        "ops": ['A) 0', 'B) 1', 'C) 2', 'D) 6'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual partícula subatômica possui carga elétrica negativa?',
        "ops": ['A) Nêutron', 'B) Fóton', 'C) Elétron', 'D) Próton'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quem descobriu a penicilina?',
        "ops": ['A) Edward Jenner', 'B) Alexander Fleming', 'C) Louis Pasteur', 'D) Robert Koch'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual órgão do corpo humano é responsável pela produção de insulina?',
        "ops": ['A) Rim', 'B) Fígado', 'C) Baço', 'D) Pâncreas'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é a velocidade aproximada do som no ar, ao nível do mar?',
        "ops": ['A) 500 m/s', 'B) 340 m/s', 'C) 1000 m/s', 'D) 150 m/s'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quem formulou as três leis fundamentais do movimento (mecânica clássica)?',
        "ops": ['A) Galileu Galilei', 'B) Isaac Newton', 'C) Albert Einstein', 'D) Johannes Kepler'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é o nome do processo pelo qual as plantas convertem luz solar em energia química?',
        "ops": ['A) Fotossíntese', 'B) Respiração celular', 'C) Quimiossíntese', 'D) Fermentação'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": "Qual é o elemento químico cujo símbolo é 'Fe'?",
        "ops": ['A) Fósforo', 'B) Ferro', 'C) Frâncio', 'D) Flúor'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quantos pares de cromossomos tem uma célula humana normal?',
        "ops": ['A) 22 pares', 'B) 23 pares', 'C) 20 pares', 'D) 24 pares'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual cientista propôs a teoria da seleção natural como mecanismo da evolução?',
        "ops": ['A) Jean-Baptiste Lamarck', 'B) Alfred Wallace', 'C) Charles Darwin', 'D) Gregor Mendel'],
        "r": 'C',
        "dif": 'dificil',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é a camada da atmosfera terrestre mais próxima da superfície, onde ocorrem os fenômenos climáticos?',
        "ops": ['A) Mesosfera', 'B) Termosfera', 'C) Troposfera', 'D) Estratosfera'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é o pH aproximado de uma solução neutra, como a água pura a 25°C?',
        "ops": ['A) 0', 'B) 7', 'C) 5', 'D) 14'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quem foi a primeira pessoa a ganhar dois Prêmios Nobel em áreas científicas diferentes (Física e Química)?',
        "ops": ['A) Dorothy Hodgkin', 'B) Frederick Sanger', 'C) Linus Pauling', 'D) Marie Curie'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é a unidade de medida de energia no Sistema Internacional?',
        "ops": ['A) Volt', 'B) Newton', 'C) Joule', 'D) Watt'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é o maior órgão do corpo humano?',
        "ops": ['A) Pele', 'B) Fígado', 'C) Pulmão', 'D) Intestino'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é o nome da camada de gases que protege a Terra da radiação ultravioleta do Sol?',
        "ops": ['A) Ionosfera', 'B) Estratopausa', 'C) Camada de ozônio', 'D) Magnetosfera'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual cientista é considerado o pai da química moderna, por seus estudos sobre a conservação da massa?',
        "ops": ['A) Robert Boyle', 'B) John Dalton', 'C) Joseph Priestley', 'D) Antoine Lavoisier'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quem desenvolveu a primeira versão amplamente aceita da tabela periódica dos elementos?',
        "ops": ['A) Niels Bohr', 'B) Dmitri Mendeleev', 'C) Marie Curie', 'D) Antoine Lavoisier'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é o nome do processo de transformação de um líquido em gás?',
        "ops": ['A) Sublimação', 'B) Vaporização', 'C) Condensação', 'D) Solidificação'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é a menor unidade estrutural e funcional dos seres vivos?',
        "ops": ['A) Célula', 'B) Átomo', 'C) Tecido', 'D) Molécula'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual cientista e padre belga propôs originalmente a teoria que evoluiu para o modelo do Big Bang?',
        "ops": ['A) Edwin Hubble', 'B) Fred Hoyle', 'C) Stephen Hawking', 'D) Georges Lemaître'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é o osso mais longo do corpo humano?',
        "ops": ['A) Tíbia', 'B) Fêmur', 'C) Úmero', 'D) Fíbula'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é a unidade de medida de pressão no Sistema Internacional?',
        "ops": ['A) Newton', 'B) Bar', 'C) Pascal', 'D) Joule'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Quem descreveu, junto com Francis Crick, a estrutura em dupla hélice do DNA?',
        "ops": ['A) Linus Pauling', 'B) Rosalind Franklin', 'C) James Watson', 'D) Gregor Mendel'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é o fenômeno óptico responsável por dividir a luz branca em várias cores, como no arco-íris?',
        "ops": ['A) Polarização', 'B) Dispersão da luz', 'C) Reflexão total', 'D) Difração simples'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'ciencias'
    },
    {
        "p": 'Qual é a fórmula química da água?',
        "ops": ['A) H2O2', 'B) O2', 'C) H2O', 'D) CO2'],
        "r": 'C',
        "dif": 'dificil',
        "categoria": 'ciencias'
    },
    {
        "p": "Quem escreveu o poema épico português 'Os Lusíadas'?",
        "ops": ['A) Eça de Queirós', 'B) Fernando Pessoa', 'C) José Saramago', 'D) Luís de Camões'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Quem pintou a Mona Lisa?',
        "ops": ['A) Leonardo da Vinci', 'B) Donatello', 'C) Rafael', 'D) Michelangelo'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Quem escreveu a peça 'Romeu e Julieta'?",
        "ops": ['A) Christopher Marlowe', 'B) Victor Hugo', 'C) William Shakespeare', 'D) Molière'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Quantas teclas tem um piano clássico padrão?',
        "ops": ['A) 76 teclas', 'B) 92 teclas', 'C) 100 teclas', 'D) 88 teclas'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Quem escreveu o romance 'Cem Anos de Solidão'?",
        "ops": ['A) Jorge Luis Borges', 'B) Gabriel García Márquez', 'C) Pablo Neruda', 'D) Mario Vargas Llosa'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Qual artista pintou a obra 'Guernica'?",
        "ops": ['A) Joan Miró', 'B) Francisco Goya', 'C) Pablo Picasso', 'D) Salvador Dalí'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Quem é o autor dos romances '1984' e 'A Revolução dos Bichos'?",
        "ops": ['A) Ray Bradbury', 'B) George Orwell', 'C) H.G. Wells', 'D) Aldous Huxley'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Qual compositor ficou completamente surdo e ainda assim compôs obras como a 9ª Sinfonia?',
        "ops": ['A) Ludwig van Beethoven', 'B) Franz Schubert', 'C) Wolfgang Amadeus Mozart', 'D) Johann Sebastian Bach'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Quem escreveu o romance 'Dom Quixote'?",
        "ops": ['A) Federico García Lorca', 'B) Calderón de la Barca', 'C) Miguel de Cervantes', 'D) Lope de Vega'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Qual escultura renascentista de Michelangelo representa o rei bíblico Davi?',
        "ops": ['A) Davi', 'B) A Piedade', 'C) O Pensador', 'D) O Rapto da Prosérpina'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Quem é o autor de 'A Divina Comédia'?",
        "ops": ['A) Torquato Tasso', 'B) Dante Alighieri', 'C) Petrarca', 'D) Giovanni Boccaccio'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Qual filósofo grego foi professor de Alexandre, o Grande?',
        "ops": ['A) Sócrates', 'B) Pitágoras', 'C) Platão', 'D) Aristóteles'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Quem pintou o teto da Capela Sistina, no Vaticano?',
        "ops": ['A) Leonardo da Vinci', 'B) Rafael', 'C) Caravaggio', 'D) Michelangelo'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Qual escritor brasileiro é autor de 'Grande Sertão: Veredas'?",
        "ops": ['A) Graciliano Ramos', 'B) Guimarães Rosa', 'C) José de Alencar', 'D) Jorge Amado'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Quem escreveu o romance 'A Metamorfose', sobre um homem que se transforma em inseto?",
        "ops": ['A) Thomas Mann', 'B) Hermann Hesse', 'C) Albert Camus', 'D) Franz Kafka'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Qual compositor austríaco é autor da ópera 'A Flauta Mágica'?",
        "ops": ['A) Ludwig van Beethoven', 'B) Richard Strauss', 'C) Joseph Haydn', 'D) Wolfgang Amadeus Mozart'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Quem escreveu o romance 'Crime e Castigo'?",
        "ops": ['A) Anton Tchekhov', 'B) Nikolai Gógol', 'C) Fiódor Dostoiévski', 'D) Liev Tolstói'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Qual escritor britânico criou o detetive Sherlock Holmes?',
        "ops": ['A) Charles Dickens', 'B) Agatha Christie', 'C) Oscar Wilde', 'D) Arthur Conan Doyle'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Qual poeta brasileiro escreveu a 'Canção do Exílio' ('Minha terra tem palmeiras...')?",
        "ops": ['A) Olavo Bilac', 'B) Castro Alves', 'C) Casimiro de Abreu', 'D) Gonçalves Dias'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": 'Qual artista é conhecido por suas obras de pop art com latas de sopa Campbell?',
        "ops": ['A) Roy Lichtenstein', 'B) Andy Warhol', 'C) Jean-Michel Basquiat', 'D) Jackson Pollock'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Qual compositor alemão é autor do ciclo de óperas 'O Anel do Nibelungo'?",
        "ops": ['A) Richard Wagner', 'B) Robert Schumann', 'C) Johannes Brahms', 'D) Felix Mendelssohn'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Quem esculpiu a famosa obra 'O Pensador'?",
        "ops": ['A) Auguste Rodin', 'B) Jean Arp', 'C) Constantin Brâncuși', 'D) Antonio Canova'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Qual escritor português é autor do romance 'Os Maias'?",
        "ops": ['A) Almeida Garrett', 'B) Eça de Queirós', 'C) Alexandre Herculano', 'D) Camilo Castelo Branco'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Qual pintor holandês do século XVII pintou 'A Ronda Noturna'?",
        "ops": ['A) Frans Hals', 'B) Johannes Vermeer', 'C) Rembrandt', 'D) Jan Steen'],
        "r": 'C',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Quem é o autor do poema épico grego 'Odisseia'?",
        "ops": ['A) Sófocles', 'B) Homero', 'C) Hesíodo', 'D) Eurípides'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Qual escritor irlandês escreveu o romance modernista 'Ulysses'?",
        "ops": ['A) Oscar Wilde', 'B) James Joyce', 'C) Bram Stoker', 'D) Samuel Beckett'],
        "r": 'B',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Qual compositor russo escreveu o balé 'O Lago dos Cisnes'?",
        "ops": ['A) Tchaikovsky', 'B) Modest Mussorgsky', 'C) Sergei Rachmaninoff', 'D) Igor Stravinsky'],
        "r": 'A',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
    },
    {
        "p": "Quem pintou a obra expressionista 'O Grito'?",
        "ops": ['A) Egon Schiele', 'B) Gustav Klimt', 'C) Wassily Kandinsky', 'D) Edvard Munch'],
        "r": 'D',
        "dif": 'extremo',
        "categoria": 'cultura_geral'
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
    {"id": "milionario_ach", "nome": "💎 Milionário", "desc": "Acumulou 100.000 <:fichas:1517923672575185048> no total", "recompensa": 1000,
     "check": lambda u: u.get("total", 0) >= 100000},
    {"id": "bilionario_ach", "nome": "🏦 Bilionário", "desc": "Acumulou 500.000 <:fichas:1517923672575185048> no total", "recompensa": 3000,
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

# ── SISTEMA DE MODERAÇÃO / ALT-BAN ──────────────────────────
CANAL_MOD       = 1517919147529343097   # canal de alertas
CARGO_DONO      = 1510825991193497631   # The Last Ronin
CARGOS_ADM      = {1491272967961837740, 1491280579126366350}  # Z Caos + Owner
CARGOS_STAFF    = {CARGO_DONO} | CARGOS_ADM

# Rastreamento em memória (reseta ao reiniciar o bot)
_spam_tracker   = {}   # uid → {"cmds": [timestamps], "warns": int}
_join_tracker   = []   # [timestamps de entradas recentes]
_msg_tracker    = {}   # uid → [timestamps de mensagens recentes]
_canal_tracker  = {}   # guild_id → {"deletes": int, "creates": int, "ts": float}
_bans_pendentes = {}   # uid → info do alerta

async def alertar_mods(guild, embed):
    """Envia embed de alerta pro canal de moderação."""
    canal = guild.get_channel(CANAL_MOD)
    if canal:
        mencoes = " ".join(f"<@&{c}>" for c in CARGOS_ADM) + f" <@&{CARGO_DONO}>"
        await canal.send(mencoes, embed=embed)

def is_staff(member):
    """Verifica se o membro tem cargo de staff."""
    if member.id == DONO_ID:
        return True
    return any(r.id in CARGOS_STAFF for r in member.roles)

async def aplicar_timeout(member, minutos, motivo):
    """Aplica timeout no membro se possível."""
    try:
        until = discord.utils.utcnow() + timedelta(minutes=minutos)
        await member.timeout(until, reason=motivo)
        return True
    except Exception:
        return False

async def banir_membro(member, motivo, moderador=None):
    """Bane o membro e registra no canal de mod."""
    try:
        await member.ban(reason=motivo, delete_message_days=1)
        embed = discord.Embed(
            title="🔨 MEMBRO BANIDO",
            color=0xFF0000
        )
        embed.add_field(name="Usuário", value=f"{member} (`{member.id}`)", inline=False)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        if moderador:
            embed.add_field(name="Banido por", value=str(moderador), inline=False)
        embed.set_footer(text=f"Conta criada em {member.created_at.strftime('%d/%m/%Y')}")
        await alertar_mods(member.guild, embed)
        return True
    except Exception:
        return False

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
            "estatisticas": {"pescar_total": 0, "cacar_total": 0, "minerar_total": 0, "roubos_sucesso": 0,
                              "quiz_acertos": 0, "fichas_roubadas_total": 0, "pescou_tubarao": False},
            "conquistas": [],
            "missoes": {"data": None, "lista": []},
            "semana_id": None, "semana_total_inicio": 0,
            "procurado": False, "recompensa_procurado": 0, "vezes_procurado": 0,
            "investimento": None,
            "trevo_ate": None
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
        u["estatisticas"] = {"pescar_total": 0, "cacar_total": 0, "minerar_total": 0, "roubos_sucesso": 0,
                              "quiz_acertos": 0, "fichas_roubadas_total": 0, "pescou_tubarao": False}
    if "fichas_roubadas_total" not in u["estatisticas"]:
        u["estatisticas"]["fichas_roubadas_total"] = 0
    if "pescou_tubarao" not in u["estatisticas"]:
        u["estatisticas"]["pescou_tubarao"] = False
    if "conquistas" not in u:
        u["conquistas"] = []
    if "missoes" not in u:
        u["missoes"] = {"data": None, "lista": []}
    if "procurado" not in u:
        u["procurado"] = False
    if "recompensa_procurado" not in u:
        u["recompensa_procurado"] = 0
    if "vezes_procurado" not in u:
        u["vezes_procurado"] = 0
    if "investimento" not in u:
        u["investimento"] = None
    if "trevo_ate" not in u:
        u["trevo_ate"] = None
    semana_id = semana_atual()
    if u.get("semana_id") != semana_id:
        u["semana_id"] = semana_id
        u["semana_total_inicio"] = u.get("total", 0)
    return u

def semana_atual():
    iso = date.today().isocalendar()
    return f"{iso[0]}-W{iso[1]}"

CLIMAS = [
    {"id": "ensolarado", "nome": "☀️ Ensolarado", "efeito": "pesca +10%"},
    {"id": "chuvoso", "nome": "🌧️ Chuvoso", "efeito": "mineração +10%"},
    {"id": "noite_tranquila", "nome": "🌙 Noite Tranquila", "efeito": "loteria mais generosa"},
    {"id": "dia_de_sorte", "nome": "🍀 Dia de Sorte", "efeito": "tudo +5%"},
]

HUMORES = [
    {"id": "feliz", "nome": "😄 Feliz", "efeito": "+10% em todas as recompensas"},
    {"id": "sonolento", "nome": "😴 Sonolento", "efeito": "cooldowns reduzidos em 20%"},
    {"id": "normal", "nome": "🙂 Normal", "efeito": "nenhum bônus especial hoje"},
]

def garantir_clima(dados):
    hoje = str(date.today())
    if dados.get("_clima", {}).get("data") != hoje:
        dados["_clima"] = {"data": hoje, "tipo": random.choice(CLIMAS)["id"]}
    return dados["_clima"]["tipo"]

def garantir_humor(dados):
    hoje_hora = f"{date.today()}-{datetime.now().hour // 6}"  # muda a cada ~6 horas
    if dados.get("_humor", {}).get("periodo") != hoje_hora:
        dados["_humor"] = {"periodo": hoje_hora, "tipo": random.choice(HUMORES)["id"]}
    return dados["_humor"]["tipo"]

def multiplicador_ganho(dados, tipo_acao):
    """Combina os bônus de clima e humor pra uma ação econômica (pescar, cacar, minerar, apostar, quiz)."""
    clima = garantir_clima(dados)
    humor = garantir_humor(dados)
    mult = 1.0
    if tipo_acao == "pescar" and clima == "ensolarado":
        mult *= 1.10
    if tipo_acao == "minerar" and clima == "chuvoso":
        mult *= 1.10
    if clima == "dia_de_sorte":
        mult *= 1.05
    if humor == "feliz":
        mult *= 1.10
    return mult

def multiplicador_loteria(dados):
    clima = garantir_clima(dados)
    if clima == "noite_tranquila":
        return 1.10
    if clima == "dia_de_sorte":
        return 1.05
    return 1.0

def registrar_evento(dados, tipo, texto):
    if "_eventos" not in dados:
        dados["_eventos"] = []
    dados["_eventos"].append({"tipo": tipo, "texto": texto, "timestamp": datetime.now().isoformat()})
    dados["_eventos"] = dados["_eventos"][-300:]  # mantém só os 300 mais recentes

def registrar_marco(dados, texto):
    if "_marcos" not in dados:
        dados["_marcos"] = []
    dados["_marcos"].append({"texto": texto, "timestamp": datetime.now().isoformat()})
    dados["_marcos"] = dados["_marcos"][-150:]  # mantém só os 150 mais recentes

def evento_aleatorio():
    """Pequena chance de um evento de sorte/azar aleatório ao usar um comando. Retorna (texto, delta) ou None."""
    if random.random() > 0.12:
        return None
    eventos = [
        ("🍀 Você encontrou {v} <:fichas:1517923672575185048> no chão.", random.randint(20, 80)),
        ("🥾 Você tropeçou e perdeu {v} <:fichas:1517923672575185048>.", -random.randint(5, 30)),
        ("📦 Um desconhecido lhe deu uma caixa com {v} <:fichas:1517923672575185048> dentro.", random.randint(15, 60)),
        ("🍪 Você encontrou {v} <:fichas:1517923672575185048> esquecidas em um bolso.", random.randint(20, 73)),
        ("🍪 Um desconhecido dividiu um biscoito com você. +{v} <:fichas:1517923672575185048>.", 20),
        ("🌧️ Você ficou olhando a chuva por alguns minutos. +{v} <:fichas:1517923672575185048> pela paz.", 5),
    ]
    texto, valor = random.choice(eventos)
    return texto.format(v=abs(valor)), valor

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
                mensagens.append(f"🎯 Missão concluída: **{m['desc']}** (+{m['recompensa']} <:fichas:1517923672575185048>)")
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
    await canal.send(f"🏆 **{nome_vencedor} venceu a luta** e roubou **{premio} <:fichas:1517923672575185048>!**")
    for m in mensagens_extra:
        await canal.send(m)
    for c in novas_conquistas:
        await canal.send(f"🏆 **Conquista desbloqueada por {nome_vencedor}:** {c['nome']} (+{c['recompensa']} <:fichas:1517923672575185048>)")

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
    def __init__(self, pergunta, fichas_ganho, fichas_perda, channel_id):
        super().__init__(timeout=20)
        self.pergunta = pergunta
        self.fichas_ganho = fichas_ganho
        self.fichas_perda = fichas_perda
        self.channel_id = channel_id
        self.finalizado = False
        self.ja_tentaram = set()

    async def responder(self, interaction, escolha):
        if self.finalizado:
            await interaction.response.send_message("❌ Esse quiz já acabou!", ephemeral=True)
            return
        if interaction.user.id in self.ja_tentaram:
            await interaction.response.send_message("❌ Você já tentou responder esse quiz!", ephemeral=True)
            return
        self.ja_tentaram.add(interaction.user.id)
        dados = carregar()
        u = get_usuario(dados, interaction.user.id)
        correta = self.pergunta["r"]
        if escolha == correta:
            self.finalizado = True
            self.stop()
            mensagens_extra = registrar_missao(u, "quiz")
            u["fichas"] += self.fichas_ganho
            u["total"] += self.fichas_ganho
            u["estatisticas"]["quiz_acertos"] = u["estatisticas"].get("quiz_acertos", 0) + 1
            mensagens_extra += registrar_missao(u, "quiz_acerto")
            novas_conquistas = verificar_conquistas(u)
            registrar_evento(dados, "quiz", f"🧠 {interaction.user.display_name} acertou o quiz primeiro e ganhou {self.fichas_ganho} <:fichas:1517923672575185048>.")
            salvar(dados)
            await interaction.response.edit_message(
                content=f"🏆 **{interaction.user.display_name}** acertou primeiro! A resposta era **{correta}**!\n💰 Ganhou **{self.fichas_ganho} <:fichas:1517923672575185048>!**",
                view=None
            )
            if self.channel_id in quizzes_ativos:
                del quizzes_ativos[self.channel_id]
            for m in mensagens_extra:
                await interaction.followup.send(m)
            for c in novas_conquistas:
                await interaction.followup.send(f"🏆 **Conquista desbloqueada por {interaction.user.display_name}:** {c['nome']} (+{c['recompensa']} <:fichas:1517923672575185048>)")
        else:
            mensagens_extra = registrar_missao(u, "quiz")
            u["fichas"] = max(0, u["fichas"] - self.fichas_perda)
            salvar(dados)
            await interaction.response.send_message(
                f"❌ {interaction.user.mention} errou! Perdeu **{self.fichas_perda} <:fichas:1517923672575185048>**. Outros ainda podem tentar!",
                ephemeral=False
            )
            for m in mensagens_extra:
                await interaction.followup.send(m)

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
        if not self.finalizado:
            self.finalizado = True
            if self.channel_id in quizzes_ativos:
                msg = quizzes_ativos[self.channel_id]
                del quizzes_ativos[self.channel_id]
                try:
                    await msg.edit(
                        content=f"⏰ **Tempo esgotado!** Ninguém acertou a tempo. A resposta era **{self.pergunta['r']}**!",
                        view=None
                    )
                except:
                    pass

@bot.event
async def on_ready():
    print(f"Bot ligado como {bot.user}")
    if not sorteio_automatico.is_running():
        sorteio_automatico.start()
    if not evento_automatico.is_running():
        evento_automatico.start()

@tasks.loop(minutes=5)
async def sorteio_automatico():
    """Verifica a cada 5 minutos se é domingo à meia-noite pra fechar a loteria automaticamente."""
    agora = datetime.now()
    if agora.weekday() != 6:  # 6 = domingo
        return
    if agora.hour != 0 or agora.minute > 5:
        return
    dados = carregar()
    loteria = get_loteria(dados)
    if not loteria["bilhetes"]:
        return
    if dados.get("_ultimo_sorteio") == str(agora.date()):
        return  # já sorteou hoje
    pool = []
    for uid, qtd in loteria["bilhetes"].items():
        pool.extend([uid] * qtd)
    vencedor_id = random.choice(pool)
    mult_lot = multiplicador_loteria(dados)
    premio = int(loteria["pote"] * mult_lot)
    u_vencedor = get_usuario(dados, vencedor_id)
    u_vencedor["fichas"] += premio
    u_vencedor["total"] += premio
    guild = bot.get_guild(bot.guilds[0].id) if bot.guilds else None
    membro = guild.get_member(int(vencedor_id)) if guild else None
    nome = membro.display_name if membro else f"<@{vencedor_id}>"
    registrar_marco(dados, f"🎰 {nome} ganhou a loteria semanal automática e levou {premio} <:fichas:1517923672575185048>!")
    dados["_loteria"] = {"bilhetes": {}, "pote": 0}
    dados["_ultimo_sorteio"] = str(agora.date())
    salvar(dados)
    canal = bot.get_channel(CANAL_BOT)
    if canal:
        mencao = membro.mention if membro else f"<@{vencedor_id}>"
        await canal.send(f"🎉🎰 **SORTEIO SEMANAL!**\n{mencao} ganhou a loteria e levou **{premio} <:fichas:1517923672575185048>**! Uma nova rodada começa agora.")

COMANDOS_MOD = {
    "altban", "timeout", "removertimeout", "kick",
    "lockdown", "unlockdown", "modinfo", "aura", "ego",
    "darfichas", "tirfichas", "setfichas", "godmode",
    "zerarfichas", "resetlimite", "resetquiz", "dano2x",
    "cancelluta", "premiarsemana", "sortearloteria",
    "addparceria", "removerparceria", "invocar"
}

@bot.check
async def apenas_canal_bot(ctx):
    if ctx.command and ctx.command.name in COMANDOS_MOD:
        return True  # comandos de mod funcionam em qualquer canal
    if ctx.channel.id != CANAL_BOT:
        await ctx.send(f"❌ Use os comandos no canal <#{CANAL_BOT}>!")
        return False
    return True

MENSAGENS_PESCAR = [
    "🎣 {nome} jogou a linha e pescou um **{item}**! {extra}",
    "🎣 A linha de {nome} tremeu... era um **{item}**! {extra}",
    "🎣 Após uma longa espera, {nome} tirou um **{item}** da água! {extra}",
]
PEIXES = [
    ("peixe dourado", "Que sorte!", 0),
    ("tilápia enorme", "Não é muito bonita, mas vale <:fichas:1517923672575185048>.", 0),
    ("bota velha", "Alguém ficou triste hoje.", -20),
    ("peixe espada", "Afiado!", 0),
    ("carpa gigante", "Pesada demais!", 0),
    ("tubarão-touro", "TUBARÃO! 🦈 O servidor vai ouvir falar disso!", 200),
    ("enguia elétrica", "Levou um choque, mas valeu.", 0),
    ("peixe palhaço", "Não é tão engraçado assim.", 0),
    ("um peixe que olhou pra você e voltou pra água", "Respeitável.", -10),
    ("lata de atum (fechada)", "Circular.", 0),
    ("polvo filosófico", "Ele tinha oito braços e nenhuma resposta.", 0),
]

@bot.command(name="pescar")
async def pescar(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if not check_limite(u, "pescar"):
        await ctx.send(f"❌ {ctx.author.mention} você já pescou **3/3** vezes hoje! Volte amanhã.")
        return
    cd = u["cooldowns"].get("pescar", 0)
    agora = datetime.now().timestamp()
    if agora < cd:
        await ctx.send(f"🎣 Aguarde **{int(cd - agora)}s** para pescar de novo!")
        return
    peixe, descricao_peixe, bonus_peixe = random.choice(PEIXES)
    mult = multiplicador_ganho(dados, "pescar")
    ganho_base = random.randint(50, 200)
    ganho = max(0, int((ganho_base + bonus_peixe) * mult))
    e_tubarao = peixe == "tubarão-touro"
    if e_tubarao:
        u["estatisticas"]["pescou_tubarao"] = True
    u["fichas"] += ganho
    u["total"] += ganho
    add_minigame(u, "pescar")
    u["estatisticas"]["pescar_total"] = u["estatisticas"].get("pescar_total", 0) + 1
    mensagens_extra = registrar_missao(u, "pescar")
    novas_conquistas = verificar_conquistas(u)
    u["cooldowns"]["pescar"] = agora + get_cooldown(u, "pescar")
    restantes = LIMITE_DIARIO - u["minigames"]["pescar"]
    template = random.choice(MENSAGENS_PESCAR)
    msg_pesca = template.format(nome=ctx.author.display_name, item=peixe, extra=descricao_peixe)
    mult_str = f" _(clima/humor: x{mult:.2f})_" if mult != 1.0 else ""
    ev_aleatorio = evento_aleatorio()
    if ev_aleatorio:
        texto_ev, delta_ev = ev_aleatorio
        u["fichas"] = max(0, u["fichas"] + delta_ev)
    registrar_evento(dados, "pescar", f"🎣 {ctx.author.display_name} pescou um {peixe} e ganhou {ganho} <:fichas:1517923672575185048>.")
    if e_tubarao:
        registrar_marco(dados, f"🦈 {ctx.author.display_name} pescou um TUBARÃO pela primeira vez!")
    salvar(dados)
    await ctx.send(f"{msg_pesca}\n💰 **+{ganho} <:fichas:1517923672575185048>**{mult_str} (**{restantes}/3** restantes hoje)")
    if ev_aleatorio:
        texto_ev, delta_ev = ev_aleatorio
        sinal = "+" if delta_ev > 0 else ""
        await ctx.send(f"✨ *Evento aleatório:* {texto_ev} (**{sinal}{delta_ev} <:fichas:1517923672575185048>**)")
    await verificar_patente(ctx, u, dados)
    for m in mensagens_extra:
        await ctx.send(m)
    for c in novas_conquistas:
        await ctx.send(f"🏆 **Conquista desbloqueada:** {c['nome']} (+{c['recompensa']} <:fichas:1517923672575185048>)")

PRESAS = [
    ("javali selvagem", "Resistiu bastante, mas você é mais esperto.", 0),
    ("veado de estimação de alguém", "Situação estranha.", -30),
    ("raposa astuta", "Quase te enganou.", 0),
    ("urso pardo", "Que coragem.", 80),
    ("coelho raro", "Rapidinho!", 0),
    ("fantasma da floresta", "Ninguém acredita, mas você capturou.", 50),
    ("pato confuso", "Ele não entendeu o que aconteceu.", 0),
    ("avestruz irada", "Não foi fácil.", 0),
    ("sombra de uma árvore", "Técnico, mas conta.", -20),
]

@bot.command(name="caçar")
async def cacar(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if not check_limite(u, "cacar"):
        await ctx.send(f"❌ {ctx.author.mention} você já caçou **3/3** vezes hoje! Volte amanhã.")
        return
    cd = u["cooldowns"].get("cacar", 0)
    agora = datetime.now().timestamp()
    if agora < cd:
        await ctx.send(f"🏹 Aguarde **{int(cd - agora)}s** para caçar de novo!")
        return
    presa, descricao_presa, bonus_presa = random.choice(PRESAS)
    mult = multiplicador_ganho(dados, "cacar")
    ganho = max(0, int((random.randint(80, 300) + bonus_presa) * mult))
    u["fichas"] += ganho
    u["total"] += ganho
    add_minigame(u, "cacar")
    u["estatisticas"]["cacar_total"] = u["estatisticas"].get("cacar_total", 0) + 1
    mensagens_extra = registrar_missao(u, "cacar")
    novas_conquistas = verificar_conquistas(u)
    u["cooldowns"]["cacar"] = agora + get_cooldown(u, "cacar")
    restantes = LIMITE_DIARIO - u["minigames"]["cacar"]
    mult_str = f" _(x{mult:.2f})_" if mult != 1.0 else ""
    ev_aleatorio = evento_aleatorio()
    if ev_aleatorio:
        texto_ev, delta_ev = ev_aleatorio
        u["fichas"] = max(0, u["fichas"] + delta_ev)
    registrar_evento(dados, "cacar", f"🏹 {ctx.author.display_name} caçou um {presa} e ganhou {ganho} <:fichas:1517923672575185048>.")
    salvar(dados)
    await ctx.send(f"🏹 {ctx.author.display_name} caçou um **{presa}**! _{descricao_presa}_\n💰 **+{ganho} <:fichas:1517923672575185048>**{mult_str} (**{restantes}/3** restantes hoje)")
    if ev_aleatorio:
        texto_ev, delta_ev = ev_aleatorio
        sinal = "+" if delta_ev > 0 else ""
        await ctx.send(f"✨ *Evento aleatório:* {texto_ev} (**{sinal}{delta_ev} <:fichas:1517923672575185048>**)")
    await verificar_patente(ctx, u, dados)
    for m in mensagens_extra:
        await ctx.send(m)
    for c in novas_conquistas:
        await ctx.send(f"🏆 **Conquista desbloqueada:** {c['nome']} (+{c['recompensa']} <:fichas:1517923672575185048>)")

MINERIOS = [
    ("pepita de ouro", "Pequena mas valiosa!", 100),
    ("carvão", "Não é ouro, mas aquece.", 0),
    ("cristal azul raro", "Reluzente!", 80),
    ("pedra comum", "Ela é só uma pedra. Mas é uma pedra bonita.", -30),
    ("diamante bruto", "DIAMANTE! 💎 Incrível!", 200),
    ("ferro enferrujado", "Dá pra fazer alguma coisa com isso.", 0),
    ("esmeralda imperfeita", "Imperfeita, mas bela.", 50),
    ("sal-gema", "Pelo menos dá pra temperar a comida.", 0),
    ("fóssil misterioso", "A ciência agradece. Você nem tanto.", 30),
    ("cobre", "Funcional.", 0),
]

@bot.command(name="minerar")
async def minerar(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if not check_limite(u, "minerar"):
        await ctx.send(f"❌ {ctx.author.mention} você já minerou **3/3** vezes hoje! Volte amanhã.")
        return
    cd = u["cooldowns"].get("minerar", 0)
    agora = datetime.now().timestamp()
    if agora < cd:
        await ctx.send(f"⛏️ Aguarde **{int(cd - agora)}s** para minerar de novo!")
        return
    minerio, descricao_minerio, bonus_minerio = random.choice(MINERIOS)
    mult = multiplicador_ganho(dados, "minerar")
    ganho = max(0, int((random.randint(100, 400) + bonus_minerio) * mult))
    u["fichas"] += ganho
    u["total"] += ganho
    add_minigame(u, "minerar")
    u["estatisticas"]["minerar_total"] = u["estatisticas"].get("minerar_total", 0) + 1
    mensagens_extra = registrar_missao(u, "minerar")
    novas_conquistas = verificar_conquistas(u)
    u["cooldowns"]["minerar"] = agora + get_cooldown(u, "minerar")
    restantes = LIMITE_DIARIO - u["minigames"]["minerar"]
    mult_str = f" _(x{mult:.2f})_" if mult != 1.0 else ""
    ev_aleatorio = evento_aleatorio()
    if ev_aleatorio:
        texto_ev, delta_ev = ev_aleatorio
        u["fichas"] = max(0, u["fichas"] + delta_ev)
    registrar_evento(dados, "minerar", f"⛏️ {ctx.author.display_name} minerou {minerio} e ganhou {ganho} <:fichas:1517923672575185048>.")
    if minerio == "diamante bruto":
        registrar_marco(dados, f"💎 {ctx.author.display_name} encontrou um diamante bruto!")
    salvar(dados)
    await ctx.send(f"⛏️ {ctx.author.display_name} encontrou **{minerio}**! _{descricao_minerio}_\n💰 **+{ganho} <:fichas:1517923672575185048>**{mult_str} (**{restantes}/3** restantes hoje)")
    if ev_aleatorio:
        texto_ev, delta_ev = ev_aleatorio
        sinal = "+" if delta_ev > 0 else ""
        await ctx.send(f"✨ *Evento aleatório:* {texto_ev} (**{sinal}{delta_ev} <:fichas:1517923672575185048>**)")
    await verificar_patente(ctx, u, dados)
    for m in mensagens_extra:
        await ctx.send(m)
    for c in novas_conquistas:
        await ctx.send(f"🏆 **Conquista desbloqueada:** {c['nome']} (+{c['recompensa']} <:fichas:1517923672575185048>)")

@bot.command(name="bilhete")
async def bilhete(ctx, quantidade: int = 1):
    if quantidade <= 0:
        await ctx.send("❌ A quantidade deve ser maior que zero!")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    custo = PRECO_BILHETE * quantidade
    if u["fichas"] < custo:
        await ctx.send(f"❌ Você precisa de **{custo} <:fichas:1517923672575185048>** para comprar {quantidade} bilhete(s). Você tem **{u['fichas']}**.")
        return
    u["fichas"] -= custo
    loteria = get_loteria(dados)
    uid = str(ctx.author.id)
    loteria["bilhetes"][uid] = loteria["bilhetes"].get(uid, 0) + quantidade
    loteria["pote"] += custo
    salvar(dados)
    total_bilhetes = loteria["bilhetes"][uid]
    await ctx.send(f"🎫 {ctx.author.mention} comprou **{quantidade} bilhete(s)** da loteria por **{custo} <:fichas:1517923672575185048>**! Você tem **{total_bilhetes}** bilhete(s) essa rodada.\n💰 Pote atual: **{loteria['pote']} <:fichas:1517923672575185048>**")

@bot.command(name="loteria")
async def loteria_status(ctx):
    dados = carregar()
    loteria = get_loteria(dados)
    total_bilhetes = sum(loteria["bilhetes"].values())
    msg = f"""🎰 **Loteria Semanal**

🎫 Preço do bilhete: **{PRECO_BILHETE} <:fichas:1517923672575185048>**
💰 Pote atual: **{loteria['pote']} <:fichas:1517923672575185048>**
🎟️ Total de bilhetes vendidos: **{total_bilhetes}**

Compre com `!bilhete [quantidade]`!"""
    await ctx.send(msg)

@bot.command(name="apostar")
async def apostar(ctx, valor: int):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if valor < 50:
        await ctx.send("❌ Aposta mínima é de **50 <:fichas:1517923672575185048>!**")
        return
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} <:fichas:1517923672575185048>!**")
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
        await ctx.send(f"🎰 {ctx.author.mention} ganhou **{ganho} <:fichas:1517923672575185048>!** 💰{bonus_msg}")
        await verificar_patente(ctx, u, dados)
    else:
        u["fichas"] -= valor
        await ctx.send(f"🎰 {ctx.author.mention} perdeu **{valor} <:fichas:1517923672575185048>!** 😢")
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
    agora = datetime.now().timestamp()
    if agora < cd:
        await ctx.send(f"🦹 Aguarde **{int(cd - agora)}s** para roubar de novo!")
        return
    if alvo["fichas"] < 50:
        await ctx.send(f"❌ {membro.mention} não tem <:fichas:1517923672575185048> suficientes!")
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
        u["estatisticas"]["fichas_roubadas_total"] = u["estatisticas"].get("fichas_roubadas_total", 0) + ganho
        novas_conquistas = verificar_conquistas(u)
        registrar_evento(dados, "roubar", f"🦹 {ctx.author.display_name} roubou {ganho} <:fichas:1517923672575185048> de {membro.display_name}.")
        # Sistema procurado: quem roubar 3+ vezes com sucesso no mesmo dia fica procurado
        roubos_hoje = u["minigames"].get("roubar", 0)
        if roubos_hoje >= 3 and not u.get("procurado"):
            recompensa_p = random.randint(200, 600)
            u["procurado"] = True
            u["recompensa_procurado"] = recompensa_p
            u["vezes_procurado"] = u.get("vezes_procurado", 0) + 1
            dados["_procurado_atual"] = {"uid": str(ctx.author.id), "nome": ctx.author.display_name, "recompensa": recompensa_p}
            registrar_marco(dados, f"🚨 {ctx.author.display_name} ficou PROCURADO com recompensa de {recompensa_p} <:fichas:1517923672575185048>!")
            await ctx.send(f"🚨 {ctx.author.mention} roubou demais e agora está **PROCURADO**! Recompensa: **{recompensa_p} <:fichas:1517923672575185048>** para quem o capturar com `!capturar @{ctx.author.display_name}`!")
        await ctx.send(f"🦹 {ctx.author.mention} roubou **{ganho} <:fichas:1517923672575185048>** de {membro.mention}! (**{restantes}/3** restantes hoje)")
        await verificar_patente(ctx, u, dados)
    else:
        multa = random.randint(50, 150)
        u["fichas"] = max(0, u["fichas"] - multa)
        registrar_evento(dados, "roubar_falhou", f"🚔 {ctx.author.display_name} tentou roubar {membro.display_name} e foi pego.")
        await ctx.send(f"🚔 {ctx.author.mention} foi pego e pagou **{multa} <:fichas:1517923672575185048>** de multa! (**{restantes}/3** restantes hoje)")
    u["cooldowns"]["roubar"] = agora + get_cooldown(u, "roubar")
    salvar(dados)
    for m in mensagens_extra:
        await ctx.send(m)
    for c in novas_conquistas:
        await ctx.send(f"🏆 **Conquista desbloqueada:** {c['nome']} (+{c['recompensa']} <:fichas:1517923672575185048>)")

PRESENTES_DIARIOS = [
    {"nome": "🍫 Chocolate", "tipo": "fichas", "valor": 50, "desc": "Ganhou +50 <:fichas:1517923672575185048> extras de bônus!"},
    {"nome": "🍫 Caixa de Chocolates Especial", "tipo": "fichas", "valor": 120, "desc": "Uma caixa inteira! +120 <:fichas:1517923672575185048> de bônus!"},
    {"nome": "🍀 Trevo da Sorte", "tipo": "trevo", "valor": 60, "desc": "Bônus de +10% em todos os ganhos por 1 hora!"},
    {"nome": "📦 Caixa Surpresa", "tipo": "caixa", "valor": 0, "desc": "Uma caixa misteriosa..."},
    {"nome": "😴 Dia de Folga", "tipo": "folga", "valor": 0, "desc": "Seus cooldowns estão zerados hoje!"},
    {"nome": "🪙 Nada especial", "tipo": "fichas", "valor": 0, "desc": "Só as <:fichas:1517923672575185048> normais mesmo."},
]

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
    recompensa_base = 100 + bonus_streak
    presente = random.choice(PRESENTES_DIARIOS)
    msg_presente = ""
    if presente["tipo"] == "fichas" and presente["valor"] > 0:
        recompensa_base += presente["valor"]
        msg_presente = f"\n🎁 **Presente:** {presente['nome']} — _{presente['desc']}_"
    elif presente["tipo"] == "trevo":
        u["trevo_ate"] = (datetime.now() + timedelta(hours=1)).isoformat()
        msg_presente = f"\n🎁 **Presente:** {presente['nome']} — _{presente['desc']}_"
    elif presente["tipo"] == "caixa":
        caixa_valor = random.randint(50, 500)
        recompensa_base += caixa_valor
        msg_presente = f"\n🎁 **Presente:** {presente['nome']} — _Continha **{caixa_valor} <:fichas:1517923672575185048>** dentro!_"
    elif presente["tipo"] == "folga":
        u["cooldowns"] = {}
        msg_presente = f"\n🎁 **Presente:** {presente['nome']} — _{presente['desc']}_"
    u["fichas"] += recompensa_base
    u["total"] += recompensa_base
    u["ultimo_diario"] = str(hoje)
    u["streak_diario"] = streak
    novas_conquistas = verificar_conquistas(u)
    registrar_evento(dados, "diario", f"📅 {ctx.author.display_name} coletou o diário e ganhou {recompensa_base} <:fichas:1517923672575185048> (streak {streak}).")
    salvar(dados)
    await ctx.send(f"📅 {ctx.author.mention} coletou a recompensa diária!\n💰 **+{recompensa_base} <:fichas:1517923672575185048>** (sequência: **{streak} dia(s)**){msg_presente}")
    await verificar_patente(ctx, u, dados)
    for c in novas_conquistas:
        await ctx.send(f"🏆 **Conquista desbloqueada:** {c['nome']} (+{c['recompensa']} <:fichas:1517923672575185048>)")

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
        await ctx.send(f"❌ Você só tem **{u['fichas']} <:fichas:1517923672575185048>!**")
        return
    destino = get_usuario(dados, membro.id)
    u["fichas"] -= valor
    destino["fichas"] += valor
    destino["total"] += valor
    salvar(dados)
    await ctx.send(f"💸 {ctx.author.mention} transferiu **{valor} <:fichas:1517923672575185048>** para {membro.mention}!")
    await verificar_patente(ctx, destino, dados)

@bot.command(name="itens")
async def itens(ctx):
    msg = "🎁 **Loja de Itens**\n\n"
    for key, item in ITENS.items():
        msg += f"{item['nome']} → **{item['preco']} <:fichas:1517923672575185048>**\n_{item['desc']}_\n`!comprar {key}`\n\n"
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
    if ctx.channel.id in quizzes_ativos:
        await ctx.send("❌ Já tem um quiz ativo nesse canal! Espere terminar.")
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
    msg_texto = f"""🧠 **QUIZ - VALENDO PRA TODO MUNDO!** {emoji} **{dif.upper()}** {f"| {nome_categoria}" if nome_categoria else ""}

**{pergunta['p']}**

{ops}

⏰ **20 segundos!** Quem acertar primeiro leva o prêmio!
✅ Acerto: **+{ganho} <:fichas:1517923672575185048>** (só pra quem acertar primeiro) | ❌ Erro: **-{perda} <:fichas:1517923672575185048>** (pra cada um que errar)"""
    view = QuizView(pergunta, ganho, perda, ctx.channel.id)
    msg = await ctx.send(msg_texto, view=view)
    quizzes_ativos[ctx.channel.id] = msg

@bot.command(name="saldo")
async def saldo(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    patente = PATENTES[u["patente"]]["nome"] if u["patente"] >= 0 else "Sem patente"
    await ctx.send(f"💰 {ctx.author.mention} tem **{u['fichas']} <:fichas:1517923672575185048>**\n🏅 Patente: **{patente}**\n📊 Total acumulado: **{u['total']} <:fichas:1517923672575185048>**")

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
        msg += f"{m['desc']} — **{status}** | recompensa: **{m['recompensa']} <:fichas:1517923672575185048>**\n"
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
        msg += f"{check} **{c['nome']}** — {c['desc']} _(+{c['recompensa']} <:fichas:1517923672575185048>)_\n"
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
        msg += f"{medal} {nome} — **{fichas} <:fichas:1517923672575185048>** | {wins} wins\n"
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
        msg += f"{medal} {nome} — **{ganho} <:fichas:1517923672575185048> ganhas**\n"
    msg += "\nA semana reseta automaticamente toda segunda-feira."
    await ctx.send(msg)

@bot.command(name="loja")
async def loja(ctx):
    msg = "🛒 **Loja de Cargos**\n\n"
    for key, item in LOJA.items():
        msg += f"{item['nome']} → **{item['preco']} <:fichas:1517923672575185048>** | `!comprar {key}`\n"
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
            await ctx.send(f"❌ Você precisa de **{produto['preco']} <:fichas:1517923672575185048>!** Você tem **{u['fichas']}**.")
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
        await ctx.send(f"❌ Você precisa de **{produto['preco']} <:fichas:1517923672575185048>!** Você tem **{u['fichas']}**.")
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

@bot.command(name="clima")
async def clima(ctx):
    dados = carregar()
    tipo = garantir_clima(dados)
    salvar(dados)
    info = next(c for c in CLIMAS if c["id"] == tipo)
    await ctx.send(f"🌍 **Clima do dia:** {info['nome']}\n_Efeito: {info['efeito']}_")

@bot.command(name="humor")
async def humor(ctx):
    dados = carregar()
    tipo = garantir_humor(dados)
    salvar(dados)
    info = next(h for h in HUMORES if h["id"] == tipo)
    await ctx.send(f"😊 **Humor do bot hoje:** {info['nome']}\n_Efeito: {info['efeito']}_")

@bot.command(name="investir")
async def investir(ctx, valor: int):
    if valor < 100:
        await ctx.send("❌ Valor mínimo para investir é **100 <:fichas:1517923672575185048>**!")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if u.get("investimento"):
        venc = datetime.fromisoformat(u["investimento"]["vence"])
        if datetime.now() < venc:
            restante = int((venc - datetime.now()).total_seconds() // 60)
            await ctx.send(f"❌ Você já tem um investimento ativo! Resgate com `!resgatar` em **{restante} min**.")
            return
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} <:fichas:1517923672575185048>**!")
        return
    u["fichas"] -= valor
    horas = random.choice([2, 4, 6, 8])
    resultado = random.choice(["lucro", "prejuizo", "nada"])
    if resultado == "lucro":
        pct = random.randint(10, 40)
        retorno = int(valor * (1 + pct / 100))
        descricao = f"📈 Lucro de {pct}% — retorno esperado: **{retorno} <:fichas:1517923672575185048>**"
    elif resultado == "prejuizo":
        pct = random.randint(5, 25)
        retorno = int(valor * (1 - pct / 100))
        descricao = f"📉 Mercado instável... retorno esperado: **{retorno} <:fichas:1517923672575185048>** (prejuízo de {pct}%)"
    else:
        retorno = valor
        descricao = f"➡️ Mercado estável. Retorno esperado: **{retorno} <:fichas:1517923672575185048>** (sem lucro nem prejuízo)"
    u["investimento"] = {
        "valor": valor,
        "retorno": retorno,
        "vence": (datetime.now() + timedelta(hours=horas)).isoformat(),
        "horas": horas,
        "descricao": descricao
    }
    registrar_evento(dados, "investir", f"📊 {ctx.author.display_name} investiu {valor} <:fichas:1517923672575185048> por {horas}h.")
    salvar(dados)
    await ctx.send(f"🏦 {ctx.author.mention} investiu **{valor} <:fichas:1517923672575185048>** por **{horas} horas**!\n{descricao}\nUse `!resgatar` depois de {horas}h para receber o retorno.")

@bot.command(name="resgatar")
async def resgatar(ctx):
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    inv = u.get("investimento")
    if not inv:
        await ctx.send(f"❌ {ctx.author.mention} você não tem investimento ativo! Use `!investir [valor]`.")
        return
    venc = datetime.fromisoformat(inv["vence"])
    if datetime.now() < venc:
        restante = int((venc - datetime.now()).total_seconds() // 60)
        await ctx.send(f"⏳ Ainda faltam **{restante} minutos** para o investimento vencer! Aguarde.")
        return
    retorno = inv["retorno"]
    lucro = retorno - inv["valor"]
    u["fichas"] += retorno
    u["total"] += max(0, lucro)
    u["investimento"] = None
    sinal = "+" if lucro >= 0 else ""
    registrar_evento(dados, "resgatar", f"🏦 {ctx.author.display_name} resgatou investimento: {sinal}{lucro} <:fichas:1517923672575185048> ({retorno} no total).")
    salvar(dados)
    await ctx.send(f"🏦 {ctx.author.mention} resgatou o investimento!\n💰 Recebeu **{retorno} <:fichas:1517923672575185048>** ({sinal}{lucro} de resultado)")
    await verificar_patente(ctx, u, dados)

@bot.command(name="procurado")
async def procurado(ctx):
    dados = carregar()
    p = dados.get("_procurado_atual")
    if not p:
        await ctx.send("🔍 Não há ninguém procurado no momento.")
        return
    await ctx.send(f"🚨 **PROCURADO:** {p['nome']}\n💰 Recompensa: **{p['recompensa']} <:fichas:1517923672575185048>**\nUse `!capturar @{p['nome']}` para capturá-lo!")

@bot.command(name="capturar")
async def capturar(ctx, alvo: discord.Member):
    dados = carregar()
    p = dados.get("_procurado_atual")
    if not p or p["uid"] != str(alvo.id):
        await ctx.send(f"❌ {alvo.display_name} não está procurado!")
        return
    if ctx.author.id == alvo.id:
        await ctx.send("❌ Você não pode se capturar!")
        return
    u_captor = get_usuario(dados, ctx.author.id)
    u_alvo = get_usuario(dados, alvo.id)
    recompensa = p["recompensa"]
    u_captor["fichas"] += recompensa
    u_captor["total"] += recompensa
    u_alvo["procurado"] = False
    u_alvo["recompensa_procurado"] = 0
    dados["_procurado_atual"] = None
    registrar_evento(dados, "captura", f"🚔 {ctx.author.display_name} capturou {alvo.display_name} (procurado) e ganhou {recompensa} <:fichas:1517923672575185048>.")
    registrar_marco(dados, f"🚔 {ctx.author.display_name} capturou o criminoso {alvo.display_name} e recebeu {recompensa} <:fichas:1517923672575185048>!")
    salvar(dados)
    await ctx.send(f"🚔 {ctx.author.mention} capturou **{alvo.display_name}** e recebeu **{recompensa} <:fichas:1517923672575185048>** de recompensa!")

@bot.command(name="jornal")
async def jornal(ctx):
    dados = carregar()
    eventos = dados.get("_eventos", [])
    if not eventos:
        await ctx.send("📰 **Jornal do Servidor**\n\n_Ainda não há eventos registrados hoje. Jogue pra aparecer aqui!_")
        return
    hoje = str(date.today())
    eventos_hoje = [e for e in eventos if e["timestamp"].startswith(hoje)][-10:]
    if not eventos_hoje:
        eventos_hoje = eventos[-8:]
    msg = "📰 **Jornal do Servidor**\n\n"
    for e in reversed(eventos_hoje):
        msg += f"• {e['texto']}\n"
    await ctx.send(msg)

@bot.command(name="memorias")
async def memorias(ctx):
    dados = carregar()
    marcos = dados.get("_marcos", [])
    if not marcos:
        await ctx.send("🌟 **Memórias do Servidor**\n\n_Nenhuma memória registrada ainda. Conquiste algo épico!_")
        return
    msg = "🌟 **Memórias do Servidor**\n\n"
    for m in reversed(marcos[-10:]):
        ts = datetime.fromisoformat(m["timestamp"])
        dias = (datetime.now() - ts).days
        if dias == 0:
            quando = "hoje"
        elif dias == 1:
            quando = "ontem"
        else:
            quando = f"há {dias} dias"
        msg += f"• _{quando}:_ {m['texto']}\n"
    await ctx.send(msg)

@bot.command(name="ajuda")
async def ajuda(ctx):
    categorias_str = ", ".join(f"`{k}`" for k in CATEGORIA_NOMES)
    msg1 = f"""🤖 **Comandos do Tigrinho — Parte 1: Diversão**

🎮 **Minigames** (3x por dia cada)
`!pescar` `!caçar` `!minerar` — Ganhe <:fichas:1517923672575185048> com mensagens engraçadas
`!apostar [valor]` — Aposta (mín. 50 <:fichas:1517923672575185048>)
`!roubar @pessoa` — Tenta roubar alguém (3x/dia)
`!diario` — Recompensa diária com presente surpresa
`!duelo @pessoa [valor]` — Pedra, papel e tesoura apostado!

🧠 **Quiz** (disputa — quem acertar primeiro ganha!)
`!quiz [categoria]` — Categorias: {categorias_str}

🐉 **Chefe do Servidor**
`!chefe` — Ver chefe ativo | `!atacarchefe` — Atacar (30s)

🎭 **Identidade Secreta**
`!identidade` — Papel secreto do dia por DM

🏦 **Banco & Investimentos**
`!investir [valor]` — Investe por 2-8h | `!resgatar` — Resgata

🎰 **Cassino** (mín. 50 <:fichas:1517923672575185048>)
`!casino` — Ver todos os jogos
`!blackjack` `!roleta` `!slots` `!dados` `!hilo` `!guerra` `!crash`

🎟️ **Loteria Semanal** (sorteio automático todo domingo)
`!bilhete [qtd]` — 100 <:fichas:1517923672575185048> cada | `!loteria` — Ver pote

🌍 **Servidor**
`!clima` `!humor` `!jornal` `!memorias` `!parcerias`

🚨 **Procurado**
`!procurado` — Ver quem está na lista | `!capturar @pessoa` — Capturar"""

    msg2 = """🤖 **Comandos do Tigrinho — Parte 2: Economia & Progresso**

💰 **Economia**
`!saldo` — <:fichas:1517923672575185048> e patente
`!perfil [@pessoa]` — Perfil completo
`!inventario` — Itens guardados
`!top` — Ranking dos mais ricos
`!topsemana` — Ranking semanal
`!pagar @pessoa [valor]` — Transferir <:fichas:1517923672575185048>

🛒 **Loja & Itens**
`!loja` — Loja de cargos
`!itens` — Loja de itens consumíveis
`!comprar [item]` — Comprar cargo ou item
`!usar [item]` — Usar item do inventário

🎯 **Progresso**
`!missoes` — Missões diárias
`!conquistas [@pessoa]` — Conquistas desbloqueadas

⚔️ **Lutas**
`!lutar @pessoa` — Desafiar alguém (use os botões para lutar)

🏅 **Patentes** (por total acumulado)
🧢 Pobre → 10k <:fichas:1517923672575185048>
💵 Rico → 50k <:fichas:1517923672575185048>
💎 Milionário → 100k <:fichas:1517923672575185048>
🏦 Bilionário → 500k <:fichas:1517923672575185048>"""

    await ctx.send(msg1)
    await ctx.send(msg2)

    msg += f"\n\n🧠 **Categorias do quiz:** {categorias_str}"
    await ctx.send(msg)

@bot.command(name="ego")
async def ego(ctx):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    await ctx.send("""```fix
╔══════════════════════════════════════╗
║        ⚙️  PAINEL DO EGO            ║
╚══════════════════════════════════════╝

💰 ECONOMIA
  !darfichas @p [v]   → Adicionar fichas
  !tirfichas @p [v]   → Remover fichas
  !setfichas @p [v]   → Definir fichas
  !godmode @p         → 999999 <:fichas:1517923672575185048>
  !zerarfichas @p     → Zerar fichas

🎮 MINIGAMES
  !resetlimite @p     → Resetar limites diários
  !resetquiz          → Resetar quiz travado

⚔️ LUTA
  !dano2x @p          → Ativar dano 2x na luta
  !cancelluta @p      → Cancelar luta

📅 SEMANAL E LOTERIA
  !premiarsemana      → Premia top 1 e reseta semana
  !sortearloteria     → Sorteia loteria e zera pote

🤝 PARCERIAS
  !addparceria [nome] → Adicionar parceria
  !removerparceria    → Remover parceria

🐉 CHEFE DO SERVIDOR
  !invocar            → Invocar chefe com HP

🎭 IDENTIDADE / EVENTOS / DUELO
  (automáticos ou iniciados por jogadores)
  Eventos disparam sozinhos a cada ~1h
```""")

@bot.command(name="aura")
async def aura(ctx):
    if not is_staff(ctx.author):
        await ctx.send("❌ Você não tem permissão!")
        return
    await ctx.send("""```ansi
\u001b[1;35m╔══════════════════════════════════════════╗
║          ⚜️   PAINEL  AURA  ⚜️           ║
║         Sistema de Moderação             ║
╠══════════════════════════════════════════╣
║                                          ║
║  🔨 BANIMENTO                            ║
║  !altban @p [motivo]                     ║
║    → Alt-ban / comportamento suspeito    ║
║                                          ║
║  👢 EXPULSÃO                             ║
║  !kick @p [motivo]                       ║
║    → Expulsa sem banir                   ║
║                                          ║
║  🔇 SILÊNCIO (TIMEOUT)                   ║
║  !timeout @p [minutos] [motivo]          ║
║    → Silencia temporariamente            ║
║  !removertimeout @p                      ║
║    → Remove o silêncio                   ║
║                                          ║
║  🔒 LOCKDOWN                             ║
║  !lockdown                               ║
║    → Bloqueia o canal durante raid       ║
║  !unlockdown                             ║
║    → Desbloqueia o canal                 ║
║                                          ║
║  🔍 INFORMAÇÕES                          ║
║  !modinfo @p                             ║
║    → Idade da conta, avisos, suspeito?   ║
║                                          ║
╠══════════════════════════════════════════╣
║  🤖 DETECÇÃO AUTOMÁTICA (sem comando)    ║
╠══════════════════════════════════════════╣
║  🚨 Raid        → 8+ entradas em 60s    ║
║  ⚠️  Conta nova → menos de 7 dias       ║
║  🔇 Spam msg    → 6+ msgs em 5s         ║
║  ⛔ Spam cmds   → 8+ cmds em 10s        ║
║  💥 Nuke        → 3+ canais deletados   ║
║  📢 Mass create → 5+ canais criados     ║
║                                          ║
║  Alertas → canal de moderação + @admins ║
╚══════════════════════════════════════════╝\u001b[0m
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
    await ctx.send(f"✅ **{valor} <:fichas:1517923672575185048>** adicionadas para {membro.mention}!")
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
    await ctx.send(f"✅ **{valor} <:fichas:1517923672575185048>** removidas de {membro.mention}!")

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
    await ctx.send(f"✅ **GOD MODE** ativado para {membro.mention}! 999999 <:fichas:1517923672575185048>!")
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
    await ctx.send(f"🏆 **{membro_top.display_name}** venceu o ranking semanal com **{ganho_top} <:fichas:1517923672575185048> ganhas** e recebeu **{premio} <:fichas:1517923672575185048>** de prêmio!\n📅 Uma nova semana de ranking começou para todos!")

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
    mult_lot = multiplicador_loteria(dados)
    premio = int(loteria["pote"] * mult_lot)
    u_vencedor = get_usuario(dados, vencedor_id)
    u_vencedor["fichas"] += premio
    u_vencedor["total"] += premio
    membro = ctx.guild.get_member(int(vencedor_id))
    nome = membro.display_name if membro else f"<@{vencedor_id}>"
    registrar_marco(dados, f"🎰 {nome} ganhou a loteria semanal e levou {premio} <:fichas:1517923672575185048>!")
    dados["_loteria"] = {"bilhetes": {}, "pote": 0}
    salvar(dados)
    bonus_str = f" _(clima noturno: x{mult_lot:.2f})_" if mult_lot != 1.0 else ""
    await ctx.send(f"🎉🎰 **{nome}** ganhou a loteria semanal e levou **{premio} <:fichas:1517923672575185048>**{bonus_str}! Uma nova rodada começou.")

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

# ============================================================
# CONSTANTES DAS NOVAS FEATURES
# ============================================================

PAPEIS_SECRETOS = [
    {"id": "ladrao_sombra",    "nome": "🦹 Ladrão Sombra",      "desc": "Chance de roubo: 70%",          "bônus": "roubar_chance"},
    {"id": "minerador_lenda",  "nome": "⛏️ Minerador Lendário",  "desc": "Mineração vale o dobro",        "bônus": "minerar_dobro"},
    {"id": "pescador_sortudo", "nome": "🎣 Pescador Sortudo",    "desc": "Pesca sempre no máximo",        "bônus": "pescar_max"},
    {"id": "apostador_nato",   "nome": "🎰 Apostador Nato",      "desc": "Aposta: 60% de chance de ganhar","bônus": "apostar_chance"},
    {"id": "caçador_elite",    "nome": "🏹 Caçador de Elite",    "desc": "Caça vale o dobro",             "bônus": "cacar_dobro"},
    {"id": "negociante",       "nome": "💼 Negociante",          "desc": "Transferências não cobram nada","bônus": "pagar_gratis"},
    {"id": "sortudo",          "nome": "🍀 Sortudo",             "desc": "+20% em todos os ganhos",       "bônus": "tudo_bonus"},
    {"id": "amaldiçoado",      "nome": "💀 Amaldiçoado",        "desc": "-10% em tudo (azar!)",          "bônus": "tudo_malus"},
]

EVENTOS_SERVIDOR = [
    {"nome": "🌧️ Chuva de Ouro",       "desc": "Uma chuva de ouro cobre o servidor!",         "tipo": "todos_ganham",  "valor": 80},
    {"nome": "🌋 Terremoto",            "desc": "Um terremoto abala a economia!",               "tipo": "todos_perdem",  "valor": 50},
    {"nome": "🎁 Generosidade Divina",  "desc": "Uma força misteriosa distribui riquezas!",    "tipo": "todos_ganham",  "valor": 150},
    {"nome": "🦠 Praga Econômica",      "desc": "Uma praga assola os cofres do servidor!",     "tipo": "todos_perdem",  "valor": 100},
    {"nome": "🌟 Festival da Sorte",    "desc": "Todos ganham o dobro por 30 minutos!",        "tipo": "boost_tempo",   "valor": 30},
    {"nome": "🔥 Grande Incêndio",      "desc": "As <:fichas:1517923672575185048> queimam! Todos perdem um pouco.",   "tipo": "todos_perdem",  "valor": 70},
    {"nome": "🎉 Aniversário Secreto",  "desc": "Alguém faz aniversário! Todos comemoram.",    "tipo": "todos_ganham",  "valor": 60},
    {"nome": "⚡ Tempestade Mágica",    "desc": "Uma tempestade mágica redistribui riquezas!", "tipo": "redistribuir",  "valor": 200},
]

duelos_pendentes = {}  # {desafiado_id: {desafiante_id, valor, canal_id}}

def get_chefe(dados):
    if "_chefe" not in dados:
        dados["_chefe"] = None
    return dados["_chefe"]

def get_parcerias(dados):
    if "_parcerias" not in dados:
        dados["_parcerias"] = {"lista": [], "total": 0}
    return dados["_parcerias"]

def get_papel_secreto(dados, uid):
    hoje = str(date.today())
    uid = str(uid)
    if "_papeis" not in dados:
        dados["_papeis"] = {}
    if uid not in dados["_papeis"] or dados["_papeis"][uid]["data"] != hoje:
        papel = random.choice(PAPEIS_SECRETOS)
        dados["_papeis"][uid] = {"data": hoje, "papel": papel}
    return dados["_papeis"][uid]["papel"]

# ============================================================
# COMANDOS: DUELO DE APOSTAS
# ============================================================

class DueloView(View):
    def __init__(self, desafiante_id, desafiado_id, valor):
        super().__init__(timeout=60)
        self.desafiante_id = desafiante_id
        self.desafiado_id = desafiado_id
        self.valor = valor

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.desafiado_id:
            await interaction.response.send_message("❌ Esse duelo não é com você!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="✅ Aceitar", style=discord.ButtonStyle.primary)
    async def aceitar(self, interaction, button):
        self.stop()
        dados = carregar()
        u_desaf = get_usuario(dados, self.desafiante_id)
        u_desal = get_usuario(dados, self.desafiado_id)
        if u_desaf["fichas"] < self.valor or u_desal["fichas"] < self.valor:
            await interaction.response.edit_message(content="❌ Um dos jogadores não tem <:fichas:1517923672575185048> suficientes!", view=None)
            return
        opcoes = ["🪨 Pedra", "📄 Papel", "✂️ Tesoura"]
        escolha_a = random.choice(opcoes)
        escolha_b = random.choice(opcoes)
        vencedor_id = None
        if escolha_a == escolha_b:
            resultado = "Empate! As <:fichas:1517923672575185048> ficam onde estão."
        elif (escolha_a == "🪨 Pedra" and escolha_b == "✂️ Tesoura") or \
             (escolha_a == "📄 Papel" and escolha_b == "🪨 Pedra") or \
             (escolha_a == "✂️ Tesoura" and escolha_b == "📄 Papel"):
            vencedor_id = self.desafiante_id
            u_desaf["fichas"] += self.valor
            u_desaf["total"] += self.valor
            u_desal["fichas"] = max(0, u_desal["fichas"] - self.valor)
            desafiante = interaction.guild.get_member(self.desafiante_id)
            resultado = f"🏆 **{desafiante.display_name if desafiante else 'Desafiante'}** venceu e ganhou **{self.valor} <:fichas:1517923672575185048>!**"
        else:
            vencedor_id = self.desafiado_id
            u_desal["fichas"] += self.valor
            u_desal["total"] += self.valor
            u_desaf["fichas"] = max(0, u_desaf["fichas"] - self.valor)
            resultado = f"🏆 **{interaction.user.display_name}** venceu e ganhou **{self.valor} <:fichas:1517923672575185048>!**"
        desafiante_membro = interaction.guild.get_member(self.desafiante_id)
        nome_desafiante = desafiante_membro.display_name if desafiante_membro else "Desafiante"
        registrar_evento(dados, "duelo", f"🥊 {nome_desafiante} vs {interaction.user.display_name} — {resultado}")
        salvar(dados)
        await interaction.response.edit_message(
            content=f"🥊 **DUELO!**\n{nome_desafiante}: **{escolha_a}** vs {interaction.user.display_name}: **{escolha_b}**\n\n{resultado}",
            view=None
        )

    @discord.ui.button(label="❌ Recusar", style=discord.ButtonStyle.danger)
    async def recusar(self, interaction, button):
        self.stop()
        await interaction.response.edit_message(content="❌ Duelo recusado.", view=None)

@bot.command(name="duelo")
async def duelo(ctx, membro: discord.Member, valor: int):
    if membro.id == ctx.author.id:
        await ctx.send("❌ Você não pode duelar consigo mesmo!")
        return
    if membro.bot:
        await ctx.send("❌ Você não pode duelar contra um bot!")
        return
    if valor < 50:
        await ctx.send("❌ Valor mínimo do duelo é **50 <:fichas:1517923672575185048>**!")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} <:fichas:1517923672575185048>**!")
        return
    view = DueloView(ctx.author.id, membro.id, valor)
    await ctx.send(
        f"🥊 {ctx.author.mention} desafia {membro.mention} para um duelo de **Pedra, Papel e Tesoura**!\n"
        f"💰 Aposta: **{valor} <:fichas:1517923672575185048>**\n"
        f"⏰ {membro.display_name} tem **60 segundos** para aceitar!",
        view=view
    )

# ============================================================
# COMANDOS: IDENTIDADE SECRETA
# ============================================================

@bot.command(name="identidade")
async def identidade(ctx):
    dados = carregar()
    papel = get_papel_secreto(dados, ctx.author.id)
    salvar(dados)
    try:
        await ctx.author.send(
            f"🎭 **Sua identidade secreta de hoje:**\n\n"
            f"**{papel['nome']}**\n"
            f"_{papel['desc']}_\n\n"
            f"Ninguém mais sabe disso! Use bem seu bônus hoje. 🤫"
        )
        await ctx.send(f"🎭 {ctx.author.mention} recebeu sua identidade secreta no privado!")
    except:
        await ctx.send(f"❌ Não consegui te enviar DM! Ative as mensagens diretas do servidor.")

# ============================================================
# COMANDOS: CHEFE DO SERVIDOR
# ============================================================

@bot.command(name="invocar")
async def invocar(ctx):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    dados = carregar()
    chefe = get_chefe(dados)
    if chefe and chefe["hp"] > 0:
        await ctx.send(f"❌ Já há um chefe ativo: **{chefe['nome']}** com **{chefe['hp']} HP** restante!")
        return
    nomes_chefes = [
        ("🐉 Dragão do Caos", 5000),
        ("👹 Demônio das Fichas", 4000),
        ("🦑 Kraken da Economia", 3500),
        ("💀 Ceifador Sombrio", 4500),
        ("🧙 Mago Amaldiçoado", 3000),
    ]
    nome, hp = random.choice(nomes_chefes)
    premio_total = random.randint(2000, 6000)
    dados["_chefe"] = {"nome": nome, "hp": hp, "hp_max": hp, "premio": premio_total,
                       "danos": {}, "invocado_por": str(ctx.author.id)}
    registrar_marco(dados, f"👹 {ctx.author.display_name} invocou o chefe {nome}!")
    salvar(dados)
    await ctx.send(
        f"⚠️ **CHEFE INVOCADO!**\n\n"
        f"**{nome}** apareceu com **{hp} HP**!\n"
        f"💰 Prêmio total: **{premio_total} <:fichas:1517923672575185048>** (dividido entre quem mais atacou)\n"
        f"Use `!atacarchefe` para atacar! O golpe final ganha bônus especial!"
    )

@bot.command(name="atacarchefe")
async def atacarchefe(ctx):
    dados = carregar()
    chefe = get_chefe(dados)
    if not chefe or chefe["hp"] <= 0:
        await ctx.send("❌ Não há nenhum chefe ativo! Peça ao dono usar `!invocar`.")
        return
    u = get_usuario(dados, ctx.author.id)
    cd_chefe = u["cooldowns"].get("chefe", 0)
    agora = datetime.now().timestamp()
    if agora < cd_chefe:
        await ctx.send(f"⚔️ Aguarde **{int(cd_chefe - agora)}s** para atacar de novo!")
        return
    dano = random.randint(80, 350)
    chefe["hp"] = max(0, chefe["hp"] - dano)
    uid = str(ctx.author.id)
    chefe["danos"][uid] = chefe["danos"].get(uid, 0) + dano
    u["cooldowns"]["chefe"] = agora + 30
    golpe_final = chefe["hp"] <= 0
    if golpe_final:
        # Distribui o prêmio
        premio_total = chefe["premio"]
        bonus_final = int(premio_total * 0.3)
        resto = premio_total - bonus_final
        total_dano = sum(chefe["danos"].values())
        msgs = [f"💀 **{chefe['nome']} foi derrotado!**\n\n🏆 {ctx.author.mention} desferiu o **golpe final** e ganhou **{bonus_final} <:fichas:1517923672575185048>** de bônus!\n\n📊 **Distribuição do prêmio:**"]
        for uid_d, dmg in sorted(chefe["danos"].items(), key=lambda x: x[1], reverse=True):
            participante = dados.get(uid_d, {})
            membro_guild = ctx.guild.get_member(int(uid_d))
            nome_p = membro_guild.display_name if membro_guild else f"<@{uid_d}>"
            parte = int((dmg / total_dano) * resto)
            u_part = get_usuario(dados, uid_d)
            u_part["fichas"] += parte
            u_part["total"] += parte
            pct = int(dmg / total_dano * 100)
            msgs.append(f"• **{nome_p}** — {dmg} de dano ({pct}%) → **+{parte} <:fichas:1517923672575185048>**")
        # Bônus do golpe final
        u["fichas"] += bonus_final
        u["total"] += bonus_final
        registrar_marco(dados, f"⚔️ {ctx.author.display_name} derrotou {chefe['nome']} com o golpe final!")
        dados["_chefe"] = None
        salvar(dados)
        await ctx.send("\n".join(msgs))
    else:
        pct_hp = int(chefe["hp"] / chefe["hp_max"] * 100)
        barra = "█" * (pct_hp // 10) + "░" * (10 - pct_hp // 10)
        salvar(dados)
        await ctx.send(
            f"⚔️ {ctx.author.mention} atacou **{chefe['nome']}** e causou **{dano} de dano!**\n"
            f"❤️ HP: `{barra}` {chefe['hp']}/{chefe['hp_max']} ({pct_hp}%)"
        )

@bot.command(name="chefe")
async def ver_chefe(ctx):
    dados = carregar()
    chefe = get_chefe(dados)
    if not chefe or chefe["hp"] <= 0:
        await ctx.send("😴 Nenhum chefe ativo no momento. Peça ao dono usar `!invocar`.")
        return
    pct_hp = int(chefe["hp"] / chefe["hp_max"] * 100)
    barra = "█" * (pct_hp // 10) + "░" * (10 - pct_hp // 10)
    top_atacantes = sorted(chefe["danos"].items(), key=lambda x: x[1], reverse=True)[:5]
    msg = (
        f"👹 **{chefe['nome']}**\n"
        f"❤️ HP: `{barra}` {chefe['hp']}/{chefe['hp_max']} ({pct_hp}%)\n"
        f"💰 Prêmio: **{chefe['premio']} <:fichas:1517923672575185048>**\n\n"
        f"🗡️ **Top atacantes:**\n"
    )
    for uid_d, dmg in top_atacantes:
        membro_guild = ctx.guild.get_member(int(uid_d))
        nome_p = membro_guild.display_name if membro_guild else f"<@{uid_d}>"
        msg += f"• {nome_p} — **{dmg} dano**\n"
    await ctx.send(msg)

# ============================================================
# TAREFA: EVENTOS AUTOMÁTICOS DO SERVIDOR
# ============================================================

@tasks.loop(minutes=60)
async def evento_automatico():
    """Dispara um evento aleatório no servidor a cada 2-6 horas com chance de 40%."""
    if random.random() > 0.40:
        return
    canal = bot.get_channel(CANAL_BOT)
    if not canal:
        return
    dados = carregar()
    evento = random.choice(EVENTOS_SERVIDOR)
    membros_ativos = [uid for uid in dados if not uid.startswith("_") and dados[uid].get("fichas", 0) > 0]
    if not membros_ativos:
        return
    if evento["tipo"] == "todos_ganham":
        for uid in membros_ativos:
            u = get_usuario(dados, uid)
            u["fichas"] += evento["valor"]
            u["total"] += evento["valor"]
        registrar_marco(dados, f"🌟 Evento: {evento['nome']} — todos ganharam {evento['valor']} <:fichas:1517923672575185048>!")
        salvar(dados)
        await canal.send(
            f"⚡ **EVENTO DO SERVIDOR!**\n\n"
            f"**{evento['nome']}**\n"
            f"_{evento['desc']}_\n\n"
            f"🎉 Todos os jogadores ganharam **+{evento['valor']} <:fichas:1517923672575185048>!**"
        )
    elif evento["tipo"] == "todos_perdem":
        for uid in membros_ativos:
            u = get_usuario(dados, uid)
            u["fichas"] = max(0, u["fichas"] - evento["valor"])
        registrar_marco(dados, f"⚠️ Evento: {evento['nome']} — todos perderam {evento['valor']} <:fichas:1517923672575185048>!")
        salvar(dados)
        await canal.send(
            f"⚡ **EVENTO DO SERVIDOR!**\n\n"
            f"**{evento['nome']}**\n"
            f"_{evento['desc']}_\n\n"
            f"💸 Todos os jogadores perderam **{evento['valor']} <:fichas:1517923672575185048>!**"
        )
    elif evento["tipo"] == "redistribuir":
        if len(membros_ativos) < 2:
            return
        uid_rico = max(membros_ativos, key=lambda uid: dados[uid].get("fichas", 0))
        u_rico = get_usuario(dados, uid_rico)
        redistribuicao = min(evento["valor"], u_rico["fichas"] // 2)
        parte = redistribuicao // (len(membros_ativos) - 1)
        u_rico["fichas"] -= redistribuicao
        for uid in membros_ativos:
            if uid != uid_rico:
                u = get_usuario(dados, uid)
                u["fichas"] += parte
                u["total"] += parte
        membro_rico = canal.guild.get_member(int(uid_rico))
        nome_rico = membro_rico.display_name if membro_rico else "o mais rico"
        registrar_marco(dados, f"⚡ Tempestade redistributiva — {redistribuicao} <:fichas:1517923672575185048> de {nome_rico} foram distribuídas!")
        salvar(dados)
        await canal.send(
            f"⚡ **EVENTO DO SERVIDOR!**\n\n"
            f"**{evento['nome']}**\n"
            f"_{evento['desc']}_\n\n"
            f"🌀 **{redistribuicao} <:fichas:1517923672575185048>** foram redistribuídas de **{nome_rico}** para todos!"
        )

# ============================================================
# COMANDOS: PLACAR DE PARCERIAS
# ============================================================

@bot.command(name="parcerias")
async def parcerias(ctx):
    dados = carregar()
    p = get_parcerias(dados)
    lista = p.get("lista", [])
    total = p.get("total", 0)

    largura = 38
    linha_topo    = "╔" + "═" * largura + "╗"
    linha_titulo  = "║" + "  🤝 PARCERIAS DA IRMANDADE  ".center(largura) + "║"
    linha_sep     = "╠" + "═" * largura + "╣"
    linha_total   = "║" + f"  Total de parcerias: {total}".ljust(largura) + "║"
    linha_sep2    = "╠" + "═" * largura + "╣"
    linha_cabec   = "║" + "  Nº   Servidor".ljust(largura) + "║"
    linha_div     = "║" + "─" * largura + "║"
    linha_fundo   = "╚" + "═" * largura + "╝"

    linhas_serv = []
    for i, s in enumerate(lista, 1):
        nome = s["nome"][:27] if len(s["nome"]) > 27 else s["nome"]
        linhas_serv.append("║" + f"  {str(i).zfill(2)}.   {nome}".ljust(largura) + "║")

    if not linhas_serv:
        linhas_serv = ["║" + "  Nenhuma parceria ainda!".ljust(largura) + "║"]

    tabela = "\n".join([
        linha_topo, linha_titulo, linha_sep,
        linha_total, linha_sep2, linha_cabec, linha_div,
        *linhas_serv,
        linha_fundo
    ])
    await ctx.send(f"```\n{tabela}\n```")

@bot.command(name="addparceria")
async def addparceria(ctx, *, nome_servidor: str):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    dados = carregar()
    p = get_parcerias(dados)
    nomes_existentes = [s["nome"].lower() for s in p["lista"]]
    if nome_servidor.lower() in nomes_existentes:
        await ctx.send(f"❌ **{nome_servidor}** já está na lista de parcerias!")
        return
    p["lista"].append({"nome": nome_servidor, "data": str(date.today())})
    p["total"] += 1
    registrar_marco(dados, f"🤝 Nova parceria firmada com: {nome_servidor}!")
    salvar(dados)
    await ctx.send(f"✅ Parceria com **{nome_servidor}** adicionada! Total: **{p['total']}** parcerias.")

@bot.command(name="removerparceria")
async def removerparceria(ctx, *, nome_servidor: str):
    if ctx.author.id != DONO_ID:
        await ctx.send("❌ Você não tem permissão!")
        return
    dados = carregar()
    p = get_parcerias(dados)
    antes = len(p["lista"])
    p["lista"] = [s for s in p["lista"] if s["nome"].lower() != nome_servidor.lower()]
    if len(p["lista"]) == antes:
        await ctx.send(f"❌ **{nome_servidor}** não encontrado na lista!")
        return
    p["total"] = len(p["lista"])
    salvar(dados)
    await ctx.send(f"✅ **{nome_servidor}** removido das parcerias. Total agora: **{p['total']}**.")


# ============================================================
# CASSINO — TODOS OS JOGOS
# ============================================================

NAIPES = ["♠️", "♥️", "♦️", "♣️"]
VALORES_CARTA = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def novo_baralho():
    return [(v, n) for n in NAIPES for v in VALORES_CARTA]

def valor_carta(carta):
    v = carta[0]
    if v in ["J", "Q", "K"]:
        return 10
    if v == "A":
        return 11
    return int(v)

def valor_mao(mao):
    total = sum(valor_carta(c) for c in mao)
    ases = sum(1 for c in mao if c[0] == "A")
    while total > 21 and ases:
        total -= 10
        ases -= 1
    return total

def fmt_mao(mao):
    return " ".join(f"{v}{n}" for v, n in mao)

blackjacks_ativos = {}  # {user_id: {mao_jogador, mao_dealer, baralho, valor, ctx}}

@bot.command(name="casino")
async def casino(ctx):
    await ctx.send("""🎰 **BEM-VINDO AO CASSINO DA IRMANDADE!**

🃏 **Blackjack** — `!blackjack [valor]`
   Tente chegar a 21 sem ultrapassar. Supere o dealer!

🎡 **Roleta** — `!roleta [valor] [aposta]`
   Apostas: `vermelho`, `preto`, `par`, `impar`, ou número 0-36
   Ex: `!roleta 100 vermelho` ou `!roleta 100 7`

🎰 **Caça-Níquel** — `!slots [valor]`
   Gire os cilindros e torça pela combinação certa!

🎲 **Dados** — `!dados [valor] [1-6]`
   Adivinhe o resultado de dois dados somados (2-12)
   Ex: `!dados 100 7`

🃏 **Hi-Lo** — `!hilo [valor] [maior/menor]`
   Uma carta é revelada. Adivinhe se a próxima é maior ou menor!
   Ex: `!hilo 100 maior`

🎴 **Guerra de Cartas** — `!guerra [valor]`
   Você e o dealer recebem uma carta. Maior carta vence!

🎳 **Crash** — `!crash [valor]`
   O multiplicador sobe... mas pode cair a qualquer momento!
   
💰 **Aposta mínima em todos:** 50 <:fichas:1517923672575185048>""")

# ─── BLACKJACK ───────────────────────────────────────────────

class BlackjackView(View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Não é seu jogo!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="🃏 Pedir carta", style=discord.ButtonStyle.primary)
    async def pedir(self, interaction, button):
        jogo = blackjacks_ativos.get(self.user_id)
        if not jogo:
            await interaction.response.edit_message(content="❌ Jogo não encontrado!", view=None)
            return
        jogo["mao_jogador"].append(jogo["baralho"].pop())
        total = valor_mao(jogo["mao_jogador"])
        if total > 21:
            dados = carregar()
            u = get_usuario(dados, self.user_id)
            u["fichas"] = max(0, u["fichas"] - jogo["valor"])
            del blackjacks_ativos[self.user_id]
            salvar(dados)
            self.stop()
            await interaction.response.edit_message(
                content=f"🃏 **BLACKJACK**\nSua mão: {fmt_mao(jogo['mao_jogador'])} = **{total}**\n💥 **Estourou!** Você perdeu **{jogo['valor']} <:fichas:1517923672575185048>**.",
                view=None
            )
        else:
            await interaction.response.edit_message(
                content=f"🃏 **BLACKJACK**\nSua mão: {fmt_mao(jogo['mao_jogador'])} = **{total}**\nDealer mostra: {fmt_mao([jogo['mao_dealer'][0]])} + 🂠\nO que deseja fazer?",
                view=self
            )

    @discord.ui.button(label="✋ Parar", style=discord.ButtonStyle.secondary)
    async def parar(self, interaction, button):
        self.stop()
        jogo = blackjacks_ativos.get(self.user_id)
        if not jogo:
            await interaction.response.edit_message(content="❌ Jogo não encontrado!", view=None)
            return
        del blackjacks_ativos[self.user_id]
        total_j = valor_mao(jogo["mao_jogador"])
        while valor_mao(jogo["mao_dealer"]) < 17:
            jogo["mao_dealer"].append(jogo["baralho"].pop())
        total_d = valor_mao(jogo["mao_dealer"])
        dados = carregar()
        u = get_usuario(dados, self.user_id)
        if total_d > 21 or total_j > total_d:
            u["fichas"] += jogo["valor"]
            u["total"] += jogo["valor"]
            resultado = f"🏆 **Você venceu!** +{jogo['valor']} <:fichas:1517923672575185048>"
        elif total_j == total_d:
            resultado = "🤝 **Empate!** Fichas devolvidas."
        else:
            u["fichas"] = max(0, u["fichas"] - jogo["valor"])
            resultado = f"😢 **Dealer venceu!** -{jogo['valor']} <:fichas:1517923672575185048>"
        salvar(dados)
        await interaction.response.edit_message(
            content=f"🃏 **BLACKJACK — RESULTADO**\nSua mão: {fmt_mao(jogo['mao_jogador'])} = **{total_j}**\nDealer: {fmt_mao(jogo['mao_dealer'])} = **{total_d}**\n\n{resultado}",
            view=None
        )

@bot.command(name="blackjack")
async def blackjack(ctx, valor: int):
    if valor < 50:
        await ctx.send("❌ Aposta mínima: **50 <:fichas:1517923672575185048>**!")
        return
    if ctx.author.id in blackjacks_ativos:
        await ctx.send("❌ Você já tem um jogo de blackjack ativo! Use os botões pra continuar.")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} <:fichas:1517923672575185048>**!")
        return
    baralho = novo_baralho()
    random.shuffle(baralho)
    mao_j = [baralho.pop(), baralho.pop()]
    mao_d = [baralho.pop(), baralho.pop()]
    blackjacks_ativos[ctx.author.id] = {"mao_jogador": mao_j, "mao_dealer": mao_d,
                                         "baralho": baralho, "valor": valor}
    total_j = valor_mao(mao_j)
    if total_j == 21:
        u["fichas"] += int(valor * 1.5)
        u["total"] += int(valor * 1.5)
        salvar(dados)
        del blackjacks_ativos[ctx.author.id]
        await ctx.send(f"🃏 **BLACKJACK NATURAL!** 🎉\nSua mão: {fmt_mao(mao_j)} = **21**\n💰 Você ganhou **{int(valor*1.5)} <:fichas:1517923672575185048>!**")
        return
    salvar(dados)
    view = BlackjackView(ctx.author.id)
    await ctx.send(
        f"🃏 **BLACKJACK** (aposta: {valor} <:fichas:1517923672575185048>)\nSua mão: {fmt_mao(mao_j)} = **{total_j}**\nDealer mostra: {fmt_mao([mao_d[0]])} + 🂠\nO que deseja fazer?",
        view=view
    )

# ─── ROLETA ──────────────────────────────────────────────────

@bot.command(name="roleta")
async def roleta(ctx, valor: int, aposta: str):
    if valor < 50:
        await ctx.send("❌ Aposta mínima: **50 <:fichas:1517923672575185048>**!")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} <:fichas:1517923672575185048>**!")
        return
    numero = random.randint(0, 36)
    vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    cor = "🔴 vermelho" if numero in vermelhos else ("⬛ preto" if numero != 0 else "🟢 zero")
    paridade = "par" if numero != 0 and numero % 2 == 0 else ("ímpar" if numero != 0 else "zero")
    aposta = aposta.lower().replace("í","i").replace("é","e")
    ganhou = False
    mult = 1
    if aposta in ["vermelho", "preto"]:
        mult = 1
        ganhou = (aposta == "vermelho" and numero in vermelhos) or \
                 (aposta == "preto" and numero not in vermelhos and numero != 0)
    elif aposta in ["par", "impar"]:
        mult = 1
        ganhou = (aposta == "par" and paridade == "par") or \
                 (aposta == "impar" and paridade == "ímpar")
    elif aposta.isdigit() and 0 <= int(aposta) <= 36:
        mult = 35
        ganhou = int(aposta) == numero
    else:
        await ctx.send("❌ Aposta inválida! Use: `vermelho`, `preto`, `par`, `impar` ou um número de 0 a 36.")
        return
    animacao = f"🎡 A roleta gira... **{numero}** {cor}!"
    if ganhou:
        u["fichas"] += valor * mult
        u["total"] += valor * mult
        resultado = f"🏆 **Acertou!** +{valor * mult} <:fichas:1517923672575185048>!"
    else:
        u["fichas"] = max(0, u["fichas"] - valor)
        resultado = f"😢 **Errou!** -{valor} <:fichas:1517923672575185048>."
    salvar(dados)
    await ctx.send(f"🎡 **ROLETA**\n{animacao}\n{resultado}")

# ─── CAÇA-NÍQUEL ─────────────────────────────────────────────

SLOTS_SIMBOLOS = ["🍒", "🍋", "🔔", "💎", "⭐", "7️⃣", "🃏", "🍀"]
SLOTS_MULT = {"💎💎💎": 50, "7️⃣7️⃣7️⃣": 30, "⭐⭐⭐": 15, "🍀🍀🍀": 10,
              "🔔🔔🔔": 8, "🍒🍒🍒": 5, "🍋🍋🍋": 4, "🃏🃏🃏": 3}

@bot.command(name="slots")
async def slots(ctx, valor: int):
    if valor < 50:
        await ctx.send("❌ Aposta mínima: **50 <:fichas:1517923672575185048>**!")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} <:fichas:1517923672575185048>**!")
        return
    resultado = [random.choice(SLOTS_SIMBOLOS) for _ in range(3)]
    chave = "".join(resultado)
    mult = SLOTS_MULT.get(chave, 0)
    barra = f"[ {resultado[0]} | {resultado[1]} | {resultado[2]} ]"
    if mult > 0:
        ganho = valor * mult
        u["fichas"] += ganho
        u["total"] += ganho
        msg_res = f"🎉 **JACKPOT x{mult}!** Você ganhou **{ganho} <:fichas:1517923672575185048>!**"
    elif resultado[0] == resultado[1] or resultado[1] == resultado[2]:
        ganho = int(valor * 0.5)
        u["fichas"] += ganho
        u["total"] += ganho
        msg_res = f"🤏 **Quase!** 2 iguais → +{ganho} <:fichas:1517923672575185048> (metade de volta)"
    else:
        u["fichas"] = max(0, u["fichas"] - valor)
        msg_res = f"😢 Sem sorte... -{valor} <:fichas:1517923672575185048>."
    salvar(dados)
    await ctx.send(f"🎰 **CAÇA-NÍQUEL**\n{barra}\n{msg_res}")

# ─── DADOS ────────────────────────────────────────────────────

@bot.command(name="dados")
async def jogar_dados(ctx, valor: int, palpite: int):
    if valor < 50:
        await ctx.send("❌ Aposta mínima: **50 <:fichas:1517923672575185048>**!")
        return
    if not 2 <= palpite <= 12:
        await ctx.send("❌ Palpite deve ser entre 2 e 12 (soma de dois dados)!")
        return
    dados_bot = carregar()
    u = get_usuario(dados_bot, ctx.author.id)
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} <:fichas:1517923672575185048>**!")
        return
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    soma = d1 + d2
    mult = {2: 10, 3: 6, 4: 4, 5: 3, 6: 2, 7: 2, 8: 2, 9: 3, 10: 4, 11: 6, 12: 10}
    if soma == palpite:
        ganho = valor * mult[soma]
        u["fichas"] += ganho
        u["total"] += ganho
        resultado = f"🎉 **Acertou!** +{ganho} <:fichas:1517923672575185048> (x{mult[soma]})"
    else:
        u["fichas"] = max(0, u["fichas"] - valor)
        resultado = f"😢 **Errou!** A soma foi **{soma}** ({d1}+{d2}). -{valor} <:fichas:1517923672575185048>."
    salvar(dados_bot)
    await ctx.send(f"🎲 **DADOS**\n🎲{d1} + 🎲{d2} = **{soma}**\nSeu palpite: **{palpite}**\n{resultado}")

# ─── HI-LO ───────────────────────────────────────────────────

@bot.command(name="hilo")
async def hilo(ctx, valor: int, escolha: str):
    if valor < 50:
        await ctx.send("❌ Aposta mínima: **50 <:fichas:1517923672575185048>**!")
        return
    escolha = escolha.lower()
    if escolha not in ["maior", "menor"]:
        await ctx.send("❌ Escolha `maior` ou `menor`!")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} <:fichas:1517923672575185048>**!")
        return
    baralho = novo_baralho()
    random.shuffle(baralho)
    carta1 = baralho.pop()
    carta2 = baralho.pop()
    v1 = valor_carta(carta1)
    v2 = valor_carta(carta2)
    acertou = (escolha == "maior" and v2 > v1) or (escolha == "menor" and v2 < v1)
    if v1 == v2:
        resultado = f"🤝 **Empate!** Cartas iguais. Fichas devolvidas."
    elif acertou:
        u["fichas"] += valor
        u["total"] += valor
        resultado = f"🏆 **Acertou!** +{valor} <:fichas:1517923672575185048>!"
    else:
        u["fichas"] = max(0, u["fichas"] - valor)
        resultado = f"😢 **Errou!** -{valor} <:fichas:1517923672575185048>."
    salvar(dados)
    await ctx.send(
        f"🃏 **HI-LO**\nCarta 1: **{carta1[0]}{carta1[1]}** (valor {v1})\nCarta 2: **{carta2[0]}{carta2[1]}** (valor {v2})\nSua escolha: **{escolha}**\n{resultado}"
    )

# ─── GUERRA DE CARTAS ────────────────────────────────────────

@bot.command(name="guerra")
async def guerra(ctx, valor: int):
    if valor < 50:
        await ctx.send("❌ Aposta mínima: **50 <:fichas:1517923672575185048>**!")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} <:fichas:1517923672575185048>**!")
        return
    baralho = novo_baralho()
    random.shuffle(baralho)
    carta_j = baralho.pop()
    carta_d = baralho.pop()
    vj = valor_carta(carta_j)
    vd = valor_carta(carta_d)
    if vj > vd:
        u["fichas"] += valor
        u["total"] += valor
        resultado = f"🏆 **Você venceu!** +{valor} <:fichas:1517923672575185048>!"
    elif vj == vd:
        resultado = "🤝 **Empate!** Fichas devolvidas."
    else:
        u["fichas"] = max(0, u["fichas"] - valor)
        resultado = f"😢 **Dealer venceu!** -{valor} <:fichas:1517923672575185048>."
    salvar(dados)
    await ctx.send(
        f"🎴 **GUERRA DE CARTAS**\nSua carta: **{carta_j[0]}{carta_j[1]}** (valor {vj})\nDealer: **{carta_d[0]}{carta_d[1]}** (valor {vd})\n{resultado}"
    )

# ─── CRASH ───────────────────────────────────────────────────

@bot.command(name="crash")
async def crash(ctx, valor: int):
    if valor < 50:
        await ctx.send("❌ Aposta mínima: **50 <:fichas:1517923672575185048>**!")
        return
    dados = carregar()
    u = get_usuario(dados, ctx.author.id)
    if u["fichas"] < valor:
        await ctx.send(f"❌ Você só tem **{u['fichas']} <:fichas:1517923672575185048>**!")
        return
    # Multiplicador final entre 1.0x e 10x, com probabilidade decrescente
    crash_em = round(random.uniform(1.0, 10.0) * random.choice([1, 1, 1, 2]), 2)
    parou_em = round(random.uniform(1.0, crash_em), 2) if crash_em > 1.2 else crash_em
    ganhou = parou_em < crash_em
    if ganhou:
        ganho = int(valor * parou_em)
        lucro = ganho - valor
        u["fichas"] += lucro
        u["total"] += max(0, lucro)
        resultado = f"✅ **Saiu em x{parou_em}!** Você ganhou **{ganho} <:fichas:1517923672575185048>** (+{lucro})"
    else:
        u["fichas"] = max(0, u["fichas"] - valor)
        resultado = f"💥 **CRASH em x{crash_em}!** Você perdeu **{valor} <:fichas:1517923672575185048>**."
    salvar(dados)
    barra_crash = "📈" * min(int(crash_em), 8) + "💥"
    await ctx.send(
        f"🚀 **CRASH**\n{barra_crash}\nMultiplicador de crash: **x{crash_em}**\nVocê saiu em: **x{parou_em}**\n{resultado}"
    )


# ============================================================
# SISTEMA ANTI-RAID / ALT-BAN / MODERAÇÃO
# ============================================================

@bot.event
async def on_member_join(member):
    """Detecta raid (muitas entradas em pouco tempo) e contas novas suspeitas."""
    import time
    agora = time.time()
    _join_tracker.append(agora)
    # Mantém só os últimos 60 segundos
    _join_tracker[:] = [t for t in _join_tracker if agora - t < 60]

    guild = member.guild
    dias_conta = (discord.utils.utcnow() - member.created_at).days

    # ── Detecção de RAID: 8+ entradas em 60s ──
    if len(_join_tracker) >= 8:
        embed = discord.Embed(
            title="🚨 POSSÍVEL RAID DETECTADO",
            description=f"**{len(_join_tracker)} membros** entraram nos últimos 60 segundos!",
            color=0xFF0000
        )
        embed.add_field(name="Último a entrar", value=f"{member} (`{member.id}`)", inline=False)
        embed.add_field(name="Ação sugerida", value="Use `!lockdown` para bloquear entradas ou `!altban @pessoa` para banir suspeitos.", inline=False)
        await alertar_mods(guild, embed)

    # ── Alerta de conta nova (menos de 7 dias) ──
    if dias_conta < 7:
        embed = discord.Embed(
            title="⚠️ CONTA NOVA ENTROU",
            description=f"{member.mention} entrou no servidor.",
            color=0xFF8800
        )
        embed.add_field(name="Conta criada há", value=f"**{dias_conta} dias**", inline=True)
        embed.add_field(name="ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="Ação", value="Use `!altban @pessoa` se necessário.", inline=False)
        await alertar_mods(guild, embed)

@bot.event
async def on_message(message):
    """Detecta spam de mensagens (fora dos comandos) no servidor inteiro."""
    import time
    if message.author.bot or not message.guild:
        await bot.process_commands(message)
        return
    if is_staff(message.author):
        await bot.process_commands(message)
        return

    agora = time.time()
    uid = message.author.id
    if uid not in _msg_tracker:
        _msg_tracker[uid] = []
    _msg_tracker[uid].append(agora)
    _msg_tracker[uid] = [t for t in _msg_tracker[uid] if agora - t < 5]

    # 6+ mensagens em 5 segundos = spam
    if len(_msg_tracker[uid]) >= 6:
        _msg_tracker[uid] = []
        aplicou = await aplicar_timeout(message.author, 10, "Spam automático detectado")
        embed = discord.Embed(
            title="🔇 SPAM DETECTADO",
            description=f"{message.author.mention} enviou **{len(_msg_tracker.get(uid, []))+6}+ mensagens** em 5 segundos.",
            color=0xFF8800
        )
        embed.add_field(name="Ação tomada", value="Timeout de **10 minutos**" if aplicou else "Não foi possível aplicar timeout (cargo alto demais)", inline=False)
        embed.add_field(name="Canal", value=message.channel.mention, inline=True)
        await alertar_mods(message.guild, embed)
        try:
            await message.channel.send(f"🔇 {message.author.mention} foi silenciado por **10 minutos** por spam.", delete_after=8)
        except Exception:
            pass

    await bot.process_commands(message)

@bot.event
async def on_guild_channel_delete(channel):
    """Detecta possível nuke (muitos canais deletados rapidamente)."""
    import time
    agora = time.time()
    gid = channel.guild.id
    if gid not in _canal_tracker:
        _canal_tracker[gid] = {"deletes": 0, "creates": 0, "ts": agora}
    if agora - _canal_tracker[gid]["ts"] > 30:
        _canal_tracker[gid] = {"deletes": 0, "creates": 0, "ts": agora}
    _canal_tracker[gid]["deletes"] += 1

    if _canal_tracker[gid]["deletes"] >= 3:
        _canal_tracker[gid]["deletes"] = 0
        embed = discord.Embed(
            title="🚨 POSSÍVEL NUKE DETECTADO",
            description=f"**3+ canais** foram deletados em menos de 30 segundos!",
            color=0xFF0000
        )
        embed.add_field(name="Último canal deletado", value=f"#{channel.name}", inline=False)
        embed.add_field(name="Ação urgente", value="Verifique os logs de auditoria e use `!altban @pessoa` imediatamente.", inline=False)
        await alertar_mods(channel.guild, embed)

@bot.event
async def on_guild_channel_create(channel):
    """Detecta criação em massa de canais (sinal de nuke/raid)."""
    import time
    agora = time.time()
    gid = channel.guild.id
    if gid not in _canal_tracker:
        _canal_tracker[gid] = {"deletes": 0, "creates": 0, "ts": agora}
    if agora - _canal_tracker[gid]["ts"] > 30:
        _canal_tracker[gid] = {"deletes": 0, "creates": 0, "ts": agora}
    _canal_tracker[gid]["creates"] += 1

    if _canal_tracker[gid]["creates"] >= 5:
        _canal_tracker[gid]["creates"] = 0
        embed = discord.Embed(
            title="🚨 CRIAÇÃO EM MASSA DE CANAIS",
            description=f"**5+ canais** foram criados em menos de 30 segundos!",
            color=0xFF0000
        )
        embed.add_field(name="Ação urgente", value="Verifique os logs de auditoria e revogue permissões suspeitas.", inline=False)
        await alertar_mods(channel.guild, embed)

@bot.event
async def on_command(ctx):
    """Detecta spam de comandos do bot."""
    import time
    if is_staff(ctx.author):
        return
    agora = time.time()
    uid = ctx.author.id
    if uid not in _spam_tracker:
        _spam_tracker[uid] = {"cmds": [], "warns": 0}
    _spam_tracker[uid]["cmds"].append(agora)
    _spam_tracker[uid]["cmds"] = [t for t in _spam_tracker[uid]["cmds"] if agora - t < 10]

    # 8+ comandos em 10 segundos
    if len(_spam_tracker[uid]["cmds"]) >= 8:
        _spam_tracker[uid]["cmds"] = []
        _spam_tracker[uid]["warns"] = _spam_tracker[uid].get("warns", 0) + 1
        warns = _spam_tracker[uid]["warns"]
        if warns >= 3:
            await banir_membro(ctx.author, f"Spam de comandos repetido ({warns}x detectado automaticamente)")
        else:
            aplicou = await aplicar_timeout(ctx.author, 15, "Spam de comandos detectado")
            embed = discord.Embed(
                title="⚠️ SPAM DE COMANDOS",
                description=f"{ctx.author.mention} usou 8+ comandos em 10 segundos. (Aviso {warns}/3)",
                color=0xFF8800
            )
            embed.add_field(name="Ação tomada", value="Timeout de **15 minutos**" if aplicou else "Timeout não aplicado", inline=False)
            embed.add_field(name="Avisos acumulados", value=f"**{warns}/3** — no 3º, ban automático.", inline=False)
            await alertar_mods(ctx.guild, embed)

# ── COMANDOS DE MODERAÇÃO ─────────────────────────────────────

@bot.command(name="altban")
async def altban(ctx, membro: discord.Member, *, motivo: str = "Comportamento suspeito / Alt-ban"):
    if not is_staff(ctx.author):
        await ctx.send("❌ Você não tem permissão!")
        return
    if is_staff(membro):
        await ctx.send("❌ Não é possível banir um membro da staff!")
        return
    dias_conta = (discord.utils.utcnow() - membro.created_at).days
    sucesso = await banir_membro(membro, motivo, ctx.author)
    if sucesso:
        await ctx.send(f"🔨 **{membro}** foi banido.\n📋 Motivo: _{motivo}_\n📅 Conta tinha **{dias_conta} dias**.")
    else:
        await ctx.send("❌ Não consegui banir. Verifique se o bot tem permissão de banir membros.")

@bot.command(name="timeout")
async def timeout_cmd(ctx, membro: discord.Member, minutos: int = 10, *, motivo: str = "Timeout aplicado pela moderação"):
    if not is_staff(ctx.author):
        await ctx.send("❌ Você não tem permissão!")
        return
    if is_staff(membro):
        await ctx.send("❌ Não é possível silenciar um membro da staff!")
        return
    sucesso = await aplicar_timeout(membro, minutos, motivo)
    if sucesso:
        await ctx.send(f"🔇 {membro.mention} foi silenciado por **{minutos} minutos**.\n📋 Motivo: _{motivo}_")
        embed = discord.Embed(title="🔇 TIMEOUT APLICADO", color=0xFF8800)
        embed.add_field(name="Usuário", value=f"{membro} (`{membro.id}`)", inline=False)
        embed.add_field(name="Duração", value=f"{minutos} minutos", inline=True)
        embed.add_field(name="Aplicado por", value=str(ctx.author), inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        await alertar_mods(ctx.guild, embed)
    else:
        await ctx.send("❌ Não consegui aplicar o timeout. Verifique as permissões do bot.")

@bot.command(name="removertimeout")
async def removertimeout(ctx, membro: discord.Member):
    if not is_staff(ctx.author):
        await ctx.send("❌ Você não tem permissão!")
        return
    try:
        await membro.timeout(None, reason=f"Timeout removido por {ctx.author}")
        await ctx.send(f"✅ Timeout de {membro.mention} removido.")
    except Exception:
        await ctx.send("❌ Não consegui remover o timeout.")

@bot.command(name="kick")
async def kick(ctx, membro: discord.Member, *, motivo: str = "Expulso pela moderação"):
    if not is_staff(ctx.author):
        await ctx.send("❌ Você não tem permissão!")
        return
    if is_staff(membro):
        await ctx.send("❌ Não é possível expulsar um membro da staff!")
        return
    try:
        await membro.kick(reason=motivo)
        await ctx.send(f"👢 **{membro}** foi expulso.\n📋 Motivo: _{motivo}_")
        embed = discord.Embed(title="👢 MEMBRO EXPULSO", color=0xFF8800)
        embed.add_field(name="Usuário", value=f"{membro} (`{membro.id}`)", inline=False)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        embed.add_field(name="Por", value=str(ctx.author), inline=False)
        await alertar_mods(ctx.guild, embed)
    except Exception:
        await ctx.send("❌ Não consegui expulsar. Verifique as permissões do bot.")

@bot.command(name="lockdown")
async def lockdown(ctx):
    """Bloqueia o envio de mensagens de membros novos no canal do bot durante um raid."""
    if not is_staff(ctx.author):
        await ctx.send("❌ Você não tem permissão!")
        return
    canal_bot = ctx.guild.get_channel(CANAL_BOT)
    if not canal_bot:
        await ctx.send("❌ Canal do bot não encontrado.")
        return
    try:
        everyone = ctx.guild.default_role
        await canal_bot.set_permissions(everyone, send_messages=False)
        await ctx.send(f"🔒 **LOCKDOWN ATIVADO** no {canal_bot.mention}! Membros não podem enviar mensagens.\nUse `!unlockdown` para desbloquear.")
        embed = discord.Embed(title="🔒 LOCKDOWN ATIVADO", description=f"Canal {canal_bot.mention} bloqueado por {ctx.author.mention}.", color=0xFF0000)
        await alertar_mods(ctx.guild, embed)
    except Exception:
        await ctx.send("❌ Não consegui aplicar o lockdown. Verifique as permissões do bot.")

@bot.command(name="unlockdown")
async def unlockdown(ctx):
    if not is_staff(ctx.author):
        await ctx.send("❌ Você não tem permissão!")
        return
    canal_bot = ctx.guild.get_channel(CANAL_BOT)
    if not canal_bot:
        await ctx.send("❌ Canal do bot não encontrado.")
        return
    try:
        everyone = ctx.guild.default_role
        await canal_bot.set_permissions(everyone, send_messages=True)
        await ctx.send(f"🔓 **Lockdown removido!** {canal_bot.mention} voltou ao normal.")
    except Exception:
        await ctx.send("❌ Não consegui remover o lockdown.")

@bot.command(name="modinfo")
async def modinfo(ctx, membro: discord.Member):
    """Mostra informações de moderação sobre um membro."""
    if not is_staff(ctx.author):
        await ctx.send("❌ Você não tem permissão!")
        return
    dias_conta = (discord.utils.utcnow() - membro.created_at).days
    dias_servidor = (discord.utils.utcnow() - membro.joined_at).days if membro.joined_at else "?"
    spam_info = _spam_tracker.get(membro.id, {})
    warns = spam_info.get("warns", 0)
    suspeito = dias_conta < 7 or warns >= 2
    embed = discord.Embed(
        title=f"🔍 Informações de Moderação — {membro}",
        color=0xFF0000 if suspeito else 0x00FF00
    )
    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.add_field(name="ID", value=f"`{membro.id}`", inline=True)
    embed.add_field(name="Conta criada há", value=f"**{dias_conta} dias**", inline=True)
    embed.add_field(name="No servidor há", value=f"**{dias_servidor} dias**", inline=True)
    embed.add_field(name="Avisos de spam", value=f"**{warns}/3**", inline=True)
    embed.add_field(name="Suspeito?", value="⚠️ **SIM**" if suspeito else "✅ Não", inline=True)
    embed.add_field(name="Cargos", value=", ".join(r.name for r in membro.roles[1:]) or "Nenhum", inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)
