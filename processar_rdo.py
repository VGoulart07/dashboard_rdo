import os
import re
import pandas as pd
from collections import defaultdict
from docx import Document  # para ler arquivos .docx

folder_path = r"C:\Users\vinic\OneDrive - DSolar\Documentos\Performance\RDO"

def ler_docx(filepath):
    doc = Document(filepath)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def parse_rdo(text):
    data_match = re.search(r'\*Data:\*\s*([\d]{2}/[\d]{2}/[\d]{4})', text)
    data = data_match.group(1) if data_match else None

    corretiva_matches = re.findall(r'\*Manutenção Corretiva\*([\s\S]*?)(?=\*\w|\Z)', text)
    preventivas_matches = re.findall(r'\*Manutenção Preventiva\*([\s\S]*?)(?=\*\w|\Z)', text)

    registros = []

    def extrair_registros(bloco, tipo_manut):
        linhas = [linha.strip() for linha in bloco.split('\n') if linha.strip()]
        local = None
        for linha in linhas:
            if linha.startswith('*Local') or linha.startswith('*Local:*'):
                local = linha.split(':',1)[1].strip()
            elif linha.startswith('*Atividade') or linha.startswith('*Atividade:*'):
                atividade = linha.split(':',1)[1].strip()
                equipamento = 'Desconhecido'
                if any(x in atividade.lower() for x in ['tracker', 'tcu']):
                    equipamento = 'Tracker'
                elif any(x in atividade.lower() for x in ['inversor', 'ventilador', 'proteção', 'fan']):
                    equipamento = 'Inversor'
                elif any(x in atividade.lower() for x in ['combiner']):
                    equipamento = 'Combiner Box'
                elif any(x in atividade.lower() for x in ['string', 'mc4', 'cabo']):
                    equipamento = 'PV String'
                elif any(x in atividade.lower() for x in ['módulo', 'module']):
                    equipamento = 'Módulo Fotovoltaico'

                registros.append({
                    'Data': data,
                    'Tipo Manutenção': tipo_manut,
                    'Local': local if local else 'Não informado',
                    'Atividade': atividade,
                    'Equipamento': equipamento,
                    'Falha': atividade,
                    'Tempo Parada (min)': None,
                    'Status': 'Desconhecido'
                })

    for bloco in corretiva_matches:
        extrair_registros(bloco, 'Corretiva')
    for bloco in preventivas_matches:
        extrair_registros(bloco, 'Preventiva')

    return registros

all_registros = []

for filename in os.listdir(folder_path):
    if filename.lower().endswith('.docx'):
        filepath = os.path.join(folder_path, filename)
        text = ler_docx(filepath)
        registros = parse_rdo(text)
        all_registros.extend(registros)

print(f"Total de registros extraídos: {len(all_registros)}")

if len(all_registros) == 0:
    print("Nenhum registro extraído. Verifique o formato dos arquivos.")
else:
    df_detalhado = pd.DataFrame(all_registros)
    print("Colunas do DataFrame detalhado:", df_detalhado.columns.tolist())

    if 'Falha' not in df_detalhado.columns:
        print("Coluna 'Falha' não encontrada no DataFrame.")
    else:
        contagem = defaultdict(int)
        for falha in df_detalhado['Falha']:
            contagem[falha] += 1

        df_contagem = pd.DataFrame({
            'Tipo Falha': list(contagem.keys()),
            'Ocorrências': list(contagem.values()),
            'Tempo total estimado (min)': None,
            'Recorrente (Sim/Não)': ['Sim' if v > 1 else 'Não' for v in contagem.values()]
        })

        df_detalhado.to_csv(os.path.join(folder_path, 'rdo_detalhado.csv'), index=False)
        df_contagem.to_csv(os.path.join(folder_path, 'rdo_contagem.csv'), index=False)

        print(f"Arquivos CSV gerados na pasta: {folder_path}")
