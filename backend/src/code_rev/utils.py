

def generate_title_from_code(code_snippet: str) -> str:
    first_line = code_snippet.strip().split("\n")[0]
    title= first_line if len(first_line) <= 50 else first_line[:47]+"..."
    return f"Review: {title}"

