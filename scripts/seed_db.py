#!/usr/bin/env python3
"""
Philia Thrifts - Database Seeding Script
========================================
Generates 40 realistic thrift items for TikTok automation bot testing.

Price Distribution:
- 15 Budget Items (1,000 - 1,500 KES): Students/Hustlers
- 15 Mid-Range Items (2,000 - 4,500 KES): Working class  
- 10 Premium Items (5,000 - 12,000 KES): Collectors/Enthusiasts

SDR Testing: 8 items have tag_size/fit_notes discrepancies to test LLM accuracy.

Usage:
    python scripts/seed_db.py seed    # Add all items
    python scripts/seed_db.py clear   # Clear all inventory
"""
import asyncio
import logging
import random
import sys
from typing import List, Dict, Any
from sqlmodel import select

# Add parent directory to path for imports
sys.path.insert(0, "c:\\projects\\philia-thrifts")

from app.db.database import async_session_maker, engine
from app.db.models import Inventory, ProductCategory, ProductTier, InventoryStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# MOCK DATA: 40 THRIFT ITEMS FOR PHILIA THRIFTS
# ============================================================================

BUDGET_ITEMS: List[Dict[str, Any]] = [
    # Budget Clothes (1,000 - 1,500 KES)
    {
        "name": "Unbranded Vintage Flannel Shirt",
        "description": "Classic thrift find from Gikomba. Soft cotton, faded red check pattern.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 1000,
        "tag_size": "L",
        "measurements": {"pit_to_pit": "22in", "shoulder_to_hem": "29in", "waist": "N/A"},
        "fit_notes": "True to size. Roomy fit, good for layering over a tee.",
        "negotiable": False,
    },
    {
        "name": "Basic Cotton Oversized Tee",
        "description": "Heavyweight cotton, boxy fit. Perfect for Juja campus vibes.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 800,
        "tag_size": "XL",
        "measurements": {"pit_to_pit": "24in", "shoulder_to_hem": "30in", "waist": "N/A"},
        "fit_notes": "Very oversized. Tag says XL but fits like XXL.",  # DISCREPANCY #1
        "negotiable": False,
    },
    {
        "name": "Grade 1 Thrift Denim Jacket",
        "description": "Light wash, minor distressing. Entry-level vintage piece.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": "Unknown",
        "price_kes": 1200,
        "tag_size": "M",
        "measurements": {"pit_to_pit": "20in", "shoulder_to_hem": "26in", "waist": "N/A"},
        "fit_notes": "Cropped fit. Tag says M but fits like S.",  # DISCREPANCY #2
        "negotiable": False,
    },
    {
        "name": "Vintage Striped Polo Shirt",
        "description": "Navy and white stripes, pique cotton. Casual Friday ready.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 1100,
        "tag_size": "M",
        "measurements": {"pit_to_pit": "20.5in", "shoulder_to_hem": "27in", "waist": "N/A"},
        "fit_notes": "True to size. Slim through the body.",
        "negotiable": False,
    },
    {
        "name": "Unbranded Cargo Pants",
        "description": "Olive green, multiple pockets. Functional streetwear.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 1300,
        "tag_size": "W32 L30",
        "measurements": {"pit_to_pit": "N/A", "shoulder_to_hem": "N/A", "waist": "32in"},
        "fit_notes": "True to size. Relaxed fit through the leg.",
        "negotiable": False,
    },
    {
        "name": "Thrift Find: Corduroy Shirt",
        "description": "Brown corduroy, button-down. 90s dad vibes.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 1000,
        "tag_size": "L",
        "measurements": {"pit_to_pit": "21.5in", "shoulder_to_hem": "28in", "waist": "N/A"},
        "fit_notes": "Slightly oversized. Tag says L but fits like oversized M.",  # DISCREPANCY #3
        "negotiable": False,
    },
    {
        "name": "Basic Hoodie - Grey",
        "description": "Fleece-lined, kangaroo pocket. Essential layering piece.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 1400,
        "tag_size": "XL",
        "measurements": {"pit_to_pit": "23in", "shoulder_to_hem": "29in", "waist": "N/A"},
        "fit_notes": "True to size. Roomy and comfortable.",
        "negotiable": False,
    },
    {
        "name": "Vintage Graphic Band Tee",
        "description": "Worn print, soft fabric. Rock aesthetic on a budget.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 900,
        "tag_size": "M",
        "measurements": {"pit_to_pit": "19.5in", "shoulder_to_hem": "26in", "waist": "N/A"},
        "fit_notes": "Fitted. If you like baggy, size up.",
        "negotiable": False,
    },
    {
        "name": "Chino Shorts - Khaki",
        "description": "Mid-length, casual wear. Perfect for Nairobi heat.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 850,
        "tag_size": "W32",
        "measurements": {"pit_to_pit": "N/A", "shoulder_to_hem": "N/A", "waist": "32in"},
        "fit_notes": "True to size. Hits just above the knee.",
        "negotiable": False,
    },
    {
        "name": "Thrift Sweater Vest",
        "description": "Knitted, earth tones. Grandpa core aesthetic.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 950,
        "tag_size": "L",
        "measurements": {"pit_to_pit": "21in", "shoulder_to_hem": "25in", "waist": "N/A"},
        "fit_notes": "True to size. Layer over a shirt or tee.",
        "negotiable": False,
    },
    {
        "name": "Workwear Jacket - Navy",
        "description": "Durable fabric, utilitarian design. Labour-ready.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 1500,
        "tag_size": "XL",
        "measurements": {"pit_to_pit": "24in", "shoulder_to_hem": "28in", "waist": "N/A"},
        "fit_notes": "Boxy fit. Good for layering.",
        "negotiable": False,
    },
    {
        "name": "Vintage Tank Top - White",
        "description": "Ribbed cotton, sleeveless. Gym or street.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 600,
        "tag_size": "M",
        "measurements": {"pit_to_pit": "19in", "shoulder_to_hem": "26in", "waist": "N/A"},
        "fit_notes": "Fitted. Size up for relaxed fit.",
        "negotiable": False,
    },
    # Budget Shoes (1,000 - 1,500 KES)
    {
        "name": "Thrifted Running Shoes",
        "description": "Well-worn but plenty of life left. Basic runner.",
        "category": ProductCategory.SHOES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 1200,
        "tag_size": "US 9",
        "measurements": {"us_size": 9, "uk_size": 8, "cm": 27},
        "fit_notes": "True to size. Good condition.",
        "negotiable": False,
    },
    {
        "name": "Canvas Slip-Ons",
        "description": "Casual, breathable. Everyday errand shoes.",
        "category": ProductCategory.SHOES,
        "tier": ProductTier.BUDGET,
        "brand": None,
        "price_kes": 800,
        "tag_size": "US 10",
        "measurements": {"us_size": 10, "uk_size": 9, "cm": 28},
        "fit_notes": "True to size. Wide feet friendly.",
        "negotiable": False,
    },
    {
        "name": "Thrift Find: Leather Loafers",
        "description": "Brown leather, classic design. Smart casual option.",
        "category": ProductCategory.SHOES,
        "tier": ProductTier.BUDGET,
        "brand": "Unknown",
        "price_kes": 1400,
        "tag_size": "US 8",
        "measurements": {"us_size": 8, "uk_size": 7, "cm": 26},
        "fit_notes": "Tag says US 8 but fits like US 9. Runs large.",  # DISCREPANCY #4
        "negotiable": False,
    },
]

