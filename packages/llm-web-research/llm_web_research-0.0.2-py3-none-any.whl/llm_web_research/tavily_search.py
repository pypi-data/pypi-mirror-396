# Tavily-only web search function
# Uses Tavily API for deep web searches, then optionally processes with an LLM

def tavily_search(
    search_question,
    search_input,
    tavily_api,
    llm_api_key=None,
    user_model="claude-sonnet-4-20250514",
    model_source="anthropic",
    answer_format="concise",
    creativity=None,
    max_results=15,
    search_depth="advanced",
    start_date=None,
    end_date=None,
    safety=False,
    filename="tavily_results.csv",
    save_directory=None,
    output_urls=True,
    time_delay=2
):
    """
    Perform web research using Tavily's search API.

    This function uses Tavily for deep web searches and optionally processes
    results with an LLM for structured answers.

    Args:
        search_question (str): The question to answer for each search item.
            Example: "current CEO" or "founding date"
        search_input (list or pd.Series): List of items to search for.
            Example: ["Apple Inc", "Microsoft", "Google"]
        tavily_api (str): Tavily API key. Get one at https://app.tavily.com/home
        llm_api_key (str): Optional API key for LLM processing. If None, returns
            raw Tavily results without LLM refinement.
        user_model (str): Model to use for LLM processing. Default "claude-sonnet-4-20250514".
        model_source (str): LLM provider - "anthropic" or "google". Default "anthropic".
        answer_format (str): How to format answers. Default "concise".
        creativity (float): Temperature setting for LLM. None uses model default.
        max_results (int): Maximum number of Tavily results per query. Default 15.
        search_depth (str): Tavily search depth - "basic" or "advanced". Default "advanced".
        start_date (str): Filter results after this date (YYYY-MM-DD).
        end_date (str): Filter results before this date (YYYY-MM-DD).
        safety (bool): If True, saves progress after each item.
        filename (str): Output filename. Default "tavily_results.csv".
        save_directory (str): Directory to save results. None uses current dir.
        output_urls (bool): Include source URLs in output. Default True.
        time_delay (int): Seconds between requests. Default 2.

    Returns:
        pd.DataFrame: Results with columns:
            - search_input: Original search item
            - answer: Extracted answer (if LLM used) or Tavily's answer
            - confidence: Confidence score 0-5 (if LLM used)
            - url_0, url_1, ...: Source URLs (if output_urls=True)

    Example:
        >>> import llm_web_research as lwr
        >>> results = lwr.tavily_search(
        ...     search_question="current CEO",
        ...     search_input=["Apple Inc", "Microsoft"],
        ...     tavily_api="your-tavily-api-key",
        ...     llm_api_key="your-anthropic-api-key"
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

    if not _validate_date(start_date):
        raise ValueError(f"start_date must be in YYYY-MM-DD format, got: {start_date}")

    if not _validate_date(end_date):
        raise ValueError(f"end_date must be in YYYY-MM-DD format, got: {end_date}")

    # Import Tavily
    try:
        from tavily import TavilyClient
    except ImportError:
        raise ImportError("Tavily not installed. Run: pip install tavily-python")

    tavily_client = TavilyClient(tavily_api)

    model_source = model_source.lower() if model_source else None

    answers = []
    extracted_jsons = []
    extracted_urls = []

    for idx, item in enumerate(tqdm(search_input, desc="Searching with Tavily")):
        if idx > 0:
            time.sleep(time_delay)

        if pd.isna(item):
            answers.append("Skipped NaN input")
            extracted_urls.append([])
            extracted_jsons.append(json.dumps({"answer": "Skipped NaN input"}))
            continue

        # Tavily search
        try:
            tavily_response = tavily_client.search(
                query=f"{item}'s {search_question}",
                include_answer=True,
                max_results=max_results,
                search_depth=search_depth,
                **({"start_date": start_date} if start_date is not None else {}),
                **({"end_date": end_date} if end_date is not None else {})
            )

            # Extract URLs
            urls = [
                result['url']
                for result in tavily_response.get('results', [])
                if 'url' in result
            ]
            seen = set()
            urls = [u for u in urls if not (u in seen or seen.add(u))]
            extracted_urls.append(urls)

            # Get Tavily's answer
            tavily_answer = tavily_response.get('answer', 'No answer found')

        except Exception as e:
            error_msg = str(e).lower()
            if "unauthorized" in error_msg or "403" in error_msg or "401" in error_msg or "api_key" in error_msg:
                raise ValueError("Invalid or missing Tavily API key. Get one at https://app.tavily.com/home") from e
            else:
                answers.append(f"Error: {e}")
                extracted_urls.append([])
                extracted_jsons.append(json.dumps({"answer": f"Error: {e}"}))
                continue

        # If no LLM key provided, use Tavily's answer directly
        if llm_api_key is None:
            answers.append(tavily_answer)
            extracted_jsons.append(json.dumps({
                "answer": tavily_answer,
                "confidence": "N/A - no LLM processing"
            }))
            continue

        # Process with LLM for structured output
        llm_prompt = f"""Based on the following search results about {item}'s {search_question}, provide your answer in this EXACT JSON format and {answer_format}:
