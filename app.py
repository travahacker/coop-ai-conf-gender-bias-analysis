import gradio as gr
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import gender_guesser.detector as gender
import plotly.express as px
import plotly.graph_objects as go
import re

class GenderResolver:
    """Resolve gênero usando múltiplas estratégias - APENAS masculino ou feminino"""
    def __init__(self):
        self.detector = gender.Detector()
        self.cache = {}
        
        # Dicionário manual baseado em pesquisa dos nomes da conferência
        self.manual_overrides = {
            'Itir': 'feminino', 'Trebor': 'masculino', 'Morshed': 'masculino',
            'Oktay': 'masculino', 'Jeongone': 'feminino', 'Akkanut': 'masculino',
            'Vangelis': 'masculino', 'Dorleta': 'feminino', 'Ganesh': 'masculino',
            'Uygar': 'masculino', 'Orkun': 'masculino', 'Alper': 'masculino',
            'Ferit': 'masculino', 'Serkan': 'masculino', 'Hatice': 'feminino',
            'Nil': 'feminino', 'Rana': 'feminino', 'Selin': 'feminino',
            'Baris': 'masculino', 'Yuliy': 'masculino', 
            'Kenzo': 'masculino', 'Anne-Pauline': 'feminino', 'Tara': 'feminino', 
            'Lila': 'feminino', 'Can': 'masculino',
        }
    
    def clean_name(self, full_name):
        full_name = full_name.strip()
        titles = ['Dr.', 'Prof.', 'Mr.', 'Mrs.', 'Ms.', 'Miss', 'Mx.']
        for title in titles:
            full_name = full_name.replace(title, '').strip()
        first_name = full_name.split()[0] if full_name else ""
        first_name = re.sub(r'[()"]', '', first_name)
        return first_name
    
    def analyze_gender(self, full_name):
        first_name = self.clean_name(full_name)
        
        if not first_name:
            return 'masculino'
        
        if first_name in self.cache:
            return self.cache[first_name]
        
        # 1. Verificar manual override primeiro
        if first_name in self.manual_overrides:
            result = self.manual_overrides[first_name]
            self.cache[first_name] = result
            return result
        
        # 2. Tentar gender_guesser
        guess = self.detector.get_gender(first_name)
        
        if guess in ['male', 'mostly_male']:
            result = 'masculino'
        elif guess in ['female', 'mostly_female']:
            result = 'feminino'
        else:
            # 3. Fallback: heurística por terminação
            if first_name[-1].lower() in ['a', 'e', 'i'] and len(first_name) > 3:
                result = 'feminino'
            else:
                result = 'masculino'
        
        self.cache[first_name] = result
        return result


def scrape_conference_program():
    """
    Extrai todas as sessões da programação do evento Cooperative AI
    """
    url = "https://platform.coop/events/cooperativeai/program/"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        sessions = []
        session_items = soup.find_all('li', class_='session')
        
        for session in session_items:
            time_elem = session.find('time', class_='session__time')
            if not time_elem:
                continue
            
            time_str = time_elem.get('datetime', '')
            title_elem = session.find('p', class_='session__title')
            title = title_elem.get_text(strip=True) if title_elem else "Sem título"
            
            participants_elem = session.find('p', class_='session__participants')
            participants = []
            if participants_elem:
                participants_text = participants_elem.get_text(strip=True)
                participants = [p.strip() for p in participants_text.split(',') if p.strip()]
            
            if time_str:
                sessions.append({
                    'time': time_str,
                    'title': title,
                    'participants': participants,
                    'num_participants': len(participants)
                })
        
        # Calcular durações
        for i in range(len(sessions)):
            current_time = datetime.fromisoformat(sessions[i]['time'])
            
            if i < len(sessions) - 1:
                next_time = datetime.fromisoformat(sessions[i+1]['time'])
                duration = (next_time - current_time).total_seconds() / 60
            else:
                duration = 60
            
            sessions[i]['duration_minutes'] = duration
            sessions[i]['time_formatted'] = current_time.strftime('%d/%m/%Y %H:%M')
        
        return sessions
    
    except Exception as e:
        return {"error": str(e)}


