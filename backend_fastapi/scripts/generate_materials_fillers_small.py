#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Materials & Fillers Generator (Small Dataset)
Generate 1,000 materials and 1,000 fillers for testing

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
from generate_materials_fillers import MaterialsFillersBulkGenerator


async def main():
    """Quick test with small dataset"""
    print("\n")
    print("=" * 60)
    print(" " * 10 + "QUICK MATERIALS & FILLERS GENERATOR")
    print("=" * 60)
    print("\nThis will generate 1,000 materials and 1,000 fillers for testing.\n")
    
    generator = MaterialsFillersBulkGenerator(
        num_materials=1000,
        num_fillers=1000
    )
    generator.batch_size = 250  # Smaller batches
    
    await generator.generate_all()
    
    print("\n[SUCCESS] Quick test data generated!\n")


if __name__ == "__main__":
    asyncio.run(main())

