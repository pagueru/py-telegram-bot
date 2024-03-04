#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Fornecem funcionalidas para interagir com a API do Telegram e o desenvolvimento de bots

from telegram import (ForceReply,Update, InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)

from telebot.types import BotCommand, BotCommandScope

from telegram.ext import (Application, ContextTypes, CommandHandler, MessageHandler,
                          ConversationHandler,filters, CallbackContext, PicklePersistence,
                          CallbackContext, CallbackQueryHandler, JobQueue)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Fornece funcionalidades para a medição e maniputalação tempo em formato timestamp
import time

# Fornece funcionalidades para a medição e maniputalação de datas
from datetime import date, time, datetime, timedelta

# Fornece funcionalidades para a edição de cores e estilos de texto
from colorama import init, Fore, Style

# Fornece funcionalidades para o agendamento e automatização de tarefas
import schedule

# Permite funcionalidades para o interpretador
import sys

# Possibilita a anotação de tipos indicando que uma variável, argumento ou valor de retorno deve ser uma lista.
from typing import List, Any

# Permite funcionalidades para interações com o sistema
import os

# Permite funcionalidades relacionadas ao tratamento de sinais, como o SIGINT Ctrl+C) --> Encerra o programa
import signal

import threading

import math

from tabulate import tabulate as tb

from flask import Flask, request

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Carrega as variáveis encontradas no arquivo .env como variáveis de ambiente 
from os import getenv
from dotenv import load_dotenv

caminho_dotenv = os.path.join(os.path.dirname(__file__), 'tokens.env') # Caminho completo do arquivo 'tokens.env' no diretório
load_dotenv(caminho_dotenv) # Execução do carregamento

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Define a localização para formatação de datas e horas como sendo o padrão brasileiro 
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR')

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Definição do bot token para o funcionamento do TeleBot
from telebot import telebot, types

bot_token = getenv('BOT_TOKEN')
bot = telebot.TeleBot(bot_token, parse_mode=None)

# Atribui o restantes das variáveis necessárias para o bot do Telegram
api_id = getenv('API_ID')
api_hash = getenv('API_HASH')

raphael_id = getenv('RAPHAEL_CHAT_ID')
carol_id = getenv('CAROL_CHAT_ID')

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Habilita o logging para retorno de mensagens de erro e informações no terminal
import logging

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO) # Configurar o logger
logger = logging.getLogger(__name__) # Criar um objeto logger
telebot.logger.setLevel(logging.INFO) # Configurar o nível de log para o logger do telebot

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Timestamp no formato de logging com formato de: ano-mês-dia hora:min:seg:ms --> 2024-01-01 12:00:00,00
def obter_timestamp():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3] # Com 3 casas após a vírgula
    return timestamp

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Habilita o Pandas e fornece a manipulação do arquivo Excel em um DataFrame
import pandas as pd

# Atribuição do caminho do arquivo através do arquivo .env
caminho_arquivo = getenv(r'CAMINHO_ARQUIVO')

# Atribuição do DataFrame
dataframe_principal = pd.read_excel(caminho_arquivo)  

# Atribuição da lista de colunas do DataFrame:
lista_colunas = dataframe_principal.columns.tolist()

# Atribuição da lista de medicamentos disponíveis
lista_medicamentos = dataframe_principal['MEDICAMENTOS'].str.capitalize().tolist()

# Adiciona um índice númerico a lista_medicamento
lista_medicamentos_enumerada = [f'{i + 1}. {medicamento}' for i, medicamento in enumerate(lista_medicamentos)]

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Formatação do DataFrame com bordas redondas
def formatar_dataframe(dataframe):
    print(tb(dataframe, headers='keys', tablefmt='rounded_grid'))

# Processa um DataFrame para gerar o campo DATA_FIM
def calcular_data_fim(dataframe, data_inicial, estoque_inicial: int, uso_em_dupla: int):

    estoque_inicial = float(estoque_inicial)
    data_inicial = pd.to_datetime(data_inicial)

    if uso_em_dupla == 1:
        data_fim = data_inicial + timedelta(days=math.floor(estoque_inicial))
    else:
        data_fim = data_inicial + timedelta(days=estoque_inicial/2)

    data_fim = datetime.strftime(data_fim, '%Y-%m-%d')

    return data_fim

