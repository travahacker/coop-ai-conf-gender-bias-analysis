import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def analyze_gender_bias():
    """
    Analyzes gender bias based on conference event data
    """
    # Load data (semicolon separated)
    df = pd.read_csv('data.csv', sep=';')
    
    # Calculate total time by gender
    gender_time = df.groupby('gender')['allocated_minutes'].sum()
    total_time = gender_time.sum()
    
    male_hours = gender_time['M'] / 60
    female_hours = gender_time['F'] / 60
    male_percent = (gender_time['M'] / total_time) * 100
    female_percent = (gender_time['F'] / total_time) * 100
    
    # Session analysis
    sessions = df.groupby(['title']).agg({
        'gender': lambda x: list(x),
        'speaker': 'count'
    }).reset_index()
    
    sessions['num_speakers'] = sessions['speaker']
    sessions['num_male'] = sessions['gender'].apply(lambda x: x.count('M'))
    sessions['num_female'] = sessions['gender'].apply(lambda x: x.count('F'))
    
    # Solo sessions
    solo_male = len(sessions[(sessions['num_speakers'] == 1) & (sessions['num_male'] == 1)])
    solo_female = len(sessions[(sessions['num_speakers'] == 1) & (sessions['num_female'] == 1)])
    
    # Sessions with more male/female
    more_male = len(sessions[sessions['num_male'] > sessions['num_female']])
    more_female = len(sessions[sessions['num_female'] > sessions['num_male']])
    balanced = len(sessions[sessions['num_female'] == sessions['num_male']])
    
    # 1. PIE CHART - % of time by gender
    fig_pie = px.pie(
        values=[female_percent, male_percent],
        names=['Female', 'Male'],
        title='Percentage of Speaking Time by Gender',
        color_discrete_sequence=['#E94B8B', '#4A90E2'],
        hole=0.4
    )
    
    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=18,
        marker=dict(line=dict(color='white', width=3))
    )
    
    fig_pie.update_layout(
        font=dict(size=16),
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=16)
        )
    )
    
    # 2. BAR CHART - Total hours Female vs Male
    fig_hours = go.Figure()
    
    fig_hours.add_trace(go.Bar(
        x=['Female', 'Male'],
        y=[female_hours, male_hours],
        marker_color=['#E94B8B', '#4A90E2'],
        text=[f'{female_hours:.1f}h', f'{male_hours:.1f}h'],
        textposition='outside',
        textfont=dict(size=18, color='black'),
        width=0.5
    ))
    
    fig_hours.update_layout(
        title='Total Hours: Female vs Male',
        xaxis_title='Gender',
        yaxis_title='Total Hours',
        font=dict(size=16),
        height=500,
        showlegend=False,
        yaxis=dict(range=[0, max(female_hours, male_hours) * 1.2])
    )
    
    # 3. BAR CHART - Solo sessions
    fig_solo = go.Figure()
    
    fig_solo.add_trace(go.Bar(
        x=['Female Solo', 'Male Solo'],
        y=[solo_female, solo_male],
        marker_color=['#E94B8B', '#4A90E2'],
        text=[solo_female, solo_male],
        textposition='outside',
        textfont=dict(size=18, color='black'),
        width=0.5
    ))
    
    fig_solo.update_layout(
        title='Number of Solo Sessions by Gender',
        xaxis_title='',
        yaxis_title='Number of Sessions',
        font=dict(size=16),
        height=400,
        showlegend=False,
        yaxis=dict(range=[0, max(solo_female, solo_male) * 1.3])
    )
    
    # 4. BAR CHART - Sessions with more male/female
    fig_sessions = go.Figure()
    
    fig_sessions.add_trace(go.Bar(
        x=['More Female', 'Balanced', 'More Male'],
        y=[more_female, balanced, more_male],
        marker_color=['#E94B8B', '#95A5A6', '#4A90E2'],
        text=[more_female, balanced, more_male],
        textposition='outside',
        textfont=dict(size=18, color='black'),
        width=0.6
    ))
    
    fig_sessions.update_layout(
        title='Session Composition',
        xaxis_title='',
        yaxis_title='Number of Sessions',
        font=dict(size=16),
        height=400,
        showlegend=False,
        yaxis=dict(range=[0, max(more_female, balanced, more_male) * 1.3])
    )
    
    # Summary text
    diff_percent = ((male_hours - female_hours) / female_hours * 100)
    
    summary_text = f"""
## 📊 Analysis Results

### Total Speaking Time:
- **Female:** {female_hours:.1f} hours ({female_percent:.1f}%)
- **Male:** {male_hours:.1f} hours ({male_percent:.1f}%)

### 🚨 Bias Analysis:
**Men have {diff_percent:.1f}% MORE speaking time than women.**

This represents a **SIGNIFICANT GENDER BIAS** in the conference organization.

---

### Session Breakdown:
- **Solo sessions (Female only):** {solo_female}
- **Solo sessions (Male only):** {solo_male}
- **Sessions with more females:** {more_female}
- **Sessions with equal gender:** {balanced}
- **Sessions with more males:** {more_male}

---

**Total speakers analyzed:** {len(df)} participations  
**Total event time:** {total_time/60:.1f} hours  
**Total sessions:** {len(sessions)}
"""
    
    # Create summary table
    summary_df = pd.DataFrame({
        'Metric': [
            'Total Hours',
            'Percentage',
            'Solo Sessions',
            'Sessions (Majority)',
            'Total Participations'
        ],
        'Female': [
            f'{female_hours:.1f}h',
            f'{female_percent:.1f}%',
            solo_female,
            more_female,
            len(df[df['gender'] == 'F'])
        ],
        'Male': [
            f'{male_hours:.1f}h',
            f'{male_percent:.1f}%',
            solo_male,
            more_male,
            len(df[df['gender'] == 'M'])
        ]
    })
    
    return summary_text, fig_pie, fig_hours, fig_solo, fig_sessions, summary_df


