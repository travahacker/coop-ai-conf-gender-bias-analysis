import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def analyze_gender_bias():
    """
    Comprehensive gender bias analysis with matplotlib charts
    """
    # Load data
    df = pd.read_csv('data.csv', sep=';')
    df['room_normalized'] = df['room'].replace({'The Pool (R1)': 'Pool (R1)'})
    
    # Calculate totals
    gender_time = df.groupby('gender')['allocated_minutes'].sum()
    total_time = gender_time.sum()
    
    male_hours = gender_time['M'] / 60
    female_hours = gender_time['F'] / 60
    male_percent = (gender_time['M'] / total_time) * 100
    female_percent = (gender_time['F'] / total_time) * 100
    diff_percent = ((male_hours - female_hours) / female_hours * 100)
    
    # ========== CHART 1: PIE ===========
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    colors = ['#E94B8B', '#4A90E2']
    wedges, texts, autotexts = ax1.pie(
        [female_percent, male_percent],
        labels=['Female', 'Male'],
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 14, 'weight': 'bold'}
    )
    ax1.set_title('Speaking Time Distribution', fontsize=16, weight='bold', pad=20)
    
    # ========== CHART 2: HOURS BAR ===========
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    bars = ax2.bar(['Female', 'Male'], [female_hours, male_hours], color=colors, width=0.5)
    ax2.set_ylabel('Hours', fontsize=12, weight='bold')
    ax2.set_title('Total Speaking Time (Hours)', fontsize=16, weight='bold', pad=20)
    ax2.set_ylim(0, max(female_hours, male_hours) * 1.2)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}h', ha='center', va='bottom', fontsize=14, weight='bold')
    
    # ========== CHART 3: BY DAY - SIMPLIFIED ===========
    by_day = df.groupby(['day', 'gender'])['allocated_minutes'].sum().unstack(fill_value=0)
    by_day_pct = by_day.div(by_day.sum(axis=1), axis=0) * 100
    day_order = ['Day 1', 'Day 2', 'Day 3', 'Day 4']
    by_day_pct = by_day_pct.reindex(day_order)
    
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    x = range(len(day_order))
    width = 0.35
    
    bars1 = ax3.bar([i - width/2 for i in x], by_day_pct['F'], width, 
                    label='Female', color='#E94B8B')
    bars2 = ax3.bar([i + width/2 for i in x], by_day_pct['M'], width,
                    label='Male', color='#4A90E2')
    
    ax3.set_ylabel('Percentage (%)', fontsize=12, weight='bold')
    ax3.set_title('Gender Distribution by Day', fontsize=16, weight='bold', pad=20)
    ax3.set_xticks(x)
    ax3.set_xticklabels(day_order)
    ax3.legend(loc='upper right', fontsize=12)
    ax3.set_ylim(0, 100)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
    
    # ========== CHART 4: BY ROOM - SIMPLIFIED ===========
    by_room = df.groupby(['room_normalized', 'gender'])['allocated_minutes'].sum().unstack(fill_value=0)
    by_room_pct = by_room.div(by_room.sum(axis=1), axis=0) * 100
    room_order = ['Hangar (R3)', 'Hobby (R2)', 'Pool (R1)']
    by_room_pct = by_room_pct.reindex(room_order)
    
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    x = range(len(room_order))
    width = 0.35
    
    bars1 = ax4.bar([i - width/2 for i in x], by_room_pct['F'], width,
                    label='Female', color='#E94B8B')
    bars2 = ax4.bar([i + width/2 for i in x], by_room_pct['M'], width,
                    label='Male', color='#4A90E2')
    
    ax4.set_ylabel('Percentage (%)', fontsize=12, weight='bold')
    ax4.set_title('Gender Distribution by Room', fontsize=16, weight='bold', pad=20)
    ax4.set_xticks(x)
    ax4.set_xticklabels(room_order, rotation=15, ha='right')
    ax4.legend(loc='upper right', fontsize=12)
    ax4.set_ylim(0, 100)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
    
    # ========== CHART 5: SESSION COMPOSITION ===========
    sessions = df.groupby('title').agg({
        'gender': lambda x: list(x),
        'speaker': 'count'
    }).reset_index()
    
    sessions['num_male'] = sessions['gender'].apply(lambda x: x.count('M'))
    sessions['num_female'] = sessions['gender'].apply(lambda x: x.count('F'))
    sessions['type'] = sessions.apply(lambda x: 
        'Mixed' if (x['num_male'] > 0 and x['num_female'] > 0) else
        'Male Only' if x['num_male'] > 0 else 'Female Only', axis=1
    )
    
    session_counts = sessions['type'].value_counts()
    
    fig5, ax5 = plt.subplots(figsize=(8, 6))
    categories = ['Female Only', 'Mixed', 'Male Only']
    values = [session_counts.get(cat, 0) for cat in categories]
    colors_session = ['#E94B8B', '#95A5A6', '#4A90E2']
    
    bars = ax5.bar(categories, values, color=colors_session, width=0.6)
    ax5.set_ylabel('Number of Sessions', fontsize=12, weight='bold')
    ax5.set_title('Session Composition', fontsize=16, weight='bold', pad=20)
    ax5.set_ylim(0, max(values) * 1.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=14, weight='bold')
    
    # Close all figures after saving
    plt.tight_layout()
    
    # ========== SUMMARY TEXT ===========
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
    
    for day in day_order:
        f_pct = by_day_pct.loc[day, 'F']
        m_pct = by_day_pct.loc[day, 'M']
        icon = "⚠️" if m_pct > 70 else "✅"
        summary_text += f"\n- **{day}:** Female {f_pct:.1f}% | Male {m_pct:.1f}% {icon}"
    
    summary_text += f"""

---

### Distribution by Room
"""
    
    for room in room_order:
        f_pct = by_room_pct.loc[room, 'F']
        m_pct = by_room_pct.loc[room, 'M']
        summary_text += f"\n- **{room}:** Female {f_pct:.1f}% | Male {m_pct:.1f}%"
    
    summary_text += f"""

---

### Session Composition
- **Mixed sessions:** {session_counts.get('Mixed', 0)}
- **Male-only sessions:** {session_counts.get('Male Only', 0)}
- **Female-only sessions:** {session_counts.get('Female Only', 0)}

→ **{session_counts.get('Male Only', 0) / max(session_counts.get('Female Only', 1), 1):.1f}× more male-only sessions**

---

### 💡 Main Takeaways
1. **Days 1 & 2** show largest imbalance (>70% male)
2. **Pool (R1)** (main stage) is heavily male-dominated  
3. **Long-format sessions** are mostly male-only
4. These patterns reflect **structural curation choices**
"""
    
    return summary_text, fig1, fig2, fig3, fig4, fig5