MID_RANGE_ITEMS: List[Dict[str, Any]] = [
    # Mid-Range Clothes (2,000 - 4,500 KES)
    {
        "name": "Zara Slim Fit Chinos",
        "description": "Navy blue, stretch cotton. Office to weekend versatility.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Zara",
        "price_kes": 2800,
        "tag_size": "W32 L32",
        "measurements": {"pit_to_pit": "N/A", "shoulder_to_hem": "N/A", "waist": "32in"},
        "fit_notes": "True to size. TTS, slight stretch in the waist.",
        "negotiable": False,
    },
    {
        "name": "H&M Oversized Hoodie",
        "description": "Grey melange, fleece-lined. Streetwear essential.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.MID_RANGE,
        "brand": "H&M",
        "price_kes": 2200,
        "tag_size": "L",
        "measurements": {"pit_to_pit": "23in", "shoulder_to_hem": "28in", "waist": "N/A"},
        "fit_notes": "Oversized fit. Tag says L but fits like XL.",  # DISCREPANCY #5
        "negotiable": False,
    },
    {
        "name": "Levi's 501 Original Jeans",
        "description": "Dark wash, button fly. Classic American denim.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Levi's",
        "price_kes": 3500,
        "tag_size": "W32 L30",
        "measurements": {"pit_to_pit": "N/A", "shoulder_to_hem": "N/A", "waist": "32in"},
        "fit_notes": "Rigid denim. Will stretch with wear. Size up if between sizes.",
        "negotiable": False,
    },
    {
        "name": "Nike Sportswear Windbreaker",
        "description": "Black with white swoosh, lightweight. Athleisure staple.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Nike",
        "price_kes": 3200,
        "tag_size": "M",
        "measurements": {"pit_to_pit": "21in", "shoulder_to_hem": "27in", "waist": "N/A"},
        "fit_notes": "Athletic fit. True to size for Nike.",
        "negotiable": False,
    },
    {
        "name": "Adidas Originals Track Jacket",
        "description": "Navy with white stripes, trefoil logo. Retro sportswear.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Adidas",
        "price_kes": 2800,
        "tag_size": "L",
        "measurements": {"pit_to_pit": "22in", "shoulder_to_hem": "28in", "waist": "N/A"},
        "fit_notes": "True to size. Classic Adidas fit.",
        "negotiable": False,
    },
    {
        "name": "Uniqlo Heattech Turtleneck",
        "description": "Black, thermal fabric. Layering essential for cold season.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Uniqlo",
        "price_kes": 1800,
        "tag_size": "M",
        "measurements": {"pit_to_pit": "20in", "shoulder_to_hem": "26in", "waist": "N/A"},
        "fit_notes": "Fitted. Size up if you want roomier fit.",
        "negotiable": False,
    },
    {
        "name": "Tommy Hilfiger Denim Shirt",
        "description": "Light wash, flag logo. Preppy meets street.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Tommy Hilfiger",
        "price_kes": 2900,
        "tag_size": "L",
        "measurements": {"pit_to_pit": "22in", "shoulder_to_hem": "29in", "waist": "N/A"},
        "fit_notes": "True to size. Roomy enough to layer.",
        "negotiable": False,
    },
    {
        "name": "Ralph Lauren Polo Shirt",
        "description": "Navy, classic fit. The icon.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Ralph Lauren",
        "price_kes": 3800,
        "tag_size": "M",
        "measurements": {"pit_to_pit": "21in", "shoulder_to_hem": "27.5in", "waist": "N/A"},
        "fit_notes": "Classic fit. Not too slim, not too baggy.",
        "negotiable": False,
    },
    {
        "name": "Puma Crewneck Sweatshirt",
        "description": "Burgundy, logo embroidered. Casual comfort.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Puma",
        "price_kes": 2400,
        "tag_size": "XL",
        "measurements": {"pit_to_pit": "24in", "shoulder_to_hem": "29in", "waist": "N/A"},
        "fit_notes": "Tag says XL but fits like L. Size up.",  # DISCREPANCY #6
        "negotiable": False,
    },
    {
        "name": "Calvin Klein Jeans Jacket",
        "description": "Vintage wash, CK patch. 90s revival.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Calvin Klein",
        "price_kes": 4200,
        "tag_size": "L",
        "measurements": {"pit_to_pit": "22.5in", "shoulder_to_hem": "26in", "waist": "N/A"},
        "fit_notes": "Cropped fit. True to size.",
        "negotiable": False,
    },
    {
        "name": "Gap Vintage Hoodie",
        "description": "Faded black, heavyweight. 90s archive piece.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Gap",
        "price_kes": 2000,
        "tag_size": "XL",
        "measurements": {"pit_to_pit": "25in", "shoulder_to_hem": "30in", "waist": "N/A"},
        "fit_notes": "Very oversized. True to vintage Gap sizing.",
        "negotiable": False,
    },
    # Mid-Range Shoes (2,000 - 4,500 KES)
    {
        "name": "Nike Air Force 1 - White",
        "description": "Classic, some creasing. The staple sneaker.",
        "category": ProductCategory.SHOES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Nike",
        "price_kes": 3500,
        "tag_size": "US 10",
        "measurements": {"us_size": 10, "uk_size": 9, "cm": 28},
        "fit_notes": "True to size. Classic AF1 fit.",
        "negotiable": False,
    },
    {
        "name": "Adidas Stan Smith - Green",
        "description": "Clean condition, retro tennis style.",
        "category": ProductCategory.SHOES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Adidas",
        "price_kes": 3200,
        "tag_size": "US 9",
        "measurements": {"us_size": 9, "uk_size": 8.5, "cm": 27},
        "fit_notes": "True to size. Leather will soften.",
        "negotiable": False,
    },
    {
        "name": "Vans Old Skool - Black",
        "description": "Skate classic, good grip remaining. Street uniform.",
        "category": ProductCategory.SHOES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Vans",
        "price_kes": 2800,
        "tag_size": "US 10.5",
        "measurements": {"us_size": 10.5, "uk_size": 10, "cm": 28.5},
        "fit_notes": "Snug fit. Tag says 10.5 but fits like 10.",  # DISCREPANCY #7
        "negotiable": False,
    },
    {
        "name": "Converse Chuck 70 - Navy",
        "description": "Canvas high-top, vintage detailing. Better quality than standard Chucks.",
        "category": ProductCategory.SHOES,
        "tier": ProductTier.MID_RANGE,
        "brand": "Converse",
        "price_kes": 3000,
        "tag_size": "US 9",
        "measurements": {"us_size": 9, "uk_size": 8, "cm": 27},
        "fit_notes": "Size down half size from your usual. Chuck 70s run big.",
        "negotiable": False,
    },
]

