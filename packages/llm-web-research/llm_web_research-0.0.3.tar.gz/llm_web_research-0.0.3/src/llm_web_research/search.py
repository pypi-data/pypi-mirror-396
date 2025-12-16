# Web research function for LLM-powered web search
# Single-step search with ambiguity detection and post-processing

def web_research(
    search_question,
    search_input,
    api_key,
    answer_format="concise",
    additional_instructions="",
    user_model="claude-sonnet-4-20250514",
    creativity=None,
    safety=False,
    filename="web_research_results.csv",
    save_directory=None,
    model_source="anthropic",
    start_date=None,
    end_date=None,
    max_retries=6,
    time_delay=5
):
    """
    Perform web research using LLMs with ambiguity detection.

    This is a faster single-step search that still includes ambiguity detection
    and confidence scoring. For maximum accuracy on ambiguous queries, use
    precise_web_research() instead.

    The function will return "Information unclear" for:
    - Ambiguous queries (common names, multiple entities with same name)
    - Low confidence answers (confidence = 0)
    - Multiple possible entities detected

    Args:
        search_question (str): The question to answer for each search item.
            Example: "current CEO" or "founding date"
        search_input (list or pd.Series): List of items to search for.
            Example: ["Apple Inc", "Microsoft", "Google"]
        api_key (str): API key for the model provider.
        answer_format (str): Expected format of the answer. Default "concise".
        additional_instructions (str): Extra instructions for the search.
        user_model (str): Model to use. Default "claude-sonnet-4-20250514".
        creativity (float): Temperature setting. None uses model default.
        safety (bool): If True, saves progress after each item.
        filename (str): Output filename. Default "web_research_results.csv".
        save_directory (str): Directory to save results. None uses current dir.
        model_source (str): Provider - "anthropic", "google", or "perplexity".
        start_date (str): Filter results after this date (YYYY-MM-DD).
        end_date (str): Filter results before this date (YYYY-MM-DD).
        max_retries (int): Retry count for rate limit errors. Default 6.
        time_delay (int): Seconds between requests. Default 5.

    Returns:
        pd.DataFrame: Results with columns:
            - search_input: Original search item
            - answer: Extracted answer or "Information unclear"/"Information not found"
            - url: Source URL for the answer

    Example:
        >>> import llm_web_research as lwr
        >>> results = lwr.web_research(
        ...     search_question="current CEO",
        ...     search_input=["Apple Inc", "Microsoft"],
        ...     api_key="your-api-key",
        ...     model_source="anthropic"
        ... )
    """
    import os
    import re
    import json
    import pandas as pd
    import regex
    from tqdm import tqdm
    import time
    from datetime import datetime

    def _validate_date(date_str):
        """Validates YYYY-MM-DD format"""
        if date_str is None:
            return True
        if not isinstance(date_str, str):
            return False
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date_str):
            return False
        try:
            year, month, day = date_str.split('-')
            datetime(int(year), int(month), int(day))
            return True
        except (ValueError, OverflowError):
            return False

    def _postprocess_result(parsed):
        """
        Post-process to ensure consistency.
        If confidence is 0 OR multiple_entities is 1, set answer to "Information unclear".
        """
        confidence = parsed.get("confidence")
        multiple = parsed.get("multiple_entities")

        # Check confidence (could be string "0" or int 0)
        if confidence == "0" or confidence == 0:
            parsed["answer"] = "Information unclear"

        # Check multiple_entities
        if multiple == "1" or multiple == 1:
            parsed["answer"] = "Information unclear"

        return parsed

    if not _validate_date(start_date):
        raise ValueError(f"start_date must be in YYYY-MM-DD format, got: {start_date}")
    if not _validate_date(end_date):
        raise ValueError(f"end_date must be in YYYY-MM-DD format, got: {end_date}")

    model_source = model_source.lower()

    # Convert dates for Perplexity format
    if model_source == "perplexity" and start_date is not None:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%m/%d/%Y")
    if model_source == "perplexity" and end_date is not None:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%m/%d/%Y")

    # Set default models for other providers
    if model_source == "google" and user_model == "claude-sonnet-4-20250514":
        user_model = "gemini-2.5-flash"
    if model_source == "perplexity" and user_model == "claude-sonnet-4-20250514":
        user_model = "sonar"

    results = []

    for idx, item in enumerate(tqdm(search_input, desc="Searching")):
        if idx > 0:
            time.sleep(time_delay)

        if pd.isna(item):
            results.append({
                "search_input": item,
                "answer": "Skipped NaN input",
                "url": ""
            })
            continue

        # Single consolidated prompt with ambiguity detection
        prompt = f"""<role>You are a research assistant specializing in finding current, factual information. You are cautious and flag any ambiguity.</role>

<task>Find information about {item}'s {search_question}</task>

<answer_format_required>{answer_format}</answer_format_required>

<rules>
- Search for the most current and authoritative information available
- Prioritize official sources when possible
- Include the URL of your most authoritative source
- CRITICAL: Provide ONLY the direct answer with no filler text
- Do NOT say "The answer is...", "Based on...", "The CEO of X is...", etc.
- Just provide the answer itself (e.g., "Satya Nadella" not "The CEO of Microsoft is Satya Nadella")
- CRITICAL: Your answer MUST follow the exact format specified in <answer_format_required>
  - If format is "name" → just the name (e.g., "Satya Nadella")
  - If format is "month, year" → use that format (e.g., "January, 2014")
  - If format is "name, date" → use that format (e.g., "Satya Nadella, February 4, 2014")
  - If format is "year" → just the year (e.g., "1976")
{additional_instructions}
</rules>

<CRITICAL_AMBIGUITY_CHECK>
You MUST set confidence to 0 if ANY of the following are true:
1. The search input "{item}" could refer to MULTIPLE different entities (e.g., "Michael Johnson" could be many people, "Springfield" exists in many states, "Washington County" exists in 30+ states)
2. You found CONFLICTING information from different sources
3. The search input is a COMMON NAME without sufficient qualifying information:
   - Common person names: John Smith, Michael Johnson, David Williams, etc.
   - Common place names: Springfield, Franklin, Washington, Clinton, etc.
   - Common county names: Washington County, Jefferson County, Franklin County, etc.
4. You cannot be 100% certain which specific entity is being discussed
5. The information found might apply to a different entity with the same name

When in doubt, set confidence to 0 - it is better to be cautious than wrong.
</CRITICAL_AMBIGUITY_CHECK>

<format>
Return your response as valid JSON with this exact structure:
{{
    "answer": "Answer in the EXACT format specified in <answer_format_required>, or 'Information not found'",
    "url": "URL of the most authoritative source",
    "confidence": "1 if confident and unambiguous, 0 if ANY doubt or ambiguity",
    "multiple_entities": "1 if the answer involves multiple entities or the query is ambiguous, 0 otherwise"
}}

IMPORTANT:
- confidence must be exactly 0 or 1
- If information is not found, use "Information not found" for answer
- If query is ambiguous, set confidence to 0
- Answer must match the exact format specified (e.g., just "Satya Nadella" not "The CEO is Satya Nadella")
</format>"""

        # Add date filtering to prompt
        if start_date is not None and end_date is not None:
            prompt = prompt.replace("<rules>", f"<rules>\n- Focus on webpages published between {start_date} and {end_date}")
        elif start_date is not None:
            prompt = prompt.replace("<rules>", f"<rules>\n- Focus on webpages published after {start_date}")
        elif end_date is not None:
            prompt = prompt.replace("<rules>", f"<rules>\n- Focus on webpages published before {end_date}")

        reply = None
        urls = []

        # Execute search based on provider
        if model_source == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            attempt = 0
            while attempt < max_retries:
                try:
                    message = client.messages.create(
                        model=user_model,
                        max_tokens=1024,
                        messages=[{"role": "user", "content": prompt}],
                        **({"temperature": creativity} if creativity is not None else {}),
                        tools=[{
                            "type": "web_search_20250305",
                            "name": "web_search"
                        }]
                    )
                    reply = " ".join(
                        block.text
                        for block in message.content
                        if getattr(block, "type", "") == "text"
                    ).strip()

                    # Extract URLs
                    urls = [
                        url_item["url"]
                        for block in message.content
                        if getattr(block, "type", "") == "web_search_tool_result"
                        for url_item in (getattr(block, "content", []) or [])
                        if isinstance(url_item, dict) and url_item.get("type") == "web_search_result" and "url" in url_item
                    ]
                    seen = set()
                    urls = [u for u in urls if not (u in seen or seen.add(u))]
                    break

                except anthropic.RateLimitError:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    attempt += 1
                except Exception as e:
                    reply = None
                    break
            else:
                reply = None

        elif model_source == "google":
            import requests
            url_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{user_model}:generateContent"
            try:
                headers = {
                    "x-goog-api-key": api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "tools": [{"google_search": {}}],
                    **({"generationConfig": {"temperature": creativity}} if creativity is not None else {})
                }

                response = requests.post(url_endpoint, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

                # Extract URLs from grounding metadata
                for cand in result.get("candidates", []):
                    rendered_html = (
                        cand.get("groundingMetadata", {})
                        .get("searchEntryPoint", {})
                        .get("renderedContent", "")
                    )
                    if rendered_html:
                        found = re.findall(
                            r'<a[^>]*class=["\']chip["\'][^>]*href=["\']([^"\']+)["\']',
                            rendered_html,
                            flags=re.IGNORECASE
                        )
                        urls.extend(found)

                seen = set()
                urls = [u for u in urls if not (u in seen or seen.add(u))]

                if "candidates" in result and result["candidates"]:
                    reply = result["candidates"][0]["content"]["parts"][0]["text"]

            except Exception as e:
                reply = None

        elif model_source == "perplexity":
            from perplexity import Perplexity
            client = Perplexity(api_key=api_key)
            try:
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=user_model,
                    max_tokens=1024,
                    **({"temperature": creativity} if creativity is not None else {}),
                    web_search_options={"search_context_size": "medium"},
                    **({"search_after_date_filter": start_date} if start_date else {}),
                    **({"search_before_date_filter": end_date} if end_date else {}),
                )

                reply = response.choices[0].message.content
                urls = list(response.citations) if hasattr(response, 'citations') else []
                seen = set()
                urls = [u for u in urls if not (u in seen or seen.add(u))]

            except Exception as e:
                reply = None

        else:
            raise ValueError(
                f"Unknown model_source: {model_source}. "
                "Supported: 'anthropic', 'google', 'perplexity'"
            )

        # Parse response and apply post-processing
        if reply is not None:
            # Extract JSON from response
            extracted_json = regex.findall(r'\{(?:[^{}]|(?R))*\}', reply, regex.DOTALL)
            if extracted_json:
                try:
                    parsed = json.loads(extracted_json[0])
                    parsed = _postprocess_result(parsed)

                    # Inject URL from search results if not in JSON
                    if (not parsed.get("url") or parsed.get("url") == "") and urls:
                        parsed["url"] = urls[0]

                    results.append({
                        "search_input": item,
                        "answer": parsed.get("answer", "Information unclear"),
                        "url": parsed.get("url", "")
                    })
                except json.JSONDecodeError:
                    results.append({
                        "search_input": item,
                        "answer": "Information unclear",
                        "url": urls[0] if urls else ""
                    })
            else:
                results.append({
                    "search_input": item,
                    "answer": "Information unclear",
                    "url": urls[0] if urls else ""
                })
        else:
            results.append({
                "search_input": item,
                "answer": "Information unclear",
                "url": ""
            })

        # Safety save after each item
        if safety:
            temp_df = pd.DataFrame(results)
            save_path = os.path.join(save_directory or os.getcwd(), filename)
            temp_df.to_csv(save_path, index=False)

    # Create final DataFrame
    df = pd.DataFrame(results)

    # Save final results if directory specified
    if save_directory is not None:
        save_path = os.path.join(save_directory, filename)
        df.to_csv(save_path, index=False)

    return df
