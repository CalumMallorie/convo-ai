# Convo-AI

A conversational AI project optimized for Mac M-series chips, using free and local tools.

![Test Status](https://github.com/calummallorie/convo-ai/actions/workflows/test.yml/badge.svg) ![Coverage](https://img.shields.io/badge/coverage-88%25-green) [![Test Coverage](https://img.shields.io/badge/coverage-88%25-green)](https://gist.github.com/CalumMallorie/0ced90b88d93397be075cdf0cbb8cf03)

## Features

- LLM client with streaming support
- Text-to-Speech with MPS optimization
- Comprehensive test suite with CI integration
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
```

4. Run the tests:
```bash
python -m pytest
```

## Test Coverage

This project maintains a high test coverage (currently 89%). You can generate a coverage report by running:

```bash
python scripts/run_coverage.py
```

This will:
- Run all tests with coverage
- Generate HTML and XML coverage reports
- Update the coverage Gist (if configured)
- Generate a coverage badge

The coverage reports will be available in the `reports/coverage/html` directory.

## Automated Testing

This project uses GitHub Actions for automated testing. Every time you push code or create a pull request, the tests will run automatically.

The CI environment is configured to:
- Run tests with coverage
- Mock external services (LLM, TTS) to ensure tests pass consistently
- Provide a coverage report

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
- ✅ Test coverage reporting (89%)
- ✅ Mock LLM service in CI

### In Progress
- 🔄 Performance benchmarks
- 🔄 Demo scripts

### Planned
- 📅 Enhance documentation
- 📅 Implement caching for LLM responses
- 📅 Add support for audio input (speech-to-text)

## Project Structure

```
convo-ai/
├── .github/
│   └── workflows/        # GitHub Actions workflows
├── scripts/              # Utility scripts
│   ├── run_coverage.py   # Run tests with coverage
│   ├── create_coverage_gist.py
│   ├── update_coverage_gist.py
│   └── generate_coverage_badge.py
├── src/                  # Source code
├── tests/                # Test files
├── requirements.txt      # Python dependencies
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