PREMIUM_ITEMS: List[Dict[str, Any]] = [
    # Premium Clothes (5,000 - 12,000 KES)
    {
        "name": "Vintage 90s Carhartt Detroit Jacket",
        "description": "Blanket-lined, duck canvas. Workwear grail. Made in USA era.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.PREMIUM,
        "brand": "Carhartt",
        "price_kes": 9500,
        "tag_size": "L",
        "measurements": {"pit_to_pit": "24in", "shoulder_to_hem": "26in", "waist": "N/A"},
        "fit_notes": "Tag says L, but vintage Carhartt sizing fits like M. Boxy workwear cut.",  # DISCREPANCY #8
        "negotiable": True,
    },
    {
        "name": "North Face Nuptse Puffer 700",
        "description": "Black, 700-fill down. Winter essential. Packs into pocket.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.PREMIUM,
        "brand": "The North Face",
        "price_kes": 8500,
        "tag_size": "M",
        "measurements": {"pit_to_pit": "23in", "shoulder_to_hem": "27in", "waist": "N/A"},
        "fit_notes": "Puffy fit. True to size but bulky due to fill.",
        "negotiable": True,
    },
    {
        "name": "Supreme Box Logo Hoodie",
        "description": "Heather grey, classic red box logo. Streetwear status symbol.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.PREMIUM,
        "brand": "Supreme",
        "price_kes": 12000,
        "tag_size": "L",
        "measurements": {"pit_to_pit": "23.5in", "shoulder_to_hem": "29in", "waist": "N/A"},
        "fit_notes": "True to size. Heavyweight cotton.",
        "negotiable": True,
    },
    {
        "name": "Stüssy Stock Logo Jacket",
        "description": "Nylon, embroidered logo. Surf meets street aesthetic.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.PREMIUM,
        "brand": "Stüssy",
        "price_kes": 6800,
        "tag_size": "XL",
        "measurements": {"pit_to_pit": "25in", "shoulder_to_hem": "30in", "waist": "N/A"},
        "fit_notes": "Oversized fit. True to Stüssy sizing.",
        "negotiable": True,
    },
    {
        "name": "Patagonia Retro Pile Fleece",
        "description": "Tan, deep pile fleece. Outdoor heritage brand.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.PREMIUM,
        "brand": "Patagonia",
        "price_kes": 7200,
        "tag_size": "M",
        "measurements": {"pit_to_pit": "22in", "shoulder_to_hem": "27in", "waist": "N/A"},
        "fit_notes": "Roomy fit. Size down if you want slimmer.",
        "negotiable": True,
    },
    {
        "name": "Aime Leon Dore Wool Overcoat",
        "description": "Camel, tailored fit. Elevated streetwear.",
        "category": ProductCategory.CLOTHES,
        "tier": ProductTier.PREMIUM,
        "brand": "Aime Leon Dore",
        "price_kes": 11500,
        "tag_size": "L",
        "measurements": {"pit_to_pit": "23in", "shoulder_to_hem": "38in", "waist": "N/A"},
        "fit_notes": "Tailored fit. True to size. Length hits mid-thigh.",
        "negotiable": True,
    },
    # Premium Shoes (5,000 - 12,000 KES)
    {
        "name": "Air Jordan 1 High - Chicago",
        "description": "2015 release, some creasing. The grail.",
        "category": ProductCategory.SHOES,
        "tier": ProductTier.PREMIUM,
        "brand": "Jordan",
        "price_kes": 11000,
        "tag_size": "US 9.5",
        "measurements": {"us_size": 9.5, "uk_size": 8.5, "cm": 27.5},
        "fit_notes": "True to size. Classic Jordan 1 fit.",
        "negotiable": True,
    },
    {
        "name": "Nike Dunk Low - Syracuse",
        "description": "Orange and white, college colorway. Dunk hype.",
        "category": ProductCategory.SHOES,
        "tier": ProductTier.PREMIUM,
        "brand": "Nike",
        "price_kes": 9000,
        "tag_size": "US 10",
        "measurements": {"us_size": 10, "uk_size": 9, "cm": 28},
        "fit_notes": "True to size. Narrow fit.",
        "negotiable": True,
    },
    {
        "name": "New Balance 990v5 - Grey",
        "description": "Made in USA, dad shoe royalty. Comfort and status.",
        "category": ProductCategory.SHOES,
        "tier": ProductTier.PREMIUM,
        "brand": "New Balance",
        "price_kes": 7800,
        "tag_size": "US 10.5",
        "measurements": {"us_size": 10.5, "uk_size": 10, "cm": 28.5},
        "fit_notes": "True to size. Wide feet friendly.",
        "negotiable": True,
    },
    {
        "name": "Yeezy Boost 350 V2 - Zebra",
        "description": "White/black stripe, Boost comfort. Kanye era classic.",
        "category": ProductCategory.SHOES,
        "tier": ProductTier.PREMIUM,
        "brand": "Adidas Yeezy",
        "price_kes": 9500,
        "tag_size": "US 11",
        "measurements": {"us_size": 11, "uk_size": 10.5, "cm": 29},
        "fit_notes": "Size up half size from your usual. Yeezys run small.",
        "negotiable": True,
    },
]


