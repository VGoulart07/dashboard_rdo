import pandas as pd
import streamlit as st
import datetime
import plotly.express as px

def carregar_dados():
    df_rdo = pd.read_csv("rdo_completo.csv", encoding='utf-8')
    df_falhas = pd.read_csv("contagem_falhas.csv", encoding='utf-8')

    # Garantir que 'Data' seja do tipo datetime.date
    df_rdo['Data'] = pd.to_datetime(df_rdo['Data'], errors='coerce').dt.date
    return df_rdo, df_falhas

def exibir_rdo_por_dia(df_filtrado):
    dias_unicos = sorted(df_filtrado['Data'].unique())
    for dia in dias_unicos:
        st.markdown(f"### 📅 {dia.strftime('%d/%m/%Y')}")
        registros = df_filtrado[df_filtrado['Data'] == dia]

        for _, row in registros.iterrows():
            equipe = row.get('Equipe', '')
            st.markdown(f"**👷 Equipe:** {equipe}")

            if pd.notna(row.get('Manutenção Corretiva')):
                st.markdown("**🔧 Manutenção Corretiva:**")
                st.markdown(row['Manutenção Corretiva'])

            if pd.notna(row.get('Manutenção Preventiva')):
                st.markdown("**🛠️ Manutenção Preventiva:**")
                st.markdown(row['Manutenção Preventiva'])

            if pd.notna(row.get('Outras Atividades')):
                st.markdown("**📌 Outras Atividades:**")
                st.markdown(row['Outras Atividades'])

            if pd.notna(row.get('Status UFV')):
                st.markdown("**✅ Status UFV:**")
                st.markdown(row['Status UFV'])

            st.markdown("---")

def exibir_grafico_falhas(df_falhas):
    st.subheader("📉 Falhas por Tipo (Total de Horas)")

    if {'Descrição', 'Quantidade', 'Horas por Evento'}.issubset(df_falhas.columns):
        df_falhas['Quantidade'] = pd.to_numeric(df_falhas['Quantidade'], errors='coerce').fillna(0)
        df_falhas['Horas por Evento'] = pd.to_numeric(df_falhas['Horas por Evento'], errors='coerce').fillna(0)

        df_falhas['Horas Totais'] = df_falhas['Quantidade'] * df_falhas['Horas por Evento']
        df_falhas_agrupado = df_falhas.groupby('Descrição', as_index=False)['Horas Totais'].sum()
        df_falhas_agrupado = df_falhas_agrupado.sort_values(by='Horas Totais', ascending=True)

        fig = px.bar(
            df_falhas_agrupado,
            x='Horas Totais',
            y='Descrição',
            orientation='h',
            text='Horas Totais',
            template='plotly_dark',
            title='⏱️ Tempo Total de Interrupção por Tipo de Falha',
            labels={'Horas Totais': 'Horas', 'Descrição': 'Tipo de Falha'}
        )

        fig.update_traces(marker_color='cyan', texttemplate='%{text:.2f}h', textposition='outside')
        fig.update_layout(
            plot_bgcolor='black',
            paper_bgcolor='black',
            font_color='white',
            margin=dict(l=120, r=30, t=60, b=30),
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ O arquivo contagem_falhas.csv precisa conter as colunas: 'Descrição', 'Quantidade' e 'Horas por Evento'.")

def main():
    st.set_page_config(layout="wide")
    st.title("📊 Dashboard RDO - UFV Coromandel")

    df_rdo, df_falhas = carregar_dados()

    # Filtro de período
    data_selecionada = st.date_input(
        "📅 Selecione o período para análise",
        value=(datetime.date(2025, 7, 1), datetime.date(2025, 7, 14))
    )

    if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
        inicio, fim = data_selecionada
    else:
        inicio = fim = data_selecionada

    df_filtrado = df_rdo[(df_rdo['Data'] >= inicio) & (df_rdo['Data'] <= fim)]

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado para o período selecionado.")
    else:
        exibir_rdo_por_dia(df_filtrado)
        exibir_grafico_falhas(df_falhas)

if __name__ == "__main__":
    main()
