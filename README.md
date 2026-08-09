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


##  System Design Interpretation

### 1. Core Idea: AI Wiki Memory System

At the center of the system is the:

> **Kaparthies LLM Wiki Component**

This acts as a persistent memory layer for all companies.

It:
- stores company knowledge
- maintains strengths & weaknesses
- merges new information instead of overwriting it
- updates based on new inputs (news, financials, videos)

 This is the **long-term intelligence layer of the system**



### 2. Data Ingestion Layer

Multiple components feed information into the system:

- `get_news_component` → financial news
- `youtube_transcript_component` → video analysis
- `html_text_parser_component` → website extraction
- `stock_market_artikel_analysis_component` → article processing

 All external data is normalized into structured text



### 3. Financial Intelligence Layer

Handles quantitative analysis:

- `financial_metric_fetcher`
- `financial_metric_calculator`
- `financial_metric_analysis_component`
- `ai_financial_metricevaluation_component`

 Combines:
- raw financial data
- computed ratios
- LLM reasoning


### 4. Watchlist & Portfolio Layer

- `watchlist_component` → potential investments tracking
- `portfolio_component` → owned assets
- `bought_stock_component` → transaction-level tracking

 These interact directly with the AI Wiki system:
every stock automatically enriches its knowledge page



### 5. Analysis & Discovery Layer

- `analysis_component` → orchestrates analysis pipelines
- `find_potential_stocks_component` → stock screening engine
- `evaluation_component` → scoring + comparison logic

 This is where “decision intelligence” happens


### 6. Industry Intelligence Layer

- `industry_component`
- `industry_ai_evaluation_compoment`

 Aggregates companies into sectors and evaluates macro patterns



### 7. Prompt & Template System

- `prompt_loader_component`
- `template_metric_component`
- `templates/`

 Enables:
- dynamic prompting
- reusable analysis strategies
- industry-specific evaluation rules


##  Overall Architecture Insight

This system is best described as:

> **A modular AI-driven investment research platform with a persistent, self-improving  Wiki at its core.**

Key architectural principles:

- Component-based modularity
- Persistent AI memory (Wiki system)
- Multi-source data fusion (news, financials, video, web)
- LLM-based reasoning pipelines
- Template-driven analysis strategies
- Separation of ingestion, analysis, and memory layers


## High-Level Structure

The system is built as a modular FastAPI-based AI investment research platform.  
It is organized into multiple domain-specific components that collectively implement:

- Watchlist analysis
- Portfolio management
- Financial evaluation pipelines
- AI-generated company knowledge (Wiki system)
- News + sentiment analysis
- Stock discovery and filtering
- Multi-source data ingestion (web, YouTube, articles)

The architecture follows a **component-based design**, where each domain is encapsulated in its own module under `src/`.

## AI Wiki System (Inspired by Andrej Karpathy’s Knowledge Accumulation Principle)

At the core of the system lies a persistent AI-driven knowledge base that implements a wiki-style memory mechanism inspired by Andrej Karpathy’s idea of structured, continuously evolving information systems for LLM applications.

Instead of treating each analysis as an isolated LLM query, the system maintains a long-term, entity-centric knowledge graph where each company, sector, or market topic is represented as a living "Wiki page".

Each Wiki page contains structured sections such as:
- Strengths
- Weaknesses
- Financial insights
- News-driven updates
- Risk factors
- Historical analysis summaries

### Key Idea: Continuous Knowledge Refinement

Rather than overwriting existing information, the system follows a **merge-and-re-evaluate strategy**:

When new data is introduced (e.g. news article, YouTube transcript, financial report, or web content), the system:

1. Retrieves the existing Wiki page for the entity (if it exists)
2. Extracts relevant structured information from the new source using LLM-based parsing
3. Compares new insights with existing knowledge
4. Merges consistent information
5. Re-evaluates conflicting statements using LLM reasoning
6. Updates the Wiki page with improved, consolidated knowledge

This creates a continuously improving memory system instead of stateless analysis outputs.


### Data-to-Knowledge Pipeline

The AI Wiki system is fed by multiple data sources:

- Financial data pipelines (fundamentals and ratios)
- News articles and market updates
- YouTube video transcripts
- Web content extraction (HTML parsing)
- Analyst-generated insights from other system components

All inputs are normalized into structured text representations before being processed by the Wiki engine.


### Strength & Weakness Evolution Model

A key feature of the system is its structured “Strengths & Weaknesses” model.

Instead of free-form summaries, each company page maintains:

- A dynamically updated list of strengths
- A dynamically updated list of weaknesses

Each item is:
- attributed to a source
- re-evaluated over time
- potentially strengthened, weakened, or removed based on new evidence

This allows the system to simulate a form of **temporal reasoning over financial knowledge**.


### Outcome

The result is an evolving AI investment knowledge base where:

- each company has a living, updated intelligence profile
- insights improve over time instead of being regenerated from scratch
- conflicting information is explicitly resolved
- analysis becomes cumulative rather than isolated

This design significantly improves consistency and depth of financial reasoning across multiple analysis workflows.

## API Keys Setup

All required API keys must be configured before running the system.

FINNHUB_API_KEY: https://finnhub.io/register

GROQ_API_KEY: https://console.groq.com/keys

SECOND_GROQ_API_KEY: https://console.groq.com/keys

FMP_API_KEY: https://site.financialmodelingprep.com/developer/docs

ALPHA_VENTAGE_API_KEY: https://www.alphavantage.co/

### Important Notes

- Be aware of HTTP 429 errors (rate limiting), which may occur frequently depending on API usage.
- If rate limits are reached:
  - Upgrade the API plan if necessary, or
  - Avoid sending repeated requests to the same model in sequence
  - Distribute requests across different models to reduce rate-limit pressure

- The system supports multiple model providers, including a secondary Groq API key for load balancing and fallback usage.

This setup helps ensure system stability under high request volume and prevents interruptions caused by API throttling.

## Running the Application

To set up and start the FastAPI backend, follow these steps:

**1. Prerequisites**
Make sure you have **Python 3.11.x** installed on your system. You can verify this with:
```bash
python3.11 --version
```

Navigate to the project root with cd Stock_management_fast_api

Create a virtual environment 

```bash
python3.11 -m venv .venv
```

 Activate the Virtual Environment

Activate the environment you just created.

(Choose the command that matches your operating system.)

Operating System	Command

macOS / Linux	source .venv/bin/activate

Windows (CMD)	.venv\Scripts\activate

Windows (PowerShell)	.venv\Scripts\Activate.ps1

After activation, (.venv) should appear at the beginning of your terminal

After activating your virtual environment, run the following commands to install all required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

To start the FastAPI backend, navigate to the project root directory (Stock_management_fast_api):

Then run the following command:

```bash
uvicorn src.main:app --reload

```

## License

This project is provided for **private, academic, educational, and
non-commercial use only**.

Commercial use is **strictly prohibited** without prior written
permission from the author.

This includes, but is not limited to:
- using the project for commercial purposes,
- incorporating the code into commercial products or services,
- selling or licensing the code,
- using the project as part of a paid service.

By using this project, you agree to these terms.


