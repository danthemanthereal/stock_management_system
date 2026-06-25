# stock_management_system

## Overview

This project is an AI-powered multi-agent investment research system designed to structure, analyze, and continuously improve investment knowledge across companies, portfolios, and markets.

The system is built around a central idea: instead of treating each analysis independently, all information is stored and refined inside a continuously evolving "AI Wiki", inspired by Andrej Karpathy’s wiki-style knowledge accumulation approach. Each company, sector, or market topic is represented as a living knowledge page that is updated over time through new data sources and LLM-based reasoning.

The platform is organized into three main workflows:

1. Watchlist Workflow – for monitoring and analyzing potential investments
2. Portfolio Workflow – for managing owned assets and tracking their aggregated intelligence
3. Analysis Workflows – for extracting structured insights from external data sources such as websites, videos, financial metrics, and news

Each workflow contributes to the shared AI Wiki, where company-level strengths and weaknesses are continuously updated, merged, and re-evaluated based on new inputs.

The system combines LLM-based information extraction, structured financial analysis, news sentiment evaluation, and rule-based filtering mechanisms to support research-driven investment decision-making.

Overall, the goal of the project is to explore how persistent memory, agent-based reasoning, and structured evaluation pipelines can improve long-term financial analysis compared to isolated LLM queries.


## Project Structure 


---

## 🧩 System Design Interpretation

### 1. Core Idea: AI Wiki Memory System

At the center of the system is the:

> **Kaparthies LLM Wiki Component**

This acts as a persistent memory layer for all companies.

It:
- stores company knowledge
- maintains strengths & weaknesses
- merges new information instead of overwriting it
- updates based on new inputs (news, financials, videos)

👉 This is the **long-term intelligence layer of the system**

---

### 2. Data Ingestion Layer

Multiple components feed information into the system:

- `get_news_component` → financial news
- `youtube_transcript_component` → video analysis
- `html_text_parser_component` → website extraction
- `stock_market_artikel_analysis_component` → article processing

👉 All external data is normalized into structured text

---

### 3. Financial Intelligence Layer

Handles quantitative analysis:

- `financial_metric_fetcher`
- `financial_metric_calculator`
- `financial_metric_analysis_component`
- `ai_financial_metricevaluation_component`

👉 Combines:
- raw financial data
- computed ratios
- LLM reasoning

---

### 4. Watchlist & Portfolio Layer

- `watchlist_component` → potential investments tracking
- `portfolio_component` → owned assets
- `bought_stock_component` → transaction-level tracking

👉 These interact directly with the AI Wiki system:
every stock automatically enriches its knowledge page

---

### 5. Analysis & Discovery Layer

- `analysis_component` → orchestrates analysis pipelines
- `find_potential_stocks_component` → stock screening engine
- `evaluation_component` → scoring + comparison logic

👉 This is where “decision intelligence” happens

---

### 6. Industry Intelligence Layer

- `industry_component`
- `industry_ai_evaluation_compoment`

👉 Aggregates companies into sectors and evaluates macro patterns

---

### 7. Prompt & Template System

- `prompt_loader_component`
- `template_metric_component`
- `templates/`

👉 Enables:
- dynamic prompting
- reusable analysis strategies
- industry-specific evaluation rules

---

## 🧠 Overall Architecture Insight

This system is best described as:

> **A modular AI-driven investment research platform with a persistent, self-improving knowledge graph (AI Wiki) at its core.**

Key architectural principles:

- Component-based modularity
- Persistent AI memory (Wiki system)
- Multi-source data fusion (news, financials, video, web)
- LLM-based reasoning pipelines
- Template-driven analysis strategies
- Separation of ingestion, analysis, and memory layers

---

## 🚀 Why this architecture is strong (important for CV / interviews)

This is not a simple “stock app”.

It demonstrates:

- AI system design thinking
- knowledge persistence (very important in LLM systems)
- multi-agent / multi-pipeline reasoning (implicit)
- real-world data integration
- scalable modular architecture
- separation of concerns

---

## 🔥 One-liner (for GitHub / CV)

> An AI-powered investment research system that builds a continuously evolving knowledge graph of companies using multi-source data ingestion, financial analysis pipelines, and LLM-based Wiki memory (Karpathy-style structured knowledge accumulation).



## Alle Api keys einflegen

-> dabei muss man aufpassen, wenn 429 häufig kommt 

-> entweder upgraden 

-> oder darauf achten, hintereinander nicht das selbe Model benutzen -> deswegen verschiedene Models 
und der Zweite Groq API Key 

## Anwendung starten 

in Stock_management_fast_api ordner :   uvicorn src.main:app --reload

## Guro Focus Fetcher 

-> dann muss man aufpassen dass man die json aus der website nimmt und einsetzen. Falls es nicht gibt dann leeres array lassen
