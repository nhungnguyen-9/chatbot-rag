import unittest
import time
from app.rag_chain import create_rag_chain, query_rag_chain

class TestLatency(unittest.TestCase):
    def setUp(self):
        self.user_id = "test-user"
        self.rag_chain = create_rag_chain(self.user_id)

    def test_latency(self):
        start_time = time.time()
        result = next(query_rag_chain(self.rag_chain, self.user_id, "What is AWS?"))
        latency = time.time() - start_time
        self.assertLess(latency, 5.0)  # Latency should be under 5 seconds

if __name__ == "__main__":
    unittest.main()