# ============================================================================
# SEEDING FUNCTIONS
# ============================================================================

async def clear_inventory() -> None:
    """Clear all inventory items from the database."""
    async with async_session_maker() as session:
        from sqlalchemy import delete
        
        logger.info("Clearing inventory table...")
        result = await session.execute(delete(Inventory))
        await session.commit()
        logger.info(f"Deleted {result.rowcount} inventory items")


async def seed_inventory() -> None:
    """Seed the database with 40 thrift items."""
    async with async_session_maker() as session:
        # Combine all items
        all_items = BUDGET_ITEMS + MID_RANGE_ITEMS + PREMIUM_ITEMS
        
        logger.info(f"Seeding {len(all_items)} items into inventory...")
        
        # Generate SKU numbers for each tier
        budget_count = 0
        mid_count = 0
        premium_count = 0
        
        created_items = []
        
        for item_data in all_items:
            # Generate SKU based on tier
            if item_data["tier"] == ProductTier.BUDGET:
                budget_count += 1
                sku = f"TH-B-{budget_count:03d}"
            elif item_data["tier"] == ProductTier.MID_RANGE:
                mid_count += 1
                sku = f"TH-M-{mid_count:03d}"
            else:  # PREMIUM
                premium_count += 1
                sku = f"TH-P-{premium_count:03d}"
            
            # Create inventory item
            inventory_item = Inventory(
                sku=sku,
                name=item_data["name"],
                description=item_data["description"],
                category=item_data["category"],
                tier=item_data["tier"],
                brand=item_data["brand"],
                price_kes=item_data["price_kes"],
                negotiable=item_data["negotiable"],
                tag_size=item_data["tag_size"],
                measurements=item_data["measurements"],
                fit_notes=item_data["fit_notes"],
                status=InventoryStatus.AVAILABLE,
            )
            created_items.append(inventory_item)
            
            logger.info(f"Created: {sku} - {item_data['name']} ({item_data['tier'].value}, {item_data['price_kes']} KES)")
        
        # Bulk insert
        session.add_all(created_items)
        await session.commit()
        
        logger.info(f"\n✅ Successfully seeded {len(created_items)} items!")
        logger.info(f"   Budget: {budget_count} items")
        logger.info(f"   Mid-Range: {mid_count} items")
        logger.info(f"   Premium: {premium_count} items")
        
        # Count items with sizing discrepancies
        discrepancy_count = sum(
            1 for item in all_items 
            if "tag says" in item["fit_notes"].lower() or "fits like" in item["fit_notes"].lower()
        )
        logger.info(f"   Items with sizing discrepancies: {discrepancy_count} (LLM test cases)")


