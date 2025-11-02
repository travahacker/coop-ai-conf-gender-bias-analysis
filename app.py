import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def analyze_gender_bias():
    """
    Analisa viés de gênero baseado na planilha de dados do evento
    """
    # Carregar dados
    df = pd.read_csv('data.csv')
    
    # Mapear M/F para português
    gender_map = {'M': 'Masculino', 'F': 'Feminino'}
    df['Gênero'] = df['gender'].map(gender_map)
    
    # Agregar tempo por gênero
    gender_summary = df.groupby('Gênero').agg({
        'allocated_minutes': 'sum',
        'speaker': 'count'
    }).reset_index()
    
    gender_summary.columns = ['Gênero', 'Tempo Total (min)', 'Participações']
    gender_summary['Tempo Total (horas)'] = (gender_summary['Tempo Total (min)'] / 60).round(2)
    
    # Calcular percentuais
    total_time = gender_summary['Tempo Total (min)'].sum()
    gender_summary['Percentual'] = ((gender_summary['Tempo Total (min)'] / total_time) * 100).round(1)
    
    # Gráfico de Pizza
    fig_pie = px.pie(
        gender_summary,
        values='Tempo Total (min)',
        names='Gênero',
        title='Distribuição de Tempo por Gênero na Conferência IA Cooperativa',
        color='Gênero',
        color_discrete_map={
            'Masculino': '#4A90E2',
            'Feminino': '#E94B8B'
        },
        hole=0.3
    )
    
    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=16,
        marker=dict(line=dict(color='white', width=2))
    )
    
    fig_pie.update_layout(
        font=dict(size=14),
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    # Gráfico de Barras
    fig_bars = go.Figure()
    
    colors = ['#4A90E2' if g == 'Masculino' else '#E94B8B' for g in gender_summary['Gênero']]
    
    fig_bars.add_trace(go.Bar(
        x=gender_summary['Gênero'],
        y=gender_summary['Tempo Total (horas)'],
        marker_color=colors,
        text=gender_summary['Tempo Total (horas)'],
        textposition='outside',
        textfont=dict(size=16)
    ))
    
    fig_bars.update_layout(
        title='Comparação de Tempo Total por Gênero (em horas)',
        xaxis_title='Gênero',
        yaxis_title='Tempo Total (horas)',
        font=dict(size=14),
        height=500,
        showlegend=False
    )
    
    # Criar tabela resumo
    summary_text = f"""
## 📊 Resultado da Análise

**Total de participações:** {len(df)}  
**Tempo total do evento:** {total_time/60:.1f} horas

### Distribuição por Gênero:
"""
    
    for _, row in gender_summary.iterrows():
        summary_text += f"""
**{row['Gênero'].upper()}**  
- Tempo total: {row['Tempo Total (horas)']} horas ({row['Percentual']:.1f}% do total)  
- Número de participações: {int(row['Participações'])}  
"""
    
    # Calcular viés
    masc = gender_summary[gender_summary['Gênero'] == 'Masculino']
    fem = gender_summary[gender_summary['Gênero'] == 'Feminino']
    
    if not masc.empty and not fem.empty:
        masc_time = masc['Tempo Total (min)'].values[0]
        fem_time = fem['Tempo Total (min)'].values[0]
        diff_percent = ((masc_time - fem_time) / fem_time * 100) if fem_time > 0 else 0
        
        summary_text += f"""
---
### 🚨 Análise de Viés:
"""
        if diff_percent > 10:
            summary_text += f"""
⚠️ **Pessoas identificadas como MASCULINO têm {diff_percent:.1f}% MAIS TEMPO** que pessoas identificadas como feminino.

Isso indica um **VIÉS DE GÊNERO SIGNIFICATIVO** na organização do evento.
"""
        elif diff_percent < -10:
            summary_text += f"""
✅ Pessoas identificadas como FEMININO têm {abs(diff_percent):.1f}% mais tempo que pessoas identificadas como masculino.
"""
        else:
            summary_text += f"""
✅ A distribuição de tempo entre gêneros está **relativamente balanceada** (diferença de {abs(diff_percent):.1f}%).
"""
    
    return summary_text, fig_pie, fig_bars, gender_summary


# Interface Gradio
with gr.Blocks(
    title="Análise de Viés de Gênero - Conferência IA Cooperativa",
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="pink"
    )
) as demo:
    
    gr.Markdown("""
    # 🔍 Análise de Viés de Gênero em Evento
    
    ## Conferência IA Cooperativa
    
    Esta ferramenta analisa a distribuição de tempo entre palestrantes por gênero 
    na Conferência de IA Cooperativa da Platform Coop.
    
    ---
    """)
    
    analyze_btn = gr.Button(
        "🚀 Analisar",
        variant="primary",
        size="lg",
        scale=1
    )
    
    with gr.Row():
        summary_output = gr.Markdown(label="Resumo da Análise")
    
    with gr.Row():
        with gr.Column():
            pie_chart = gr.Plot(label="Distribuição Percentual")
        with gr.Column():
            bar_chart = gr.Plot(label="Comparação em Horas")
    
    with gr.Accordion("📈 Dados Detalhados", open=False):
        summary_table = gr.Dataframe(label="Resumo por Gênero")
    
    gr.Markdown("""
    ---
    ### ⚠️ Nota Importante
    
    Esta análise utiliza categorias binárias (masculino/feminino) baseadas nos dados fornecidos.  
    Reconhecemos que gênero é um espectro e esta simplificação tem limitações.
    
    **Desenvolvido sob perspectiva crítica e contracolonial** para expor possíveis vieses estruturais.
    
    ---
    *Desenvolvido por [Veronyka](https://huggingface.co/Veronyka)* 💜
    """)
    
    analyze_btn.click(
        fn=analyze_gender_bias,
        inputs=[],
        outputs=[summary_output, pie_chart, bar_chart, summary_table]
    )

if __name__ == "__main__":
    demo.launch()
