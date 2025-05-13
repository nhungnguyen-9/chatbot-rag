import unittest
from app.rag_chain import create_rag_chain, query_rag_chain

class TestChatbotQueries(unittest.TestCase):
    def setUp(self):
        self.user_id = "test-user"
        self.rag_chain = create_rag_chain(self.user_id)

    def test_query_1(self):
        result = next(query_rag_chain(self.rag_chain, self.user_id, "What is the capital of France?"))
        response, _ = result
        self.assertIn("France", response)

    def test_query_2(self):
        result = next(query_rag_chain(self.rag_chain, self.user_id, "What is AWS?"))
        response, _ = result
        self.assertIn("Amazon Web Services", response)

    def test_query_3(self):
        result = next(query_rag_chain(self.rag_chain, self.user_id, "How does RAG work?"))
        response, _ = result
        self.assertIn("Retrieval-Augmented Generation", response)

    def test_query_4(self):
        result = next(query_rag_chain(self.rag_chain, self.user_id, "What is the weather like today?"))
        response, _ = result
        self.assertIn("I can search for that", response)

    def test_query_5(self):
        result = next(query_rag_chain(self.rag_chain, self.user_id, "Summarize the document."))
        response, _ = result
        self.assertTrue(len(response) > 50)

if __name__ == "__main__":
    unittest.main()