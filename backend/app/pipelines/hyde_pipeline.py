from core.database import get_chroma_db_service
from services.anthropic_service import client

class HydePipeline:
    def __init__(self):
        """Initialize HydePipeline"""
        self.anthropic = client
        self.db = get_chroma_db_service()

    def generate_response(self, query: str) -> str:
        """Generate hypotetical response from query."""
        response = self.anthropic.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": query
                }],
        )
        return response.content[0].text

    def anthropic_stream_response(self, query: str):
        stream = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": query
            }],
            stream=True,
        )
        for chunk in stream:
            if chunk.type == "content_block_delta":
                yield chunk.delta.text

    def process_query(self, query: str) -> str:
        """Process query."""
        prompt = f"""Provide an hypothetical answer to the given question. 
                     Quesetion: {query}"""
        hyde_response = self.generate_response(prompt)
        print(f"Hyde response: {hyde_response}")
        
        search_query = f"{query} {hyde_response}"
        results = self.db.query(query_texts=search_query, n_results=5, where=None)
        relevant_chunks = [txt for sublist in results["documents"] for txt in sublist]
        context = "\n\n".join(relevant_chunks)
        print(f"Context: {context}")
        
        final_query = f"""
            You have been tasked with helping us to answer the following query: 
            <query>
            {query}
            </query>
            You have access to the following documents which are meant to provide context as you answer the query:
            <documents>
            {context}
            </documents>
            Please remain faithful to the underlying context, and only deviate from it if you are 100% sure that you know the answer already. 
            Answer the question now, and avoid providing preamble such as 'Here is the answer', etc
            """
        return self.anthropic_stream_response(final_query)