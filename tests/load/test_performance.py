# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import asyncio
import time
import statistics
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from tests.conftest import TestConfig


class LoadTestResults:
    """Container for load test results and metrics."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.success_count: int = 0
        self.error_count: int = 0
        self.errors: List[str] = []
        self.start_time: float = 0
        self.end_time: float = 0
    
    @property
    def total_requests(self) -> int:
        return self.success_count + self.error_count
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.success_count / self.total_requests) * 100
    
    @property
    def average_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def median_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.median(self.response_times)
    
    @property
    def p95_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.quantiles(self.response_times, n=20)[18]  # 95th percentile
    
    @property
    def total_duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def requests_per_second(self) -> float:
        if self.total_duration == 0:
            return 0.0
        return self.total_requests / self.total_duration


class PlantworksLoadTester:
    """Load tester for Plantworks ADK application."""
    
    def __init__(self, base_url: str = "http://localhost:9999"):
        self.base_url = base_url
        self.test_queries = TestConfig.TEST_QUERIES
        self.test_plants = TestConfig.TEST_PLANTS
        self.test_locations = TestConfig.TEST_LOCATIONS
    
    async def single_request(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """Make a single request to the agent."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/run",
                    json={
                        "message": query,
                        "session_id": session_id or f"load_test_{int(time.time())}"
                    }
                )
                response.raise_for_status()
                
                end_time = time.time()
                response_time = end_time - start_time
                
                return {
                    "success": True,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "response_data": response.json()
                }
        
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "success": False,
                "response_time": response_time,
                "error": str(e)
            }
    
    async def health_check(self) -> bool:
        """Check if the server is healthy before load testing."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False
    
    async def concurrent_load_test(
        self,
        concurrent_users: int = TestConfig.CONCURRENT_USERS,
        requests_per_user: int = TestConfig.REQUESTS_PER_USER,
        ramp_up_time: int = TestConfig.RAMP_UP_TIME
    ) -> LoadTestResults:
        """Run concurrent load test with multiple users."""
        
        results = LoadTestResults()
        results.start_time = time.time()
        
        # Create tasks for concurrent execution
        tasks = []
        
        for user_id in range(concurrent_users):
            # Stagger user start times for ramp-up
            delay = (user_id * ramp_up_time) / concurrent_users
            
            for request_id in range(requests_per_user):
                query = self.test_queries[request_id % len(self.test_queries)]
                session_id = f"load_test_user_{user_id}_req_{request_id}"
                
                task = asyncio.create_task(
                    self._delayed_request(query, session_id, delay)
                )
                tasks.append(task)
        
        # Execute all tasks concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results.end_time = time.time()
        
        # Process results
        for response in responses:
            if isinstance(response, Exception):
                results.error_count += 1
                results.errors.append(str(response))
            elif response.get("success"):
                results.success_count += 1
                results.response_times.append(response["response_time"])
            else:
                results.error_count += 1
                results.errors.append(response.get("error", "Unknown error"))
        
        return results
    
    async def _delayed_request(self, query: str, session_id: str, delay: float) -> Dict[str, Any]:
        """Make a request after a specified delay."""
        await asyncio.sleep(delay)
        return await self.single_request(query, session_id)
    
    async def stress_test(
        self,
        duration_seconds: int = 60,
        concurrent_users: int = 20
    ) -> LoadTestResults:
        """Run stress test for a specified duration."""
        
        results = LoadTestResults()
        results.start_time = time.time()
        end_time = results.start_time + duration_seconds
        
        tasks = []
        
        # Create continuous load for the duration
        for user_id in range(concurrent_users):
            task = asyncio.create_task(
                self._continuous_requests(user_id, end_time)
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results.end_time = time.time()
        
        # Flatten and process all responses
        for user_responses in responses:
            if isinstance(user_responses, Exception):
                results.error_count += 1
                results.errors.append(str(user_responses))
            else:
                for response in user_responses:
                    if response.get("success"):
                        results.success_count += 1
                        results.response_times.append(response["response_time"])
                    else:
                        results.error_count += 1
                        results.errors.append(response.get("error", "Unknown error"))
        
        return results
    
    async def _continuous_requests(self, user_id: int, end_time: float) -> List[Dict[str, Any]]:
        """Make continuous requests until end time."""
        responses = []
        request_count = 0
        
        while time.time() < end_time:
            query = self.test_queries[request_count % len(self.test_queries)]
            session_id = f"stress_test_user_{user_id}_req_{request_count}"
            
            response = await self.single_request(query, session_id)
            responses.append(response)
            request_count += 1
            
            # Small delay to prevent overwhelming the server
            await asyncio.sleep(0.1)
        
        return responses


class TestLoadPerformance:
    """Load and performance tests for Plantworks ADK."""
    
    @pytest.fixture
    def load_tester(self):
        """Create load tester instance."""
        return PlantworksLoadTester()
    
    @pytest.mark.asyncio
    async def test_server_health_before_load(self, load_tester):
        """Verify server is healthy before running load tests."""
        is_healthy = await load_tester.health_check()
        if not is_healthy:
            pytest.skip("Server is not healthy - skipping load tests")
    
    @pytest.mark.asyncio
    async def test_single_request_performance(self, load_tester):
        """Test performance of single requests."""
        query = "What is Monstera deliciosa?"
        
        response = await load_tester.single_request(query)
        
        assert response["success"], f"Request failed: {response.get('error')}"
        assert response["response_time"] < 10.0, f"Response time too slow: {response['response_time']}s"
        assert response["status_code"] == 200
        assert "response_data" in response
    
    @pytest.mark.asyncio
    async def test_multiple_sequential_requests(self, load_tester):
        """Test performance of multiple sequential requests."""
        queries = TestConfig.TEST_QUERIES[:3]  # Test first 3 queries
        response_times = []
        
        for query in queries:
            response = await load_tester.single_request(query)
            assert response["success"], f"Request failed for query '{query}': {response.get('error')}"
            response_times.append(response["response_time"])
        
        # Check that response times are reasonable
        avg_response_time = statistics.mean(response_times)
        assert avg_response_time < 8.0, f"Average response time too slow: {avg_response_time}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_users_load(self, load_tester):
        """Test performance with concurrent users."""
        concurrent_users = 5
        requests_per_user = 3
        
        results = await load_tester.concurrent_load_test(
            concurrent_users=concurrent_users,
            requests_per_user=requests_per_user,
            ramp_up_time=2
        )
        
        # Validate results
        expected_total = concurrent_users * requests_per_user
        assert results.total_requests == expected_total
        assert results.success_rate >= 80.0, f"Success rate too low: {results.success_rate}%"
        assert results.average_response_time < 15.0, f"Average response time too slow: {results.average_response_time}s"
        assert results.requests_per_second > 0.1, f"Throughput too low: {results.requests_per_second} req/s"
    
    @pytest.mark.asyncio
    async def test_agent_response_consistency(self, load_tester):
        """Test that agents provide consistent responses under load."""
        query = "Where can I buy a snake plant?"
        responses = []
        
        # Make multiple requests with the same query
        for i in range(5):
            response = await load_tester.single_request(query, f"consistency_test_{i}")
            assert response["success"], f"Request {i} failed: {response.get('error')}"
            responses.append(response["response_data"]["response"])
        
        # Check that all responses contain expected marketplace information
        for response_text in responses:
            assert "sill" in response_text.lower() or "planterina" in response_text.lower()
            assert "price" in response_text.lower() or "$" in response_text
    
    @pytest.mark.asyncio
    async def test_different_agent_types_performance(self, load_tester):
        """Test performance across different agent types."""
        agent_queries = {
            "botanist": "What is Monstera deliciosa?",
            "gardener": "How do I care for a snake plant?",
            "ecologist": "What native plants grow in California?",
            "merchant": "Where can I buy a fiddle leaf fig?"
        }
        
        results = {}
        
        for agent_type, query in agent_queries.items():
            response = await load_tester.single_request(query)
            assert response["success"], f"{agent_type} query failed: {response.get('error')}"
            results[agent_type] = response["response_time"]
        
        # Check that all agent types respond within reasonable time
        for agent_type, response_time in results.items():
            assert response_time < 12.0, f"{agent_type} response time too slow: {response_time}s"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_sustained_load(self, load_tester):
        """Test performance under sustained load (marked as slow test)."""
        duration = 30  # 30 seconds
        concurrent_users = 8
        
        results = await load_tester.stress_test(
            duration_seconds=duration,
            concurrent_users=concurrent_users
        )
        
        # Validate sustained performance
        assert results.total_requests > 0, "No requests completed during stress test"
        assert results.success_rate >= 70.0, f"Success rate under sustained load too low: {results.success_rate}%"
        assert results.average_response_time < 20.0, f"Average response time under load too slow: {results.average_response_time}s"
        
        # Check for performance degradation
        if len(results.response_times) > 10:
            first_half = results.response_times[:len(results.response_times)//2]
            second_half = results.response_times[len(results.response_times)//2:]
            
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            
            # Response time shouldn't degrade by more than 100%
            degradation = (second_avg - first_avg) / first_avg * 100
            assert degradation < 100, f"Performance degraded too much: {degradation}%"
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, load_tester):
        """Test that memory usage remains stable under load."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run load test
        results = await load_tester.concurrent_load_test(
            concurrent_users=5,
            requests_per_user=5,
            ramp_up_time=1
        )
        
        # Check memory usage after load test
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for this test)
        assert memory_increase < 100, f"Memory usage increased too much: {memory_increase}MB"
        assert results.success_rate >= 80.0, "Load test failed while checking memory"


