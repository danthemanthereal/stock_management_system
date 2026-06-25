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




## Alle Api keys einflegen

-> dabei muss man aufpassen, wenn 429 häufig kommt 

-> entweder upgraden 

-> oder darauf achten, hintereinander nicht das selbe Model benutzen -> deswegen verschiedene Models 
und der Zweite Groq API Key 

## Anwendung starten 

in Stock_management_fast_api ordner :   uvicorn src.main:app --reload

## Guro Focus Fetcher 

-> dann muss man aufpassen dass man die json aus der website nimmt und einsetzen. Falls es nicht gibt dann leeres array lassen
