# ai-lls-lib

[![PyPI version](https://badge.fury.io/py/ai-lls-lib.svg)](https://badge.fury.io/py/ai-lls-lib)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/augmenting-integrations/ai-lls-lib/actions/workflows/pipeline.yaml/badge.svg)](https://github.com/augmenting-integrations/ai-lls-lib/actions)
[![License](https://img.shields.io/badge/license-proprietary-red.svg)](LICENSE)

Core Python library for Landline Scrubber - phone verification and DNC (Do Not Call) checking.

## Documentation & Reports

| Resource | Description |
|----------|-------------|
| [API Documentation](https://augmenting-integrations.github.io/ai-lls-lib/ai_lls_lib/) | pdoc-generated API reference |
| [Test Coverage](https://augmenting-integrations.github.io/ai-lls-lib/coverage/) | HTML coverage report |
| [Test Results](https://augmenting-integrations.github.io/ai-lls-lib/tests/test-report.html) | Unit test results |
| [Security Scans](https://augmenting-integrations.github.io/ai-lls-lib/security/security-reports.html) | Bandit, Safety, pip-audit results |
| [License Compliance](https://augmenting-integrations.github.io/ai-lls-lib/compliance/license-report.html) | Dependency license report |
| [PyPI Package](https://pypi.org/project/ai-lls-lib/) | Published package |

## Features

- Phone number normalization (E.164 format)
- Line type detection (mobile/landline/VoIP)
- DNC list checking via landlineremover.com API
- DynamoDB caching with 30-day TTL
- Bulk CSV processing with streaming support
- Stripe payment integration
- CLI for admin operations

## Installation

```bash
pip install ai-lls-lib
```

For development:

```bash
git clone https://github.com/augmenting-integrations/ai-lls-lib.git
cd ai-lls-lib
uv sync --all-extras
```

## Quick Start

### Single Phone Verification

```python
from ai_lls_lib import PhoneVerifier, DynamoDBCache

cache = DynamoDBCache(table_name="phone-cache")
verifier = PhoneVerifier(cache)

result = verifier.verify("+15551234567")
print(f"Line type: {result.line_type}")  # mobile, landline, voip, unknown
print(f"DNC: {result.dnc}")              # True/False
print(f"Cached: {result.cached}")        # True/False
```

### Bulk Processing

```python
from ai_lls_lib import BulkProcessor, PhoneVerifier, DynamoDBCache

cache = DynamoDBCache(table_name="phone-cache")
verifier = PhoneVerifier(cache)
processor = BulkProcessor(verifier)

csv_text = "name,phone\nJohn,+15551234567\nJane,+15551234568"
results = processor.process_csv(csv_text)

# Generate results CSV with added columns
results_csv = processor.generate_results_csv(csv_text, results)
```

### Streaming Large Files

```python
from ai_lls_lib import BulkProcessor, PhoneVerifier, DynamoDBCache

cache = DynamoDBCache(table_name="phone-cache")
verifier = PhoneVerifier(cache)
processor = BulkProcessor(verifier)

csv_lines = open('large_file.csv').readlines()
for batch in processor.process_csv_stream(csv_lines, batch_size=100):
    print(f"Processed batch of {len(batch)} phones")
```

### Custom Verification Providers

```python
from ai_lls_lib import PhoneVerifier, DynamoDBCache
from ai_lls_lib.providers import StubProvider

# Use stub provider for testing (deterministic results)
cache = DynamoDBCache(table_name="phone-cache")
provider = StubProvider()
verifier = PhoneVerifier(cache, provider=provider)
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LANDLINE_REMOVER_API_KEY` | API key for landlineremover.com | Yes (for production) |
| `AWS_REGION` | AWS region for DynamoDB | No (default: us-east-1) |

## CLI

```bash
# Verify single phone
ai-lls verify phone +15551234567 --stack landline-api

# Bulk verify CSV
ai-lls verify bulk input.csv -o output.csv --stack landline-api

# Cache management
ai-lls cache stats --stack landline-api
ai-lls cache get +15551234567 --stack landline-api

# Admin commands
ai-lls admin user-credits user123 --add 100
ai-lls admin api-keys --user user123

# Test stack management
ai-lls test-stack deploy
ai-lls test-stack status
ai-lls test-stack delete
```

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run linting
uv run pre-commit run --all-files

# Type checking
uv run mypy src/

# Build package
uv build
```

## Testing

```bash
# Unit tests (mocked AWS)
uv run pytest tests/unit -v

# Integration tests (requires AWS + test stack)
TEST_STACK_NAME=ai-lls-lib-test uv run pytest tests/integration -v

# Coverage report
uv run pytest --cov=src --cov-report=html --cov-fail-under=80
```

## Project Structure

```
src/ai_lls_lib/
├── __init__.py      # Public exports, version
├── core/            # PhoneVerifier, BulkProcessor, DynamoDBCache
├── auth/            # JWT/API key authentication
├── payment/         # StripeManager, CreditManager
├── admin/           # AdminService
├── providers/       # External API clients
├── cli/             # Command-line interface
└── testing/         # Test fixtures
```

## License

Proprietary - All rights reserved
