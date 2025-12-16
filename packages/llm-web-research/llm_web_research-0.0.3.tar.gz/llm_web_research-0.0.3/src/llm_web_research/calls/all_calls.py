# Funnel of Verification (FoVe) calls for all providers
import json as json_module

from .prompts import (
    get_step1_prompt,
    get_step2_prompt,
    get_step3_prompt,
    get_step4_prompt,
    STEP4_JSON_SCHEMA,
    EARLY_EXIT_NOT_FOUND,
    EARLY_EXIT_NOT_CONFIDENT,
    EARLY_EXIT_ERROR
)


def _postprocess_result(result_json):
    """
    Post-process the FoVe result to ensure consistency.
    If confidence is 0 OR multiple_entities is 1, set answer to "Information unclear".
    Then drop confidence and multiple_entities (internal use only).

    Args:
        result_json (str): JSON string with answer, url, confidence, multiple_entities

    Returns:
        str: Processed JSON string with only answer and url
    """
    try:
        parsed = json_module.loads(result_json)
        # Set answer to "Information unclear" if confidence is 0 OR multiple entities detected
        if (parsed.get("confidence") == "0" or parsed.get("confidence") == 0 or
            parsed.get("multiple_entities") == "1" or parsed.get("multiple_entities") == 1):
            parsed["answer"] = "Information unclear"
        # Drop internal fields - only return answer and url
        final_result = {
            "answer": parsed.get("answer", "Information unclear"),
            "url": parsed.get("url", "")
        }
        return json_module.dumps(final_result)
    except (json_module.JSONDecodeError, TypeError):
        return result_json


# =============================================================================
# ANTHROPIC
# =============================================================================

def funnel_of_verification_anthropic(
    item,
    search_question,
    answer_format,
    additional_instructions,
    client,
    user_model,
    creativity,
    verbose=False
):
    """
    Execute Funnel of Verification (FoVe) process for Anthropic Claude.

    Args:
        item: The entity to search for
        search_question: The question to answer about the entity
        answer_format: Expected format of the answer (e.g., "name", "year")
        additional_instructions: Extra instructions to include in prompts
        client: Anthropic client instance
        user_model: Model to use (e.g., "claude-sonnet-4-20250514")
        creativity: Temperature setting (None for default)
        verbose: If True, print each prompt and response for debugging

    Returns:
        str: JSON string with answer, url, confidence, multiple_entities
    """
    try:
        # STEP 1: Gather broad information (web search)
        step1_prompt = get_step1_prompt(item, search_question)

        step1_response = client.messages.create(
            model=user_model,
            messages=[{'role': 'user', 'content': step1_prompt}],
            max_tokens=4096,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 10
            }],
            **({"temperature": creativity} if creativity is not None else {})
        )

        item_context = " ".join(
            block.text
            for block in step1_response.content
            if getattr(block, "type", "") == "text"
        ).strip()

        if verbose:
            print("\n" + "="*80)
            print("STEP 1: Gather broad information (web search)")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step1_prompt)
            print("\n--- RESPONSE ---")
            print(item_context[:2000] + "..." if len(item_context) > 2000 else item_context)

        # Extract URLs from step 1
        urls = [
            url_item["url"]
            for block in step1_response.content
            if getattr(block, "type", "") == "web_search_tool_result"
            for url_item in (getattr(block, "content", []) or [])
            if isinstance(url_item, dict) and url_item.get("type") == "web_search_result" and "url" in url_item
        ]

        # Deduplicate URLs
        seen = set()
        urls = [u for u in urls if not (u in seen or seen.add(u))]

        if verbose:
            print(f"\n--- URLs found: {len(urls)} ---")
            for u in urls[:5]:
                print(f"  {u}")
            if len(urls) > 5:
                print(f"  ... and {len(urls) - 5} more")

        # Check for early exit: ANSWER NOT FOUND
        if "ANSWER NOT FOUND" in item_context.upper():
            if verbose:
                print("\n>>> EARLY EXIT: ANSWER NOT FOUND <<<")
            return EARLY_EXIT_NOT_FOUND

        # STEP 2: Extract concise answer (no web search)
        step2_prompt = get_step2_prompt(item, search_question, item_context, additional_instructions)

        step2_response = client.messages.create(
            model=user_model,
            messages=[{'role': 'user', 'content': step2_prompt}],
            max_tokens=1024,
            **({"temperature": creativity} if creativity is not None else {})
        )

        initial_reply = step2_response.content[0].text

        if verbose:
            print("\n" + "="*80)
            print("STEP 2: Extract concise answer (no web search)")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step2_prompt[:1500] + "..." if len(step2_prompt) > 1500 else step2_prompt)
            print("\n--- RESPONSE ---")
            print(initial_reply)

        # Check for early exit: RESPONSE NOT CONFIDENT
        if "RESPONSE NOT CONFIDENT" in initial_reply.upper():
            if verbose:
                print("\n>>> EARLY EXIT: RESPONSE NOT CONFIDENT <<<")
            return EARLY_EXIT_NOT_CONFIDENT

        # STEP 3: Skeptical verification (web search)
        step3_prompt = get_step3_prompt(item, search_question, initial_reply, answer_format, additional_instructions)

        step3_response = client.messages.create(
            model=user_model,
            messages=[{'role': 'user', 'content': step3_prompt}],
            max_tokens=4096,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 5
            }],
            **({"temperature": creativity} if creativity is not None else {})
        )

        verification_result = " ".join(
            block.text
            for block in step3_response.content
            if getattr(block, "type", "") == "text"
        ).strip()

        if verbose:
            print("\n" + "="*80)
            print("STEP 3: Skeptical verification (web search)")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step3_prompt[:1500] + "..." if len(step3_prompt) > 1500 else step3_prompt)
            print("\n--- RESPONSE ---")
            print(verification_result[:2000] + "..." if len(verification_result) > 2000 else verification_result)

        # STEP 4: Format output as strict JSON
        json_tools = [{
            "name": "return_result",
            "description": "Return the final research result",
            "input_schema": STEP4_JSON_SCHEMA
        }]

        step4_prompt = get_step4_prompt(verification_result, answer_format)

        step4_response = client.messages.create(
            model=user_model,
            max_tokens=1024,
            tools=json_tools,
            tool_choice={"type": "tool", "name": "return_result"},
            messages=[{'role': 'user', 'content': step4_prompt}],
            **({"temperature": creativity} if creativity is not None else {})
        )

        json_reply = step4_response.content[0].input
        verified_reply = json_module.dumps(json_reply)

        # Post-process result
        verified_reply = _postprocess_result(verified_reply)

        if verbose:
            print("\n" + "="*80)
            print("STEP 4: Format as strict JSON")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step4_prompt)
            print("\n--- RESPONSE (JSON) ---")
            print(verified_reply)
            print("\n" + "="*80)
            print("FINAL RESULT")
            print("="*80)

        return verified_reply

    except Exception as e:
        return EARLY_EXIT_ERROR


