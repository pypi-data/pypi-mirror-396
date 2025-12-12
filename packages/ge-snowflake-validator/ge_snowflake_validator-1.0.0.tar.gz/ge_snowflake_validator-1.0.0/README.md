# GE Snowflake Validator

Dynamic data quality validation for Snowflake using Great Expectations.

## Installation
```bash
pip install ge-snowflake-validator
```

## Quick Start
```python
from ge_snowflake import Validator

validator = Validator(
    account='your_account',
    user='your_user',
    password='your_password',
    warehouse='YOUR_WAREHOUSE',
    database='YOUR_DATABASE',
    schema='YOUR_SCHEMA'
)

# Profile tables (one-time)
validator.profile_all()

# Validate data (daily)
results = validator.validate_all()
print(f'Success Rate: {results[\"success_rate\"]}%')
```

## Features

- 289+ automated quality checks
- Zero configuration needed
- Dynamic profiling (adapts to your schema)
- Lightning fast (all validation in Snowflake)

## License

MIT License - see LICENSE file for details.