# Gradio Interface
with gr.Blocks(
    title="Gender Bias Analysis - Cooperative AI Conference",
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="pink"
    )
) as demo:
    
    gr.Markdown("""
    # 🔍 Gender Bias Analysis
    
    ## Cooperative AI Conference
    
    This tool analyzes the time distribution among speakers by gender 
    at the Cooperative AI Conference by Platform Coop.
    
    ---
    """)
    
    analyze_btn = gr.Button(
        "🚀 Analyze",
        variant="primary",
        size="lg",
        scale=1
    )
    
    with gr.Row():
        summary_output = gr.Markdown(label="Analysis Summary")
    
    gr.Markdown("## Time Distribution")
    
    with gr.Row():
        with gr.Column():
            pie_chart = gr.Plot(label="% of Speaking Time")
        with gr.Column():
            hours_chart = gr.Plot(label="Total Hours Comparison")
    
    gr.Markdown("## Session Analysis")
    
    with gr.Row():
        with gr.Column():
            solo_chart = gr.Plot(label="Solo Sessions")
        with gr.Column():
            sessions_chart = gr.Plot(label="Session Composition")
    
    with gr.Accordion("📈 Summary Table", open=False):
        summary_table = gr.Dataframe(label="Metrics by Gender")
    
    gr.Markdown("""
    ---
    ### ⚠️ Important Note
    
    This analysis uses binary categories (male/female) based on the provided data.  
    We recognize that gender is a spectrum and this simplification has limitations.
    
    **Developed from a critical and anti-colonial perspective** to expose structural biases.
    
    ---
    *Developed by [Veronyka](https://huggingface.co/Veronyka)* 💜
    """)
    
    analyze_btn.click(
        fn=analyze_gender_bias,
        inputs=[],
        outputs=[summary_output, pie_chart, hours_chart, solo_chart, sessions_chart, summary_table]
    )

if __name__ == "__main__":
    demo.launch()
