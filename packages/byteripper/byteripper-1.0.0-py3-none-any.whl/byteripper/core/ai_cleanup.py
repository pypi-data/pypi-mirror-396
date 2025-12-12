try:
    from g4f.client import Client
    g4f_available = True
except importerror:
    g4f_available = False

def is_ai_available():
    return g4f_available

def cleanup_code(source_code, model="gpt-4o-mini"):
    if not g4f_available:
        return source_code, "g4f not available"
    if not source_code or len(source_code.strip()) == 0:
        return source_code, "empty source code"
    try:
        client = Client()
        prompt = f"""fix and format this python code. only output the fixed code, no explanations:

{source_code}"""
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content
        if result.startswith("```python"):
            result = result[9:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        return result.strip(), None
    except exception as e:
        return source_code, f"ai cleanup failed: {str(e)}"

def format_code(source_code, model="gpt-4o-mini"):
    if not g4f_available:
        return source_code, "g4f not available"
    try:
        client = Client()
        prompt = f"""format this python code properly with correct indentation. only output the formatted code:

{source_code}"""
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content
        if result.startswith("```python"):
            result = result[9:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        return result.strip(), None
    except exception as e:
        return source_code, f"formatting failed: {str(e)}"

exception = Exception
importerror = ImportError