def analyze_conference_bias():
    """
    Analisa possível viés de gênero na distribuição de tempo por palestrante
    """
    sessions = scrape_conference_program()
    
    if isinstance(sessions, dict) and 'error' in sessions:
        return f"Erro ao extrair dados: {sessions['error']}", None, None, None, None
    
    # Inicializar resolver
    resolver = GenderResolver()
    
    # Criar lista detalhada de participantes com tempo
    participants_data = []
    
    for session in sessions:
        if session['participants']:
            time_per_person = session['duration_minutes'] / len(session['participants'])
            
            for participant in session['participants']:
                gender_guess = resolver.analyze_gender(participant)
                participants_data.append({
                    'Nome': participant,
                    'Sessão': session['title'],
                    'Horário': session['time_formatted'],
                    'Duração da Sessão (min)': session['duration_minutes'],
                    'Tempo Atribuído (min)': time_per_person,
                    'Gênero Estimado': gender_guess
                })
    
    # Criar DataFrame
    df = pd.DataFrame(participants_data)
    
    # Análise agregada por gênero
    gender_summary = df.groupby('Gênero Estimado').agg({
        'Tempo Atribuído (min)': ['sum', 'count', 'mean']
    }).round(2)
    
    gender_summary.columns = ['Tempo Total (min)', 'Número de Participações', 'Tempo Médio por Participação (min)']
    gender_summary = gender_summary.reset_index()
    
    # Converter tempo para horas
    gender_summary['Tempo Total (horas)'] = (gender_summary['Tempo Total (min)'] / 60).round(2)
    
    # Gráfico de pizza
    fig_pie = px.pie(
        gender_summary, 
        values='Tempo Total (min)', 
        names='Gênero Estimado',
        title='Distribuição de Tempo Total por Gênero Estimado',
        color_discrete_map={
            'masculino': '#4A90E2',
            'feminino': '#E94B8B'
        }
    )
    
    # Gráfico de barras
    fig_bars = go.Figure()
    
    colors_map = {'masculino': '#4A90E2', 'feminino': '#E94B8B'}
    bar_colors = [colors_map.get(g, '#95A5A6') for g in gender_summary['Gênero Estimado']]
    
    fig_bars.add_trace(go.Bar(
        name='Tempo Total (horas)',
        x=gender_summary['Gênero Estimado'],
        y=gender_summary['Tempo Total (horas)'],
        marker_color=bar_colors
    ))
    
    fig_bars.update_layout(
        title='Tempo Total de Participação por Gênero',
        xaxis_title='Gênero Estimado',
        yaxis_title='Tempo Total (horas)',
        showlegend=False
    )
    
    # Estatísticas
    total_time = gender_summary['Tempo Total (min)'].sum()
    gender_summary['Percentual do Tempo'] = ((gender_summary['Tempo Total (min)'] / total_time) * 100).round(2)
    
    # Texto de análise
    analysis_text = f"""
## 🔍 Análise de Viés de Gênero - Cooperative AI Conference

### Resumo Geral:
- **Total de participações analisadas:** {len(df)}
- **Tempo total de programação:** {total_time/60:.2f} horas
- **Número de sessões:** {len(sessions)}

### Distribuição por Gênero:
"""
    
    for _, row in gender_summary.iterrows():
        analysis_text += f"""
**{row['Gênero Estimado'].upper()}:**
- Tempo total: {row['Tempo Total (horas)']} horas ({row['Percentual do Tempo']:.1f}% do total)
- Número de participações: {int(row['Número de Participações'])}
- Tempo médio por participação: {row['Tempo Médio por Participação (min)']:.1f} minutos
"""
    
    # Calcular diferença entre masculino e feminino
    masc_row = gender_summary[gender_summary['Gênero Estimado'] == 'masculino']
    fem_row = gender_summary[gender_summary['Gênero Estimado'] == 'feminino']
    
    if not masc_row.empty and not fem_row.empty:
        masc_time = masc_row['Tempo Total (min)'].values[0]
        fem_time = fem_row['Tempo Total (min)'].values[0]
        diff_percent = ((masc_time - fem_time) / fem_time * 100) if fem_time > 0 else 0
        
        analysis_text += f"""
### 🚨 Análise de Viés:
"""
        if diff_percent > 10:
            analysis_text += f"""
- Pessoas identificadas como **masculino** têm **{diff_percent:.1f}% mais tempo** que pessoas identificadas como feminino.
- Isso indica um **VIÉS DE GÊNERO SIGNIFICATIVO** na organização do evento.
"""
        elif diff_percent < -10:
            analysis_text += f"""
- Pessoas identificadas como **feminino** têm **{abs(diff_percent):.1f}% mais tempo** que pessoas identificadas como masculino.
"""
        else:
            analysis_text += f"""
- A distribuição de tempo entre gêneros está **relativamente balanceada** (diferença de {abs(diff_percent):.1f}%).
"""
    
    analysis_text += """

### ⚠️ Limitações da Análise:
- A detecção de gênero é baseada em **nomes** e pode conter erros
- **Assume gênero binário** (masculino/feminino) - simplificação problemática
- Não captura identidades não-binárias, transgênero ou de gênero diverso
- Classificação baseada em nome ≠ identidade de gênero real
- Esta análise é um **indicador aproximado** e não uma verdade absoluta
"""
    
    return analysis_text, df, gender_summary, fig_pie, fig_bars


