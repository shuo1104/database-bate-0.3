#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bulk Test Data Generator for PostgreSQL Database
Generate 990,000 project records with related data

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
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

# Set environment before importing app modules
os.environ["ENVIRONMENT"] = "dev"

from app.core.database import async_engine, AsyncSessionLocal
from app.api.v1.modules.projects.model import (
    ProjectModel, 
    ProjectTypeModel,
    FormulaCompositionModel,
    TestResultInkModel,
    TestResultCoatingModel,
    TestResult3DPrintModel,
    TestResultCompositeModel
)
from app.api.v1.modules.materials.model import MaterialModel, MaterialCategoryModel
from app.api.v1.modules.fillers.model import FillerModel, FillerTypeModel


# ==================== Data Templates ====================
class DataTemplates:
    """Data generation templates"""
    
    PROJECT_NAMES = [
        "High Performance", "Advanced", "Experimental", "Prototype", "Research",
        "Development", "Commercial", "Industrial", "Laboratory", "Testing"
    ]
    
    PROJECT_SUFFIXES = [
        "Formulation", "Mix", "Blend", "Composite", "Solution",
        "System", "Matrix", "Compound", "Polymer", "Material"
    ]
    
    SUBSTRATES = [
        "Glass", "Metal", "Plastic", "Wood", "Paper",
        "Ceramic", "Composite", "Fabric", "Silicon", "Polymer"
    ]
    
    APPLICATIONS = [
        "Coating", "Printing", "3D Manufacturing", "Industrial Use",
        "Consumer Products", "Electronics", "Automotive", "Aerospace",
        "Medical Devices", "Packaging"
    ]
    
    FORMULATORS = [
        "Zhang Wei", "Li Ming", "Wang Fang", "Liu Yang", "Chen Jing",
        "Zhou Lin", "Wu Qiang", "Xu Min", "Sun Hui", "Ma Xin",
        "John Smith", "Emma Johnson", "Michael Brown", "Sophia Davis",
        "James Wilson", "Olivia Taylor", "Robert Anderson", "Emily Thomas"
    ]
    
    ADDITION_METHODS = [
        "Direct mixing", "Pre-dispersion", "In-situ polymerization",
        "Melt blending", "Solution blending", "Mechanical stirring",
        "High-speed mixing", "Ball milling", "Ultrasonic dispersion"
    ]
    
    NOTES = [
        "Good performance", "Needs optimization", "Excellent results",
        "Further testing required", "Ready for production", "Under evaluation",
        "Promising candidate", "Baseline formulation", "Modified version"
    ]


