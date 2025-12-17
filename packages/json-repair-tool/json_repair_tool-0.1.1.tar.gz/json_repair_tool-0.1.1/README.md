# Json Repair Tool 🛠️

**Stop your AI pipelines from crashing on bad JSON.**

`json-repair-tool` is a zero-config wrapper that combines fuzzy JSON repair with "soft coercion" for Pydantic models. It is designed specifically for handling the messy, non-deterministic output of Large Language Models (LLMs).

## The Problem

LLMs are bad at strict structured output. They often return:

- Markdown code blocks (` ```json ... `)
- Python booleans (`True` instead of `true`)
- Chatty prefixes ("Here is your data: { ... }")
- "Fuzzy" types ("$100" instead of `100.0`)

## Quick Start

```bash
pip install json-repair-tool
```
