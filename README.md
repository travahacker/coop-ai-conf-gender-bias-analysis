---
title: Gender Bias Analysis - Cooperative AI Conference
emoji: 🔍
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
license: mit
---

# 🔍 Gender Bias Analysis - Cooperative AI Conference

## About

This tool analyzes the schedule of the [Cooperative AI Conference](https://platform.coop/events/cooperativeai/program/) by Platform Cooperativism Consortium and identifies potential gender biases in the distribution of speaking time.

## Objective

To verify if there is a structural bias in the allocation of speaking time, especially if people identified as cis men receive more time due to the organization's composition.

## Methodology

1. **Data Loading**: Uses curated CSV data with speaker information and allocated time
2. **Gender Mapping**: Maps binary gender categories (M/F) for analysis
3. **Aggregation**: Calculates time distribution statistics by gender
4. **Visualization**: Generates charts and tables to facilitate analysis

## Features

- ✅ Clean and focused interface
- ✅ Interactive visualizations (pie and bar charts)
- ✅ Detailed tables by gender
- ✅ Aggregate statistics
- ✅ Percentage calculations and comparisons

## Limitations and Ethical Considerations

⚠️ **Important**: This tool has several limitations that should be considered:

1. **Binary gender**: The analysis assumes binary categories (male/female), which is a problematic simplification of gender reality
2. **Non-binary identities**: Does not adequately capture non-binary, transgender, or gender-diverse people
3. **Data-based**: Analysis is based on provided data classification

## Development Context

This tool was developed from a **critical and anti-colonial perspective** to:
- Expose possible structural biases in academic and conference spaces
- Question the distribution of power and voice at events
- Provide data for reflections on equity
- **NOT** to reinforce binary views or gender essentialism

## Responsible Use

This analysis should be used as:
- ✅ Starting point for discussions about equity
- ✅ Tool for reflection on structural biases
- ✅ Approximate indicator (not absolute truth)

And **NOT** as:
- ❌ Definitive determination of people's gender
- ❌ Surveillance or classification tool for individuals
- ❌ Substitute for self-declaration

## Technologies

- **Python 3.10+**
- **Gradio**: Web interface
- **Pandas**: Data analysis
- **Plotly**: Interactive visualizations

## How to Use

1. Click the "🚀 Analyze" button
2. Wait for data processing
3. Explore the generated charts and tables
4. Download data for additional analysis if desired

## Development

Developed by [Veronyka](https://huggingface.co/Veronyka)

From a critical, feminist, and anti-colonial perspective 💜

## License

MIT License - Free use with attribution

---

**Note**: This is a research and reflection tool. Results should be interpreted with caution and awareness of its limitations.
