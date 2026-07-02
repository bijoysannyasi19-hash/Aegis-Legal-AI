from locust import HttpUser, task, between

class LegalAssistantLoadTester(HttpUser):
    """
    Basic Locust stress testing script for the backend inference and search APIs.
    """
    # Simulate realistic user delay between 1 and 5 seconds
    wait_time = between(1, 5)

    @task(1)
    def test_audit_endpoint_stress(self):
        """Stress testing the secondary Auditor Agent inference pipeline."""
        payload = {
            "draft": "The Vendor's liability shall not exceed the total amounts paid under this Agreement. This Agreement shall be governed by the laws of the State of Delaware."
        }
        with self.client.post("/api/audit", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Audit API failure. Status: {response.status_code}")

    @task(2)
    def test_chat_generation_endpoint(self):
        """Stress testing the primary Dual-Engine Hybrid Search and LLM Generation pipeline."""
        payload = {
            "session_id": "automated-stress-test-session",
            "prompt": "Draft a standard mutual indemnification clause referencing uploaded precedents."
        }
        with self.client.post("/api/chat", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Chat API failure. Status: {response.status_code}")
