from services.chromadb_serivce import ChromaDBService
from services.anthropic_service import client

class HydePipeline:
    def __init__(self):
        """Initialize HydePipeline"""
        self.anthropic = client
        self.db = ChromaDBService()
    
    def generate_response(self, query: str, prompt: str) -> str:
        """Generate hypotetical response from query."""
        response = self.anthropic.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user", 
                "content": f"{prompt} {query}"
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
        prompt = f"Make a hypotetical response to the following query: "
        hyde_response = self.generate_response(query, prompt)
        print(f"Hyde response: {hyde_response}")
        search_query = f"{query} {hyde_response}"
        relevant_documents = self.db.query(search_query)
        print(f"Relevant documents: {relevant_documents['documents']}")
        
        flattened_docs = []
        for doc in relevant_documents['documents']:
            if isinstance(doc, list) and doc:  # Check if list and not empty
                flattened_docs.append(doc[0])
            elif not isinstance(doc, list):  # If not list, add directly
                flattened_docs.append(doc)
                
        context = " ".join(doc for doc in flattened_docs if doc)  # Skip empty docs

        print(f"Context: {context}")
        final_prompt = f"Give a response and say this is HYDE pipeline at the end to the following query: "
        final_query = f"{final_prompt} {context} {query}"
        return self.anthropic_stream_response(final_query)