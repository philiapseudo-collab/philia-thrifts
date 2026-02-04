"""Direct database seeding endpoint - runs seeding inside the app context."""
import logging
from typing import Dict, List, Any
from fastapi import APIRouter
from sqlalchemy import delete
from app.db.database import async_session_maker
from app.db.models import Inventory

logger = logging.getLogger(__name__)
router = APIRouter(tags=["seed"])


# 40 thrift items data
BUDGET_ITEMS: List[Dict[str, Any]] = [
    {"name": "Unbranded Vintage Flannel Shirt", "description": "Classic thrift find from Gikomba. Soft cotton, faded red check pattern.", "category": "CLOTHES", "tier": "BUDGET", "brand": None, "price_kes": 1000, "tag_size": "L", "measurements": {"pit_to_pit": "22in", "shoulder_to_hem": "29in"}, "fit_notes": "True to size. Roomy fit, good for layering over a tee.", "negotiable": False},
    {"name": "Basic Cotton Oversized Tee", "description": "Heavyweight cotton, boxy fit. Perfect for Juja campus vibes.", "category": "CLOTHES", "tier": "BUDGET", "brand": None, "price_kes": 800, "tag_size": "XL", "measurements": {"pit_to_pit": "24in", "shoulder_to_hem": "30in"}, "fit_notes": "Very oversized. Tag says XL but fits like XXL.", "negotiable": False},
    {"name": "Grade 1 Thrift Denim Jacket", "description": "Light wash, minor distressing. Entry-level vintage piece.", "category": "CLOTHES", "tier": "BUDGET", "brand": "Unknown", "price_kes": 1200, "tag_size": "M", "measurements": {"pit_to_pit": "20in", "shoulder_to_hem": "26in"}, "fit_notes": "Cropped fit. Tag says M but fits like S.", "negotiable": False},
    {"name": "Vintage Striped Polo Shirt", "description": "Navy and white stripes, pique cotton. Casual Friday ready.", "category": "CLOTHES", "tier": "BUDGET", "brand": None, "price_kes": 1100, "tag_size": "M", "measurements": {"pit_to_pit": "20.5in", "shoulder_to_hem": "27in"}, "fit_notes": "True to size. Slim through the body.", "negotiable": False},
    {"name": "Unbranded Cargo Pants", "description": "Olive green, multiple pockets. Functional streetwear.", "category": "CLOTHES", "tier": "BUDGET", "brand": None, "price_kes": 1300, "tag_size": "W32 L30", "measurements": {"waist": "32in"}, "fit_notes": "True to size. Relaxed fit through the leg.", "negotiable": False},
    {"name": "Thrift Find: Corduroy Shirt", "description": "Brown corduroy, button-down. 90s dad vibes.", "category": "CLOTHES", "tier": "BUDGET", "brand": None, "price_kes": 1000, "tag_size": "L", "measurements": {"pit_to_pit": "21.5in", "shoulder_to_hem": "28in"}, "fit_notes": "Slightly oversized. Tag says L but fits like oversized M.", "negotiable": False},
    {"name": "Basic Hoodie - Grey", "description": "Fleece-lined, kangaroo pocket. Essential layering piece.", "category": "CLOTHES", "tier": "BUDGET", "brand": None, "price_kes": 1400, "tag_size": "XL", "measurements": {"pit_to_pit": "23in", "shoulder_to_hem": "29in"}, "fit_notes": "True to size. Roomy and comfortable.", "negotiable": False},
    {"name": "Vintage Graphic Band Tee", "description": "Worn print, soft fabric. Rock aesthetic on a budget.", "category": "CLOTHES", "tier": "BUDGET", "brand": None, "price_kes": 900, "tag_size": "M", "measurements": {"pit_to_pit": "19.5in", "shoulder_to_hem": "26in"}, "fit_notes": "Fitted. If you like baggy, size up.", "negotiable": False},
    {"name": "Chino Shorts - Khaki", "description": "Mid-length, casual wear. Perfect for Nairobi heat.", "category": "CLOTHES", "tier": "BUDGET", "brand": None, "price_kes": 850, "tag_size": "W32", "measurements": {"waist": "32in"}, "fit_notes": "True to size. Hits just above the knee.", "negotiable": False},
    {"name": "Thrift Sweater Vest", "description": "Knitted, earth tones. Grandpa core aesthetic.", "category": "CLOTHES", "tier": "BUDGET", "brand": None, "price_kes": 950, "tag_size": "L", "measurements": {"pit_to_pit": "21in", "shoulder_to_hem": "25in"}, "fit_notes": "True to size. Layer over a shirt or tee.", "negotiable": False},
    {"name": "Workwear Jacket - Navy", "description": "Durable fabric, utilitarian design. Labour-ready.", "category": "CLOTHES", "tier": "BUDGET", "brand": None, "price_kes": 1500, "tag_size": "XL", "measurements": {"pit_to_pit": "24in", "shoulder_to_hem": "28in"}, "fit_notes": "Boxy fit. Good for layering.", "negotiable": False},
    {"name": "Vintage Tank Top - White", "description": "Ribbed cotton, sleeveless. Gym or street.", "category": "CLOTHES", "tier": "BUDGET", "brand": None, "price_kes": 600, "tag_size": "M", "measurements": {"pit_to_pit": "19in", "shoulder_to_hem": "26in"}, "fit_notes": "Fitted. Size up for relaxed fit.", "negotiable": False},
    {"name": "Thrifted Running Shoes", "description": "Well-worn but plenty of life left. Basic runner.", "category": "SHOES", "tier": "BUDGET", "brand": None, "price_kes": 1200, "tag_size": "US 9", "measurements": {"us_size": 9, "uk_size": 8, "cm": 27}, "fit_notes": "True to size. Good condition.", "negotiable": False},
    {"name": "Canvas Slip-Ons", "description": "Casual, breathable. Everyday errand shoes.", "category": "SHOES", "tier": "BUDGET", "brand": None, "price_kes": 800, "tag_size": "US 10", "measurements": {"us_size": 10, "uk_size": 9, "cm": 28}, "fit_notes": "True to size. Wide feet friendly.", "negotiable": False},
    {"name": "Thrift Find: Leather Loafers", "description": "Brown leather, classic design. Smart casual option.", "category": "SHOES", "tier": "BUDGET", "brand": "Unknown", "price_kes": 1400, "tag_size": "US 8", "measurements": {"us_size": 8, "uk_size": 7, "cm": 26}, "fit_notes": "Tag says US 8 but fits like US 9. Runs large.", "negotiable": False},
]