# Processa um DataFrame para gerar o campo DIAS_FALTANTES
def calcular_dias_faltantes(data_fim):
    
    data_fim = pd.to_datetime(data_fim)

    dias_faltantes = (data_fim - datetime.now()).days
    return dias_faltantes

# Adiciona uma coluna a um DataFrame
def adicionar_coluna(dataframe, nome_coluna, valor, indice_linha):
    dataframe.at[indice_linha, nome_coluna] = valor

# Processa o DataFrame com base nos cálculos dos campos
def processar_dataframe(dataframe):
    try:
        for indice, linha in dataframe.iterrows():
            if not pd.isnull(linha['MEDICAMENTOS']):
                uso_em_dupla = int(linha['USO_EM_DUPLA'])
                estoque_inicial = int(linha['ESTOQUE_INICIAL'])
                data_inicial = pd.to_datetime(linha['DATA_INICIAL'])

                # Calcula e carrega o campo no DataFrame - Data Fim = Data Inicial + Estoque Inicial
                data_fim = calcular_data_fim(dataframe, data_inicial, estoque_inicial, uso_em_dupla)

                # Calcula e carrega o campo no DataFrame -  Dias Faltantes = Data do Fim - Data de Hoje
                dias_faltantes = calcular_dias_faltantes(data_fim)

                dataframe.at[indice, 'DATA_FIM'] = data_fim
                dataframe.at[indice, 'DIAS_FALTANTES'] = dias_faltantes

        dataframe.to_excel(caminho_arquivo, index=False)  # Salva a atualização do DataFrame
        logger.info(f'DataFrame processado com sucesso!')

    except Exception as e:
        logger.info(f'Erro ao processar o DataFrame – {e}')

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    
# Definição dos comandos do bot e suas descrições, além da adição em formato de lista
definicao_comandos = [
    telebot.types.BotCommand('/start', 'Mensagem de início do bot'),
    telebot.types.BotCommand('/help', 'Retornar a lista de comandos'),
    telebot.types.BotCommand('/info', 'Informações sobre o usuário'),
    telebot.types.BotCommand('/consultar', 'Consultar medicamento na lista'),
    telebot.types.BotCommand('/lista', 'Retornar uma lista com o nome dos medicamentos'),
    telebot.types.BotCommand('/sair', 'Finalizar o bot'),
    telebot.types.BotCommand('/atualizar', 'Atualiza o DataFrame manualmente'),
    telebot.types.BotCommand('/adicionar', 'Adicionar um novo medicamento na lista'),
]

bot.set_my_commands(definicao_comandos) # Define o comandos

# Atribui a lista de comandos
for comando in definicao_comandos:
    lista_comandos = []
    lista_comandos.append(comando.command) 

# Atribui o botão clicável abaixo da mensagem do bot
chamar_teclado = types.InlineKeyboardMarkup()

# Atribui os botões clicáveis para Sim e Não
botao_sim = types.InlineKeyboardButton(text="Sim", callback_data="sim")
botao_nao = types.InlineKeyboardButton(text="Não", callback_data="nao")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Retorna em formato de lista o conteúdo da coluna definida
def retornar_colunas_dataframe(coluna):
    try:
        logger.info(f'A coluna "{coluna}" será retornada com sucesso')
        return dataframe_principal[coluna].str.capitalize().tolist() 
         
    except Exception as e:
        logger.info(f'A coluna {coluna} não existe –  {e}')

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Verifica se o medicamento existe na listagem
def pesquisar_medicamento(mensagem_medicamento):
    
    if mensagem_medicamento in dataframe_principal['MEDICAMENTOS']:
        logger.info(f'O medicamento "{mensagem_medicamento}" foi encontrado com sucesso na tabela.')
        indice_medicamento = dataframe_principal.index[dataframe_principal['MEDICAMENTOS'].str.capitalize() == mensagem_medicamento.capitalize()].tolist()
        return indice_medicamento 
    else:
        logger.info(f'O medicamento "{mensagem_medicamento}" escolhido pelo usuário não existe na tabela.')
        mensagem_desconhecida()

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

