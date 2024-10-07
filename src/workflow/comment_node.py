from langchain.prompts import PromptTemplate
from config.model_config import create_chat_model
from langchain_core.output_parsers import JsonOutputParser

# LLM
llm = create_chat_model()

# prompt
template = """
You are given a file patch and its contents from a pull request. Your task is to generate context-aware review comments focused on code quality, 
best practices, and handling edge cases. These comments should be concise, precise, and relevant to the provided content. Avoid inventing issues or 
making up details that are not present in the code. Return the output as list of JSON objects.

Instructions:
A. For Review Comments:
    1. Generate only at most 3 review comments that are specific to lines in the file (subject_type: line). 
    2. Generate a comment only if makes sense in the context. Do not generate very generic comments.
    3. Avoid adding comments on blank lines.
    4. Each line comment should include:
        * body: The comment text.
        * subject_type: line (indicating it's a line-specific comment).
        * line: The line number in the patch where the comment applies. Important: Line number must be part of the diff.
    5. Prioritize the most critical comments for line-specific review (e.g., potential bugs, poor practices, missed edge cases).
    6. Important: If you are unsure of the line number get it from the file contents. Never make it up. And be careful 
        to consider blank lines. Make sure the line number is in the diff always.

B. General Comments:
    1. After analyzing the entire file, provide a general file-level review comment if necessary (subject_type: file). 
    2. This comment should summarize broader concerns or improvements that don't apply to specific lines but are important for overall code quality.
    3. File-level comments should be used to address any additional concerns that couldn't fit within the line-specific limit.

Output Format: JSON List
```
[
    {{
        "body": "<review_comment>",
        "subject_type": "line",
        "line": <line_number>,
        "start_line: <sart_line_number>
    }},
    ...
    {{
        "body": "<general_file_comment>",
        "subject_type": "file"
    }}
]
```
The body of the comments can be in markdown string format.
Inputs:

Numbered File contents:
{file_contents}

File patch:
{file_patch}
"""

prompt = PromptTemplate(template=template, input_variables=["file_contents", "file_patch"])

comment_reviewer = prompt | llm | JsonOutputParser()