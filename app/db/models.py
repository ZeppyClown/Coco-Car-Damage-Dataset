from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func, Numeric, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Part(Base):
    """Parts table model"""
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    part_number = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True)
    oem = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    compatibility = relationship("PartCompatibility", back_populates="part")

    def __repr__(self):
        return f"<Part {self.part_number}: {self.name}>"


class Vehicle(Base):
    """Vehicles table model"""
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String(17), unique=True, nullable=True, index=True)
    make = Column(String(50), nullable=False, index=True)
    model = Column(String(50), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    trim = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    specifications = relationship("Specification", back_populates="vehicle")
    compatibility = relationship("PartCompatibility", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle {self.year} {self.make} {self.model}>"


class Specification(Base):
    """Specifications table model"""
    __tablename__ = "specifications"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    spec_type = Column(String(50), nullable=False)  # engine, transmission, dimensions, etc.
    spec_key = Column(String(100), nullable=False)
    spec_value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="specifications")

    def __repr__(self):
        return f"<Specification {self.spec_type}.{self.spec_key}>"


class PartCompatibility(Base):
    """Part compatibility table model"""
    __tablename__ = "part_compatibility"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    compatible = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    part = relationship("Part", back_populates="compatibility")
    vehicle = relationship("Vehicle", back_populates="compatibility")

    def __repr__(self):
        return f"<PartCompatibility part_id={self.part_id} vehicle_id={self.vehicle_id}>"


class PaintCode(Base):
    """Paint codes table model"""
    __tablename__ = "paint_codes"

    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String(50), nullable=False, index=True)
    paint_code = Column(String(50), nullable=False)
    color_name = Column(String(100), nullable=False)
    year_start = Column(Integer)
    year_end = Column(Integer)
    formula = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PaintCode {self.manufacturer} {self.paint_code}: {self.color_name}>"


class FaultCode(Base):
    """Fault codes table model"""
    __tablename__ = "fault_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    system = Column(String(50), index=True)  # engine, transmission, brakes, etc.
    description = Column(Text, nullable=False)
    severity = Column(String(20))  # low, medium, high, critical
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FaultCode {self.code}: {self.system}>"


# ============================================================================
# PHASE 3: Parts Lookup Module Models
# ============================================================================

class PartsCatalog(Base):
    """Parts catalog from multiple sources (eBay, Lazada, Shopee, etc.)"""
    __tablename__ = "parts_catalog"

    id = Column(Integer, primary_key=True, index=True)
    part_number = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)  # ebay, lazada, shopee, synthetic
    source_id = Column(String(200), index=True)  # ID from source API
    name = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    brand = Column(String(100), index=True)
    oem_or_aftermarket = Column(String(20))
    condition = Column(String(50))  # new, used, refurbished
    attributes = Column(JSON)  # flexible attributes
    image_url = Column(String(1000))  # primary image URL
    image_urls = Column(JSON)  # array of additional image URLs
    ships_to_singapore = Column(Boolean, default=True, index=True)  # Singapore shipping
    data_source = Column(String(50), index=True)  # 🏷️ HYBRID SYSTEM: synthetic, google_cse, ebay_api, etc.
    retrieved_at = Column(DateTime)  # when data was fetched
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync = Column(DateTime)  # last API sync

    # Relationships
    prices = relationship("PartPrice", back_populates="part", cascade="all, delete-orphan")
    compatibility = relationship("PartCompatibilityEnhanced", back_populates="part", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PartsCatalog {self.part_number} from {self.source}>"


class PartPrice(Base):
    """Pricing information from different sources/sellers"""
    __tablename__ = "part_prices"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts_catalog.id", ondelete="CASCADE"), nullable=False, index=True)
    currency = Column(String(10), nullable=False, index=True)  # SGD, USD, etc.
    price_sgd = Column(Numeric(10, 2), nullable=False, index=True)  # Price in SGD
    price = Column(Numeric(10, 2))  # Original currency price (for reference)
    original_price = Column(Numeric(10, 2))  # for discounts
    shipping_cost = Column(Numeric(10, 2))
    seller_name = Column(String(200))
    seller_rating = Column(Numeric(3, 2))  # 0.00 - 5.00
    availability = Column(String(50))  # in_stock, out_of_stock, limited, preorder
    condition = Column(String(50))  # new, used, refurbished
    in_stock = Column(Boolean)  # deprecated, use availability
    stock_quantity = Column(Integer)
    ships_to_singapore = Column(Boolean, index=True)
    delivery_days_min = Column(Integer)
    delivery_days_max = Column(Integer)
    source_url = Column(String(1000))  # Product URL
    url = Column(String(1000))  # deprecated, use source_url
    last_updated = Column(DateTime)  # when price was last updated
    valid_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    part = relationship("PartsCatalog", back_populates="prices")

    def __repr__(self):
        return f"<PartPrice {self.currency} {self.price} for part_id={self.part_id}>"


class PartCompatibilityEnhanced(Base):
    """Enhanced compatibility data for parts"""
    __tablename__ = "part_compatibility_enhanced"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts_catalog.id", ondelete="CASCADE"), nullable=False, index=True)
    make = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    year_start = Column(Integer, nullable=False, index=True)
    year_end = Column(Integer, nullable=False, index=True)
    trim = Column(String(100))
    engine = Column(String(100))
    transmission = Column(String(50))
    drive_type = Column(String(20))  # FWD, RWD, AWD
    position = Column(String(50))  # front, rear, left, right
    notes = Column(Text)
    confidence = Column(Numeric(3, 2))  # 0.00 - 1.00
    is_universal = Column(Boolean, default=False, index=True)
    source = Column(String(50))  # where compatibility data came from
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    part = relationship("PartsCatalog", back_populates="compatibility")

    def __repr__(self):
        return f"<PartCompatibilityEnhanced {self.make} {self.model} {self.year_start}-{self.year_end}>"


class SearchCache(Base):
    """Cache for parts search results"""
    __tablename__ = "search_cache"

    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String(64), unique=True, nullable=False, index=True)
    query_text = Column(String(500), nullable=False, index=True)
    vehicle_make = Column(String(50))
    vehicle_model = Column(String(100))
    vehicle_year = Column(Integer)
    results = Column(JSON, nullable=False)  # cached results
    result_count = Column(Integer, nullable=False)
    sources_queried = Column(JSON)  # which APIs were called
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    hit_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<SearchCache '{self.query_text}' ({self.result_count} results)>"


class APIRateLimit(Base):
    """Track API usage and rate limits"""
    __tablename__ = "api_rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # ebay, lazada, shopee
    endpoint = Column(String(200), nullable=False)
    call_count = Column(Integer, default=0)
    reset_at = Column(DateTime, nullable=False, index=True)
    daily_limit = Column(Integer)
    remaining = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<APIRateLimit {self.source} {self.call_count}/{self.daily_limit}>"