# Interface Gradio
with gr.Blocks(title="Análise de Viés de Gênero - Cooperative AI Conference", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🔍 Análise de Viés de Gênero em Conferência
    
    ## Cooperative AI Conference - Platform Coop
    
    Esta ferramenta analisa a programação do evento [Cooperative AI](https://platform.coop/events/cooperativeai/program/) 
    e identifica possíveis vieses de gênero na distribuição de tempo entre palestrantes.
    
    **Metodologia:**
    1. Extrai todas as sessões e participantes do site do evento
    2. Calcula a duração de cada sessão
    3. Estima o gênero dos participantes baseado em seus nomes (masculino ou feminino)
    4. Analisa a distribuição de tempo por gênero estimado
    
    **Objetivo:** Verificar se há viés de gênero na alocação de tempo.
    
    ---
    """)
    
    analyze_btn = gr.Button("🚀 Analisar Programação", variant="primary", size="lg")
    
    with gr.Row():
        with gr.Column():
            analysis_output = gr.Markdown(label="Análise")
        with gr.Column():
            pie_chart = gr.Plot(label="Distribuição de Tempo por Gênero")
    
    bar_chart = gr.Plot(label="Comparação de Tempo por Gênero")
    
    with gr.Accordion("📊 Dados Detalhados por Participante", open=False):
        detailed_table = gr.Dataframe(label="Dados Completos")
    
    with gr.Accordion("📈 Sumário por Gênero", open=False):
        summary_table = gr.Dataframe(label="Resumo Estatístico")
    
    gr.Markdown("""
    ---
    ### ⚠️ Notas Importantes:
    
    - **Limitações Éticas**: Esta análise assume gênero binário baseado em nomes, o que é uma simplificação problemática.
    - **Contexto**: Desenvolvida sob perspectiva crítica e contracolonial para expor possíveis vieses estruturais.
    - **Precisão**: A detecção automática de gênero por nome tem limitações significativas.
    - **Uso**: Ferramenta para reflexão e não como verdade absoluta sobre identidades.
    
    ---
    
    Desenvolvido por [Veronyka](https://huggingface.co/Veronyka)
    """)
    
    def run_analysis():
        text, df, summary, pie, bars = analyze_conference_bias()
        return text, pie, bars, df, summary
    
    analyze_btn.click(
        fn=run_analysis,
        inputs=[],
        outputs=[analysis_output, pie_chart, bar_chart, detailed_table, summary_table]
    )

if __name__ == "__main__":
    demo.launch()
