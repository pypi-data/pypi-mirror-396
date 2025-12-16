# Precise web research function using Funnel of Verification (FoVe)
# Prioritizes accuracy over speed through multi-step verification

def precise_web_research(
    search_question,
    search_input,
    api_key,
    answer_format="concise",
    additional_instructions="",
    user_model="claude-sonnet-4-20250514",
    creativity=None,
    safety=False,
    filename="precise_web_research_results.csv",
    save_directory=None,
    model_source="anthropic",
    start_date=None,
    end_date=None,
    max_retries=6,
    time_delay=5,
    verbose=False
):
    """
    Perform precision-focused web research using Funnel of Verification (FoVe).

    This function uses a 4-step verification pipeline to maximize accuracy:
    1. Broad information gathering (web search)
    2. Critical ambiguity check (flags common names, conflicting info)
    3. Skeptical verification (searches for contradicting info)
    4. Structured output formatting

    Unlike basic web_research(), this function will return "Information unclear"
    rather than risk providing incorrect answers for ambiguous queries.

    Args:
        search_question (str): The question to answer for each search item.
            Example: "current CEO" or "founding date"
        search_input (list or pd.Series): List of items to search for.
            Example: ["Apple Inc", "Microsoft", "Google"]
        api_key (str): API key for the model provider.
        answer_format (str): Expected format of the answer (e.g., "name", "year").
            Default "concise".
        additional_instructions (str): Extra instructions for the search.
        user_model (str): Model to use. Default "claude-sonnet-4-20250514".
        creativity (float): Temperature setting. None uses model default.
        safety (bool): If True, saves progress after each item to prevent data loss.
        filename (str): Output filename. Default "precise_web_research_results.csv".
        save_directory (str): Directory to save results. None uses current dir.
        model_source (str): Provider - "anthropic", "google", or "perplexity".
        start_date (str): Filter results after this date (YYYY-MM-DD). Perplexity only.
        end_date (str): Filter results before this date (YYYY-MM-DD). Perplexity only.
        max_retries (int): Retry count for rate limit errors. Default 6.
        time_delay (int): Seconds between requests. Default 5.
        verbose (bool): If True, print each step's prompt and response.

    Returns:
        pd.DataFrame: Results with columns:
            - search_input: Original search item
            - answer: Verified answer or "Information unclear"/"Information not found"
            - url: Source URL for the answer

    Example:
        >>> import llm_web_research as lwr
        >>> results = lwr.precise_web_research(
        ...     search_question="current CEO",
        ...     search_input=["Apple Inc", "Microsoft"],
        ...     api_key="your-api-key",
        ...     model_source="anthropic"
        ... )
    """
    import os
    import json
    import pandas as pd
    from tqdm import tqdm
    import time
    import re
    from datetime import datetime

    from .calls.all_calls import (
        funnel_of_verification_anthropic,
        funnel_of_verification_google,
        funnel_of_verification_perplexity
    )

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

    model_source = model_source.lower()

    # Convert dates for Perplexity format
    if model_source == "perplexity" and start_date is not None:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%m/%d/%Y")
    if model_source == "perplexity" and end_date is not None:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%m/%d/%Y")

    # Set default model for Google if using Anthropic default
    if model_source == "google" and user_model == "claude-sonnet-4-20250514":
        user_model = "gemini-2.5-flash"

    # Set default model for Perplexity if using Anthropic default
    if model_source == "perplexity" and user_model == "claude-sonnet-4-20250514":
        user_model = "sonar"

    # Initialize client based on provider
    client = None
    url = None
    headers = None
    make_google_request = None

    if model_source == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

    elif model_source == "google":
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{user_model}:generateContent"
        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }

        def make_google_request(url, headers, payload):
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    elif model_source == "perplexity":
        from perplexity import Perplexity
        client = Perplexity(api_key=api_key)

    else:
        raise ValueError(
            f"Unknown model_source: {model_source}. "
            "Supported: 'anthropic', 'google', 'perplexity'"
        )

    results = []

    for idx, item in enumerate(tqdm(search_input, desc="Precise searching")):
        if idx > 0:
            time.sleep(time_delay)

        if pd.isna(item):
            results.append({
                "search_input": item,
                "answer": "Skipped NaN input",
                "url": ""
            })
            continue

        # Execute FoVe pipeline based on provider
        attempt = 0
        result_json = None

        while attempt < max_retries:
            try:
                if model_source == "anthropic":
                    result_json = funnel_of_verification_anthropic(
                        item=item,
                        search_question=search_question,
                        answer_format=answer_format,
                        additional_instructions=additional_instructions,
                        client=client,
                        user_model=user_model,
                        creativity=creativity,
                        verbose=verbose
                    )
                elif model_source == "google":
                    result_json = funnel_of_verification_google(
                        item=item,
                        search_question=search_question,
                        answer_format=answer_format,
                        additional_instructions=additional_instructions,
                        url=url,
                        headers=headers,
                        creativity=creativity,
                        make_google_request=make_google_request,
                        verbose=verbose
                    )
                elif model_source == "perplexity":
                    result_json = funnel_of_verification_perplexity(
                        item=item,
                        search_question=search_question,
                        answer_format=answer_format,
                        additional_instructions=additional_instructions,
                        client=client,
                        user_model=user_model,
                        creativity=creativity,
                        start_date=start_date,
                        end_date=end_date,
                        verbose=verbose
                    )
                break

            except Exception as e:
                if "rate" in str(e).lower() or "429" in str(e):
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    attempt += 1
                else:
                    result_json = json.dumps({
                        "answer": "Information unclear",
                        "url": ""
                    })
                    break

        if result_json is None:
            result_json = json.dumps({
                "answer": "Max retries exceeded",
                "url": ""
            })

        # Parse result
        try:
            parsed = json.loads(result_json)
            results.append({
                "search_input": item,
                "answer": parsed.get("answer", "Information unclear"),
                "url": parsed.get("url", "")
            })
        except json.JSONDecodeError:
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
