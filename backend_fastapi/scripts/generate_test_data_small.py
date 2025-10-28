#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Test Data Generator (Small Dataset)
Generate 1,000 project records for testing

Author: System
Date: 2025-10-28
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio

# Set environment before importing app modules
os.environ["ENVIRONMENT"] = "dev"

# Import from the main generator
from generate_test_data import BulkDataGenerator


async def main():
    """Quick test with small dataset"""
    print("\n")
    print("=" * 60)
    print(" " * 15 + "QUICK TEST DATA GENERATOR")
    print("=" * 60)
    print("\nThis will generate 1,000 test records for quick testing.\n")
    
    generator = BulkDataGenerator(total_projects=1000)
    generator.batch_size = 250  # Smaller batches for testing
    
    await generator.generate_all_data()
    
    print("\n[SUCCESS] Quick test data generated!\n")


if __name__ == "__main__":
    asyncio.run(main())