class TestPerformanceBenchmarks:
    """Performance benchmark tests for comparison and monitoring."""
    
    @pytest.mark.asyncio
    async def test_response_time_benchmarks(self):
        """Test response time benchmarks for different query types."""
        load_tester = PlantworksLoadTester()
        
        benchmarks = {
            "simple_identification": ("What is a snake plant?", 8.0),
            "complex_care": ("How do I care for a Monstera deliciosa in low light conditions?", 12.0),
            "marketplace_search": ("Where can I buy a fiddle leaf fig for under $50?", 10.0),
            "native_plants": ("What native plants grow well in Texas?", 10.0)
        }
        
        for test_name, (query, max_time) in benchmarks.items():
            response = await load_tester.single_request(query)
            
            assert response["success"], f"Benchmark {test_name} failed: {response.get('error')}"
            assert response["response_time"] < max_time, \
                f"Benchmark {test_name} too slow: {response['response_time']}s > {max_time}s"
    
    @pytest.mark.asyncio
    async def test_throughput_benchmark(self):
        """Test throughput benchmark."""
        load_tester = PlantworksLoadTester()
        
        results = await load_tester.concurrent_load_test(
            concurrent_users=10,
            requests_per_user=2,
            ramp_up_time=1
        )
        
        # Benchmark: Should handle at least 1 request per second
        assert results.requests_per_second >= 1.0, \
            f"Throughput benchmark failed: {results.requests_per_second} req/s < 1.0 req/s"
        
        # Benchmark: Should maintain 90% success rate
        assert results.success_rate >= 90.0, \
            f"Success rate benchmark failed: {results.success_rate}% < 90%"


if __name__ == "__main__":
    # Run load tests with specific markers
    pytest.main([__file__, "-v", "-m", "not slow"])

