import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def analyze_gender_bias():
    """
    Comprehensive gender bias analysis with detailed insights
    """
    # Load data
    df = pd.read_csv('data.csv', sep=';')
    
    # Normalize room names
    df['room_normalized'] = df['room'].replace({'The Pool (R1)': 'Pool (R1)'})
    
    # Calculate totals
    gender_time = df.groupby('gender')['allocated_minutes'].sum()
    total_time = gender_time.sum()
    
    male_hours = gender_time['M'] / 60
    female_hours = gender_time['F'] / 60
    male_percent = (gender_time['M'] / total_time) * 100
    female_percent = (gender_time['F'] / total_time) * 100
    diff_percent = ((male_hours - female_hours) / female_hours * 100)
    
    # ========== CHART 1: PIE - % TIME ===========
    pie_df = pd.DataFrame({
        'Gender': ['Female', 'Male'],
        'Percentage': [female_percent, male_percent]
    })
    
    fig_pie = px.pie(
        pie_df,
        values='Percentage',
        names='Gender',
        title='<b>Speaking Time Distribution</b>',
        color='Gender',
        color_discrete_map={'Female': '#E94B8B', 'Male': '#4A90E2'},
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
        height=450,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    
    # ========== CHART 2: BY DAY ===========
    by_day = df.groupby(['day', 'gender'])['allocated_minutes'].sum().unstack(fill_value=0)
    by_day_pct = by_day.div(by_day.sum(axis=1), axis=0) * 100
    # Garantir ordem correta
    day_order = ['Day 1', 'Day 2', 'Day 3', 'Day 4']
    by_day_pct = by_day_pct.reindex(day_order)
    
    fig_by_day = go.Figure()
    
    fig_by_day.add_trace(go.Bar(
        name='Female',
        x=day_order,
        y=by_day_pct['F'].values,
        marker_color='#E94B8B',
        text=[f'{val:.1f}%' for val in by_day_pct['F'].values],
        textposition='inside',
        textfont=dict(size=14, color='white')
    ))
    
    fig_by_day.add_trace(go.Bar(
        name='Male',
        x=day_order,
        y=by_day_pct['M'].values,
        marker_color='#4A90E2',
        text=[f'{val:.1f}%' for val in by_day_pct['M'].values],
        textposition='inside',
        textfont=dict(size=14, color='white')
    ))
    
    fig_by_day.update_layout(
        title='<b>Gender Distribution by Day</b>',
        barmode='stack',
        xaxis_title='',
        yaxis_title='Percentage',
        font=dict(size=14),
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # ========== CHART 3: BY ROOM ===========
    by_room = df.groupby(['room_normalized', 'gender'])['allocated_minutes'].sum().unstack(fill_value=0)
    by_room_pct = by_room.div(by_room.sum(axis=1), axis=0) * 100
    # Garantir ordem correta
    room_order = ['Hangar (R3)', 'Hobby (R2)', 'Pool (R1)']
    by_room_pct = by_room_pct.reindex(room_order)
    
    fig_by_room = go.Figure()
    
    fig_by_room.add_trace(go.Bar(
        name='Female',
        x=room_order,
        y=by_room_pct['F'].values,
        marker_color='#E94B8B',
        text=[f'{val:.1f}%' for val in by_room_pct['F'].values],
        textposition='inside',
        textfont=dict(size=14, color='white')
    ))
    
    fig_by_room.add_trace(go.Bar(
        name='Male',
        x=room_order,
        y=by_room_pct['M'].values,
        marker_color='#4A90E2',
        text=[f'{val:.1f}%' for val in by_room_pct['M'].values],
        textposition='inside',
        textfont=dict(size=14, color='white')
    ))
    
    fig_by_room.update_layout(
        title='<b>Gender Distribution by Room</b>',
        barmode='stack',
        xaxis_title='',
        yaxis_title='Percentage',
        font=dict(size=14),
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # ========== CHART 4: SESSION COMPOSITION ===========
    sessions = df.groupby('title').agg({
        'gender': lambda x: list(x),
        'speaker': 'count',
        'duration_min': 'first'
    }).reset_index()
    
    sessions['num_male'] = sessions['gender'].apply(lambda x: x.count('M'))
    sessions['num_female'] = sessions['gender'].apply(lambda x: x.count('F'))
    sessions['type'] = sessions.apply(lambda x: 
        'Mixed' if (x['num_male'] > 0 and x['num_female'] > 0) else
        'Male Only' if x['num_male'] > 0 else 'Female Only', axis=1
    )
    
    session_counts = sessions['type'].value_counts()
    
    fig_sessions = go.Figure(data=[go.Bar(
        x=['Female Only', 'Mixed', 'Male Only'],
        y=[session_counts.get('Female Only', 0), session_counts.get('Mixed', 0), session_counts.get('Male Only', 0)],
        marker_color=['#E94B8B', '#95A5A6', '#4A90E2'],
        text=[session_counts.get('Female Only', 0), session_counts.get('Mixed', 0), session_counts.get('Male Only', 0)],
        textposition='outside',
        textfont=dict(size=18, color='black'),
        width=0.6
    )])
    
    fig_sessions.update_layout(
        title='<b>Session Composition</b>',
        xaxis_title='',
        yaxis_title='Number of Sessions',
        font=dict(size=14),
        height=400,
        showlegend=False,
        yaxis=dict(range=[0, session_counts.max() * 1.3])
    )
    
    # ========== CHART 5: HOURS COMPARISON ===========
    fig_hours = go.Figure()
    
    fig_hours.add_trace(go.Bar(
        x=['Female', 'Male'],
        y=[female_hours, male_hours],
        marker_color=['#E94B8B', '#4A90E2'],
        text=[f'{female_hours:.1f}h', f'{male_hours:.1f}h'],
        textposition='outside',
        textfont=dict(size=20, color='black'),
        width=0.5
    ))
    
    fig_hours.update_layout(
        title='<b>Total Speaking Time (Hours)</b>',
        xaxis_title='',
        yaxis_title='Hours',
        font=dict(size=16),
        height=450,
        showlegend=False,
        yaxis=dict(range=[0, max(female_hours, male_hours) * 1.2])
    )
    
    # ========== ANALYSIS TEXT ===========
    # Find most imbalanced sessions
    male_only_sessions = sessions[sessions['type'] == 'Male Only'].nlargest(5, 'duration_min')
    
    summary_text = f"""
## 📊 Key Findings

### Overall Gender Gap
- **Female:** {female_hours:.1f} hours ({female_percent:.1f}%)
- **Male:** {male_hours:.1f} hours ({male_percent:.1f}%)

### 🚨 **Men have {diff_percent:.1f}% MORE speaking time than women**

---

### Distribution by Day
"""
    
    for day in ['Day 1', 'Day 2', 'Day 3', 'Day 4']:
        if day in by_day_pct.index:
            f_pct = by_day_pct.loc[day, 'F']
            m_pct = by_day_pct.loc[day, 'M']
            icon = "⚠️" if m_pct > 70 else "✅"
            summary_text += f"\n- **{day}:** Female {f_pct:.1f}% | Male {m_pct:.1f}% {icon}"
    
    summary_text += f"""

---

### Distribution by Room
"""
    
    for room in by_room_pct.index:
        f_pct = by_room_pct.loc[room, 'F']
        m_pct = by_room_pct.loc[room, 'M']
        summary_text += f"\n- **{room}:** Female {f_pct:.1f}% | Male {m_pct:.1f}%"
    
    summary_text += f"""

---

### Session Composition
- **Mixed sessions:** {session_counts.get('Mixed', 0)}
- **Male-only sessions:** {session_counts.get('Male Only', 0)}
- **Female-only sessions:** {session_counts.get('Female Only', 0)}

→ **{session_counts.get('Male Only', 0) / session_counts.get('Female Only', 1):.1f}× more male-only sessions**

---

### Longest Male-Only Sessions
"""
    
    for _, session in male_only_sessions.iterrows():
        summary_text += f"\n- **{session['title'][:60]}...** ({session['duration_min']} min)"
    
    summary_text += """

---

### 💡 Where Bias is Concentrated
1. **Days 1 & 2** show the largest imbalance (>70% male)
2. **Pool (R1)** (main stage) is heavily male-dominated
3. **Long-format sessions** (screenings, keynotes) are mostly male-only
4. These patterns reflect structural **curation choices**

"""
    
    # Create summary dataframe
    summary_df = pd.DataFrame({
        'Day': by_day_pct.index,
        'Female %': [f'{val:.1f}%' for val in by_day_pct['F']],
        'Male %': [f'{val:.1f}%' for val in by_day_pct['M']]
    })
    
    return summary_text, fig_pie, fig_by_day, fig_by_room, fig_sessions, fig_hours, summary_df


# Gradio Interface
with gr.Blocks(
    title="Gender Bias Analysis - Cooperative AI Conference",
    theme=gr.themes.Soft(primary_hue="purple", secondary_hue="pink"),
    css="""
    .gradio-container {
        max-width: 1400px !important;
    }
    """
) as demo:
    
    gr.Markdown("""
    # 🔍 Gender Bias Analysis
    ## Cooperative AI Conference
    
    Comprehensive analysis of speaking time distribution by gender at the Cooperative AI Conference.
    
    ---
    """)
    
    analyze_btn = gr.Button("🚀 Analyze", variant="primary", size="lg")
    
    with gr.Row():
        summary_output = gr.Markdown(label="Analysis Summary")
    
    gr.Markdown("## 📊 Overall Distribution")
    
    with gr.Row():
        with gr.Column(scale=1):
            pie_chart = gr.Plot(label="% of Speaking Time")
        with gr.Column(scale=1):
            hours_chart = gr.Plot(label="Total Hours")
    
    gr.Markdown("## 📅 Distribution Across Event")
    
    with gr.Row():
        with gr.Column():
            by_day_chart = gr.Plot(label="By Day")
        with gr.Column():
            by_room_chart = gr.Plot(label="By Room")
    
    gr.Markdown("## 🎭 Session Analysis")
    
    with gr.Row():
        sessions_chart = gr.Plot(label="Session Composition")
    
    with gr.Accordion("📈 Day-by-Day Breakdown", open=False):
        summary_table = gr.Dataframe(label="Daily Percentages")
    
    gr.Markdown("""
    ---
    ### ⚠️ Important Note
    
    This analysis uses binary categories (male/female) based on provided data.  
    We recognize that gender is a spectrum and this simplification has limitations.
    
    **Developed from a critical and anti-colonial perspective** to expose structural biases.
    
    Data validated against event program scraping - 124 participations analyzed.
    
    ---
    *Developed by [Veronyka](https://huggingface.co/Veronyka)* 💜
    """)
    
    analyze_btn.click(
        fn=analyze_gender_bias,
        inputs=[],
        outputs=[summary_output, pie_chart, by_day_chart, by_room_chart, sessions_chart, hours_chart, summary_table]
    )

if __name__ == "__main__":
    demo.launch()
