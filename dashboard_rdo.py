import pandas as pd
import streamlit as st
import datetime

def carregar_dados(caminho_rdo, caminho_contagem):
    # Lê os CSVs
    df_rdo = pd.read_csv(caminho_rdo, parse_dates=['Data'], dayfirst=True, encoding='utf-8')
    df_contagem = pd.read_csv(caminho_contagem, encoding='utf-8')
    df_rdo.rename(columns=lambda x: x.strip(), inplace=True)
    df_contagem.rename(columns=lambda x: x.strip(), inplace=True)
    
    # Remove componente horário: converte coluna Data para datetime.date (apenas data)
    df_rdo['Data'] = df_rdo['Data'].dt.date
    
    # Se existir a coluna 'Manutenção Corretiva', tenta separar Local e Atividade
    if 'Manutenção Corretiva' in df_rdo.columns:
        # Divide a coluna em duas partes na primeira quebra de linha
        split_col = df_rdo['Manutenção Corretiva'].str.split('\n', n=1, expand=True)
        df_rdo['Local'] = split_col[0].fillna("")
        df_rdo['Atividade'] = split_col[1].fillna("")
    else:
        df_rdo['Local'] = ""
        df_rdo['Atividade'] = ""
    
    return df_rdo, df_contagem

def main():
    st.title("Dashboard RDO - Usina Solar UFV Coromandel")
    
    caminho_rdo = r"C:\Users\vinic\OneDrive - DSolar\Documentos\Performance\RDO\rdo_extraido.csv"
    caminho_contagem = r"C:\Users\vinic\OneDrive - DSolar\Documentos\Performance\RDO\contagem_falhas.csv"
    
    df_rdo, df_contagem = carregar_dados(caminho_rdo, caminho_contagem)

    # Seleção de intervalo ou data única com garantia de datetime.date
    data_selecionada = st.date_input(
        "Selecione o período para análise",
        value=(datetime.date(2025, 7, 1), datetime.date(2025, 7, 14)),
        help="Selecione uma única data ou um intervalo de datas."
    )

    if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
        inicio, fim = data_selecionada
    else:
        inicio = fim = data_selecionada

    # Como df_rdo['Data'] e inicio/fim são datetime.date, filtro direto
    df_filtrado = df_rdo[(df_rdo['Data'] >= inicio) & (df_rdo['Data'] <= fim)]

    st.subheader("RDO filtrado pelo período")
    st.dataframe(df_filtrado[['Data', 'Equipe', 'Local', 'Atividade']])

    st.subheader("Contagem de Falhas por Tipo")
    if 'Descrição' in df_contagem.columns and 'Quantidade' in df_contagem.columns:
        df_contagem = df_contagem.dropna(subset=['Descrição', 'Quantidade'])
        df_contagem['Quantidade'] = pd.to_numeric(df_contagem['Quantidade'], errors='coerce').fillna(0)
        falhas_agrupadas = df_contagem.groupby('Descrição')['Quantidade'].sum().sort_values(ascending=False)
        st.bar_chart(falhas_agrupadas)
    else:
        st.warning("Colunas 'Descrição' e 'Quantidade' não encontradas no arquivo de contagem de falhas.")

if __name__ == "__main__":
    main()
