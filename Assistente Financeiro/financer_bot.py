import asyncio
from pandas.io.formats.format import return_docstring
from telegram import Update
import json
import os
from telegram import ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application, MessageHandler, filters

def salvar_dados():
    with open("dados_financeiros.json", "w") as arquivo:
        json.dump(financas, arquivo, indent=4)
    print("Dados salvos com sucesso!")
def carregar_dados():
    if os.path.exists("dados_financeiros.json"):
        with open("dados_financeiros.json", "r") as arquivo:
            return json.load(arquivo)
    return {"Ganhos": [], "Gastos": []}
def registrar_no_sistema(tipo, valor, descricao, categoria):
    novo_item = {
        "descricao": descricao,
        "valor": valor,
        "categoria": categoria,
    }
    if valor > 0:
        if tipo == 'ganho':
            financas["Ganhos"].append(novo_item)
        else:
            financas["Gastos"].append(novo_item)

        salvar_dados()
        return True
    return False
def calcular_saldo():
    ganhos_totais = 0
    for ganho in financas["Ganhos"]:
        ganhos_totais += ganho["valor"]

    gastos_totais = 0
    for gasto in financas["Gastos"]:
        gastos_totais += gasto["valor"]
    return   ganhos_totais-gastos_totais
def limpar_dados():
    financas["Ganhos"] = []
    financas["Gastos"] = []
    salvar_dados()
def resumo_mensal():
    tot_ganhos = sum(g["valor"] for g in financas["Ganhos"])
    tot_gastos = sum(g["valor"] for g in financas["Gastos"])
    categorias_soma = {}
    for g in financas["Gastos"]:
        cat = g["categoria"]
        valor = g["valor"]
        categorias_soma[cat] = categorias_soma.get(cat, 0) + g["valor"]
    saldo = tot_ganhos - tot_gastos
    return tot_ganhos, tot_gastos, saldo, categorias_soma

financas = carregar_dados()

teclado = [["💰 Adicionar Ganho"],["💸 Adicionar Gasto"],["💲 Ver Saldo"],["🗑 Limpar Dados"],["📊 Resumo Mensal"]] #cria o teclado
teclado_markup = ReplyKeyboardMarkup(
    teclado,
    resize_keyboard=True)
async def start(update, context):
    await update.message.reply_text('Olá, seja bem vindo!',reply_markup=teclado_markup) #espera um pouco e responde com o texto escolhido
async def processar_mensagem(update, context):
    opcao = update.message.text
    if opcao == "💰 Adicionar Ganho":
        context.user_data['escolha'] = 'ganho'
        await update.message.reply_text("Envie o ganho no formato: valor, descrição, categoria (ex: 2000, Salário, Trabalho)")
    elif opcao == "💸 Adicionar Gasto":
        context.user_data['escolha'] = 'gasto'
        await update.message.reply_text("Envie o gasto no formato: valor, descrição, categoria (ex: 250, Mercado, Alimentos)")
    elif "," in opcao:
        tipo = context.user_data.get('escolha')
        if tipo:
            dados = opcao.split(",")
            if len(dados) == 3:
                # Preparando os dados
                v = float(dados[0].strip())
                d = dados[1].strip().capitalize()
                c = dados[2].strip().capitalize()
                sucesso = registrar_no_sistema(tipo, v, d, c)
                if sucesso:
                    await update.message.reply_text(f"✅ {tipo} de R$ {v:.2f} salvo!")
                else:
                    await update.message.reply_text("❌ Erro: O valor deve ser maior que 0.")
                context.user_data['escolha'] = None
    elif opcao == "💲 Ver Saldo":
        saldo = calcular_saldo()
        await update.message.reply_text(f"Seu saldo atual: R${saldo:.2f}")
    elif opcao == "🗑 Limpar Dados":
        limpar_dados()
        await update.message.reply_text("Dados apagados com sucesso! 🧹")
    elif opcao == "📊 Resumo Mensal":
        gan, gas, s, cats = resumo_mensal()
        msg = (f"Resumo Geral:\nGanhos: {gan:.2f}\n"
               f"Gastos: {gas:.2f}\nSaldo: {s:.2f}\n\n")
        msg += "Gastos por Categoria:\n"
        for categoria, valor in cats.items():
            msg += f"• {categoria}: R$ {valor:.2f}\n"
        await update.message.reply_text(msg)

bot = ApplicationBuilder().token("").build()
bot.add_handler(CommandHandler('start', start))
bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_mensagem))
bot.run_polling()




