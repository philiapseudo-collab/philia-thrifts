"""Seed endpoint for populating database with inventory items."""
import logging
import subprocess
from typing import Dict
from fastapi import APIRouter, HTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/seed", tags=["admin"])


@router.post("/run")
async def run_seed() -> Dict[str, str]:
    """
    Run the database seed script to populate inventory.
    
    Returns:
        Status of seeding operation
    """
    if not settings.DATABASE_URL:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        logger.info("Running database seed script...")
        result = subprocess.run(
            ["python", "scripts/seed_db.py", "seed"],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        logger.info("Seed script completed successfully")
        
        return {
            "status": "success",
            "message": "Database seeded successfully",
            "details": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Seed script failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Seed failed: {e.stderr[-1000:]}"
        )
    except subprocess.TimeoutExpired:
        logger.error("Seed script timed out")
        raise HTTPException(status_code=504, detail="Seed operation timed out")
    except Exception as e:
        logger.error(f"Unexpected error during seed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/clear")
async def clear_seed() -> Dict[str, str]:
    """
    Clear all inventory items from the database.
    
    Returns:
        Status of clear operation
    """
    if not settings.DATABASE_URL:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        logger.info("Clearing inventory...")
        result = subprocess.run(
            ["python", "scripts/seed_db.py", "clear"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        return {
            "status": "success",
            "message": "Inventory cleared",
            "details": result.stdout
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Clear failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error during clear: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/verify")
async def verify_seed() -> Dict:
    """
    Verify the current inventory count.
    
    Returns:
        Inventory statistics
    """
    if not settings.DATABASE_URL:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        result = subprocess.run(
            ["python", "scripts/seed_db.py", "verify"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        return {
            "status": "success",
            "details": result.stdout
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Verify failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verify failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error during verify: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
