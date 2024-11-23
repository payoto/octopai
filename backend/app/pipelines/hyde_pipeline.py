from typing import Generator
from ..core.database import get_chroma_db_service
from ..core.context import log_response_messages
from ..services.anthropic_service import client, AnthropicRequest

class HydePipeline:
    def __init__(self):
        """Initialize HydePipeline"""
        self.anthropic = client
        self.db = get_chroma_db_service()

    def anthropic_stream_response(self, query: str):
        messages = [{
            "role": "user",
            "content": query
        }]
        stream = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            messages=messages,
            stream=True,
        )
        output = ""
        for chunk in stream:
            if chunk.type == "content_block_delta":
                output += chunk.delta.text
                yield chunk.delta.text
        messages.append({
            "role": "assistant",
            "content": output
        })
        log_response_messages(messages)

    def process_query(self, query: AnthropicRequest | str) -> Generator[str, None, None]:
        """Apply HyDE to the query

        - takes the last message
        - generates a hypothetical response
        - uses the response to search for relevant documents
        - returns the documents
        - prompts the model to answer the question using the documents
        """
        if isinstance(query, AnthropicRequest):
            question = query.messages[-1].content
        else:
            question = query
        yield "<hyde>"
        prompt = f"""Provide an hypothetical answer to the given question.
                     Question: {question}"""
        yield f"<hyde_prompt>\n{prompt}\n</hyde_prompt>\n"
        yield f"<hyde_response>"
        hyde_response = ""
        for o in self.anthropic_stream_response(prompt):
            hyde_response += o
            yield o
        yield f"</hyde_response>"
        search_query = f"{question} {hyde_response}"
        yield f"<search_query>\n{search_query}\n</search_query>\n"

        results = self.db.query(query_texts=search_query, n_results=5, where=None)
        relevant_chunks = [txt for sublist in results["documents"] for txt in sublist]
        context = "\n\n".join(relevant_chunks)

        yield f"<context>\n{context}\n</context>\n"
        # TODO: refactor so that hyde only returns the context
        final_query = f"""
            You have been tasked with helping us to answer the following query:
            <query>
            {question}
            </query>
            You have access to the following documents which are meant to provide context as you answer the query:
            <documents>
            {context}
            </documents>
            Please remain faithful to the underlying context, and only deviate from it if you are 100% sure that you know the answer already.
            Answer the question now, and avoid providing preamble such as 'Here is the answer', etc
            """
        yield f"<final_query>\n{final_query}\n</final_query>\n"
        yield "</hyde>"
        for o in self.anthropic_stream_response(final_query):
            yield o
