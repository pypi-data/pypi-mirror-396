![llm-web-research Logo](https://github.com/chrissoria/llm-web-research/blob/main/images/logo_small.png?raw=True)

# llm-web-research

A precision-focused LLM-powered web research tool that prioritizes **accuracy over quantity**.

## Philosophy

Unlike traditional web scraping or search tools that aim to return as much information as possible, `llm-web-research` is designed with a different goal: **reducing false positives**.

This tool is built for use cases where:
- **Accuracy matters more than completeness** - You'd rather get fewer results that are correct than many results with errors
- **Confidence thresholds are important** - The tool will return a non-answer rather than provide uncertain information
- **Verification is built-in** - Results are cross-checked and validated before being returned

## Installation

```bash
pip install llm-web-research
```

## Quick Start

```python
import llm_web_research as lwr

# Search for CEO information with confidence scoring
results = lwr.web_research(
    search_question="current CEO",
    search_input=["Apple Inc", "Microsoft", "Google"],
    api_key="your-anthropic-api-key",
    model_source="anthropic"
)

# Returns a pandas DataFrame with answer and source URL for each input
print(results[['search_input', 'answer', 'url']])
```

### Using Different Providers

```python
# Google Gemini with grounded search
results = lwr.web_research(
    search_question="founding year",
    search_input=["Tesla", "SpaceX"],
    api_key="your-google-api-key",
    model_source="google",
    user_model="gemini-2.5-flash"
)

# Perplexity for enhanced search
results = lwr.web_research(
    search_question="headquarters location",
    search_input=["OpenAI", "Anthropic"],
    api_key="your-perplexity-api-key",
    model_source="perplexity"
)
```

### Advanced Search with Tavily

For deeper searches, use Tavily's advanced search:

```python
results = lwr.web_research(
    search_question="recent acquisitions",
    search_input=["Amazon", "Meta"],
    api_key="your-anthropic-api-key",
    model_source="anthropic",
    search_depth="advanced",
    tavily_api="your-tavily-api-key"
)
```

### Date Filtering

```python
results = lwr.web_research(
    search_question="stock price",
    search_input=["NVIDIA"],
    api_key="your-api-key",
    model_source="anthropic",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## The Problem: LLM Bias Toward Finding Answers

Large Language Models have a well-documented tendency to **provide answers even when the best response is "I don't know."** This bias becomes particularly problematic in web research scenarios:

### Answer Hallucination Under Ambiguity

When faced with ambiguous queries, LLMs tend to **latch onto the most prominent entity** rather than acknowledging uncertainty. For example:

- **"Michael Johnson height"** - The model may confidently return the height of Michael Johnson the Olympic sprinter, even though there are thousands of people named Michael Johnson. Without additional context specifying *which* Michael Johnson, any answer is potentially wrong.

- **"Springfield population"** - The model might return data for Springfield, Illinois (the state capital) when the user meant Springfield, Massachusetts, or any of the 30+ other Springfields in the US.

- **"Washington County median income"** - With Washington County existing in 30+ US states, the model often defaults to the most populous or most-searched one rather than flagging the ambiguity.

### The Confidence Illusion

Traditional LLM responses often sound confident regardless of actual certainty. A model might state "Michael Johnson is 6'1" tall" with the same tone it would use for "The Earth orbits the Sun" - even though the former is answering an fundamentally ambiguous question.

## Our Solution: Funnel of Verification (FoVe)

This package attempts to correct for these biases through a novel **Funnel of Verification (FoVe)** prompting method combined with algorithmic post-processing.

### How FoVe Works

The Funnel of Verification is a multi-step pipeline that progressively narrows down and validates information:

1. **Step 1 - Broad Information Gathering** (web search): Cast a wide net to understand what the entity is and gather context. Includes an early exit if no information is found ("ANSWER NOT FOUND").

2. **Step 2 - Critical Ambiguity Check** (no web search): Analyze the gathered context with explicit instructions to flag ambiguity. The model is prompted to identify:
   - Multiple entities with the same name
   - Common names (people, places, counties, companies)
   - Conflicting information
   - Insufficient qualifying information

   If ambiguity is detected, the pipeline exits early with "RESPONSE NOT CONFIDENT" rather than guessing.

3. **Step 3 - Skeptical Verification** (web search): For queries that pass the ambiguity check, perform a verification search specifically looking for contradicting information or potential confusions.

4. **Step 4 - Structured Output** (no web search): Format the final answer as strict JSON with binary confidence scoring.

### Internal Confidence Scoring

Internally, FoVe uses **binary confidence scoring (0 or 1)** to make decisions:

- **1** = The answer has been verified, applies to a uniquely identified entity, and no contradicting information was found
- **0** = Any doubt exists, including ambiguity, conflicting sources, or uncertainty about which entity is being discussed

When confidence is 0, the answer is automatically set to "Information unclear" rather than returning a potentially wrong answer. This binary approach forces the system to make a clear decision: either we're confident enough to stand behind this answer, or we're not.

### Early Exit Strategy

A key feature of FoVe is its **early exit strategy**. Rather than pushing through ambiguous queries and returning potentially wrong answers, the pipeline exits as soon as uncertainty is detected:

```
Query: "John Smith net worth"
Step 1: Gathers information about various John Smiths
Step 2: Detects "John Smith" is a common name with multiple possible referents
→ EARLY EXIT: Returns {"answer": "Information unclear", "url": ""}
```

This is intentional - **no answer is better than a wrong answer** for precision-focused use cases.

## Key Features

- **Structured DataFrame Output**: Simply provide a question and a list of inputs, and receive a clean pandas DataFrame with answers and source URLs
- **Incremental Saving (Safety Mode)**: Save results to CSV after each query, protecting against API failures or interruptions during long-running searches
- **Funnel of Verification**: Multi-step pipeline that catches ambiguity before it becomes error
- **Early exit on ambiguity**: Returns "Information unclear" rather than guessing
- **Multi-provider support**: Works with Anthropic, Google, and Perplexity APIs
- **Citation tracking**: Source URLs included with every result
- **Verbose mode**: Debug output showing each prompt and response in the pipeline
- **Date filtering**: Constrain results to specific time periods

### Structured Output

The package returns results as a pandas DataFrame, making it easy to integrate into data analysis workflows:

```python
results = lwr.web_research(
    search_question="founding year",
    search_input=["Apple", "Microsoft", "Google", "Amazon"],
    api_key="your-api-key",
    model_source="anthropic"
)

# Results DataFrame:
#   search_input    answer              url
# 0 Apple           1976                https://...
# 1 Microsoft       1975                https://...
# 2 Google          1998                https://...
# 3 Amazon          1994                https://...
```

### Safety Mode: Incremental Saving

For large batch searches, enable safety mode to save progress after each query. This prevents data loss if the API fails mid-run:

```python
results = lwr.web_research(
    search_question="current CEO",
    search_input=large_company_list,  # hundreds of companies
    api_key="your-api-key",
    model_source="anthropic",
    safety=True,
    filename="ceo_research.csv"  # saves after each query
)
```

If the process is interrupted, you'll have all completed results saved to the CSV file.

## Use Cases

- Fact-checking claims with high accuracy requirements
- Academic research requiring verifiable sources
- Building high-quality datasets where precision matters
- Automated due diligence tasks

## Related Projects

This package is part of the `cat-llm` ecosystem. For text and image categorization tasks, see [cat-llm](https://github.com/chrissoria/cat-llm).

## License

MIT License - see LICENSE file for details.

## Author

Chris Soria (chrissoria@berkeley.edu)
