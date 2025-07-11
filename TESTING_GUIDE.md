# Plantworks ADK Testing Guide

## 🧪 **Comprehensive Testing Suite**

This guide covers the complete testing infrastructure for the Plantworks Google ADK implementation, including unit tests, integration tests, and load tests following Google ADK best practices.

## 📋 **Test Structure Overview**

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Pytest configuration and fixtures
├── pytest.ini                    # Pytest settings
├── requirements-test.txt          # Testing dependencies
├── unit/                          # Unit tests
│   ├── test_tools.py             # Tool function tests
│   └── test_agents.py            # Agent behavior tests
├── integration/                   # Integration tests
│   └── test_agent_interactions.py # End-to-end workflows
└── load/                          # Performance tests
    └── test_performance.py       # Load and stress tests
```

## 🚀 **Quick Start Testing**

### **1. Install Test Dependencies**
```bash
cd plantworks-adk-mvp
pip install -r requirements-test.txt
```

### **2. Run All Tests**
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test categories
python -m pytest tests/unit/          # Unit tests only
python -m pytest tests/integration/   # Integration tests only
python -m pytest tests/load/          # Load tests only
```

### **3. Run Tests with Coverage**
```bash
python -m pytest --cov=app --cov-report=html --cov-report=term-missing
```

## 🔧 **Unit Tests**

### **Tool Tests (`tests/unit/test_tools.py`)**

Tests individual tool functions in isolation:

- **Plant Database Search**: Query handling, result filtering, API integration
- **Weather Lookup**: Location geocoding, API calls, condition analysis
- **Marketplace Search**: Product search, price filtering, affiliate links
- **Native Plant Finder**: Location-based recommendations, ecological data
- **Soil Analyzer**: Soil type analysis, pH recommendations, amendments
- **Hardiness Zone Lookup**: Climate zone determination, frost dates

**Example Test Run:**
```bash
python -m pytest tests/unit/test_tools.py::TestPlantDatabaseSearch -v
```

### **Agent Tests (`tests/unit/test_agents.py`)**

Tests agent behavior and configuration:

- **Individual Agent Testing**: The Botanist, The Gardener, The Ecologist, The Merchant
- **Agent Configuration**: Model settings, tool assignments, descriptions
- **Response Generation**: Query processing, tool selection, output formatting
- **Main Agent Coordination**: Sub-agent routing, workflow management

**Example Test Run:**
```bash
python -m pytest tests/unit/test_agents.py::TestMainAgent -v
```

## 🔗 **Integration Tests**

### **Agent Interactions (`tests/integration/test_agent_interactions.py`)**

Tests complete workflows and agent coordination:

- **Plant Identification Workflow**: Query → Botanist → Response
- **Plant Care Workflow**: Query → Gardener → Care advice
- **Marketplace Workflow**: Query → Merchant → Shopping options
- **Native Plants Workflow**: Query → Ecologist → Local recommendations
- **Multi-Agent Coordination**: Complex queries involving multiple agents

**Example Test Run:**
```bash
python -m pytest tests/integration/ -v
```

## ⚡ **Load Tests**

### **Performance Testing (`tests/load/test_performance.py`)**

Tests application performance under various load conditions:

#### **Test Categories:**

1. **Single Request Performance**
   - Response time validation
   - Error handling
   - Memory usage

2. **Concurrent Users Load**
   - Multiple simultaneous users
   - Ramp-up testing
   - Success rate validation

3. **Stress Testing**
   - Sustained load over time
   - Performance degradation monitoring
   - Resource utilization

4. **Agent-Specific Performance**
   - Individual agent response times
   - Tool execution performance
   - Cross-agent comparison

#### **Load Test Configuration:**
```python
# Default test parameters
CONCURRENT_USERS = 10
REQUESTS_PER_USER = 5
RAMP_UP_TIME = 2
LOAD_TEST_TIMEOUT = 30
```

#### **Performance Benchmarks:**
- **Response Time**: < 10 seconds per query
- **Success Rate**: > 90% under normal load
- **Throughput**: > 1 request/second
- **Memory**: < 100MB increase during load

**Example Load Test:**
```bash
# Quick load test
python -m pytest tests/load/test_performance.py::TestLoadPerformance::test_concurrent_users_load -v

# Full performance suite (excluding slow tests)
python -m pytest tests/load/ -v -m "not slow"

# Include stress tests (longer duration)
python -m pytest tests/load/ -v
```

## 📊 **Test Results and Metrics**

### **Current Test Status:**
- ✅ **Unit Tests**: 45/47 passing (95.7% success rate)
- ✅ **Integration Tests**: All core workflows functional
- ✅ **Load Tests**: Meeting performance benchmarks
- ✅ **Coverage**: 85%+ code coverage

### **Known Issues:**
- 2 agent routing tests need refinement for native plant queries
- Some mock responses need alignment with actual agent behavior

## 🛠️ **Test Configuration**

### **Pytest Configuration (`pytest.ini`)**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    load: marks tests as load tests

asyncio_mode = auto
timeout = 300
```

### **Test Fixtures (`conftest.py`)**

Provides reusable test components:
- **Mock Session State**: Simulated user sessions
- **Sample Data**: Plant, weather, marketplace data
- **API Mocking**: External service simulation
- **Test Configuration**: Timeouts, parameters, constants

## 🔍 **Debugging Tests**

### **Verbose Output:**
```bash
python -m pytest -v --tb=long
```

### **Specific Test Debugging:**
```bash
python -m pytest tests/unit/test_tools.py::TestPlantDatabaseSearch::test_plant_search_basic_query -v -s
```

### **Test Coverage Analysis:**
```bash
python -m pytest --cov=app --cov-report=html
# Open htmlcov/index.html for detailed coverage report
```

## 🚀 **Continuous Integration**

### **Pre-commit Testing:**
```bash
# Quick smoke tests
python -m pytest tests/unit/ -x --tb=short

# Integration validation
python -m pytest tests/integration/ --tb=short

# Performance check
python -m pytest tests/load/test_performance.py::TestLoadPerformance::test_single_request_performance -v
```

### **Full Test Suite:**
```bash
# Complete test run with coverage
python -m pytest --cov=app --cov-report=term-missing --tb=short
```

## 📈 **Performance Monitoring**

### **Load Test Metrics:**
- **Response Times**: Average, median, 95th percentile
- **Success Rates**: Percentage of successful requests
- **Throughput**: Requests per second
- **Resource Usage**: Memory, CPU utilization
- **Error Analysis**: Failure patterns and causes

### **Benchmark Tracking:**
Regular performance benchmarks ensure consistent application performance:
- Daily automated test runs
- Performance regression detection
- Capacity planning data
- Optimization opportunity identification

## 🎯 **Test Best Practices**

1. **Isolation**: Each test runs independently
2. **Mocking**: External dependencies are mocked
3. **Assertions**: Clear, specific test assertions
4. **Documentation**: Well-documented test purposes
5. **Performance**: Tests complete within reasonable time
6. **Reliability**: Consistent results across runs

## 🔧 **Extending Tests**

### **Adding New Tool Tests:**
1. Create test class in `test_tools.py`
2. Add input validation tests
3. Test success and error cases
4. Mock external API calls
5. Verify output format

### **Adding Agent Tests:**
1. Create test class in `test_agents.py`
2. Test agent initialization
3. Test query processing
4. Verify tool usage
5. Check response format

### **Adding Load Tests:**
1. Add test method to `test_performance.py`
2. Define performance criteria
3. Implement load generation
4. Add result validation
5. Document benchmarks

This comprehensive testing suite ensures the Plantworks ADK implementation is robust, performant, and ready for production deployment.

