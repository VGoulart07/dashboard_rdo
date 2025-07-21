import pandas as pd
import streamlit as st
import datetime
import re

def carregar_dados():
    df_rdo = pd.read_csv("rdo_completo.csv", encoding='utf-8')
    df_rdo['Data'] = pd.to_datetime(df_rdo['Data'], errors='coerce').dt.date
    return df_rdo

def limpar_dois_pontos_inicio(texto):
    if texto is None:
        return ""
    texto = texto.strip()
    # Remove todos os ":" do início (ex: ":::", "::", ":")
    while texto.startswith(":"):
        texto = texto[1:].strip()
    return texto

def formatar_local_atividade(texto):
    if pd.isna(texto) or texto.strip() == "":
        return ""

    texto = texto.strip()
    padrao = re.compile(r'(Local:.*?)(Atividade:.*?)(?=Local:|$)', re.DOTALL | re.IGNORECASE)
    partes = padrao.findall(texto)

    if not partes:
        # Remove prefixo "Local:" se estiver no começo (sem repetir ":")
        texto_limpo = texto
        if texto_limpo.lower().startswith("local:"):
            texto_limpo = texto_limpo[6:].strip()
        texto_limpo = limpar_dois_pontos_inicio(texto_limpo)
        return texto_limpo.replace('\n', '<br>')

    resultado = ""
    for local_texto, atividade_texto in partes:
        local_clean = local_texto.strip()
        atividade_clean = atividade_texto.strip()

        if local_clean.lower().startswith("local:"):
            local_clean = local_clean[6:].strip()
        if atividade_clean.lower().startswith("atividade:"):
            atividade_clean = atividade_clean[9:].strip()

        local_clean = limpar_dois_pontos_inicio(local_clean)
        atividade_clean = limpar_dois_pontos_inicio(atividade_clean)

        resultado += f"**Local:** {local_clean}  \n"
        resultado += f"**Atividade:** {atividade_clean}  \n\n"
    return resultado

def exibir_relatorio_dia(df, dia):
    st.markdown(f"### 📅 {dia.strftime('%d/%m/%Y')}")

    df_dia = df[df['Data'] == dia]
    if df_dia.empty:
        st.write("Nenhum dado para este dia.")
        return

    for _, row in df_dia.iterrows():
        equipe = row.get('Equipe', '')
        if equipe:
            st.markdown(f"**👷 Equipe:** {equipe}")

        if pd.notna(row.get('Manutenção Corretiva')) and row['Manutenção Corretiva'].strip():
            st.markdown("**🔧 Manutenção Corretiva:**")
            texto_formatado = formatar_local_atividade(row['Manutenção Corretiva'])
            st.markdown(texto_formatado, unsafe_allow_html=True)

        if pd.notna(row.get('Manutenção Preventiva')) and row['Manutenção Preventiva'].strip():
            st.markdown("**🛠️ Manutenção Preventiva:**")
            texto_formatado = formatar_local_atividade(row['Manutenção Preventiva'])
            st.markdown(texto_formatado, unsafe_allow_html=True)

        if pd.notna(row.get('Outras Atividades')) and row['Outras Atividades'].strip():
            st.markdown("**📌 Outras Atividades:**")
            outras = limpar_dois_pontos_inicio(row['Outras Atividades'].strip())
            outras = outras.replace('\n', '  \n')
            st.markdown(outras)

        if pd.notna(row.get('Status UFV')) and row['Status UFV'].strip():
            st.markdown("**✅ Status UFV:**")
            status_texto = limpar_dois_pontos_inicio(row['Status UFV'].strip())
            linhas = status_texto.split('\n')
            linhas_filtradas = [l for l in linhas if l.strip() not in ["Relatório Diário de Operação", "UFV Coromandel"]]
            status_limpo = '\n'.join(linhas_filtradas).replace('\n', '  \n')
            st.markdown(status_limpo)

        st.markdown("---")

def main():
    st.set_page_config(layout="wide")
    st.title("📋 Dashboard RDO - UFV Coromandel")

    df_rdo = carregar_dados()

    data_selecionada = st.date_input(
        "📅 Selecione o período para análise",
        value=(datetime.date(2025, 7, 1), datetime.date(2025, 7, 20)),
        key="date_input",
        help="Escolha o intervalo de datas para filtrar os dados"
    )

    if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
        inicio, fim = data_selecionada
    else:
        inicio = fim = data_selecionada

    df_filtrado = df_rdo[(df_rdo['Data'] >= inicio) & (df_rdo['Data'] <= fim)]

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado para o período selecionado.")
    else:
        dias_unicos = sorted(df_filtrado['Data'].unique())
        for dia in dias_unicos:
            exibir_relatorio_dia(df_filtrado, dia)

if __name__ == "__main__":
    main()
