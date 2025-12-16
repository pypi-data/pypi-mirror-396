from client.ai_client import LMStudioClient

def call_ai(prompt_str):

    # AIを呼び出し
    ai_client = LMStudioClient()
    #
    result_content = remove_markdown_code_block(ai_client.call(prompt_str))

    return result_content

def remove_markdown_code_block(content):
    content = content.strip()
    if content.startswith('```') and content.endswith('```'):
        lines = content.split('\n')
        if len(lines) >= 3:
            return '\n'.join(lines[1:-1])
        else:
            return '\n'.join(lines[1:-1]) if len(lines) > 2 else ''
    return content