MID_RANGE_ITEMS: List[Dict[str, Any]] = [
    {"name": "Zara Slim Fit Chinos", "description": "Navy blue, stretch cotton. Office to weekend versatility.", "category": "CLOTHES", "tier": "MID_RANGE", "brand": "Zara", "price_kes": 2800, "tag_size": "W32 L32", "measurements": {"waist": "32in"}, "fit_notes": "True to size. TTS, slight stretch in the waist.", "negotiable": False},
    {"name": "H&M Oversized Hoodie", "description": "Grey melange, fleece-lined. Streetwear essential.", "category": "CLOTHES", "tier": "MID_RANGE", "brand": "H&M", "price_kes": 2200, "tag_size": "L", "measurements": {"pit_to_pit": "23in", "shoulder_to_hem": "28in"}, "fit_notes": "Oversized fit. Tag says L but fits like XL.", "negotiable": False},
    {"name": "Levi's 501 Original Jeans", "description": "Dark wash, button fly. Classic American denim.", "category": "CLOTHES", "tier": "MID_RANGE", "brand": "Levi's", "price_kes": 3500, "tag_size": "W32 L30", "measurements": {"waist": "32in"}, "fit_notes": "Rigid denim. Will stretch with wear. Size up if between sizes.", "negotiable": False},
    {"name": "Nike Sportswear Windbreaker", "description": "Black with white swoosh, lightweight. Athleisure staple.", "category": "CLOTHES", "tier": "MID_RANGE", "brand": "Nike", "price_kes": 3200, "tag_size": "M", "measurements": {"pit_to_pit": "21in", "shoulder_to_hem": "27in"}, "fit_notes": "Athletic fit. True to size for Nike.", "negotiable": False},
    {"name": "Adidas Originals Track Jacket", "description": "Navy with white stripes, trefoil logo. Retro sportswear.", "category": "CLOTHES", "tier": "MID_RANGE", "brand": "Adidas", "price_kes": 2800, "tag_size": "L", "measurements": {"pit_to_pit": "22in", "shoulder_to_hem": "28in"}, "fit_notes": "True to size. Classic Adidas fit.", "negotiable": False},
    {"name": "Uniqlo Heattech Turtleneck", "description": "Black, thermal fabric. Layering essential for cold season.", "category": "CLOTHES", "tier": "MID_RANGE", "brand": "Uniqlo", "price_kes": 1800, "tag_size": "M", "measurements": {"pit_to_pit": "20in", "shoulder_to_hem": "26in"}, "fit_notes": "Fitted. Size up if you want roomier fit.", "negotiable": False},
    {"name": "Tommy Hilfiger Denim Shirt", "description": "Light wash, flag logo. Preppy meets street.", "category": "CLOTHES", "tier": "MID_RANGE", "brand": "Tommy Hilfiger", "price_kes": 2900, "tag_size": "L", "measurements": {"pit_to_pit": "22in", "shoulder_to_hem": "29in"}, "fit_notes": "True to size. Roomy enough to layer.", "negotiable": False},
    {"name": "Ralph Lauren Polo Shirt", "description": "Navy, classic fit. The icon.", "category": "CLOTHES", "tier": "MID_RANGE", "brand": "Ralph Lauren", "price_kes": 3800, "tag_size": "M", "measurements": {"pit_to_pit": "21in", "shoulder_to_hem": "27.5in"}, "fit_notes": "Classic fit. Not too slim, not too baggy.", "negotiable": False},
    {"name": "Puma Crewneck Sweatshirt", "description": "Burgundy, logo embroidered. Casual comfort.", "category": "CLOTHES", "tier": "MID_RANGE", "brand": "Puma", "price_kes": 2400, "tag_size": "XL", "measurements": {"pit_to_pit": "24in", "shoulder_to_hem": "29in"}, "fit_notes": "Tag says XL but fits like L. Size up.", "negotiable": False},
    {"name": "Calvin Klein Jeans Jacket", "description": "Vintage wash, CK patch. 90s revival.", "category": "CLOTHES", "tier": "MID_RANGE", "brand": "Calvin Klein", "price_kes": 4200, "tag_size": "L", "measurements": {"pit_to_pit": "22.5in", "shoulder_to_hem": "26in"}, "fit_notes": "Cropped fit. True to size.", "negotiable": False},
    {"name": "Gap Vintage Hoodie", "description": "Faded black, heavyweight. 90s archive piece.", "category": "CLOTHES", "tier": "MID_RANGE", "brand": "Gap", "price_kes": 2000, "tag_size": "XL", "measurements": {"pit_to_pit": "25in", "shoulder_to_hem": "30in"}, "fit_notes": "Very oversized. True to vintage Gap sizing.", "negotiable": False},
    {"name": "Nike Air Force 1 - White", "description": "Classic, some creasing. The staple sneaker.", "category": "SHOES", "tier": "MID_RANGE", "brand": "Nike", "price_kes": 3500, "tag_size": "US 10", "measurements": {"us_size": 10, "uk_size": 9, "cm": 28}, "fit_notes": "True to size. Classic AF1 fit.", "negotiable": False},
    {"name": "Adidas Stan Smith - Green", "description": "Clean condition, retro tennis style.", "category": "SHOES", "tier": "MID_RANGE", "brand": "Adidas", "price_kes": 3200, "tag_size": "US 9", "measurements": {"us_size": 9, "uk_size": 8.5, "cm": 27}, "fit_notes": "True to size. Leather will soften.", "negotiable": False},
    {"name": "Vans Old Skool - Black", "description": "Skate classic, good grip remaining. Street uniform.", "category": "SHOES", "tier": "MID_RANGE", "brand": "Vans", "price_kes": 2800, "tag_size": "US 10.5", "measurements": {"us_size": 10.5, "uk_size": 10, "cm": 28.5}, "fit_notes": "Snug fit. Tag says 10.5 but fits like 10.", "negotiable": False},
    {"name": "Converse Chuck 70 - Navy", "description": "Canvas high-top, vintage detailing. Better quality than standard Chucks.", "category": "SHOES", "tier": "MID_RANGE", "brand": "Converse", "price_kes": 3000, "tag_size": "US 9", "measurements": {"us_size": 9, "uk_size": 8, "cm": 27}, "fit_notes": "Size down half size from your usual. Chuck 70s run big.", "negotiable": False},
]

