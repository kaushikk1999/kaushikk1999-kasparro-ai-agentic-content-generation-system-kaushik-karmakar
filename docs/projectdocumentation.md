# Project Documentation

## Problem Statement
The goal is to automate content generation for e-commerce products.

## Solution Overview
An agentic system utilizing LLMs to generate FAQs, product pages, and comparisons.

## Scopes & Assumptions
- Input is structured JSON.
- Output is JSON.
- Offline mode supported.

## System Design
The system uses a Directed Acyclic Graph (DAG) approach to orchestrate a series of specialized agents.

### Agent boundaries and I/O contracts
Each agent is single-responsibility with explicit inputs and outputs; no hidden state.

*   **ParseProductAgent**
    *   Input: raw product dict
    *   Output: ProductData
    *   Writes state key: `product`

*   **ProductBGeneratorAgent**
    *   Input: none (deterministic config/seed if used)
    *   Output: ProductBData (fictional)
    *   Writes: `product_b`

*   **GenerateQuestionsAgent**
    *   Input: ProductData
    *   Output: CategorizedQuestions
    *   Writes: `questions`

*   **FaqPageAgent**
    *   Input: ProductData, CategorizedQuestions
    *   Output: FAQ draft dict
    *   Writes: `drafts.faq`

*   **ProductPageAgent**
    *   Input: ProductData
    *   Output: product page draft dict
    *   Writes: `drafts.product_page`

*   **ComparisonPageAgent**
    *   Input: ProductData, ProductBData
    *   Output: comparison draft dict
    *   Writes: `drafts.comparison_page`

*   **JsonWriterAgent**
    *   Input: drafts
    *   Output: JSON files on disk
    *   Writes: `output_paths.*`

*   **ValidatorAgent**
    *   Input: JSON outputs + schemas + parsed product facts
    *   Output: pass/fail (raises or returns report)
    *   Writes: `validation_report`

*   **DagRunner**
    *   Input: nodes + dependencies + initial state
    *   Output: final state

### Orchestration DAG and pipeline state

```text
ParseProductAgent ──> GenerateQuestionsAgent ──> FaqPageAgent ──> JsonWriterAgent
        │                    │
        │                    └──────────────> ProductPageAgent ──> JsonWriterAgent
        └──> ProductBGeneratorAgent ────────> ComparisonPageAgent ─> JsonWriterAgent
                                                        │
                                                    ValidatorAgent
```

**State Contract**
*   `product`: ProductData (from ParseProductAgent)
*   `product_b`: ProductBData (from ProductBGeneratorAgent)
*   `questions`: CategorizedQuestions (from GenerateQuestionsAgent)
*   `drafts.faq`: dict (from FaqPageAgent)
*   `drafts.product_page`: dict (from ProductPageAgent)
*   `drafts.comparison_page`: dict (from ComparisonPageAgent)
*   `output_paths.faq_json`: str (from JsonWriterAgent)
*   `output_paths.product_page_json`: str (from JsonWriterAgent)
*   `output_paths.comparison_page_json`: str (from JsonWriterAgent)
*   `validation_report`: dict/boolean (from ValidatorAgent)

**Reads/Writes**

| Node | Reads | Writes |
| :--- | :--- | :--- |
| `parse_product` | `raw_product` | `product` |
| `gen_product_b` | *(none)* | `product_b` |
| `gen_questions` | `product` | `questions` |
| `build_*` | `product` (+ others) | `*_draft` |
| `write_json` | `drafts` | `output_paths` |
| `validate_outputs` | `outputs`, `schema_paths`, `product` | `validation_report` |

### Validation gates (schemas + fact guard)

**Schema validation gate (hard fail)**: after JSON is written, validate each output (faq.json, product_page.json, comparison_page.json) against its JSON Schema (Draft 2020-12). If any schema validation fails, abort the pipeline with a non-zero exit. (This matches how your verify flow is structured.)

**Business-rule gate (hard fail)**: enforce the assignment constraints as validations (e.g., minimum FAQ Q&As, question count/categories, Product B marked fictional, outputs are machine-readable JSON). These checks run after generation and before final success.

**Fact guard gate (hard fail)**: verify generated outputs contain only facts present in the provided GlowBoost dataset, using an allowlist derived from the internal ProductData fields (e.g., ingredients/benefits lists from the parsed input). Any unexpected product facts → fail validation. (No external facts permitted.)
