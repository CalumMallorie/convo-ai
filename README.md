# Convo-AI

A conversational AI project optimized for Mac M-series chips, using free and local tools.

![Test Status](https://github.com/calummallorie/convo-ai/actions/workflows/test.yml/badge.svg) ![Coverage](https://img.shields.io/badge/coverage-92%25-green) [![Test Coverage](https://img.shields.io/badge/coverage-92%25-green)](https://gist.github.com/CalumMallorie/0ced90b88d93397be075cdf0cbb8cf03)

## Features

- LLM client with streaming support
- Text-to-Speech with MPS optimization
- Comprehensive test suite with CI integration
- Performance benchmarking and metrics tracking
- Optimized for Mac M-series chips

## Setup

1. Clone the repository:
```bash
git clone https://github.com/calummallorie/convo-ai.git
cd convo-ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .  # Install package in development mode
```

4. Run the tests:
```bash
python -m pytest
```

## Test Coverage

This project maintains a high test coverage (currently 92%). You can generate a coverage report by running:

```bash
python scripts/run_coverage.py
```

This will:
- Run all tests with coverage
- Generate HTML and XML coverage reports
- Update the coverage Gist (if configured)
- Generate a coverage badge

The coverage reports will be available in the `reports/coverage/html` directory.

## Performance Benchmarking

The project includes built-in performance benchmarking tools. You can use the `@benchmark` decorator to track function execution time and memory usage:

```python
from src.benchmarks import benchmark

@benchmark("my_function")
def my_function():
    # Your code here
    pass
```

Metrics are automatically saved to `output/performance_metrics.json` and include:
- Execution time
- Memory usage
- CPU utilization
- System metrics

You can view benchmark results by running:
```bash
python scripts/benchmark_demo.py
```

## Automated Testing

This project uses GitHub Actions for automated testing. Every time you push code or create a pull request, the tests will run automatically.

The CI environment is configured to:
- Run tests with coverage
- Mock external services (LLM, TTS) to ensure tests pass consistently
- Provide a coverage report
- Track performance metrics

To see the test results:
1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Click on any workflow run to see the results

## Project Roadmap

### Completed
- ✅ LLM client with streaming support 
- ✅ TTS client with MPS optimization
- ✅ Comprehensive test suite
- ✅ Configuration system
- ✅ CI integration with GitHub Actions
- ✅ Test coverage reporting (92%)
- ✅ Mock LLM service in CI
- ✅ Performance benchmarks
- ✅ Demo scripts

### In Progress
- 🔄 Enhance documentation
- 🔄 Implement caching for LLM responses

### Planned
- 📅 Add support for audio input (speech-to-text)
- 📅 Real-time performance monitoring
- 📅 Automated performance regression testing

## Project Structure

```
convo-ai/
├── .github/
│   └── workflows/        # GitHub Actions workflows
├── scripts/
│   ├── run_coverage.py   # Run tests with coverage
│   ├── create_coverage_gist.py
│   ├── update_coverage_gist.py
│   ├── generate_coverage_badge.py
│   └── benchmark_demo.py # Performance benchmarking demo
├── src/                  # Source code
│   ├── benchmarks.py     # Performance tracking utilities
│   ├── llm.py           # LLM client implementation
│   └── tts.py           # Text-to-speech implementation
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── setup.py             # Package installation
├── pytest.ini           # Pytest configuration
└── README.md            # This file
```

## Contributing

1. Create a new branch for your changes
2. Make your changes
3. Run the tests to make sure everything works
4. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 