PREMIUM_ITEMS: List[Dict[str, Any]] = [
    {"name": "Vintage 90s Carhartt Detroit Jacket", "description": "Blanket-lined, duck canvas. Workwear grail. Made in USA era.", "category": "CLOTHES", "tier": "PREMIUM", "brand": "Carhartt", "price_kes": 9500, "tag_size": "L", "measurements": {"pit_to_pit": "24in", "shoulder_to_hem": "26in"}, "fit_notes": "Tag says L, but vintage Carhartt sizing fits like M. Boxy workwear cut.", "negotiable": True},
    {"name": "North Face Nuptse Puffer 700", "description": "Black, 700-fill down. Winter essential. Packs into pocket.", "category": "CLOTHES", "tier": "PREMIUM", "brand": "The North Face", "price_kes": 8500, "tag_size": "M", "measurements": {"pit_to_pit": "23in", "shoulder_to_hem": "27in"}, "fit_notes": "Puffy fit. True to size but bulky due to fill.", "negotiable": True},
    {"name": "Supreme Box Logo Hoodie", "description": "Heather grey, classic red box logo. Streetwear status symbol.", "category": "CLOTHES", "tier": "PREMIUM", "brand": "Supreme", "price_kes": 12000, "tag_size": "L", "measurements": {"pit_to_pit": "23.5in", "shoulder_to_hem": "29in"}, "fit_notes": "True to size. Heavyweight cotton.", "negotiable": True},
    {"name": "Stüssy Stock Logo Jacket", "description": "Nylon, embroidered logo. Surf meets street aesthetic.", "category": "CLOTHES", "tier": "PREMIUM", "brand": "Stüssy", "price_kes": 6800, "tag_size": "XL", "measurements": {"pit_to_pit": "25in", "shoulder_to_hem": "30in"}, "fit_notes": "Oversized fit. True to Stüssy sizing.", "negotiable": True},
    {"name": "Patagonia Retro Pile Fleece", "description": "Tan, deep pile fleece. Outdoor heritage brand.", "category": "CLOTHES", "tier": "PREMIUM", "brand": "Patagonia", "price_kes": 7200, "tag_size": "M", "measurements": {"pit_to_pit": "22in", "shoulder_to_hem": "27in"}, "fit_notes": "Roomy fit. Size down if you want slimmer.", "negotiable": True},
    {"name": "Aime Leon Dore Wool Overcoat", "description": "Camel, tailored fit. Elevated streetwear.", "category": "CLOTHES", "tier": "PREMIUM", "brand": "Aime Leon Dore", "price_kes": 11500, "tag_size": "L", "measurements": {"pit_to_pit": "23in", "shoulder_to_hem": "38in"}, "fit_notes": "Tailored fit. True to size. Length hits mid-thigh.", "negotiable": True},
    {"name": "Air Jordan 1 High - Chicago", "description": "2015 release, some creasing. The grail.", "category": "SHOES", "tier": "PREMIUM", "brand": "Jordan", "price_kes": 11000, "tag_size": "US 9.5", "measurements": {"us_size": 9.5, "uk_size": 8.5, "cm": 27.5}, "fit_notes": "True to size. Classic Jordan 1 fit.", "negotiable": True},
    {"name": "Nike Dunk Low - Syracuse", "description": "Orange and white, college colorway. Dunk hype.", "category": "SHOES", "tier": "PREMIUM", "brand": "Nike", "price_kes": 9000, "tag_size": "US 10", "measurements": {"us_size": 10, "uk_size": 9, "cm": 28}, "fit_notes": "True to size. Narrow fit.", "negotiable": True},
    {"name": "New Balance 990v5 - Grey", "description": "Made in USA, dad shoe royalty. Comfort and status.", "category": "SHOES", "tier": "PREMIUM", "brand": "New Balance", "price_kes": 7800, "tag_size": "US 10.5", "measurements": {"us_size": 10.5, "uk_size": 10, "cm": 28.5}, "fit_notes": "True to size. Wide feet friendly.", "negotiable": True},
    {"name": "Yeezy Boost 350 V2 - Zebra", "description": "White/black stripe, Boost comfort. Kanye era classic.", "category": "SHOES", "tier": "PREMIUM", "brand": "Adidas Yeezy", "price_kes": 9500, "tag_size": "US 11", "measurements": {"us_size": 11, "uk_size": 10.5, "cm": 29}, "fit_notes": "Size up half size from your usual. Yeezys run small.", "negotiable": True},
]


