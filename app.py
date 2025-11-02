import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def analyze_gender_bias():
    """
    Analyzes gender bias based on conference event data
    """
    # Load data (semicolon separated)
    df = pd.read_csv('data.csv', sep=';')
    
    # Map M/F to English
    gender_map = {'M': 'Male', 'F': 'Female'}
    df['Gender'] = df['gender'].map(gender_map)
    
    # Aggregate time by gender
    gender_summary = df.groupby('Gender').agg({
        'allocated_minutes': 'sum',
        'speaker': 'count'
    }).reset_index()
    
    gender_summary.columns = ['Gender', 'Total Time (min)', 'Participations']
    gender_summary['Total Time (hours)'] = (gender_summary['Total Time (min)'] / 60).round(2)
    
    # Calculate percentages
    total_time = gender_summary['Total Time (min)'].sum()
    gender_summary['Percentage'] = ((gender_summary['Total Time (min)'] / total_time) * 100).round(1)
    
    # Pie Chart
    fig_pie = px.pie(
        gender_summary,
        values='Total Time (min)',
        names='Gender',
        title='Time Distribution by Gender at Cooperative AI Conference',
        color='Gender',
        color_discrete_map={
            'Male': '#4A90E2',
            'Female': '#E94B8B'
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
    
    # Bar Chart
    fig_bars = go.Figure()
    
    colors = ['#4A90E2' if g == 'Male' else '#E94B8B' for g in gender_summary['Gender']]
    
    fig_bars.add_trace(go.Bar(
        x=gender_summary['Gender'],
        y=gender_summary['Total Time (hours)'],
        marker_color=colors,
        text=gender_summary['Total Time (hours)'],
        textposition='outside',
        textfont=dict(size=16)
    ))
    
    fig_bars.update_layout(
        title='Total Time Comparison by Gender (hours)',
        xaxis_title='Gender',
        yaxis_title='Total Time (hours)',
        font=dict(size=14),
        height=500,
        showlegend=False
    )
    
    # Create summary text
    summary_text = f"""
## 📊 Analysis Results

**Total participations:** {len(df)}  
**Total event time:** {total_time/60:.1f} hours

### Distribution by Gender:
"""
    
    for _, row in gender_summary.iterrows():
        summary_text += f"""
**{row['Gender'].upper()}**  
- Total time: {row['Total Time (hours)']} hours ({row['Percentage']:.1f}% of total)  
- Number of participations: {int(row['Participations'])}  
"""
    
    # Calculate bias
    male = gender_summary[gender_summary['Gender'] == 'Male']
    female = gender_summary[gender_summary['Gender'] == 'Female']
    
    if not male.empty and not female.empty:
        male_time = male['Total Time (min)'].values[0]
        female_time = female['Total Time (min)'].values[0]
        diff_percent = ((male_time - female_time) / female_time * 100) if female_time > 0 else 0
        
        summary_text += f"""
---
### 🚨 Bias Analysis:
"""
        if diff_percent > 10:
            summary_text += f"""
⚠️ **People identified as MALE have {diff_percent:.1f}% MORE TIME** than people identified as female.

This indicates a **SIGNIFICANT GENDER BIAS** in the event organization.
"""
        elif diff_percent < -10:
            summary_text += f"""
✅ People identified as FEMALE have {abs(diff_percent):.1f}% more time than people identified as male.
"""
        else:
            summary_text += f"""
✅ Time distribution between genders is **relatively balanced** ({abs(diff_percent):.1f}% difference).
"""
    
    return summary_text, fig_pie, fig_bars, gender_summary


# Gradio Interface
with gr.Blocks(
    title="Gender Bias Analysis - Cooperative AI Conference",
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="pink"
    )
) as demo:
    
    gr.Markdown("""
    # 🔍 Gender Bias Analysis in Event
    
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
    
    with gr.Row():
        with gr.Column():
            pie_chart = gr.Plot(label="Percentage Distribution")
        with gr.Column():
            bar_chart = gr.Plot(label="Hours Comparison")
    
    with gr.Accordion("📈 Detailed Data", open=False):
        summary_table = gr.Dataframe(label="Summary by Gender")
    
    gr.Markdown("""
    ---
    ### ⚠️ Important Note
    
    This analysis uses binary categories (male/female) based on the provided data.  
    We recognize that gender is a spectrum and this simplification has limitations.
    
    **Developed from a critical and anti-colonial perspective** to expose possible structural biases.
    
    ---
    *Developed by [Veronyka](https://huggingface.co/Veronyka)* 💜
    """)
    
    analyze_btn.click(
        fn=analyze_gender_bias,
        inputs=[],
        outputs=[summary_output, pie_chart, bar_chart, summary_table]
    )

if __name__ == "__main__":
    demo.launch()