#### Definição de Handlers para o Bot ####   
 
    
#----------------------------------------------------------------------------------------------------------------------------------------------------------------#
       
       
# Definiçao do comando /start
@bot.message_handler(commands=['start'])
def comando_start(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} selecionou o comando /start')
    bot.send_message(message.chat.id, f'Olá {message.from_user.first_name}!')
    bot.send_message(message.chat.id, f'Use /help para ver a lista de comandos disponíveis.')
    return ConversationHandler.END

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Definição do comando /info
@bot.message_handler(commands=['info'])
def comando_info(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} selecionou o comando /info')
    bot.send_message(message.chat.id, f'Segue seus dados do Telegram:')
    bot.send_message(message.chat.id, f'ID: {message.from_user.id}\n'
                                      f'Nome: {message.from_user.first_name}\n'
                                      f'Sobrenome: {message.from_user.last_name}\n'
                                      f'Username: @{message.from_user.username}\n'
                                      f'Língua: {message.from_user.language_code}\n')
    return ConversationHandler.END

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Definição do comando /help
@bot.message_handler(commands=['help'])
def command_help(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} selecionou o comando /start')
    bot.send_message(message.chat.id, '/start - Inicia o bot\n'
                                      '/info - Exibe os seus dados do Telegram\n'
                                      '/help - Exibe a lista de comandos\n'
                                      '/consultar - Consulta um medicamento\n'
                                      '/adicionar - Adiciona um novo medicamento\n'
                                      '/listar - Lista todos os medicamentos\n'
                                      '/alterar - Modifica um medicamento\n'
                                      '/remover - Remove um medicamento\n'
                                      '/sair - Encerra o bot\n'
                                      '/atualizar - Atualiza o DataFrame manualmente')

    return ConversationHandler.END

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Definição do comando /lista
@bot.message_handler(commands=['lista'])
def comando_lista(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} selecionou o comando /lista')
    lista_medicamentos = [medicamento.capitalize() for medicamento in dataframe_principal['MEDICAMENTOS'].tolist()]
    lista_enumerados = '\n'.join([f'{i + 1}. {medicamento}' for i, medicamento in enumerate(lista_medicamentos)])  
    bot.send_message(message.chat.id, lista_enumerados)

    return ConversationHandler.END

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Definição do comando /sair
@bot.message_handler(commands=['sair'])
def comando_sair(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} selecionou o comando /sair')
    bot.send_message(message.chat.id, 'Tudo bem! Saindo do comando.')
    bot.stop_polling()
    bot.send_message(message.chat.id, 'Quase lá! Aguarde...')
    return ConversationHandler.END

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Definição do comando /consultar
@bot.message_handler(commands=['consultar'])
def comando_consultar(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} selecionou o comando /consultar')
    mensagem_consulta = bot.send_message(message.chat.id, 'Digite o nome do medicamento')
    bot.register_next_step_handler(mensagem_consulta, responder_consulta)

# Execução da consulta após receber o nome do medicamento
def responder_consulta(message: types.Message):

    # Obtém o texto da mensagem enviada pelo usuário
    mensagem_consulta = message.text

    # Retorna a pesquisa do medicamento
    indice_linha = pesquisar_medicamento(mensagem_consulta)
    
    if indice_linha == []:
        print(f'Erro encontrado na pesquisa do medicamento {mensagem_consulta}')
        return ConversationHandler.END
    else:
        # Calcula e retorna os campos/
        dias_faltantes = int(dataframe_principal.at[indice_linha[0], 'DIAS_FALTANTES'])
        dt_fim = dataframe_principal.at[indice_linha[0], 'DT_FIM']       

        # Envia a resposta da função de volta ao usuário
        logger.info(f'Retornando a consulta do medicamento "{mensagem_consulta}" para o usuário @{message.from_user.username}')
        bot.send_message(message.chat.id, f'Faltam {dias_faltantes} dias para o medicamento {mensagem_consulta} acabar (previsto para {dt_fim})')

        return ConversationHandler.END

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Definição do comando /atualizar
@bot.message_handler(commands=['atualizar'])
def comando_consultar(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} selecionou o comando /atualizar')
    processar_dataframe(dataframe_principal)
    bot.send_message(message.chat.id, 'O DataFrame foi atualizado manualmente com sucesso!')

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Cria um DataFrame com as colunas do arquivo original
novo_medicamento = pd.DataFrame(columns=lista_colunas)