# =============================================================================
# GOOGLE
# =============================================================================

def funnel_of_verification_google(
    item,
    search_question,
    answer_format,
    additional_instructions,
    url,
    headers,
    creativity,
    make_google_request,
    verbose=False
):
    """
    Execute Funnel of Verification (FoVe) process for Google Gemini.

    Args:
        item: The entity to search for
        search_question: The question to answer about the entity
        answer_format: Expected format of the answer (e.g., "name", "year")
        additional_instructions: Extra instructions to include in prompts
        url: Google API endpoint URL
        headers: Request headers with API key
        creativity: Temperature setting (None for default)
        make_google_request: Function to make Google API requests
        verbose: If True, print each prompt and response for debugging

    Returns:
        str: JSON string with answer, url, confidence, multiple_entities
    """
    import re

    try:
        # STEP 1: Gather broad information (web search)
        step1_prompt = get_step1_prompt(item, search_question)

        payload_step1 = {
            "contents": [{"parts": [{"text": step1_prompt}]}],
            "tools": [{"google_search": {}}],
            **({"generationConfig": {"temperature": creativity}} if creativity is not None else {})
        }

        result_step1 = make_google_request(url, headers, payload_step1)
        item_context = result_step1["candidates"][0]["content"]["parts"][0]["text"]

        if verbose:
            print("\n" + "="*80)
            print("STEP 1: Gather broad information (web search)")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step1_prompt)
            print("\n--- RESPONSE ---")
            print(item_context[:2000] + "..." if len(item_context) > 2000 else item_context)

        # Extract URLs from step 1
        urls = []
        for cand in result_step1.get("candidates", []):
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

        # Deduplicate URLs
        seen = set()
        urls = [u for u in urls if not (u in seen or seen.add(u))]

        if verbose:
            print(f"\n--- URLs found: {len(urls)} ---")
            for u in urls[:5]:
                print(f"  {u}")
            if len(urls) > 5:
                print(f"  ... and {len(urls) - 5} more")

        # Check for early exit: ANSWER NOT FOUND
        if "ANSWER NOT FOUND" in item_context.upper():
            if verbose:
                print("\n>>> EARLY EXIT: ANSWER NOT FOUND <<<")
            return EARLY_EXIT_NOT_FOUND

        # STEP 2: Extract concise answer (no web search)
        step2_prompt = get_step2_prompt(item, search_question, item_context, additional_instructions)

        payload_step2 = {
            "contents": [{"parts": [{"text": step2_prompt}]}],
            **({"generationConfig": {"temperature": creativity}} if creativity is not None else {})
        }

        result_step2 = make_google_request(url, headers, payload_step2)
        initial_reply = result_step2["candidates"][0]["content"]["parts"][0]["text"]

        if verbose:
            print("\n" + "="*80)
            print("STEP 2: Extract concise answer (no web search)")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step2_prompt[:1500] + "..." if len(step2_prompt) > 1500 else step2_prompt)
            print("\n--- RESPONSE ---")
            print(initial_reply)

        # Check for early exit: RESPONSE NOT CONFIDENT
        if "RESPONSE NOT CONFIDENT" in initial_reply.upper():
            if verbose:
                print("\n>>> EARLY EXIT: RESPONSE NOT CONFIDENT <<<")
            return EARLY_EXIT_NOT_CONFIDENT

        # STEP 3: Skeptical verification (web search)
        step3_prompt = get_step3_prompt(item, search_question, initial_reply, answer_format, additional_instructions)

        payload_step3 = {
            "contents": [{"parts": [{"text": step3_prompt}]}],
            "tools": [{"google_search": {}}],
            **({"generationConfig": {"temperature": creativity}} if creativity is not None else {})
        }

        result_step3 = make_google_request(url, headers, payload_step3)
        verification_result = result_step3["candidates"][0]["content"]["parts"][0]["text"]

        # Extract URLs from step 3
        step3_urls = []
        for cand in result_step3.get("candidates", []):
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
                step3_urls.extend(found)

        # Deduplicate and combine URLs (step 3 takes priority)
        seen = set()
        step3_urls = [u for u in step3_urls if not (u in seen or seen.add(u))]
        all_urls = step3_urls + [u for u in urls if u not in seen]

        if verbose:
            print("\n" + "="*80)
            print("STEP 3: Skeptical verification (web search)")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step3_prompt[:1500] + "..." if len(step3_prompt) > 1500 else step3_prompt)
            print("\n--- RESPONSE ---")
            print(verification_result[:2000] + "..." if len(verification_result) > 2000 else verification_result)
            print(f"\n--- Step 3 URLs found: {len(step3_urls)} ---")
            for u in step3_urls[:3]:
                print(f"  {u}")

        # STEP 4: Format output as strict JSON
        step4_prompt = get_step4_prompt(verification_result, answer_format)
        step4_prompt += "\n\nReturn ONLY the JSON object, nothing else."

        payload_step4 = {
            "contents": [{"parts": [{"text": step4_prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                **({"temperature": creativity} if creativity is not None else {})
            }
        }

        result_step4 = make_google_request(url, headers, payload_step4)
        verified_reply = result_step4["candidates"][0]["content"]["parts"][0]["text"]

        # Inject URL from grounding metadata if LLM didn't extract one
        try:
            parsed_reply = json_module.loads(verified_reply)
            if (not parsed_reply.get("url") or parsed_reply.get("url") == "") and all_urls:
                parsed_reply["url"] = all_urls[0]
                verified_reply = json_module.dumps(parsed_reply)
        except (json_module.JSONDecodeError, TypeError):
            pass

        # Post-process result
        verified_reply = _postprocess_result(verified_reply)

        if verbose:
            print("\n" + "="*80)
            print("STEP 4: Format as strict JSON")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step4_prompt)
            print("\n--- RESPONSE (JSON) ---")
            print(verified_reply)
            print("\n" + "="*80)
            print("FINAL RESULT")
            print("="*80)

        return verified_reply

    except Exception as e:
        return EARLY_EXIT_ERROR


# =============================================================================
# PERPLEXITY
# =============================================================================

def funnel_of_verification_perplexity(
    item,
    search_question,
    answer_format,
    additional_instructions,
    client,
    user_model,
    creativity,
    start_date=None,
    end_date=None,
    verbose=False
):
    """
    Execute Funnel of Verification (FoVe) process for Perplexity.

    Args:
        item: The entity to search for
        search_question: The question to answer about the entity
        answer_format: Expected format of the answer (e.g., "name", "year")
        additional_instructions: Extra instructions to include in prompts
        client: Perplexity client instance
        user_model: Model to use (e.g., "sonar")
        creativity: Temperature setting (None for default)
        start_date: Filter results after this date
        end_date: Filter results before this date
        verbose: If True, print each prompt and response for debugging

    Returns:
        str: JSON string with answer, url, confidence, multiple_entities
    """
    try:
        # STEP 1: Gather broad information (web search)
        step1_prompt = get_step1_prompt(item, search_question)

        step1_response = client.chat.completions.create(
            model=user_model,
            messages=[{'role': 'user', 'content': step1_prompt}],
            web_search_options={"search_context_size": "high"},
            **({"search_after_date_filter": start_date} if start_date else {}),
            **({"search_before_date_filter": end_date} if end_date else {}),
            **({"temperature": creativity} if creativity is not None else {})
        )

        item_context = step1_response.choices[0].message.content

        if verbose:
            print("\n" + "="*80)
            print("STEP 1: Gather broad information (web search)")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step1_prompt)
            print("\n--- RESPONSE ---")
            print(item_context[:2000] + "..." if len(item_context) > 2000 else item_context)

        # Extract URLs from step 1
        urls = list(step1_response.citations) if hasattr(step1_response, 'citations') else []

        # Deduplicate URLs
        seen = set()
        urls = [u for u in urls if not (u in seen or seen.add(u))]

        if verbose:
            print(f"\n--- URLs found: {len(urls)} ---")
            for u in urls[:5]:
                print(f"  {u}")
            if len(urls) > 5:
                print(f"  ... and {len(urls) - 5} more")

        # Check for early exit: ANSWER NOT FOUND
        if "ANSWER NOT FOUND" in item_context.upper():
            if verbose:
                print("\n>>> EARLY EXIT: ANSWER NOT FOUND <<<")
            return EARLY_EXIT_NOT_FOUND

        # STEP 2: Extract concise answer (no web search)
        step2_prompt = get_step2_prompt(item, search_question, item_context, additional_instructions)

        step2_response = client.chat.completions.create(
            model=user_model,
            messages=[{'role': 'user', 'content': step2_prompt}],
            **({"temperature": creativity} if creativity is not None else {})
        )

        initial_reply = step2_response.choices[0].message.content

        if verbose:
            print("\n" + "="*80)
            print("STEP 2: Extract concise answer (no web search)")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step2_prompt[:1500] + "..." if len(step2_prompt) > 1500 else step2_prompt)
            print("\n--- RESPONSE ---")
            print(initial_reply)

        # Check for early exit: RESPONSE NOT CONFIDENT
        if "RESPONSE NOT CONFIDENT" in initial_reply.upper():
            if verbose:
                print("\n>>> EARLY EXIT: RESPONSE NOT CONFIDENT <<<")
            return EARLY_EXIT_NOT_CONFIDENT

        # STEP 3: Skeptical verification (web search)
        step3_prompt = get_step3_prompt(item, search_question, initial_reply, answer_format, additional_instructions)

        step3_response = client.chat.completions.create(
            model=user_model,
            messages=[{'role': 'user', 'content': step3_prompt}],
            web_search_options={"search_context_size": "high"},
            **({"search_after_date_filter": start_date} if start_date else {}),
            **({"search_before_date_filter": end_date} if end_date else {}),
            **({"temperature": creativity} if creativity is not None else {})
        )

        verification_result = step3_response.choices[0].message.content

        if verbose:
            print("\n" + "="*80)
            print("STEP 3: Skeptical verification (web search)")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step3_prompt[:1500] + "..." if len(step3_prompt) > 1500 else step3_prompt)
            print("\n--- RESPONSE ---")
            print(verification_result[:2000] + "..." if len(verification_result) > 2000 else verification_result)

        # STEP 4: Format output as strict JSON
        step4_prompt = get_step4_prompt(verification_result, answer_format)

        step4_response = client.chat.completions.create(
            model=user_model,
            messages=[{'role': 'user', 'content': step4_prompt}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "schema": STEP4_JSON_SCHEMA
                }
            },
            **({"temperature": creativity} if creativity is not None else {})
        )

        verified_reply = step4_response.choices[0].message.content

        # Post-process result
        verified_reply = _postprocess_result(verified_reply)

        if verbose:
            print("\n" + "="*80)
            print("STEP 4: Format as strict JSON")
            print("="*80)
            print("\n--- PROMPT ---")
            print(step4_prompt)
            print("\n--- RESPONSE (JSON) ---")
            print(verified_reply)
            print("\n" + "="*80)
            print("FINAL RESULT")
            print("="*80)

        return verified_reply

    except Exception as e:
        return EARLY_EXIT_ERROR
