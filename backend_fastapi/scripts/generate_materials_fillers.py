#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bulk Materials and Fillers Data Generator
Generate 500,000 materials and 500,000 fillers for PostgreSQL Database

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
from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

# Set environment before importing app modules
os.environ["ENVIRONMENT"] = "dev"

from app.core.database import async_engine, AsyncSessionLocal
from app.api.v1.modules.materials.model import MaterialModel, MaterialCategoryModel
from app.api.v1.modules.fillers.model import FillerModel, FillerTypeModel


# ==================== Data Templates ====================
class MaterialTemplates:
    """Material data generation templates"""
    
    # 化学品前缀
    CHEMICAL_PREFIXES = [
        "Poly", "Mono", "Di", "Tri", "Tetra", "Penta", "Hexa", "Cyclo",
        "Iso", "Neo", "Ortho", "Meta", "Para", "Alpha", "Beta", "Gamma"
    ]
    
    # 化学品中间部分
    CHEMICAL_MIDDLES = [
        "ethyl", "methyl", "propyl", "butyl", "pentyl", "hexyl",
        "acryl", "methacryl", "vinyl", "allyl", "phenyl", "benzyl",
        "glycol", "glycer", "ester", "ether", "amide", "amine",
        "urethane", "carbonate", "siloxane", "silane", "oxide"
    ]
    
    # 化学品后缀
    CHEMICAL_SUFFIXES = [
        "ate", "ene", "ane", "ide", "ite", "ol", "one", "al",
        "amine", "acid", "ester", "ether", "polymer", "resin"
    ]
    
    # 商品名前缀
    TRADE_PREFIXES = [
        "Lux", "Ultra", "Super", "Mega", "Hyper", "Neo", "Pro", "Max",
        "Elite", "Prime", "Apex", "Titan", "Omega", "Alpha", "Beta",
        "Delta", "Sigma", "Gamma", "Nova", "Stellar", "Quantum"
    ]
    
    # 商品名后缀
    TRADE_SUFFIXES = [
        "Tech", "Pol", "Chem", "Res", "Sol", "Flex", "Flow", "Bond",
        "Coat", "Cure", "Link", "Blend", "Mix", "Plus", "Pro", "X"
    ]
    
    # 供应商
    SUPPLIERS = [
        "BASF", "Dow Chemical", "DuPont", "Solvay", "Evonik", "Huntsman",
        "Arkema", "Covestro", "Eastman", "Momentive", "Wacker", "Shin-Etsu",
        "Mitsubishi Chemical", "Sumitomo", "Mitsui Chemicals", "LG Chem",
        "Samsung SDI", "Formosa Plastics", "SABIC", "Ineos", "Celanese",
        "Lanxess", "Clariant", "Croda", "Ashland", "Air Products",
        "Chemours", "Cabot", "Lubrizol", "Nouryon", "Univar Solutions"
    ]
    
    # 功能描述
    FUNCTIONS = [
        "Cross-linking agent", "Photoinitiator", "Reactive diluent",
        "Oligomer", "Monomer", "Co-monomer", "Surfactant", "Dispersant",
        "Wetting agent", "Defoamer", "Leveling agent", "Adhesion promoter",
        "UV absorber", "Antioxidant", "Stabilizer", "Catalyst",
        "Inhibitor", "Accelerator", "Plasticizer", "Flow modifier",
        "Rheology modifier", "Thickener", "Binder", "Film former"
    ]