@router.post("/admin/seed-now")
async def seed_database_direct() -> Dict[str, str]:
    """
    Seed the database directly with 40 thrift items.
    """
    try:
        async with async_session_maker() as session:
            # Clear existing inventory
            logger.info("Clearing existing inventory...")
            await session.execute(delete(Inventory))
            await session.commit()
            
            # Combine all items
            all_items_data = BUDGET_ITEMS + MID_RANGE_ITEMS + PREMIUM_ITEMS
            
            # Generate SKU numbers
            budget_count = 0
            mid_count = 0
            premium_count = 0
            
            created_items = []
            
            for item_data in all_items_data:
                # Generate SKU based on tier
                if item_data["tier"] == "BUDGET":
                    budget_count += 1
                    sku = f"TH-B-{budget_count:03d}"
                elif item_data["tier"] == "MID_RANGE":
                    mid_count += 1
                    sku = f"TH-M-{mid_count:03d}"
                else:
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
                    status="AVAILABLE",
                )
                created_items.append(inventory_item)
                logger.info(f"Created: {sku} - {item_data['name']}")
            
            # Bulk insert
            session.add_all(created_items)
            await session.commit()
            
            logger.info(f"Successfully seeded {len(created_items)} items!")
            
            return {
                "status": "success",
                "message": f"Database seeded with {len(created_items)} items",
                "budget": budget_count,
                "mid_range": mid_count,
                "premium": premium_count
            }
            
    except Exception as e:
        logger.error(f"Seed failed: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Seed failed: {str(e)}"
        }


@router.post("/admin/clear-now")
async def clear_database_direct() -> Dict[str, str]:
    """
    Clear all inventory items.
    """
    try:
        async with async_session_maker() as session:
            await session.execute(delete(Inventory))
            await session.commit()
            
            return {
                "status": "success",
                "message": "Inventory cleared successfully"
            }
            
    except Exception as e:
        logger.error(f"Clear failed: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Clear failed: {str(e)}"
        }
