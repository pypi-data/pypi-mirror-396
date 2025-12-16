# Centralized prompts for Funnel of Verification (FoVe)
# All three providers (Anthropic, Google, Perplexity) use these same prompts


def get_step1_prompt(item, search_question):
    """
    Step 1: Broad Information Gathering (web search enabled)
    Cast a wide net to understand what the entity is and gather context.
    """
    return f"""<role>You are a research assistant specializing in finding current, factual information.</role>

<task>Gather comprehensive background information about {item} that will help answer a question about their {search_question}</task>

<rules>
- Search for the most current and authoritative information available
- Gather context that will help identify the correct entity (there may be multiple entities with this name)
- Note any potential ambiguities (e.g., multiple people/places/companies with the same name)
- Include relevant identifying details (dates, locations, affiliations) to disambiguate
</rules>

<format>
Provide a comprehensive summary of the information found.
If no information can be found, respond with "ANSWER NOT FOUND" and explain why.
</format>"""


def get_step2_prompt(item, search_question, item_context, additional_instructions):
    """
    Step 2: Critical Ambiguity Check (no web search)
    Analyze the gathered context with explicit instructions to flag ambiguity.
    """
    return f"""<role>You are a research assistant that extracts precise answers from provided information. You are cautious and flag any ambiguity.</role>

<context>Here is background information about {item}:
{item_context}</context>

<task>Based ONLY on the information above, extract a concise answer to: What is {item}'s {search_question}?</task>

<rules>
- Use only the information provided in the context above
- Provide a direct, concise answer ONLY if there is ONE clear, unambiguous answer
- If the answer is not clearly stated in the context, say "Information not found in context"
- Do not search for additional information
{additional_instructions}
</rules>

<CRITICAL_AMBIGUITY_CHECK>
You MUST respond with "RESPONSE NOT CONFIDENT" if ANY of the following are true:
1. The context mentions MULTIPLE entities with the same or similar name (e.g., "Springfield" exists in many US states, "Michael Johnson" could be many people, "Washington County" exists in 30+ states)
2. The context provides CONFLICTING information or different values for the same attribute
3. The search input "{item}" is a COMMON NAME that could refer to many different entities:
   - Common person names: John Smith, Michael Johnson, David Williams, etc.
   - Common place names: Springfield, Franklin, Washington, Clinton, Madison, etc.
   - Common county names: Washington County, Jefferson County, Franklin County, etc.
   - Generic company/org names that exist in multiple locations or industries
4. The context expresses ANY uncertainty about which specific entity is being discussed
5. The context discusses multiple possible answers without clearly identifying one as correct
6. You cannot be 100% certain the answer applies to ONE specific, uniquely identified entity
7. The entity lacks sufficient qualifying information (e.g., "Springfield" without a state, "Washington County" without a state)

When in doubt, ALWAYS respond with "RESPONSE NOT CONFIDENT" - it is better to be cautious than wrong.
</CRITICAL_AMBIGUITY_CHECK>

<format>
If confident: Provide a single, concise statement answering the question.
If ANY ambiguity exists: Respond with "RESPONSE NOT CONFIDENT" followed by a brief explanation of why (e.g., "multiple entities with this name", "name exists in multiple states", "conflicting information", etc.)
</format>"""


def get_step3_prompt(item, search_question, initial_reply, answer_format, additional_instructions):
    """
    Step 3: Skeptical Verification (web search enabled)
    For queries that pass the ambiguity check, perform a verification search.
    """
    return f"""<role>You are a fact-checker who verifies information and provides a final answer with source.</role>

<previous_answer>For the question "What is {item}'s {search_question}?", the proposed answer is:
{initial_reply}</previous_answer>

<task>Verify whether this answer is correct and provide the final answer with a source URL.</task>

<answer_format_required>{answer_format}</answer_format_required>

<rules>
- Search to confirm or refute the proposed answer
- Look for potential confusions: Are there other entities with similar names that could be confused with {item}?
- Check if the answer might be outdated or referring to a different time period
- Look for contradicting information from authoritative sources
- If you find evidence the answer is wrong, use the corrected information
- If the answer is confirmed, use it
- CRITICAL: Provide ONLY the direct answer with no filler text
- Do NOT say "The answer is...", "Based on...", "The CEO of X is...", etc.
- Just provide the answer itself (e.g., "Satya Nadella" not "The CEO of Microsoft is Satya Nadella")
- Include the URL of the most authoritative source that confirms your answer
- CRITICAL: Your answer MUST follow the exact format specified in <answer_format_required>
  - If format is "name" → just the name (e.g., "Satya Nadella")
  - If format is "month, year" → use that format (e.g., "January, 2014")
  - If format is "name, date" → use that format (e.g., "Satya Nadella, February 4, 2014")
  - If format is "year" → just the year (e.g., "1976")
- Determine if the correct answer involves MULTIPLE entities (e.g., Apple has multiple co-founders: Steve Jobs, Steve Wozniak, Ronald Wayne)
{additional_instructions}
</rules>

<format>
Return your response as valid JSON with this exact structure:
{{
    "answer": "Answer in the EXACT format specified in <answer_format_required>, or 'Information not found'",
    "url": "URL of the source that confirms the answer",
    "confidence": "1 if confident and verified, 0 if ANY doubt or uncertainty",
    "multiple_entities": "1 if the correct answer involves multiple entities/people/values (e.g., multiple founders, multiple locations), 0 if single answer"
}}

IMPORTANT: confidence must be exactly 0 or 1 (binary). Use 1 ONLY if certain. Use 0 for any doubt.
IMPORTANT: multiple_entities should be 1 if the question legitimately has multiple correct answers (e.g., "founders of Apple" = multiple people), not for ambiguity.
</format>"""


def get_step4_prompt(verification_result, answer_format):
    """
    Step 4: Structured Output (no web search)
    Format the final answer as strict JSON.
    """
    return f"""Based on the following verification result, extract the final answer, source URL, confidence, and whether multiple entities are involved.

Verification result:
{verification_result}

Extract:
1. answer: The direct answer (no filler text) in the format: {answer_format}
2. url: The most authoritative source URL
3. confidence: "1" if verified and certain, "0" if any doubt
4. multiple_entities: "1" if the answer involves multiple entities (e.g., multiple founders, multiple locations), "0" if single answer"""


# JSON schema for Step 4 (used by Anthropic and Perplexity)
STEP4_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "url": {"type": "string"},
        "confidence": {"type": "string", "enum": ["0", "1"]},
        "multiple_entities": {"type": "string", "enum": ["0", "1"]}
    },
    "required": ["answer", "url", "confidence", "multiple_entities"]
}

# Early exit JSON responses (only answer and url - internal fields dropped)
EARLY_EXIT_NOT_FOUND = '{"answer": "Information not found", "url": ""}'
EARLY_EXIT_NOT_CONFIDENT = '{"answer": "Information unclear", "url": ""}'
EARLY_EXIT_ERROR = '{"answer": "Information unclear", "url": ""}'
