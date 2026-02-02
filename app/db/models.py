"""
Database models using SQLModel (SQLAlchemy 2.0 + Pydantic).
Strict typing and enum constraints for production safety.

Phase 2 Refinements:
- User: tiktok_id as string PK, last_interaction_at indexed
- Inventory: measurements as Dict[str, float] for decimal support
- Order: Removed items_json, relies on OrderItem junction table
- OrderItem: New junction table for Order-Inventory relationship
- MessageRole: Kept explicit name (not generic "Role")
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional, Dict, Union
from sqlmodel import Field, SQLModel, Column, String, JSON, DECIMAL
from sqlalchemy import Enum as SQLEnum


# ============================================================================
# Enums (Database-Level Constraints)
# ============================================================================

class InventoryStatus(str, PyEnum):
    """Inventory item availability status."""
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"


class OrderStatus(str, PyEnum):
    """Order processing status."""
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class MessageRole(str, PyEnum):
    """
    Conversation message role for AI context.
    Kept as MessageRole (not generic "Role") for semantic clarity.
    """
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ============================================================================
# Database Models
# ============================================================================

class User(SQLModel, table=True):
    """
    TikTok user interacting with the bot.
    
    Primary Key: tiktok_id (TikTok OpenID) - No separate integer ID.
    This simplifies foreign key relationships and removes unnecessary lookups.
    """
    __tablename__ = "users"
    
    tiktok_id: str = Field(primary_key=True, max_length=255)
    username: Optional[str] = Field(default=None, max_length=255)
    last_interaction_at: datetime = Field(
        default_factory=datetime.utcnow, 
        index=True  # Indexed for fast 48-hour window checks
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    """
    Message history for AI context management.
    Stores role (USER/ASSISTANT/SYSTEM) and message content.
    """
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.tiktok_id", index=True, max_length=255)
    role: MessageRole = Field(
        sa_column=Column(SQLEnum(MessageRole, native_enum=False))
    )
    content: str = Field(sa_column=Column(String))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Inventory(SQLModel, table=True):
    """
    Unique thrift items with strict status management.
    
    Key Fields:
    - measurements: Dict[str, float] for decimal precision (e.g., {"pit_to_pit": 22.5})
    - status: AVAILABLE/RESERVED/SOLD (enum constraint)
    - price: Decimal(10, 2) for financial accuracy
    """
    __tablename__ = "inventory"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True, max_length=100)
    name: str = Field(max_length=255, index=True)  # Indexed for ILIKE searches
    description: Optional[str] = Field(default=None, sa_column=Column(String))
    price: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2))  # Max $99,999.99
    )
    size_label: Optional[str] = Field(default=None, max_length=50)  # e.g., "L", "W32 L30"
    measurements: Optional[Dict[str, float]] = Field(
        default=None, 
        sa_column=Column(JSON)  # Stores {"pit_to_pit": 22.5, "length": 28.0}
    )
    status: InventoryStatus = Field(
        default=InventoryStatus.AVAILABLE,
        sa_column=Column(SQLEnum(InventoryStatus, native_enum=False)),
        index=True  # Indexed for fast available item queries
    )
    image_url: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Order(SQLModel, table=True):
    """
    Customer orders linked to users.
    
    Design Decision: Removed items_json field.
    Relies entirely on OrderItem junction table for order contents.
    """
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.tiktok_id", index=True, max_length=255)
    status: OrderStatus = Field(
        default=OrderStatus.PENDING,
        sa_column=Column(SQLEnum(OrderStatus, native_enum=False))
    )
    tiktok_event_id: Optional[str] = Field(default=None, max_length=255, index=True)
    total_amount: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2))
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrderItem(SQLModel, table=True):
    """
    Junction table linking Orders to Inventory items.
    
    Design Decisions:
    - References inventory.id (immutable), not SKU (mutable)
    - Stores price_at_purchase for historical accuracy
    - Quantity always 1 for thrift items (unique pieces)
    """
    __tablename__ = "order_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    inventory_id: int = Field(foreign_key="inventory.id", index=True)
    price_at_purchase: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2))  # Historical price snapshot
    )
    quantity: int = Field(default=1)  # Always 1 for thrift (unique items)


class IdempotencyLog(SQLModel, table=True):
    """
    Track processed TikTok webhook events to prevent duplicate processing.
    Critical for idempotency guarantees.
    """
    __tablename__ = "idempotency_logs"
    
    event_id: str = Field(primary_key=True, max_length=255)
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(max_length=50)  # "SUCCESS", "FAILED", etc.
