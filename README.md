# Kasparro AI Agentic Content Generation System

An agentic pipeline utilizing LLM-based agents to autonomously generate structured e-commerce content (Product Pages, FAQs, Comparisons) from raw product datasets. This system adheres to strict constraints: **Dataset-Only** (no external facts) and **Modular Architecture**.

![Status](https://img.shields.io/badge/Status-Verified-success)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)

## Live Demo (Streamlit)
Deployed Streamlit App: **https://jvqjteycvgtb6sx5agj5oh.streamlit.app/**

## Features
- **Agentic Orchestration:** Directed Acyclic Graph (DAG) managing specialized agents.
- **Dataset-Only Guarantee:** Strict "Fact Guard" ensures no hallucinations or external knowledge leakage.
- **Structured Output:** Generates strictly typed JSON artifacts (`product_page.json`, `faq.json`, `comparison_page.json`).
- **Streamlit Processor:** Built-in dashboard for viewing and validating generated content.

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd kasparro-ai-agentic-content-generation-system-kaushik-karmakar
Create Virtual Environment

bash
Copy code
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install Dependencies

bash
Copy code
pip install -r requirements.txt
Usage
1. Run the Pipeline (CLI)
Generate content artifacts from the input data.

bash
Copy code
python main.py
Outputs will be generated in outputs/.

2. Run the Viewer (Streamlit)
Launch the interactive dashboard to view content and validate outputs.

bash
Copy code
streamlit run app.py
Access locally at http://localhost:8501.

Deployed Streamlit App: https://jvqjteycvgtb6sx5agj5oh.streamlit.app/

Verification
This repository includes a comprehensive self-verification suite to prove compliance with all project constraints.

Run the Master Verification Script:

bash
Copy code
python verify.py
This will verify:

Repository Naming & Documentation

Pipeline Execution

Schema Compliance (Strict JSON Schema)

Business Constraints (Counts, Fictionality)

"No New Facts" Policy (Fact Guard)

Modularity

Architecture
src/agents/: Individual agent modules (Single Responsibility).

src/orchestrator/: DAG runner logic.

src/schemas/: JSON schemas for validation.

data/: Input product datasets.

outputs/: Generated results.

Author: Kaushik Karmakar
License: MIT

makefile
Copy code
::contentReference[oaicite:1]{index=1}