# Definição do comando /adicionar
@bot.message_handler(commands=['adicionar'])
def comando_adicionar(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} selecionou o comando /adicionar')
    bot.send_message(message.chat.id, 'Digite o nome do medicamento:')
    bot.register_next_step_handler(message, receber_nome)

# Recebe e adiciona o nome do novo medicamento
def receber_nome(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} digitou o nome "{message.text}" para o novo medicamento')

    adicionar_coluna(novo_medicamento, 'MEDICAMENTOS', message.text, 0)

    # Pergunta pelo número de unidades
    bot.send_message(message.chat.id, f'O nome do medicamento será {novo_medicamento.at[0, "MEDICAMENTOS"]}. Agora digite o número de unidades:')
    bot.register_next_step_handler(message, receber_unidades)


def receber_unidades(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} digitou "{message.text}" para as unidades do novo medicamento')

    adicionar_coluna(novo_medicamento, 'UNIDADES', message.text, 0)

    # Pergunta pelo estoque inicial
    bot.send_message(message.chat.id, f'O medicamento terá {novo_medicamento.at[0, "UNIDADES"]} unidades. Agora digite o número de estoque inicial:')
    bot.register_next_step_handler(message, receber_estoque)


def receber_estoque(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} digitou "{message.text}" para o estoque inicial do novo medicamento')

    adicionar_coluna(novo_medicamento, 'ESTOQUE_INICIAL', message.text, 0)

    # Pergunta se é para uso em dupla com uma InlineKeyboardMarkup
    #botao_sim = types.InlineKeyboardButton("Sim", callback_data=1)
    #botao_nao = types.InlineKeyboardButton("Não", callback_data=0)
    #chamar_teclado.add(botao_sim, botao_nao)

    bot.send_message(message.chat.id, f'O medicamento {novo_medicamento.at[0, "UNIDADES"]} será de uso em dupla?')#, reply_markup=chamar_teclado)
    bot.register_next_step_handler(message, receber_uso_em_dupla)

def receber_uso_em_dupla(message: types.Message):
    logger.info(f'O usuário @{message.from_user.username} digitou "{message.text}" para o uso em dupla do novo medicamento')

    global dataframe_principal

    uso_em_dupla = message.text.capitalize()

    if uso_em_dupla == 'Sim':
        uso_em_dupla = adicionar_coluna(novo_medicamento, 'USO_EM_DUPLA', 1, 0)

    elif uso_em_dupla in ['Nao','Não']:
        uso_em_dupla = adicionar_coluna(novo_medicamento, 'USO_EM_DUPLA', 0, 0)
    
    data_inicial = datetime.now().strftime('%Y-%m-%d')
    adicionar_coluna(novo_medicamento, 'DATA_INICIAL', data_inicial, 0) 

    adicionar_coluna(novo_medicamento, 'DATA_FIM', calcular_data_fim(novo_medicamento,
                                                    novo_medicamento.at[0, 'DATA_INICIAL'],
                                                    int(novo_medicamento.at[0, 'ESTOQUE_INICIAL']),
                                                    novo_medicamento.at[0, 'USO_EM_DUPLA']),0)

    adicionar_coluna(novo_medicamento,'DIAS_FALTANTES', calcular_dias_faltantes(novo_medicamento.at[0, 'DATA_FIM']), 0)

    # Retorno do DataFrame no terminal
    logger.info(f'O usuário @{message.from_user.username} finalizou a criação da DataFrame:')
    formatar_dataframe(novo_medicamento)

    bot.send_message(message.chat.id, f'Ok! Vamos continuar e atualizar os dados.')

    # Adiciona os novos dados ao DataFrame existente
    dataframe_principal = pd.concat([dataframe_principal, novo_medicamento], ignore_index=True)

    # Salva o DataFrame no arquivo Excel
    dataframe_principal.to_excel(caminho_arquivo, index=False)
    processar_dataframe(dataframe_principal)
    bot.send_message(message.chat.id, 'Medicamento adicionado a lista com sucesso!')
    dataframe_principal = dataframe_principal.truncate(before=0, after=-1)
    pass



