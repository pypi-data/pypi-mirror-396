# Baseline web research - simple prompt without ambiguity detection
# FOR INTERNAL TESTING ONLY - not exported in package

def baseline_web_research(
    search_question,
    search_input,
    api_key,
    answer_format="concise",
    additional_instructions="",
    user_model="claude-sonnet-4-20250514",
    creativity=None,
    safety=False,
    filename="baseline_results.csv",
    save_directory=None,
    model_source="anthropic",
    start_date=None,
    end_date=None,
    max_retries=6,
    time_delay=5
):
    """
    Baseline web research - simple prompt without ambiguity detection.

    FOR INTERNAL TESTING ONLY. Use this to compare against web_research()
    and precise_web_research() to measure the impact of ambiguity detection.

    This function:
    - Uses a simple, straightforward prompt
    - Does NOT check for ambiguity
    - Does NOT filter out uncertain responses
    - Returns whatever answer the model provides

    Args:
        search_question (str): The question to answer for each search item.
        search_input (list or pd.Series): List of items to search for.
        api_key (str): API key for the model provider.
        answer_format (str): Expected format of the answer. Default "concise".
        additional_instructions (str): Extra instructions for the search.
        user_model (str): Model to use. Default "claude-sonnet-4-20250514".
        creativity (float): Temperature setting. None uses model default.
        safety (bool): If True, saves progress after each item.
        filename (str): Output filename. Default "baseline_results.csv".
        save_directory (str): Directory to save results. None uses current dir.
        model_source (str): Provider - "anthropic", "google", or "perplexity".
        start_date (str): Filter results after this date (YYYY-MM-DD).
        end_date (str): Filter results before this date (YYYY-MM-DD).
        max_retries (int): Retry count for rate limit errors. Default 6.
        time_delay (int): Seconds between requests. Default 5.

    Returns:
        pd.DataFrame: Results with columns:
            - search_input: Original search item
            - answer: The model's answer (no filtering)
            - url: Source URL for the answer
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

    if not _validate_date(start_date):
        raise ValueError(f"start_date must be in YYYY-MM-DD format, got: {start_date}")
    if not _validate_date(end_date):
        raise ValueError(f"end_date must be in YYYY-MM-DD format, got: {end_date}")

    model_source = model_source.lower()

    if model_source == "perplexity" and start_date is not None:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%m/%d/%Y")
    if model_source == "perplexity" and end_date is not None:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%m/%d/%Y")

    if model_source == "google" and user_model == "claude-sonnet-4-20250514":
        user_model = "gemini-2.5-flash"
    if model_source == "perplexity" and user_model == "claude-sonnet-4-20250514":
        user_model = "sonar"

    results = []

    for idx, item in enumerate(tqdm(search_input, desc="Baseline searching")):
        if idx > 0:
            time.sleep(time_delay)

        if pd.isna(item):
            results.append({
                "search_input": item,
                "answer": "Skipped NaN input",
                "url": ""
            })
            continue

        # Simple straightforward prompt - no ambiguity detection
        prompt = f"""Find information about {item}'s {search_question}.

<answer_format_required>{answer_format}</answer_format_required>

<rules>
- Provide ONLY the direct answer with no filler text
- Do NOT say "The answer is...", "Based on...", "The CEO of X is...", etc.
- Just provide the answer itself (e.g., "Satya Nadella" not "The CEO of Microsoft is Satya Nadella")
- Your answer MUST follow the exact format specified in <answer_format_required>
  - If format is "name" → just the name (e.g., "Satya Nadella")
  - If format is "month, year" → use that format (e.g., "January, 2014")
  - If format is "name, date" → use that format (e.g., "Satya Nadella, February 4, 2014")
  - If format is "year" → just the year (e.g., "1976")
{additional_instructions}
</rules>

Return your response as JSON:
{{
    "answer": "Answer in the EXACT format specified above",
    "url": "Source URL"
}}"""

        # Add date filtering
        if start_date is not None and end_date is not None:
            prompt += f"\n\nFocus on information from between {start_date} and {end_date}."
        elif start_date is not None:
            prompt += f"\n\nFocus on information from after {start_date}."
        elif end_date is not None:
            prompt += f"\n\nFocus on information from before {end_date}."

        reply = None
        urls = []

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

        # Parse response - NO post-processing, just extract answer
        if reply is not None:
            extracted_json = regex.findall(r'\{(?:[^{}]|(?R))*\}', reply, regex.DOTALL)
            if extracted_json:
                try:
                    parsed = json.loads(extracted_json[0])
                    # Inject URL if not in JSON
                    if (not parsed.get("url") or parsed.get("url") == "") and urls:
                        parsed["url"] = urls[0]

                    results.append({
                        "search_input": item,
                        "answer": parsed.get("answer", reply),  # Fall back to raw reply
                        "url": parsed.get("url", "")
                    })
                except json.JSONDecodeError:
                    # If JSON parsing fails, use raw reply as answer
                    results.append({
                        "search_input": item,
                        "answer": reply[:500],  # Truncate if too long
                        "url": urls[0] if urls else ""
                    })
            else:
                # No JSON found, use raw reply
                results.append({
                    "search_input": item,
                    "answer": reply[:500],
                    "url": urls[0] if urls else ""
                })
        else:
            results.append({
                "search_input": item,
                "answer": "Error: No response",
                "url": ""
            })

        # Safety save
        if safety:
            temp_df = pd.DataFrame(results)
            save_path = os.path.join(save_directory or os.getcwd(), filename)
            temp_df.to_csv(save_path, index=False)

    df = pd.DataFrame(results)

    if save_directory is not None:
        save_path = os.path.join(save_directory, filename)
        df.to_csv(save_path, index=False)

    return df
