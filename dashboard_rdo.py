import pandas as pd
import streamlit as st
import datetime
import plotly.express as px

def separar_local_atividade(texto):
    if pd.isna(texto) or texto.strip() == "":
        return "", ""
    partes = texto.split('\n', 1)
    local = partes[0].strip()
    atividade = partes[1].strip() if len(partes) > 1 else ""
    return local, atividade

def carregar_dados(caminho_rdo, caminho_contagem):
    df_rdo = pd.read_csv(caminho_rdo, parse_dates=['Data'], dayfirst=True, encoding='utf-8')
    df_contagem = pd.read_csv(caminho_contagem, encoding='utf-8')

    df_rdo.rename(columns=lambda x: x.strip(), inplace=True)
    df_contagem.rename(columns=lambda x: x.strip(), inplace=True)

    df_rdo['Data'] = df_rdo['Data'].dt.date

    if 'Manutenção Corretiva' in df_rdo.columns:
        df_rdo[['Local Corretiva', 'Atividade Corretiva']] = df_rdo['Manutenção Corretiva'].apply(
            lambda x: pd.Series(separar_local_atividade(x))
        )
    else:
        df_rdo['Local Corretiva'] = ""
        df_rdo['Atividade Corretiva'] = ""

    if 'Manutenção Preventiva' in df_rdo.columns:
        df_rdo[['Local Preventiva', 'Atividade Preventiva']] = df_rdo['Manutenção Preventiva'].apply(
            lambda x: pd.Series(separar_local_atividade(x))
        )
    else:
        df_rdo['Local Preventiva'] = ""
        df_rdo['Atividade Preventiva'] = ""

    return df_rdo, df_contagem

def main():
    st.set_page_config(layout="wide")
    st.title("📊 Dashboard RDO - Usina Solar UFV Coromandel")

    # Caminhos relativos para funcionar no Streamlit Cloud
    caminho_rdo = "rdo_extraido.csv"
    caminho_contagem = "contagem_falhas.csv"

    df_rdo, df_contagem = carregar_dados(caminho_rdo, caminho_contagem)

    data_selecionada = st.date_input(
        "📅 Selecione o período para análise",
        value=(datetime.date(2025, 7, 1), datetime.date(2025, 7, 14))
    )

    if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
        inicio, fim = data_selecionada
    else:
        inicio = fim = data_selecionada

    df_filtrado = df_rdo[(df_rdo['Data'] >= inicio) & (df_rdo['Data'] <= fim)]

    st.subheader("📌 Relatório diário consolidado")

    for data, grupo in df_filtrado.groupby('Data'):
        st.markdown(f"### 📅 {data.strftime('%d/%m/%Y')}")
        equipe = grupo['Equipe'].iloc[0] if 'Equipe' in grupo.columns else ""
        st.markdown(f"👷 Equipe: **{equipe}**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("🔧 **Manutenção Corretiva**")
            for local, atividade in zip(grupo['Local Corretiva'], grupo['Atividade Corretiva']):
                if atividade:
                    st.markdown(f"- **{local}**: {atividade}")

        with col2:
            st.markdown("🛠️ **Manutenção Preventiva**")
            for local, atividade in zip(grupo['Local Preventiva'], grupo['Atividade Preventiva']):
                if atividade:
                    st.markdown(f"- **{local}**: {atividade}")

        outras_colunas = [col for col in grupo.columns if "Outras" in col or "Status" in col]
        for col in outras_colunas:
            st.markdown(f"📎 **{col}**")
            st.text(grupo[col].iloc[0])

    st.divider()
    st.subheader("📉 Gráfico de Falhas por Tipo")

    if 'Descrição' in df_contagem.columns and 'Quantidade' in df_contagem.columns:
        df_contagem = df_contagem.dropna(subset=['Descrição', 'Quantidade'])
        df_contagem['Quantidade'] = pd.to_numeric(df_contagem['Quantidade'], errors='coerce').fillna(0)

        # Estimar horas associadas (baseado no padrão de descrição)
        def estimar_horas(desc):
            import re
            match = re.search(r'(\d+)\s*(minutos|min|hora|horas)', desc.lower())
            if match:
                val = int(match.group(1))
                unidade = match.group(2)
                if 'hora' in unidade:
                    return val
                elif 'min' in unidade:
                    return val / 60
            return 0

        df_contagem['Horas Estimadas'] = df_contagem['Descrição'].apply(estimar_horas)

        fig = px.bar(
            df_contagem,
            x='Descrição',
            y='Quantidade',
            color='Horas Estimadas',
            hover_data=['Horas Estimadas'],
            title="Falhas registradas por tipo",
            color_continuous_scale='turbo',
            template='plotly_dark'
        )
        fig.update_layout(xaxis_title="Tipo de Falha", yaxis_title="Ocorrências", height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Arquivo de contagem de falhas sem as colunas esperadas.")

if __name__ == "__main__":
    main()