#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

@bot.message_handler(commands=['reiniciar'])
def restart(message):
    bot.send_message(message.chat.id, 'O bot está sendo reiniciado...')
    bot.stop_polling()

    # Substitua 'C:/caminho/completo/para/main.py' pelo caminho completo para o seu main.py
    caminho_main = r'C:\Lillith\Projetos\Python\LilithProjectsRepository\personal-telegram-bot\main.py'

    # Obtém o diretório do main.py
    main_py_directory = os.path.dirname(caminho_main)

    # Altera o diretório de trabalho para o diretório do main.py
    os.chdir(main_py_directory)

    os.exit()

    # Reinicia o bot chamando main.py
    os.system('python main.py')








# Definição de um tratador para mensagem fora das definições
@bot.message_handler(func=lambda message: True)
def mensagem_desconhecida(message: types.Message):
    if message.text in lista_comandos:
        pass
    elif message.text.startswith('/'):
        logger.info(f'O usuário @{message.from_user.username} enviou um comando desconhecido: {message.text}')
        bot.send_message(message.chat.id, 'Desculpe, não reconheço esse comando. Tente novamente.')
    else:
        logger.info(f'O usuário @{message.from_user.username} enviou uma mensagem desconhecida: {message.text}')
        bot.send_message(message.chat.id, 'Desculpe, não entendi a sua mensagem. Tente novamente com um comando válido.')

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Envia uma mensagem de alerta para medicamentos próximos de acabar
def mensagem_alerta_medicamento(medicamento, dias_faltantes):
    mensagem = f'Atenção! O medicamento {medicamento} está com {dias_faltantes} dias ou menos restantes.'
    bot.send_message(chat_id=raphael_id, text=mensagem)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Verifica se há medicamentos próximo de acabar e envia o alerta
def verificar_medicamentos_proximos_acabar():
    for medicamento,coluna in dataframe_principal.iterrows():
        dias_faltantes = coluna['DIAS_FALTANTES']
        if dias_faltantes is not None and dias_faltantes <= 7:
            mensagem_alerta_medicamento(medicamento, dias_faltantes)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Tarefas agendadas
schedule.every().day.at('00:00').do(processar_dataframe) # Atualizar a tabela
schedule.every().day.at('00:00').do(verificar_medicamentos_proximos_acabar) # Verifica medicamentos próximos de acabar

#----------------------------------------------------------------------------------------------------------------------------------------------------------------#
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Executar o bot
def executar_telebot():
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        logger.error(f'Erro durante a execução do bot: {e}')

# Executa tarefas agendadas
def executar_tarefas():
    while True:
        try:
            schedule.run_pending()
            #time.sleep(5)  # Tempo que o bot vai rodar o schedule
            #logger.info('Passou-se 1 hora e o schedule foi executado.')
        except Exception as e:
            logger.error(f'Erro durante a execução do bot: {e}')
    
#----------------------------------------------------------------------------------------------------------------------------------------------------------------#
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
#----------------------------------------------------------------------------------------------------------------------------------------------------------------#
            
# Executar o script
if __name__ == '__main__':
    try:
        # Atualiza o DataFrame
        processar_dataframe(dataframe_principal)

        # Cria e inicia as threads para executar o bot e o schedule simultaneamente
        threading.Thread(target=executar_telebot).start()
        threading.Thread(target=executar_tarefas).start()

    except Exception as e:
        logger.error(f'Erro durante a execução do bot: {e}')