class FillerTemplates:
    """Filler data generation templates"""
    
    # 填料基础名称
    BASE_NAMES = [
        "Silica", "Alumina", "Titania", "Zirconia", "Calcium Carbonate",
        "Barium Sulfate", "Talc", "Kaolin", "Mica", "Wollastonite",
        "Glass Beads", "Ceramic Beads", "Silicate", "Aluminosilicate",
        "Titanium Dioxide", "Zinc Oxide", "Magnesium Oxide", "Iron Oxide",
        "Carbon Black", "Graphene", "Carbon Nanotubes", "Nanocellulose"
    ]
    
    # 表面处理
    SURFACE_TREATMENTS = [
        "untreated", "silanized", "coated", "modified", "functionalized",
        "hydrophobic", "hydrophilic", "amino-functionalized", "epoxy-functionalized"
    ]
    
    # 等级/规格
    GRADES = [
        "Standard", "Premium", "High Purity", "Technical", "Industrial",
        "Pharmaceutical", "Food Grade", "Electronic", "Nano", "Micro",
        "Ultrafine", "Fine", "Medium", "Coarse"
    ]
    
    # 偶联剂
    COUPLING_AGENTS = [
        "APTES", "GPTMS", "MPTMS", "VTMS", "OTES", "PFOTES",
        "KH-550", "KH-560", "KH-570", "A-174", "A-187", "Z-6011",
        "Silquest A-1100", "Dynasylan AMEO", "CoatOSil 1770"
    ]
    
    # 供应商（填料专用）
    SUPPLIERS = [
        "Evonik", "Cabot", "Wacker", "Shin-Etsu", "PPG", "W.R. Grace",
        "Imerys", "Omya", "Minerals Technologies", "Huber Engineered Materials",
        "US Silica", "Sibelco", "Quarzwerke", "Hoffmann Mineral", "BASF",
        "AkzoNobel", "Huntsman", "Nanoshel", "Nanocyl", "Thomas Swan",
        "Sigma-Aldrich", "Merck", "Fisher Scientific", "Alfa Aesar"
    ]