class BulkDataGenerator:
    """High-performance bulk data generator"""
    
    def __init__(self, total_projects: int = 990000):
        self.total_projects = total_projects
        self.batch_size = 5000  # Process 5000 records per batch
        self.project_types = []
        self.materials = []
        self.fillers = []
        
    async def load_reference_data(self, db: AsyncSession):
        """Load reference data (types, materials, fillers)"""
        print("Loading reference data...")
        
        # Load project types
        result = await db.execute(select(ProjectTypeModel))
        self.project_types = result.scalars().all()
        print(f"  + Loaded {len(self.project_types)} project types")
        
        # Load materials
        result = await db.execute(select(MaterialModel))
        self.materials = result.scalars().all()
        print(f"  + Loaded {len(self.materials)} materials")
        
        # Load fillers
        result = await db.execute(select(FillerModel))
        self.fillers = result.scalars().all()
        print(f"  + Loaded {len(self.fillers)} fillers")
        
        if not self.project_types:
            raise ValueError("No project types found! Please run create_tables.py first.")
    
    def generate_project_batch(self, start_idx: int, batch_size: int) -> List[dict]:
        """Generate a batch of project data"""
        projects = []
        base_date = datetime(2020, 1, 1)
        
        for i in range(start_idx, start_idx + batch_size):
            project_type = random.choice(self.project_types)
            formulator = random.choice(DataTemplates.FORMULATORS)
            
            # Generate date within last 5 years
            days_offset = random.randint(0, 1825)  # 5 years
            formula_date = base_date + timedelta(days=days_offset)
            
            # Generate formula code
            type_code = project_type.TypeCode
            formula_code = f"{type_code}{formula_date.strftime('%Y%m%d')}{i:06d}"
            
            project_name = f"{random.choice(DataTemplates.PROJECT_NAMES)} {random.choice(DataTemplates.PROJECT_SUFFIXES)} #{i+1}"
            substrate = f"{random.choice(DataTemplates.SUBSTRATES)} - {random.choice(DataTemplates.APPLICATIONS)}"
            
            projects.append({
                'ProjectName': project_name,
                'ProjectType_FK': project_type.TypeID,
                'SubstrateApplication': substrate,
                'FormulatorName': formulator,
                'FormulationDate': formula_date.date(),
                'FormulaCode': formula_code
            })
        
        return projects
    
    def generate_compositions(self, project_ids: List[int]) -> List[dict]:
        """Generate formula compositions for projects"""
        compositions = []
        
        for project_id in project_ids:
            # Each project has 3-8 components
            num_components = random.randint(3, 8)
            total_percentage = 0
            
            for j in range(num_components):
                # Last component fills to 100%
                if j == num_components - 1:
                    percentage = 100 - total_percentage
                else:
                    # Random percentage, ensure sum doesn't exceed 100
                    max_percentage = min(50, 100 - total_percentage - (num_components - j - 1))
                    percentage = random.uniform(5, max_percentage)
                
                total_percentage += percentage
                
                # 70% chance material, 30% chance filler
                if random.random() < 0.7 and self.materials:
                    material_id = random.choice(self.materials).MaterialID
                    filler_id = None
                elif self.fillers:
                    material_id = None
                    filler_id = random.choice(self.fillers).FillerID
                else:
                    material_id = random.choice(self.materials).MaterialID if self.materials else None
                    filler_id = None
                
                compositions.append({
                    'ProjectID_FK': project_id,
                    'MaterialID_FK': material_id,
                    'FillerID_FK': filler_id,
                    'WeightPercentage': round(percentage, 4),
                    'AdditionMethod': random.choice(DataTemplates.ADDITION_METHODS),
                    'Remarks': random.choice(DataTemplates.NOTES) if random.random() < 0.3 else None
                })
        
        return compositions
    
    def generate_test_results(self, project_ids: List[int], type_name: str) -> List[dict]:
        """Generate test results based on project type"""
        results = []
        base_date = datetime(2020, 1, 1)
        
        for project_id in project_ids:
            test_date = base_date + timedelta(days=random.randint(0, 1825))
            
            if type_name == "喷墨":
                results.append({
                    'ProjectID_FK': project_id,
                    'Ink_Viscosity': f"{random.uniform(5, 50):.2f} mPa·s",
                    'Ink_Reactivity': f"{random.uniform(0.5, 10):.2f} s",
                    'Ink_ParticleSize': f"{random.uniform(20, 200):.1f} nm",
                    'Ink_SurfaceTension': f"{random.uniform(25, 45):.2f} mN/m",
                    'Ink_ColorValue': f"L*={random.uniform(30,90):.1f}, a*={random.uniform(-20,20):.1f}, b*={random.uniform(-20,20):.1f}",
                    'Ink_RheologyNote': random.choice(DataTemplates.NOTES) if random.random() < 0.4 else None,
                    'TestDate': test_date.date(),
                    'Notes': random.choice(DataTemplates.NOTES) if random.random() < 0.5 else None
                })
            
            elif type_name == "涂层":
                results.append({
                    'ProjectID_FK': project_id,
                    'Coating_Adhesion': f"{random.randint(0, 5)}B",
                    'Coating_Transparency': f"{random.uniform(80, 99):.1f}%",
                    'Coating_SurfaceHardness': f"{random.choice(['2H', 'H', 'F', 'HB', 'B', '2B'])}",
                    'Coating_ChemicalResistance': random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
                    'Coating_CostEstimate': f"{random.uniform(5, 50):.2f} EUR/kg",
                    'TestDate': test_date.date(),
                    'Notes': random.choice(DataTemplates.NOTES) if random.random() < 0.5 else None
                })
            
            elif type_name == "3D打印":
                results.append({
                    'ProjectID_FK': project_id,
                    'Print3D_Shrinkage': f"{random.uniform(0.1, 5):.2f}%",
                    'Print3D_YoungsModulus': f"{random.uniform(500, 3000):.0f} MPa",
                    'Print3D_FlexuralStrength': f"{random.uniform(30, 150):.1f} MPa",
                    'Print3D_ShoreHardness': f"{random.choice(['Shore A', 'Shore D'])} {random.randint(60, 95)}",
                    'Print3D_ImpactResistance': f"{random.uniform(2, 20):.1f} kJ/m²",
                    'TestDate': test_date.date(),
                    'Notes': random.choice(DataTemplates.NOTES) if random.random() < 0.5 else None
                })
            
            elif type_name == "复合材料":
                results.append({
                    'ProjectID_FK': project_id,
                    'Composite_FlexuralStrength': f"{random.uniform(50, 200):.1f} MPa",
                    'Composite_YoungsModulus': f"{random.uniform(1000, 5000):.0f} MPa",
                    'Composite_ImpactResistance': f"{random.uniform(5, 30):.1f} kJ/m²",
                    'Composite_ConversionRate': f"{random.uniform(85, 99):.1f}%",
                    'Composite_WaterAbsorption': f"{random.uniform(0.1, 2):.2f}%",
                    'TestDate': test_date.date(),
                    'Notes': random.choice(DataTemplates.NOTES) if random.random() < 0.5 else None
                })
        
        return results
    
    async def insert_batch(self, db: AsyncSession, table_name: str, data: List[dict]):
        """Bulk insert using raw SQL for maximum performance"""
        if not data:
            return
        
        # Build column names and placeholders
        columns = list(data[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        columns_str = ', '.join([f'"{col}"' for col in columns])
        
        # Quote table name for PostgreSQL case sensitivity
        sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})'
        
        await db.execute(text(sql), data)
    
    async def generate_all_data(self):
        """Main generation process"""
        print("=" * 80)
        print("BULK TEST DATA GENERATOR")
        print("=" * 80)
        print(f"Target: {self.total_projects:,} project records")
        print(f"Batch size: {self.batch_size:,}")
        print("=" * 80)
        
        async with AsyncSessionLocal() as db:
            try:
                # Load reference data
                await self.load_reference_data(db)
                
                # Calculate type distribution
                type_distribution = {}
                projects_per_type = self.total_projects // len(self.project_types)
                
                for i, ptype in enumerate(self.project_types):
                    if i == len(self.project_types) - 1:
                        # Last type gets remaining
                        type_distribution[ptype] = self.total_projects - (projects_per_type * i)
                    else:
                        type_distribution[ptype] = projects_per_type
                
                print("\nDistribution:")
                for ptype, count in type_distribution.items():
                    print(f"  - {ptype.TypeName}: {count:,} projects")
                
                print("\n" + "=" * 80)
                print("Starting data generation...")
                print("=" * 80)
                
                total_generated = 0
                start_time = datetime.now()
                global_idx = 1
                
                for project_type, count in type_distribution.items():
                    print(f"\nProcessing: {project_type.TypeName} ({count:,} records)")
                    print("-" * 80)
                    
                    batches = (count + self.batch_size - 1) // self.batch_size
                    
                    for batch_num in range(batches):
                        batch_start = batch_num * self.batch_size
                        current_batch_size = min(self.batch_size, count - batch_start)
                        
                        # Generate projects
                        projects_data = self.generate_project_batch(global_idx, current_batch_size)
                        
                        # Insert projects and get IDs
                        await self.insert_batch(db, 'tbl_ProjectInfo', projects_data)
                        await db.commit()
                        
                        # Get inserted project IDs
                        result = await db.execute(
                            select(ProjectModel.ProjectID)
                            .order_by(ProjectModel.ProjectID.desc())
                            .limit(current_batch_size)
                        )
                        project_ids = [row[0] for row in result.fetchall()]
                        project_ids.reverse()  # Restore original order
                        
                        # Generate compositions
                        compositions_data = self.generate_compositions(project_ids)
                        await self.insert_batch(db, 'tbl_FormulaComposition', compositions_data)
                        
                        # Generate test results based on type
                        test_results = self.generate_test_results(project_ids, project_type.TypeName)
                        
                        if project_type.TypeName == "喷墨":
                            await self.insert_batch(db, 'tbl_TestResults_Ink', test_results)
                        elif project_type.TypeName == "涂层":
                            await self.insert_batch(db, 'tbl_TestResults_Coating', test_results)
                        elif project_type.TypeName == "3D打印":
                            await self.insert_batch(db, 'tbl_TestResults_3DPrint', test_results)
                        elif project_type.TypeName == "复合材料":
                            await self.insert_batch(db, 'tbl_TestResults_Composite', test_results)
                        
                        await db.commit()
                        
                        total_generated += current_batch_size
                        global_idx += current_batch_size
                        
                        # Progress update
                        elapsed = (datetime.now() - start_time).total_seconds()
                        rate = total_generated / elapsed if elapsed > 0 else 0
                        progress = (total_generated / self.total_projects) * 100
                        
                        print(f"  Batch {batch_num + 1}/{batches}: "
                              f"{current_batch_size:,} records | "
                              f"Total: {total_generated:,}/{self.total_projects:,} ({progress:.1f}%) | "
                              f"Rate: {rate:.0f} rec/s")
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print("\n" + "=" * 80)
                print("GENERATION COMPLETE!")
                print("=" * 80)
                print(f"Total records generated: {total_generated:,}")
                print(f"Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
                print(f"Average rate: {total_generated/duration:.0f} records/second")
                print("=" * 80)
                
                # Verify counts
                print("\nVerifying data...")
                result = await db.execute(text('SELECT COUNT(*) FROM "tbl_ProjectInfo"'))
                project_count = result.scalar()
                
                result = await db.execute(text('SELECT COUNT(*) FROM "tbl_FormulaComposition"'))
                composition_count = result.scalar()
                
                print(f"  + Projects: {project_count:,}")
                print(f"  + Compositions: {composition_count:,}")
                print("\n" + "=" * 80)
                
            except Exception as e:
                print(f"\nX ERROR: {e}")
                import traceback
                traceback.print_exc()
                await db.rollback()
                raise


async def main():
    """Main entry point"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "BULK TEST DATA GENERATOR" + " " * 34 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    # Confirm before starting
    response = input("This will generate 990,000 test records. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Operation cancelled.")
        return
    
    generator = BulkDataGenerator(total_projects=990000)
    await generator.generate_all_data()
    
    print("\n[SUCCESS] Data generation completed successfully!\n")


if __name__ == "__main__":
    asyncio.run(main())

