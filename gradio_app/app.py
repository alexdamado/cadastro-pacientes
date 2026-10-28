import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import gradio as gr
import pandas as pd

ARQUIVO_CSV = Path(__file__).with_name('pacientes.csv')
COLUNAS = ['timestamp', 'nome', 'idade', 'convenio', 'prioridade', 'motivo']
CONVENIOS = ['Particular', 'Unimed', 'Bradesco Saúde', 'SulAmérica', 'Outro']


def ultimos():
    if not ARQUIVO_CSV.exists():
        return pd.DataFrame(columns=COLUNAS)
    return pd.read_csv(ARQUIVO_CSV, encoding='utf-8-sig').tail(5)


def cadastrar_paciente(nome, idade, convenio, prioridade, motivo):
    nome = (nome or '').strip()
    if not nome:
        return '⚠️ Informe o nome do paciente.', ultimos()
    if idade is None or not float(idade).is_integer() or not 0 <= idade <= 120:
        return '⚠️ Informe uma idade inteira entre 0 e 120.', ultimos()
    if convenio not in CONVENIOS:
        return '⚠️ Selecione um convênio.', ultimos()
    linha = {
        'timestamp': datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S'),
        'nome': nome,
        'idade': int(idade),
        'convenio': convenio,
        'prioridade': int(prioridade),
        'motivo': (motivo or '').strip(),
    }
    novo_arquivo = not ARQUIVO_CSV.exists() or ARQUIVO_CSV.stat().st_size == 0
    with ARQUIVO_CSV.open('a', encoding='utf-8-sig' if novo_arquivo else 'utf-8', newline='') as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        if novo_arquivo:
            escritor.writeheader()
        escritor.writerow(linha)
    return f'✅ Paciente {nome} cadastrado com sucesso!', ultimos()


with gr.Blocks(title='Cadastro de Pacientes') as demo:
    gr.Markdown('# 🏥 Cadastro de Pacientes\nRegistro de atendimento — dados fictícios para atividade acadêmica.')
    nome = gr.Textbox(label='Nome do paciente', placeholder='Nome completo')
    idade = gr.Number(label='Idade', precision=0, minimum=0, maximum=120, value=30)
    convenio = gr.Dropdown(CONVENIOS, label='Convênio', value='Particular')
    prioridade = gr.Slider(1, 5, step=1, value=3, label='Prioridade do atendimento (5 = urgente)')
    motivo = gr.Textbox(label='Motivo da consulta / observações', lines=3)
    botao = gr.Button('Cadastrar', variant='primary')
    saida_msg = gr.Textbox(label='Status', interactive=False)
    tabela = gr.Dataframe(value=ultimos(), label='Últimos 5 pacientes cadastrados', interactive=False)
    botao.click(cadastrar_paciente, inputs=[nome, idade, convenio, prioridade, motivo], outputs=[saida_msg, tabela])

if __name__ == '__main__':
    demo.launch()
