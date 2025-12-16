from langchain_core.prompts import ChatPromptTemplate

class GenericPrompts:
    """
    Collection of generic, reusable prompt templates for various standard tasks.
    """

    UNIVERSAL_JSON_EXTRACTION = ChatPromptTemplate.from_template("""
You are a precise data extractor. Your task is to extract structured data from the provided text according to the given schema.

Rules:
1.  **Strict JSON Output**: Output strictly valid JSON. No markdown, no comments.
2.  **Schema Compliance**: Adhere exactly to the provided schema.
3.  **No Hallucination**: Only extract information present in the input.

Schema:
{format_instructions}

Input Text:
{input_text}
""")

    UNIVERSAL_SUMMARY = ChatPromptTemplate.from_template("""
You are an expert summarizer. Create a concise summary of the following text.

Guidelines:
1.  Capture the main points and key details.
2.  Maintain the original tone and intent.
3.  Keep it within {max_words} words (optional constraint).

Input Text:
{input_text}
""")

    UNIVERSAL_RAG_QA = ChatPromptTemplate.from_template("""
You are a helpful assistant answering questions based *only* on the provided context.

Context:
{context}

Question:
{question}

Instructions:
- If the answer is in the context, answer clearly and concisely.
- If the answer is NOT in the context, say "I don't know based on the provided context."
- Do not make up information.
""")

    UNIVERSAL_QUERY_REWRITE = ChatPromptTemplate.from_template("""
Rewrite the following user query to be standalone and self-contained, resolving any pronouns or references using the chat history.

Chat History:
{chat_history}

User Query:
{input}

Rewritten Query:
""")

    UNIVERSAL_CLASSIFICATION = ChatPromptTemplate.from_template("""
Classify the following text into one of the provided categories.

Categories:
{categories}

Text to Classify:
{input_text}

Output only the category name.
""")

def get_generic_prompt(prompt_name: str) -> ChatPromptTemplate:
    """
    Retrieve a generic prompt by name.
    
    Args:
        prompt_name: The name of the prompt (case-insensitive).
                     e.g., 'json_extraction', 'summary', 'rag_qa', 'query_rewrite', 'classification'
    
    Returns:
        ChatPromptTemplate: The requested prompt template.
    
    Raises:
        ValueError: If the prompt name is not found.
    """
    normalized_name = prompt_name.upper()
    if not normalized_name.startswith("UNIVERSAL_"):
         normalized_name = f"UNIVERSAL_{normalized_name}"
    
    if hasattr(GenericPrompts, normalized_name):
        return getattr(GenericPrompts, normalized_name)
    
    raise ValueError(f"Prompt '{prompt_name}' not found in GenericPrompts.")