# Gradio Interface
with gr.Blocks(
    title="Gender Bias Analysis - Cooperative AI Conference",
    theme=gr.themes.Soft(primary_hue="purple", secondary_hue="pink")
) as demo:
    
    gr.Markdown("""
    # 🔍 Gender Bias Analysis
    ## Cooperative AI Conference
    
    Analysis of speaking time distribution by gender at the Cooperative AI Conference.
    
    **Data:** 124 participations | **Updated:** Nov 2024
    
    ---
    """)
    
    analyze_btn = gr.Button("🚀 Analyze", variant="primary", size="lg")
    
    with gr.Row():
        summary_output = gr.Markdown(label="📊 Analysis Summary")
    
    gr.Markdown("## Overall Distribution")
    
    with gr.Row():
        with gr.Column():
            pie_chart = gr.Plot(label="% of Speaking Time")
        with gr.Column():
            hours_chart = gr.Plot(label="Total Hours")
    
    gr.Markdown("## Distribution by Day & Room")
    
    with gr.Row():
        by_day_chart = gr.Plot(label="By Day (Grouped Bars)")
    
    with gr.Row():
        by_room_chart = gr.Plot(label="By Room (Grouped Bars)")
    
    gr.Markdown("## Session Analysis")
    
    with gr.Row():
        sessions_chart = gr.Plot(label="Session Composition")
    
    gr.Markdown("""
    ---
    ### ⚠️ Important Note
    
    This analysis uses binary categories (male/female) based on provided data.  
    We recognize that gender is a spectrum and this simplification has limitations.
    
    **Developed from a critical and anti-colonial perspective** to expose structural biases.
    
    ---
    *Developed by [Veronyka](https://huggingface.co/Veronyka)* 💜
    """)
    
    analyze_btn.click(
        fn=analyze_gender_bias,
        inputs=[],
        outputs=[summary_output, pie_chart, hours_chart, by_day_chart, by_room_chart, sessions_chart]
    )

if __name__ == "__main__":
    demo.launch()
