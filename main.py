import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# --- 1. Configuração da Página ---
st.set_page_config(layout="wide", page_title="Dashboard de Pesquisa de Mercado", page_icon="📊")


# --- 2. Carregamento dos Dados ---
@st.cache_data
def load_data(file_path):
    """Carrega o arquivo CSV, tratando possíveis erros e limpando nomes de colunas."""
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{file_path}' não encontrado.")
        st.info("Por favor, certifique-se de que o arquivo CSV está na mesma pasta que o script.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo: {e}")
        return None


# Nome exato do arquivo
FILE_NAME = "Pesquisa de Mercado - Preferências de Compra E-commerce X Loja Física .csv"
df = load_data(FILE_NAME)

if df is not None:
    # --- 3. Título e KPIs Principais ---
    st.title("📊 Preferências de Compra E-commerce vs. Loja Física")
    st.markdown("---")

    # KPIs no topo
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

    total_respondentes = len(df)
    col_onde_compra = "Onde você realiza a maioria das suas compras atualmente?"
    col_desistencia = "Você já desistiu de comprar em algum canal (online ou físico)?"
    col_confianca_online = "Em uma escala de 1 a 5, o quanto você confia nas compras online?"
    col_exp_fisica = "Em uma escala de 1 a 5, como você avalia sua experiência média ao comprar em loja física?"

    with col_kpi1:
        st.metric("📝 Total de Respondentes", total_respondentes)

    with col_kpi2:
        canal_mais_popular = df[col_onde_compra].value_counts().index[0]
        perc_canal = (df[col_onde_compra].value_counts().iloc[0] / total_respondentes * 100)
        st.metric("🏆 Canal Mais Popular", canal_mais_popular, f"{perc_canal:.1f}%")

    with col_kpi3:
        avg_confianca = df[col_confianca_online].mean()
        st.metric("⭐ Confiança Online Média", f"{avg_confianca:.2f}/5",
                  f"{(avg_confianca / 5) * 100:.0f}%")

    st.markdown("---")

    # --- 4. Seção: Perfil Demográfico ---
    st.header("👥 Perfil Demográfico dos Respondentes")

    col1, col2, col3 = st.columns(3)

    col_faixa_etaria = "Qual a sua faixa etária ?"
    col_genero = "Gênero"
    col_frequencia = "Com que frequência você realiza compras?"

    with col1:
        st.subheader("Faixa Etária")
        df_faixa = df[col_faixa_etaria].value_counts().reset_index()
        df_faixa.columns = ['Faixa Etária', 'Contagem']

        chart_faixa = alt.Chart(df_faixa).mark_bar(color='#1f77b4').encode(
            x=alt.X('Contagem', title='Respondentes'),
            y=alt.Y('Faixa Etária', sort='-x', title=None),
            tooltip=['Faixa Etária', 'Contagem']
        ).properties(height=250)
        st.altair_chart(chart_faixa, use_container_width=True)

    with col2:
        st.subheader("Gênero")
        df_genero = df[col_genero].value_counts().reset_index()
        df_genero.columns = ['Gênero', 'Contagem']

        base = alt.Chart(df_genero).encode(
            theta=alt.Theta("Contagem:Q", stack=True),
            color=alt.Color('Gênero:N', scale=alt.Scale(scheme='category10'))
        )
        pie = base.mark_arc(outerRadius=100, innerRadius=60)
        text = base.mark_text(radius=120, size=14).encode(text='Contagem:Q')
        st.altair_chart(pie + text, use_container_width=True)

    with col3:
        st.subheader("Frequência de Compras")
        df_freq = df[col_frequencia].value_counts().reset_index()
        df_freq.columns = ['Frequência', 'Contagem']

        chart_freq = alt.Chart(df_freq).mark_bar(color='#2ca02c').encode(
            x=alt.X('Contagem', title='Respondentes'),
            y=alt.Y('Frequência', sort='-x', title=None),
            tooltip=['Frequência', 'Contagem']
        ).properties(height=250)
        st.altair_chart(chart_freq, use_container_width=True)

    st.markdown("---")

    # --- 5. Seção: Preferências de Canal ---
    st.header("🛒 Análise de Canais de Compra")

    col4, col5 = st.columns([1.5, 1])

    with col4:
        st.subheader("Preferência de Canal por Faixa Etária")
        df_faixa_canal = df.groupby([col_faixa_etaria, col_onde_compra]).size().reset_index(name='Contagem')

        # Ordenar faixas etárias
        ordem_faixa = ['18 a 24 anos', '25 a 34 anos', '35 a 44 anos', '45 a 54 anos', '55 anos ou mais']

        chart_faixa_canal = alt.Chart(df_faixa_canal).mark_bar().encode(
            x=alt.X('Contagem:Q', title='Número de Respondentes', stack='normalize'),
            y=alt.Y(f'{col_faixa_etaria}:N', title='Faixa Etária',
                    sort=ordem_faixa),
            color=alt.Color(f'{col_onde_compra}:N',
                            title='Canal de Compra',
                            scale=alt.Scale(scheme='tableau10')),
            tooltip=[col_faixa_etaria, col_onde_compra, 'Contagem']
        ).properties(height=300)

        st.altair_chart(chart_faixa_canal, use_container_width=True)

    with col5:
        st.subheader("Distribuição Geral de Canais")
        df_canal = df[col_onde_compra].value_counts().reset_index()
        df_canal.columns = ['Canal', 'Contagem']
        df_canal['Percentual'] = (df_canal['Contagem'] / total_respondentes * 100).round(1)

        for idx, row in df_canal.iterrows():
            st.metric(
                label=row['Canal'],
                value=f"{row['Contagem']} pessoas",
                delta=f"{row['Percentual']}% do total"
            )

    st.markdown("---")

    # --- 6. Seção: Motivações ---
    st.header("💡 Principais Motivações de Compra")

    col6, col7 = st.columns(2)

    col_motivo_online = "Qual o principal motivo para preferir comprar online?"
    col_motivo_fisico = "Qual o principal motivo para preferir comprar em loja física?"

    with col6:
        st.subheader("🌐 Motivos para Comprar Online")
        df_mot_online = df[col_motivo_online].value_counts().reset_index()
        df_mot_online.columns = ['Motivo', 'Contagem']
        df_mot_online['Percentual'] = (df_mot_online['Contagem'] / df_mot_online['Contagem'].sum() * 100).round(1)

        chart_mot_online = alt.Chart(df_mot_online.head(8)).mark_bar(color='#ff7f0e').encode(
            x=alt.X('Contagem:Q', title='Número de Menções'),
            y=alt.Y('Motivo:N', sort='-x', title=None),
            tooltip=['Motivo', 'Contagem', alt.Tooltip('Percentual:Q', format='.1f', title='%')]
        ).properties(height=350)
        st.altair_chart(chart_mot_online, use_container_width=True)

    with col7:
        st.subheader("🏪 Motivos para Comprar em Loja Física")
        df_mot_fisico = df[col_motivo_fisico].value_counts().reset_index()
        df_mot_fisico.columns = ['Motivo', 'Contagem']
        df_mot_fisico['Percentual'] = (df_mot_fisico['Contagem'] / df_mot_fisico['Contagem'].sum() * 100).round(1)

        chart_mot_fisico = alt.Chart(df_mot_fisico.head(8)).mark_bar(color='#9467bd').encode(
            x=alt.X('Contagem:Q', title='Número de Menções'),
            y=alt.Y('Motivo:N', sort='-x', title=None),
            tooltip=['Motivo', 'Contagem', alt.Tooltip('Percentual:Q', format='.1f', title='%')]
        ).properties(height=350)
        st.altair_chart(chart_mot_fisico, use_container_width=True)

    st.markdown("---")

    # --- 7. Seção: Avaliações e Confiança ---
    st.header("⭐ Avaliação de Confiança e Experiência")

    col8, col9, col10 = st.columns([1, 1, 1])

    with col8:
        st.subheader("Confiança em Compras Online")
        df_conf = df[col_confianca_online].value_counts().sort_index().reset_index()
        df_conf.columns = ['Nota', 'Contagem']

        chart_conf = alt.Chart(df_conf).mark_bar(color='#2ca02c').encode(
            x=alt.X('Nota:O', title='Nota', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Contagem:Q', title='Respondentes'),
            tooltip=['Nota', 'Contagem']
        ).properties(height=300)
        st.altair_chart(chart_conf, use_container_width=True)

        # Estatísticas
        media_conf = df[col_confianca_online].mean()
        mediana_conf = df[col_confianca_online].median()
        st.info(f"**Média:** {media_conf:.2f} | **Mediana:** {mediana_conf:.0f}")

    with col9:
        st.subheader("Experiência em Loja Física")
        df_exp = df[col_exp_fisica].value_counts().sort_index().reset_index()
        df_exp.columns = ['Nota', 'Contagem']

        chart_exp = alt.Chart(df_exp).mark_bar(color='#ff7f0e').encode(
            x=alt.X('Nota:O', title='Nota', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Contagem:Q', title='Respondentes'),
            tooltip=['Nota', 'Contagem']
        ).properties(height=300)
        st.altair_chart(chart_exp, use_container_width=True)

        # Estatísticas
        media_exp = df[col_exp_fisica].mean()
        mediana_exp = df[col_exp_fisica].median()
        st.info(f"**Média:** {media_exp:.2f} | **Mediana:** {mediana_exp:.0f}")

    with col10:
        st.subheader("Comparativo")

        # Gráfico de comparação
        df_comparativo = pd.DataFrame({
            'Canal': ['Online', 'Física'],
            'Média': [media_conf, media_exp]
        })

        chart_comp = alt.Chart(df_comparativo).mark_bar(size=80).encode(
            x=alt.X('Canal:N', title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Média:Q', title='Avaliação Média', scale=alt.Scale(domain=[0, 5])),
            color=alt.Color('Canal:N', scale=alt.Scale(
                domain=['Online', 'Física'],
                range=['#2ca02c', '#ff7f0e']
            ), legend=None),
            tooltip=['Canal', alt.Tooltip('Média:Q', format='.2f')]
        ).properties(height=300)

        st.altair_chart(chart_comp, use_container_width=True)

        diferenca = media_exp - media_conf
        if diferenca > 0:
            st.success(f"Loja física está **{diferenca:.2f} pontos** à frente")
        else:
            st.success(f"Online está **{abs(diferenca):.2f} pontos** à frente")

    st.markdown("---")

    # --- 8. Seção: Produtos Mais Comprados ---
    st.header("🛍️ Categorias de Produtos por Canal")

    col_prod_online = "Quais tipos de produto você costuma comprar online?"
    col_prod_fisico = "Quais tipos de produto você costuma comprar em loja física?"


    def processar_multiselecao(df, nome_coluna):
        """Processa colunas de multiseleção (separadas por ';')"""
        dados = df[nome_coluna].str.split(';').explode().str.strip()
        dados = dados[dados != ''].value_counts().reset_index()
        dados.columns = ['Produto', 'Contagem']
        return dados


    df_prod_online = processar_multiselecao(df, col_prod_online)
    df_prod_fisico = processar_multiselecao(df, col_prod_fisico)

    col11, col12 = st.columns(2)

    with col11:
        st.subheader("🌐 Top 10 Produtos Online")
        df_prod_online_top = df_prod_online.head(10)
        df_prod_online_top['Percentual'] = (
                    df_prod_online_top['Contagem'] / df_prod_online_top['Contagem'].sum() * 100).round(1)

        chart_prod_online = alt.Chart(df_prod_online_top).mark_bar(color='#17becf').encode(
            x=alt.X('Contagem:Q', title='Menções'),
            y=alt.Y('Produto:N', sort='-x', title=None),
            tooltip=['Produto', 'Contagem', alt.Tooltip('Percentual:Q', format='.1f', title='%')]
        ).properties(height=400)
        st.altair_chart(chart_prod_online, use_container_width=True)

    with col12:
        st.subheader("🏪 Top 10 Produtos em Loja Física")
        df_prod_fisico_top = df_prod_fisico.head(10)
        df_prod_fisico_top['Percentual'] = (
                    df_prod_fisico_top['Contagem'] / df_prod_fisico_top['Contagem'].sum() * 100).round(1)

        chart_prod_fisico = alt.Chart(df_prod_fisico_top).mark_bar(color='#bcbd22').encode(
            x=alt.X('Contagem:Q', title='Menções'),
            y=alt.Y('Produto:N', sort='-x', title=None),
            tooltip=['Produto', 'Contagem', alt.Tooltip('Percentual:Q', format='.1f', title='%')]
        ).properties(height=400)
        st.altair_chart(chart_prod_fisico, use_container_width=True)

    st.markdown("---")

    # --- 9. Seção: Análise de Desistência ---
    st.header("❌ Análise de Desistência de Compra")

    col13, col14 = st.columns([2, 1])

    with col13:
        st.subheader("Principais Motivos de Desistência")
        df_desist = df[col_desistencia].str.split(';').explode().str.strip()
        df_desist = df_desist[df_desist != ''].value_counts().reset_index()
        df_desist.columns = ['Motivo', 'Contagem']
        df_desist['Percentual'] = (df_desist['Contagem'] / total_respondentes * 100).round(1)

        chart_desist = alt.Chart(df_desist.head(10)).mark_bar(color='#d62728').encode(
            x=alt.X('Contagem:Q', title='Número de Menções'),
            y=alt.Y('Motivo:N', sort='-x', title=None),
            tooltip=['Motivo', 'Contagem', alt.Tooltip('Percentual:Q', format='.1f', title='% do total')]
        ).properties(height=400)
        st.altair_chart(chart_desist, use_container_width=True)

    with col14:
        st.subheader("Resumo")

        # Top 3 motivos
        st.markdown("**🔝 Top 3 Motivos:**")
        for i, row in df_desist.head(3).iterrows():
            st.write(f"{i + 1}. **{row['Motivo']}**")
            st.progress(row['Percentual'] / 100)
            st.caption(f"{row['Contagem']} menções ({row['Percentual']}%)")
            st.write("")

    st.markdown("---")

    # --- 10. Seção: Insights Finais ---
    st.header("📊 Principais Insights da Pesquisa")

    col15, col16, col17 = st.columns(3)

    with col15:
        st.markdown("### 🎯 Perfil do Público")
        faixa_dominante = df[col_faixa_etaria].value_counts().index[0]
        genero_dominante = df[col_genero].value_counts().index[0]
        freq_dominante = df[col_frequencia].value_counts().index[0]

        st.write(f"- **Faixa etária predominante:** {faixa_dominante}")
        st.write(f"- **Gênero predominante:** {genero_dominante}")
        st.write(f"- **Frequência mais comum:** {freq_dominante}")

    with col16:
        st.markdown("### 💡 Comportamento")
        motivo_online_top = df[col_motivo_online].value_counts().index[0]
        motivo_fisico_top = df[col_motivo_fisico].value_counts().index[0]

        st.write(f"- **Principal motivo online:** {motivo_online_top}")
        st.write(f"- **Principal motivo físico:** {motivo_fisico_top}")
        # st.write(f"- **Taxa de desistência:** {taxa_desistencia:.1f}%")

    with col17:
        st.markdown("### 🏆 Produtos Campeões")
        prod_online_top = df_prod_online.iloc[0]['Produto']
        prod_fisico_top = df_prod_fisico.iloc[0]['Produto']

        st.write(f"- **Mais comprado online:** {prod_online_top}")
        st.write(f"- **Mais comprado físico:** {prod_fisico_top}")
        st.write(f"- **Avaliação física > online**")

    st.markdown("---")

    # --- 11. Seção: Dados Completos ---
    with st.expander("📋 Ver Dados Completos da Pesquisa"):
        st.dataframe(df, use_container_width=True)

        # Opção de download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name='dados_pesquisa.csv',
            mime='text/csv',
        )

else:

    st.error("Não foi possível carregar os dados. Verifique o arquivo CSV.")