If you can't find the information, respond with 'Information not found'.
{{"answer": "your answer here or 'Information not found'",
"second_best_answer": "your second best answer here or 'Information not found'",
"confidence": "confidence in response 0-5 or 'Information not found'"}}

Tavily's answer: {tavily_answer}

Search results:
{chr(10).join([f"- {r.get('title', '')}: {r.get('content', '')}" for r in tavily_response.get('results', [])[:5]])}

Return ONLY the JSON object, no other text."""

        reply = None

        if model_source == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=llm_api_key)

            try:
                message = client.messages.create(
                    model=user_model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": llm_prompt}],
                    **({"temperature": creativity} if creativity is not None else {})
                )

                reply = " ".join(
                    block.text
                    for block in message.content
                    if getattr(block, "type", "") == "text"
                ).strip()

            except Exception as e:
                answers.append(f"LLM Error: {e}")
                extracted_jsons.append(json.dumps({"answer": tavily_answer, "confidence": "LLM error"}))
                continue

        elif model_source == "google":
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{user_model}:generateContent"

            try:
                headers = {
                    "x-goog-api-key": llm_api_key,
                    "Content-Type": "application/json"
                }

                payload = {
                    "contents": [{"parts": [{"text": llm_prompt}]}],
                    **({"generationConfig": {"temperature": creativity}} if creativity is not None else {})
                }

                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()

                if "candidates" in result and result["candidates"]:
                    reply = result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    reply = None

            except Exception as e:
                answers.append(f"LLM Error: {e}")
                extracted_jsons.append(json.dumps({"answer": tavily_answer, "confidence": "LLM error"}))
                continue

        else:
            raise ValueError(f"Unknown model_source: {model_source}. Use 'anthropic' or 'google'.")

        # Parse LLM response
        if reply is not None:
            extracted_json = regex.findall(r'\{(?:[^{}]|(?R))*\}', reply, regex.DOTALL)
            if extracted_json:
                raw_json = extracted_json[0].strip()
                try:
                    parsed_obj = json.loads(raw_json)
                    answers.append(parsed_obj.get('answer', reply))
                    extracted_jsons.append(json.dumps(parsed_obj))
                except json.JSONDecodeError:
                    answers.append(reply)
                    extracted_jsons.append(raw_json)
            else:
                answers.append(reply)
                extracted_jsons.append(json.dumps({"answer": reply}))
        else:
            answers.append(tavily_answer)
            extracted_jsons.append(json.dumps({"answer": tavily_answer, "confidence": "LLM returned None"}))

        # Safety save
        if safety:
            _save_progress(search_input[:idx+1], answers, extracted_jsons, extracted_urls,
                          save_directory, filename)

    # Build final DataFrame
    normalized_data_list = []
    for json_str in extracted_jsons:
        try:
            parsed_obj = json.loads(json_str)
            normalized_data_list.append(pd.json_normalize(parsed_obj))
        except json.JSONDecodeError:
            normalized_data_list.append(pd.DataFrame({"answer": ["e"]}))
    normalized_data = pd.concat(normalized_data_list, ignore_index=True)

    df_urls = pd.DataFrame(extracted_urls).add_prefix("url_")

    result_df = pd.DataFrame({
        'search_input': (
            search_input.reset_index(drop=True) if isinstance(search_input, (pd.DataFrame, pd.Series))
            else pd.Series(search_input)
        ),
    })
    result_df = pd.concat([result_df, normalized_data], axis=1)
    result_df = pd.concat([result_df, df_urls], axis=1)

    # Clean up columns
    result_df = result_df.drop(columns=["second_best_answer"], errors='ignore')

    if not output_urls:
        result_df = result_df.drop(columns=[col for col in result_df.columns if col.startswith("url_")])

    if save_directory is not None:
        save_path = os.path.join(save_directory, filename)
        result_df.to_csv(save_path, index=False)

    return result_df


def _save_progress(search_input, answers, extracted_jsons, extracted_urls, save_directory, filename):
    """Helper function for safety saves."""
    import os
    import json
    import pandas as pd

    normalized_data_list = []
    for json_str in extracted_jsons:
        try:
            parsed_obj = json.loads(json_str)
            normalized_data_list.append(pd.json_normalize(parsed_obj))
        except json.JSONDecodeError:
            normalized_data_list.append(pd.DataFrame({"answer": ["e"]}))
    normalized_data = pd.concat(normalized_data_list, ignore_index=True)

    temp_urls = pd.DataFrame(extracted_urls).add_prefix("url_")

    temp_df = pd.DataFrame({'search_input': search_input})
    temp_df = pd.concat([temp_df, normalized_data], axis=1)
    temp_df = pd.concat([temp_df, temp_urls], axis=1)

    if save_directory is None:
        save_directory = os.getcwd()
    temp_df.to_csv(os.path.join(save_directory, filename), index=False)
