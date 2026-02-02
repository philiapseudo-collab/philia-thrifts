"""
Database seeding script for realistic thrift inventory.

Usage:
    python scripts/seed_db.py

This script populates the inventory table with 10 realistic thrift items
including vintage clothing, streetwear, and designer pieces.
"""
import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import async_session_maker
from app.db.models import Inventory, InventoryStatus


# ============================================================================
# Realistic Thrift Inventory Data
# ============================================================================

SEED_ITEMS = [
    {
        "sku": "VNT-NIKE-WB-001",
        "name": "Vintage Nike Windbreaker",
        "description": "90s Nike windbreaker in excellent condition. Classic colorblock design with swoosh logo. Perfect for retro streetwear fits.",
        "price": Decimal("45.00"),
        "size_label": "L",
        "measurements": {
            "pit_to_pit": 24.5,
            "length": 28.0,
            "sleeve_length": 25.5
        },
        "status": InventoryStatus.AVAILABLE,
        "image_url": "https://example.com/nike-windbreaker.jpg"
    },
    {
        "sku": "CRH-DET-BLK-002",
        "name": "Carhartt Detroit Jacket - Black",
        "description": "Classic Carhartt Detroit jacket. Heavy-duty duck canvas with blanket lining. Minimal wear, broken in perfectly.",
        "price": Decimal("89.99"),
        "size_label": "XL",
        "measurements": {
            "pit_to_pit": 26.0,
            "length": 30.5,
            "shoulder": 21.0,
            "sleeve_length": 26.0
        },
        "status": InventoryStatus.AVAILABLE,
        "image_url": "https://example.com/carhartt-jacket.jpg"
    },
    {
        "sku": "LEV-501-W32L30-003",
        "name": "Levi's 501 Original Fit Jeans",
        "description": "Classic straight leg Levi's 501. Medium wash, no major distressing. True vintage feel.",
        "price": Decimal("35.00"),
        "size_label": "W32 L30",
        "measurements": {
            "waist": 32.0,
            "inseam": 30.0,
            "rise": 11.5,
            "leg_opening": 8.0
        },
        "status": InventoryStatus.AVAILABLE,
        "image_url": "https://example.com/levis-501.jpg"
    },
    {
        "sku": "ADI-TRK-NVY-004",
        "name": "Adidas Track Jacket - Navy",
        "description": "Adidas originals track jacket with trefoil logo. Navy blue with white stripes. Clean, no flaws.",
        "price": Decimal("38.50"),
        "size_label": "M",
        "measurements": {
            "pit_to_pit": 22.0,
            "length": 26.5,
            "sleeve_length": 24.0
        },
        "status": InventoryStatus.AVAILABLE,
        "image_url": "https://example.com/adidas-track.jpg"
    },
    {
        "sku": "PTG-FLC-GRY-005",
        "name": "Patagonia Synchilla Fleece",
        "description": "Patagonia classic synchilla fleece pullover. Gray colorway. Super warm and cozy. Light pilling (normal for fleece).",
        "price": Decimal("55.00"),
        "size_label": "L",
        "measurements": {
            "pit_to_pit": 23.5,
            "length": 27.0,
            "sleeve_length": 25.0
        },
        "status": InventoryStatus.AVAILABLE,
        "image_url": "https://example.com/patagonia-fleece.jpg"
    },
    {
        "sku": "CHM-WRK-BLU-006",
        "name": "Vintage Chambray Work Shirt",
        "description": "Thick chambray work shirt (no tags). Perfectly faded blue. Chest pocket, single needle stitching. True workwear staple.",
        "price": Decimal("42.00"),
        "size_label": "M (fits oversized)",
        "measurements": {
            "pit_to_pit": 21.5,
            "length": 28.5,
            "shoulder": 18.5,
            "sleeve_length": 24.5
        },
        "status": InventoryStatus.AVAILABLE,
        "image_url": "https://example.com/chambray-shirt.jpg"
    },
    {
        "sku": "NBL-992-GRY-007",
        "name": "New Balance 992 - Gray",
        "description": "New Balance 992 'Made in USA'. Gray colorway. Used but excellent condition, tons of life left. Cleaned and ready to wear.",
        "price": Decimal("125.00"),
        "size_label": "US 10",
        "measurements": {
            "length": 11.5,
            "width": 4.25
        },
        "status": InventoryStatus.RESERVED,  # Example of reserved item
        "image_url": "https://example.com/nb-992.jpg"
    },
    {
        "sku": "RLH-PLO-NVY-008",
        "name": "Ralph Lauren Polo - Navy",
        "description": "Classic Ralph Lauren polo shirt. Navy with green pony logo. No stains, perfect for smart casual.",
        "price": Decimal("28.00"),
        "size_label": "L",
        "measurements": {
            "pit_to_pit": 22.0,
            "length": 29.0
        },
        "status": InventoryStatus.AVAILABLE,
        "image_url": "https://example.com/rl-polo.jpg"
    },
    {
        "sku": "CMP-BCH-TAN-009",
        "name": "Champion Reverse Weave - Tan",
        "description": "Champion reverse weave crewneck. Tan/beige colorway. Thick heavyweight cotton. Small C logo on chest.",
        "price": Decimal("65.00"),
        "size_label": "XL (fits L)",
        "measurements": {
            "pit_to_pit": 23.0,
            "length": 26.5,
            "sleeve_length": 23.5
        },
        "status": InventoryStatus.AVAILABLE,
        "image_url": "https://example.com/champion-crewneck.jpg"
    },
    {
        "sku": "DKS-CHN-BLK-010",
        "name": "Dickies Chino Pants - Black",
        "description": "Dickies 874 work pants. Black, regular fit. Hemmed to 30in inseam. Great condition.",
        "price": Decimal("32.00"),
        "size_label": "W34 L30",
        "measurements": {
            "waist": 34.0,
            "inseam": 30.0,
            "rise": 12.0,
            "leg_opening": 8.5
        },
        "status": InventoryStatus.SOLD,  # Example of sold item
        "image_url": "https://example.com/dickies-chino.jpg"
    }
]


