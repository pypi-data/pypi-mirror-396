"""
Command-line interface for ge-snowflake-validator
"""

import argparse
import sys
from ..validator import Validator


def profile_command():
    """CLI: ge-snowflake-profile"""
    parser = argparse.ArgumentParser(
        description='Profile Snowflake tables and generate expectations'
    )
    parser.add_argument('--account', required=True, help='Snowflake account')
    parser.add_argument('--user', required=True, help='Snowflake username')
    parser.add_argument('--password', required=True, help='Snowflake password')
    parser.add_argument('--warehouse', required=True, help='Warehouse name')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--schema', required=True, help='Schema name')
    parser.add_argument('--role', help='Role (optional)')
    
    args = parser.parse_args()
    
    validator = Validator(
        account=args.account,
        user=args.user,
        password=args.password,
        warehouse=args.warehouse,
        database=args.database,
        schema=args.schema,
        role=args.role
    )
    
    results = validator.profile_all()
    print(f"\n✅ Profiling complete!")


def validate_command():
    """CLI: ge-snowflake-validate"""
    parser = argparse.ArgumentParser(
        description='Validate Snowflake data quality'
    )
    parser.add_argument('--account', required=True, help='Snowflake account')
    parser.add_argument('--user', required=True, help='Snowflake username')
    parser.add_argument('--password', required=True, help='Snowflake password')
    parser.add_argument('--warehouse', required=True, help='Warehouse name')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--schema', required=True, help='Schema name')
    parser.add_argument('--role', help='Role (optional)')
    
    args = parser.parse_args()
    
    validator = Validator(
        account=args.account,
        user=args.user,
        password=args.password,
        warehouse=args.warehouse,
        database=args.database,
        schema=args.schema,
        role=args.role
    )
    
    results = validator.validate_all()
    
    print(f"\n{'='*60}")
    print(f"VALIDATION RESULTS")
    print(f"{'='*60}")
    print(f"Total Checks: {results['total_checks']}")
    print(f"Passed: {results['passed']} ✅")
    print(f"Failed: {results['failed']} ❌")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"{'='*60}\n")
    
    if results['failed'] > 0:
        sys.exit(1)


def init_command():
    """CLI: ge-snowflake-init"""
    print("🚀 Initializing GE Snowflake Validator...")
    print("✅ No initialization needed - you're ready to go!")
    print("\nUsage:")
    print("  ge-snowflake-validate --account XXX --user XXX --password XXX ...")