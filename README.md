---
title: Análise de Viés de Gênero - Cooperative AI Conference
emoji: 🔍
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 4.50.0
app_file: app.py
pinned: false
license: mit
---

# 🔍 Análise de Viés de Gênero - Cooperative AI Conference

## Sobre

Esta ferramenta analisa a programação da [Cooperative AI Conference](https://platform.coop/events/cooperativeai/program/) da Platform Cooperativism Consortium e identifica possíveis vieses de gênero na distribuição de tempo entre palestrantes.

## Objetivo

Verificar se há um viés estrutural na alocação de tempo de fala, especialmente se pessoas identificadas como homens cis recebem mais tempo devido à composição da organização.

## Metodologia

1. **Scraping**: Extrai automaticamente todas as sessões e participantes do site oficial do evento
2. **Cálculo de duração**: Determina quanto tempo cada sessão tem baseado na programação
3. **Análise de gênero**: Estima o gênero dos participantes baseado em seus primeiros nomes usando a biblioteca `gender-guesser`
4. **Agregação**: Calcula estatísticas de distribuição de tempo por gênero estimado
5. **Visualização**: Gera gráficos e tabelas para facilitar a análise

## Funcionalidades

- ✅ Extração automática da programação em tempo real
- ✅ Análise de gênero por nomes internacionais
- ✅ Visualizações interativas (gráficos de pizza e barras)
- ✅ Tabelas detalhadas por participante
- ✅ Estatísticas agregadas por gênero
- ✅ Cálculo de percentuais e comparações

## Limitações e Considerações Éticas

⚠️ **Importante**: Esta ferramenta tem várias limitações que devem ser consideradas:

1. **Gênero binário**: A análise assume categorias binárias (masculino/feminino), o que é uma simplificação problemática da realidade de gênero
2. **Detecção por nome**: Gênero não pode ser determinado por nome. Esta é apenas uma aproximação estatística
3. **Viés cultural**: A biblioteca de detecção tem viés para nomes ocidentais
4. **Identidades não-binárias**: Não captura adequadamente pessoas não-binárias, transgênero ou com identidades de gênero diversas
5. **Precisão limitada**: Especialmente para nomes internacionais e multiculturais

## Contexto de Desenvolvimento

Esta ferramenta foi desenvolvida sob uma **perspectiva crítica e contracolonial** para:
- Expor possíveis vieses estruturais em espaços acadêmicos e de conferências
- Questionar a distribuição de poder e voz em eventos
- Fornecer dados para reflexões sobre equidade
- **NÃO** para reforçar binarismos ou essencialismos de gênero

## Uso Responsável

Esta análise deve ser usada como:
- ✅ Ponto de partida para discussões sobre equidade
- ✅ Ferramenta de reflexão sobre vieses estruturais
- ✅ Indicador aproximado (não verdade absoluta)

E **NÃO** como:
- ❌ Determinação definitiva de gênero de pessoas
- ❌ Ferramenta de vigilância ou classificação de indivíduos
- ❌ Substituto para autodeclaração

## Tecnologias

- **Python 3.12+**
- **Gradio**: Interface web
- **BeautifulSoup**: Web scraping
- **Pandas**: Análise de dados
- **Gender Guesser**: Estimativa de gênero por nome
- **Plotly**: Visualizações interativas

## Como Usar

1. Clique no botão "🚀 Analisar Programação"
2. Aguarde a extração e análise dos dados
3. Explore os gráficos e tabelas gerados
4. Baixe os dados para análise adicional se desejar

## Desenvolvimento

Desenvolvido por [Veronyka](https://huggingface.co/Veronyka)

Sob perspectiva crítica, feminista e contracolonial 💜

## Licença

MIT License - Uso livre com atribuição

---

**Nota**: Esta é uma ferramenta de pesquisa e reflexão. Os resultados devem ser interpretados com cautela e consciência de suas limitações.
