import json
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
import asyncio


materias = {
    'Linguagens': ['Interpretação de Texto', 'Gêneros Textuais', 'Figuras de Linguagem', 'Variação Linguística', 'Gramática Aplicada'],
    'Matematica': ['Porcentagem','Regra de três','Gráficos e Tabelas','Estatísticas','Geometria', 'Funções','Raciocínio Lógico'],
    'Biologia':['Ecologia e Ecossistemas','Corpo Humano e Saúde Pública','Genética e Biotecnologia', 'Citologia (Células)'],
    'Quimica':['Misturas e Separação de Materiais','Estados Físicos da Matéria', 'Química Ambiental','Tabela Periódica Básica'],
    'Física':['Eletricidade e Consumo de Energia','Termologia','Cinemática','Leis de Newton'],
    'História':['Brasil Colônia e Império','Era Vargas e Populismo','Ditadura Militar no Brasil', 'Revoluções Industriais'],
    'Sociologia e Filosofia':['Ética e Cidadania','Direitos Humanos','Movimentos Sociais', 'Surgimento da Sociologia'],
    'Geografia':['Meio Ambiente e Sustentabilidade','Globalização e Economia', 'Geografia Urbana e População','Cartografia (Mapas e Fusos)'],
    'Redação': ['Estrutura Dissertativo-Argumentativa','Repertório Sociocultural', 'Proposta de Intervenção','Uso de Conectivos'],
    'Inglês':['Interpretação de Textos','Vocabulário Técnico','Cognatos e Falsos Cognatos']
}
status = {
    'Aprendido': []
}

def salvar_no_arquivo():
    dados_para_salvar = {
        'materias': materias,
        'status': status
    }
    with open('estudos.json', 'w', encoding='utf-8') as file:
        json.dump(dados_para_salvar, file, ensure_ascii=False, indent=4)
    print("Progresso salvo com sucesso no arquivo!")
def carregar_do_arquivo():
    global materias, status
    try:
        with open('estudos.json', 'r', encoding='utf-8') as file:
            dados = json.load(file)
            materias = dados.get('materias', materias)
            status = dados.get('status', status)
            print("✅ Dados carregados do arquivo estudos.json")
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ Arquivo não encontrado ou vazio. Usando dados padrão.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Olá, Sou seu Assistente. Use /materias para ver seu cronograma \n'
                                    '/status para ver seu progresso,\n'
                                    '\concluido (matéria) para marcar a matéria como concluída \n'
                                    '/salvar para salvar o progresso!')
async def comando_salvar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    salvar_no_arquivo()
    await update.message.reply_text("Progresso salvo manualmente!")
async def comando_carregar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    carregar_do_arquivo()
    await update.message.reply_text("Seu progresso foi recarregado do arquivo!")
async def listar_materias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_lista = "📚 **Seu Cronograma:**\n\n"
    for materia, topicos in materias.items():
        texto_lista += f"🔹 *{materia}*:\n"
        for topico in topicos:
            check = "✅" if topico in status['Aprendido'] else "⚪"
            texto_lista += f"  {check} {topico}\n"
        texto_lista += "\n"
    await update.message.reply_text(texto_lista, parse_mode='Markdown')
async def concluir_materia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    materia_nome = " ".join(context.args)
    if not materia_nome:
        await update.message.reply_text("Diga qual matéria concluiu. Ex: /concluido matematica")
        return

    encontrada = False
    for categoria, lista in materias.items():
        if materia_nome in lista:
            encontrada = True
            if materia_nome not in status['Aprendido']:
                status['Aprendido'].append(materia_nome)
                salvar_no_arquivo()
                await update.message.reply_text(f"Parabéns '{materia_nome}' concluída!")
            else:
                await update.message.reply_text("Você já estudou essa!")
            break

    if not encontrada:
        await update.message.reply_text("Não achei essa matéria. Verifique se escreveu igual ao /materias.")
async def ver_progresso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_progresso = "📊 **Seu Progresso por Disciplina:**\n\n"

    for categoria, lista_topicos in materias.items():
        total = len(lista_topicos)
        concluidos = len([t for t in lista_topicos if t in status['Aprendido']])
        porcentagem = (concluidos / total) * 100 if total > 0 else 0
        barra = "🟩" * concluidos + "⬜" * (total - concluidos)
        texto_progresso += f"*{categoria}*: {porcentagem:.0f}%\n{barra}\n\n"
    await update.message.reply_text(texto_progresso, parse_mode='Markdown')
carregar_do_arquivo()

TOKEN = ""
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('salvar', comando_salvar))
app.add_handler(CommandHandler('concluido', concluir_materia))
app.add_handler(CommandHandler('materias', listar_materias))
app.add_handler(CommandHandler('status', ver_progresso))
app.run_polling()