async def verify_seed() -> None:
    """Verify the seeding was successful."""
    async with async_session_maker() as session:
        from sqlalchemy import func, select
        
        # Count by tier
        for tier in [ProductTier.BUDGET, ProductTier.MID_RANGE, ProductTier.PREMIUM]:
            result = await session.execute(
                select(func.count(Inventory.id)).where(Inventory.tier == tier)
            )
            count = result.scalar()
            logger.info(f"{tier.value}: {count} items in database")
        
        # Count by category
        for category in [ProductCategory.CLOTHES, ProductCategory.SHOES]:
            result = await session.execute(
                select(func.count(Inventory.id)).where(Inventory.category == category)
            )
            count = result.scalar()
            logger.info(f"{category.value}: {count} items in database")
        
        # Show sample items
        logger.info("\n📦 Sample items:")
        result = await session.execute(
            select(Inventory).limit(3)
        )
        items = result.scalars().all()
        for item in items:
            logger.info(f"   {item.sku}: {item.name} - {item.price_kes} KES")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point for the seed script."""
    if len(sys.argv) < 2:
        print("Usage: python seed_db.py [seed|clear|verify]")
        print("  seed   - Clear and re-seed the database")
        print("  clear  - Clear all inventory items")
        print("  verify - Verify current inventory count")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "clear":
        await clear_inventory()
    elif command == "seed":
        await clear_inventory()
        await seed_inventory()
        await verify_seed()
    elif command == "verify":
        await verify_seed()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python seed_db.py [seed|clear|verify]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
