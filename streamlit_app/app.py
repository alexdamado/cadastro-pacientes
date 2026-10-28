import csv
from datetime import datetime
from io import StringIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

COLUNAS = ['timestamp', 'nome', 'idade', 'convenio', 'prioridade', 'motivo']
CONVENIOS = ['Particular', 'Unimed', 'Bradesco Saúde', 'SulAmérica', 'Outro']
ARQUIVO_CSV = Path(__file__).with_name('pacientes.csv')

st.set_page_config(page_title='Cadastro de Pacientes', page_icon='🏥', layout='centered')
st.title('🏥 Cadastro de Pacientes')
st.caption('Registro de atendimento — utilize somente dados fictícios.')

if 'pacientes' not in st.session_state:
    st.session_state.pacientes = pd.DataFrame(columns=COLUNAS)

with st.form('cadastro', clear_on_submit=True):
    nome = st.text_input('Nome do paciente')
    idade = st.number_input('Idade', min_value=0, max_value=120, value=30, step=1)
    convenio = st.selectbox('Convênio', CONVENIOS)
    prioridade = st.slider('Prioridade do atendimento (5 = urgente)', 1, 5, 3)
    motivo = st.text_area('Motivo da consulta / observações')
    enviado = st.form_submit_button('Cadastrar', type='primary')

if enviado:
    if not nome.strip():
        st.error('Informe o nome do paciente.')
    else:
        linha = {
            'timestamp': datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S'),
            'nome': nome.strip(), 'idade': int(idade), 'convenio': convenio,
            'prioridade': int(prioridade), 'motivo': motivo.strip(),
        }
        st.session_state.pacientes = pd.concat(
            [st.session_state.pacientes, pd.DataFrame([linha])], ignore_index=True
        )
        # Arquivo temporário do servidor; a fonte de verdade da sessão é session_state.
        try:
            novo = not ARQUIVO_CSV.exists() or ARQUIVO_CSV.stat().st_size == 0
            with ARQUIVO_CSV.open('a', newline='', encoding='utf-8-sig' if novo else 'utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=COLUNAS)
                if novo:
                    writer.writeheader()
                writer.writerow(linha)
        except OSError:
            st.warning('Registro salvo na sessão, mas não foi possível atualizar o CSV temporário.')
        st.success(f'Paciente {nome.strip()} cadastrado com sucesso!')

st.subheader('Últimos 5 pacientes cadastrados')
st.dataframe(st.session_state.pacientes.tail(5), use_container_width=True, hide_index=True)
csv_bytes = st.session_state.pacientes.to_csv(index=False).encode('utf-8-sig')
st.download_button('📥 Baixar CSV', data=csv_bytes, file_name='pacientes.csv', mime='text/csv')
st.caption('Os registros da sessão podem ser perdidos ao reiniciar o aplicativo. Baixe o CSV para guardá-los.')