# ============================================================================
# Seed Functions
# ============================================================================

async def seed_inventory():
    """
    Seed database with realistic thrift inventory items.
    
    Safety:
    - Checks for existing items by SKU (idempotent)
    - Only adds new items
    """
    async with async_session_maker() as session:
        async with session.begin():
            print("🌱 Starting database seed...")
            
            added_count = 0
            skipped_count = 0
            
            for item_data in SEED_ITEMS:
                # Check if item already exists
                from sqlalchemy import select
                statement = select(Inventory).where(
                    Inventory.sku == item_data["sku"]
                )
                result = await session.execute(statement)
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"⏭️  Skipping {item_data['sku']} (already exists)")
                    skipped_count += 1
                    continue
                
                # Create new inventory item
                item = Inventory(**item_data)
                session.add(item)
                print(f"✅ Added: {item_data['name']} ({item_data['sku']})")
                added_count += 1
            
            await session.commit()
            
            print("\n" + "="*60)
            print(f"✨ Seed completed!")
            print(f"   Added: {added_count} items")
            print(f"   Skipped: {skipped_count} items (already existed)")
            print("="*60)


async def clear_inventory():
    """
    Clear all inventory items (DANGEROUS - use with caution).
    
    This is useful for testing, but should NEVER be run in production.
    """
    print("⚠️  WARNING: This will DELETE all inventory items!")
    confirmation = input("Type 'DELETE ALL' to confirm: ")
    
    if confirmation != "DELETE ALL":
        print("❌ Aborted. No items were deleted.")
        return
    
    async with async_session_maker() as session:
        async with session.begin():
            from sqlalchemy import delete
            statement = delete(Inventory)
            result = await session.execute(statement)
            await session.commit()
            
            print(f"🗑️  Deleted {result.rowcount} items")


# ============================================================================
# CLI Entry Point
# ============================================================================

async def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database seeding utility")
    parser.add_argument(
        "command",
        choices=["seed", "clear"],
        help="Command to run (seed=add items, clear=delete all)"
    )
    
    args = parser.parse_args()
    
    if args.command == "seed":
        await seed_inventory()
    elif args.command == "clear":
        await clear_inventory()


if __name__ == "__main__":
    asyncio.run(main())