class MaterialsFillersBulkGenerator:
    """High-performance bulk generator for materials and fillers"""
    
    def __init__(self, num_materials: int = 500000, num_fillers: int = 500000):
        self.num_materials = num_materials
        self.num_fillers = num_fillers
        self.batch_size = 5000
        self.material_categories = []
        self.filler_types = []
        
    async def load_reference_data(self, db: AsyncSession):
        """Load category and type data"""
        print("Loading reference data...")
        
        # Load material categories
        result = await db.execute(select(MaterialCategoryModel))
        self.material_categories = result.scalars().all()
        print(f"  + Loaded {len(self.material_categories)} material categories")
        
        # Load filler types
        result = await db.execute(select(FillerTypeModel))
        self.filler_types = result.scalars().all()
        print(f"  + Loaded {len(self.filler_types)} filler types")
        
        if not self.material_categories or not self.filler_types:
            raise ValueError("Missing categories or types! Please run create_tables.py first.")
    
    def generate_material_batch(self, start_idx: int, batch_size: int) -> List[dict]:
        """Generate a batch of material data"""
        materials = []
        
        for i in range(start_idx, start_idx + batch_size):
            category = random.choice(self.material_categories)
            supplier = random.choice(MaterialTemplates.SUPPLIERS)
            
            # Generate trade name
            prefix = random.choice(MaterialTemplates.TRADE_PREFIXES)
            suffix = random.choice(MaterialTemplates.TRADE_SUFFIXES)
            trade_name = f"{prefix}{suffix}-{i+1:06d}"
            
            # Generate CAS number (fake but realistic format)
            cas_part1 = random.randint(10000, 99999)
            cas_part2 = random.randint(10, 99)
            cas_part3 = random.randint(0, 9)
            cas_number = f"{cas_part1}-{cas_part2}-{cas_part3}"
            
            # Generate density (0.8 - 2.5 g/cm³)
            density = round(random.uniform(0.8, 2.5), 4)
            
            # Generate viscosity (1 - 10000 mPa·s)
            viscosity = round(random.uniform(1, 10000), 4) if random.random() < 0.8 else None
            
            # Generate function description
            function = random.choice(MaterialTemplates.FUNCTIONS)
            if random.random() < 0.3:
                function += f", {random.choice(MaterialTemplates.FUNCTIONS)}"
            
            materials.append({
                'TradeName': trade_name,
                'Category_FK': category.CategoryID,
                'Supplier': supplier,
                'CAS_Number': cas_number,
                'Density': density,
                'Viscosity': viscosity,
                'FunctionDescription': function
            })
        
        return materials
    
    def generate_filler_batch(self, start_idx: int, batch_size: int) -> List[dict]:
        """Generate a batch of filler data"""
        fillers = []
        
        for i in range(start_idx, start_idx + batch_size):
            filler_type = random.choice(self.filler_types)
            supplier = random.choice(FillerTemplates.SUPPLIERS)
            
            # Generate trade name
            base_name = random.choice(FillerTemplates.BASE_NAMES)
            grade = random.choice(FillerTemplates.GRADES)
            treatment = random.choice(FillerTemplates.SURFACE_TREATMENTS)
            trade_name = f"{base_name} {grade} ({treatment}) - {i+1:06d}"
            
            # Generate particle size
            d50 = random.uniform(0.01, 100)  # 0.01 to 100 microns
            if d50 < 0.1:
                particle_size = f"D50: {d50*1000:.0f} nm"
            else:
                particle_size = f"D50: {d50:.2f} μm"
            
            # Add distribution if needed
            if random.random() < 0.5:
                d10 = d50 * random.uniform(0.3, 0.6)
                d90 = d50 * random.uniform(1.5, 2.5)
                if d50 < 0.1:
                    particle_size += f", D10: {d10*1000:.0f} nm, D90: {d90*1000:.0f} nm"
                else:
                    particle_size += f", D10: {d10:.2f} μm, D90: {d90:.2f} μm"
            
            # Is silanized?
            is_silanized = 1 if "silanized" in treatment or random.random() < 0.4 else 0
            
            # Coupling agent
            coupling_agent = None
            if is_silanized:
                coupling_agent = random.choice(FillerTemplates.COUPLING_AGENTS)
            
            # Surface area (1 - 500 m²/g)
            # Smaller particles have larger surface area
            surface_area = round(random.uniform(50/d50, 500/d50), 4)
            surface_area = min(surface_area, 500)  # Cap at 500
            
            fillers.append({
                'TradeName': trade_name,
                'FillerType_FK': filler_type.FillerTypeID,
                'Supplier': supplier,
                'ParticleSize': particle_size,
                'IsSilanized': is_silanized,
                'CouplingAgent': coupling_agent,
                'SurfaceArea': surface_area
            })
        
        return fillers
    
    async def insert_batch(self, db: AsyncSession, table_name: str, data: List[dict]):
        """Bulk insert using raw SQL"""
        if not data:
            return
        
        columns = list(data[0].keys())
        placeholders = ', '.join([f':{col}' for col in columns])
        columns_str = ', '.join([f'"{col}"' for col in columns])
        
        sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})'
        
        await db.execute(text(sql), data)
    
    async def generate_materials(self, db: AsyncSession):
        """Generate all materials"""
        print("\n" + "=" * 80)
        print(f"GENERATING {self.num_materials:,} MATERIALS")
        print("=" * 80)
        
        batches = (self.num_materials + self.batch_size - 1) // self.batch_size
        start_time = datetime.now()
        total_generated = 0
        
        for batch_num in range(batches):
            batch_start = batch_num * self.batch_size
            current_batch_size = min(self.batch_size, self.num_materials - batch_start)
            
            # Generate and insert
            materials_data = self.generate_material_batch(batch_start, current_batch_size)
            await self.insert_batch(db, 'tbl_RawMaterials', materials_data)
            await db.commit()
            
            total_generated += current_batch_size
            
            # Progress
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = total_generated / elapsed if elapsed > 0 else 0
            progress = (total_generated / self.num_materials) * 100
            
            print(f"  Batch {batch_num + 1}/{batches}: "
                  f"{current_batch_size:,} records | "
                  f"Total: {total_generated:,}/{self.num_materials:,} ({progress:.1f}%) | "
                  f"Rate: {rate:.0f} rec/s")
        
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n+ Materials generation complete!")
        print(f"  Total: {total_generated:,} records in {duration:.1f} seconds ({rate:.0f} rec/s)")
    
    async def generate_fillers(self, db: AsyncSession):
        """Generate all fillers"""
        print("\n" + "=" * 80)
        print(f"GENERATING {self.num_fillers:,} FILLERS")
        print("=" * 80)
        
        batches = (self.num_fillers + self.batch_size - 1) // self.batch_size
        start_time = datetime.now()
        total_generated = 0
        
        for batch_num in range(batches):
            batch_start = batch_num * self.batch_size
            current_batch_size = min(self.batch_size, self.num_fillers - batch_start)
            
            # Generate and insert
            fillers_data = self.generate_filler_batch(batch_start, current_batch_size)
            await self.insert_batch(db, 'tbl_InorganicFillers', fillers_data)
            await db.commit()
            
            total_generated += current_batch_size
            
            # Progress
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = total_generated / elapsed if elapsed > 0 else 0
            progress = (total_generated / self.num_fillers) * 100
            
            print(f"  Batch {batch_num + 1}/{batches}: "
                  f"{current_batch_size:,} records | "
                  f"Total: {total_generated:,}/{self.num_fillers:,} ({progress:.1f}%) | "
                  f"Rate: {rate:.0f} rec/s")
        
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n+ Fillers generation complete!")
        print(f"  Total: {total_generated:,} records in {duration:.1f} seconds ({rate:.0f} rec/s)")
    
    async def generate_all(self):
        """Generate all data"""
        print("\n")
        print("=" * 80)
        print(" " * 20 + "MATERIALS & FILLERS GENERATOR")
        print("=" * 80)
        print(f"Target: {self.num_materials:,} materials + {self.num_fillers:,} fillers")
        print(f"Batch size: {self.batch_size:,}")
        print("=" * 80)
        
        async with AsyncSessionLocal() as db:
            try:
                # Load reference data
                await self.load_reference_data(db)
                
                overall_start = datetime.now()
                
                # Generate materials
                await self.generate_materials(db)
                
                # Generate fillers
                await self.generate_fillers(db)
                
                # Summary
                overall_duration = (datetime.now() - overall_start).total_seconds()
                total_records = self.num_materials + self.num_fillers
                
                print("\n" + "=" * 80)
                print("GENERATION COMPLETE!")
                print("=" * 80)
                print(f"Total materials: {self.num_materials:,}")
                print(f"Total fillers: {self.num_fillers:,}")
                print(f"Total records: {total_records:,}")
                print(f"Total time: {overall_duration:.1f} seconds ({overall_duration/60:.1f} minutes)")
                print(f"Average rate: {total_records/overall_duration:.0f} records/second")
                print("=" * 80)
                
                # Verify
                print("\nVerifying data...")
                result = await db.execute(text('SELECT COUNT(*) FROM "tbl_RawMaterials"'))
                mat_count = result.scalar()
                
                result = await db.execute(text('SELECT COUNT(*) FROM "tbl_InorganicFillers"'))
                fill_count = result.scalar()
                
                print(f"  + Materials in database: {mat_count:,}")
                print(f"  + Fillers in database: {fill_count:,}")
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
    print("║" + " " * 18 + "MATERIALS & FILLERS GENERATOR" + " " * 31 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    # Confirm
    response = input("This will generate 500,000 materials and 500,000 fillers. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Operation cancelled.")
        return
    
    generator = MaterialsFillersBulkGenerator(
        num_materials=500000,
        num_fillers=500000
    )
    await generator.generate_all()
    
    print("\n[SUCCESS] Data generation completed successfully!\n")


if __name__ == "__main__":
    asyncio.run(main())

