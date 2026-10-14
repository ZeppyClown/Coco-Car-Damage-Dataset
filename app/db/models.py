from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func, Numeric, JSON, Index, UniqueConstraint, CheckConstraint, Uuid, text, Date, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, deferred
from datetime import datetime
from uuid import uuid4

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
    __table_args__ = (
        Index('ix_parts_catalog_brand', 'brand'),
        Index('ix_parts_catalog_category', 'category'),
        Index('ix_parts_catalog_data_source', 'data_source'),
        Index('ix_parts_catalog_part_number', 'part_number'),
        Index("ix_parts_catalog_search", text("to_tsvector('english'::regconfig, (name::text || ' '::text) || COALESCE(description, ''::text))"), postgresql_using="gin").ddl_if(dialect="postgresql"),
        Index('ix_parts_catalog_ships_to_singapore', 'ships_to_singapore'),
        Index('ix_parts_catalog_source', 'source'),
        Index('ix_parts_catalog_source_id', 'source_id'),
    )

    id = Column(Integer, primary_key=True)
    part_number = Column(String(100), nullable=False)
    source = Column(String(50), nullable=False)  # ebay, lazada, shopee, synthetic
    source_id = Column(String(200))  # ID from source API
    name = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    subcategory = Column(String(100))
    brand = Column(String(100))
    oem_or_aftermarket = Column(String(20))
    condition = Column(String(50))  # new, used, refurbished
    attributes = Column(JSON)  # flexible attributes
    image_url = Column(String(1000))  # primary image URL
    image_urls = Column(JSON)  # array of additional image URLs
    ships_to_singapore = Column(Boolean)  # Singapore shipping
    data_source = Column(String(50))  # 🏷️ HYBRID SYSTEM: synthetic, google_cse, ebay_api, etc.
    retrieved_at = Column(DateTime)  # when data was fetched
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now(), nullable=False)
    last_sync = Column(DateTime)  # last API sync

    # Relationships
    prices = relationship("PartPrice", back_populates="part", cascade="all, delete-orphan")
    compatibility = relationship("PartCompatibilityEnhanced", back_populates="part", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PartsCatalog {self.part_number} from {self.source}>"


class PartPrice(Base):
    """Pricing information from different sources/sellers"""
    __tablename__ = "part_prices"
    __table_args__ = (
        Index('ix_part_prices_currency', 'currency'),
        Index('ix_part_prices_part_id', 'part_id'),
        Index('ix_part_prices_price', 'price'),
        Index('ix_part_prices_price_sgd', 'price_sgd'),
        Index('ix_part_prices_ships_to_singapore', 'ships_to_singapore'),
    )

    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("parts_catalog.id", ondelete="CASCADE"), nullable=False)
    currency = Column(String(10), nullable=False)  # SGD, USD, etc.
    price_sgd = Column(Numeric(10, 2), nullable=True)  # Price in SGD
    price = Column(Numeric(10, 2))  # Original currency price (for reference)
    original_price = Column(Numeric(10, 2))  # for discounts
    shipping_cost = Column(Numeric(10, 2))
    seller_name = Column(String(200))
    seller_rating = Column(Numeric(3, 2))  # 0.00 - 5.00
    availability = Column(String(50))  # in_stock, out_of_stock, limited, preorder
    condition = Column(String(50))  # new, used, refurbished
    in_stock = Column(Boolean)  # deprecated, use availability
    stock_quantity = Column(Integer)
    ships_to_singapore = Column(Boolean)
    delivery_days_min = Column(Integer)
    delivery_days_max = Column(Integer)
    source_url = Column(String(1000))  # Product URL
    url = Column(String(1000))  # deprecated, use source_url
    last_updated = Column(DateTime)  # when price was last updated
    valid_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now(), nullable=False)

    # Relationships
    part = relationship("PartsCatalog", back_populates="prices")

    def __repr__(self):
        return f"<PartPrice {self.currency} {self.price} for part_id={self.part_id}>"


class PartCompatibilityEnhanced(Base):
    """Enhanced compatibility data for parts"""
    __tablename__ = "part_compatibility_enhanced"
    __table_args__ = (
        Index('ix_part_compat_make', 'make'),
        Index('ix_part_compat_model', 'model'),
        Index('ix_part_compat_part_id', 'part_id'),
        Index('ix_part_compat_universal', 'is_universal'),
        Index('ix_part_compat_year', 'year_start', 'year_end'),
    )

    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("parts_catalog.id", ondelete="CASCADE"), nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    year_start = Column(Integer, nullable=False)
    year_end = Column(Integer, nullable=False)
    trim = Column(String(100))
    engine = Column(String(100))
    transmission = Column(String(50))
    drive_type = Column(String(20))  # FWD, RWD, AWD
    position = Column(String(50))  # front, rear, left, right
    notes = Column(Text)
    confidence = Column(Numeric(3, 2))  # 0.00 - 1.00
    is_universal = Column(Boolean, default=False)
    source = Column(String(50))  # where compatibility data came from
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False)

    # Relationships
    part = relationship("PartsCatalog", back_populates="compatibility")

    def __repr__(self):
        return f"<PartCompatibilityEnhanced {self.make} {self.model} {self.year_start}-{self.year_end}>"


class SearchCache(Base):
    """Cache for parts search results"""
    __tablename__ = "search_cache"
    __table_args__ = (
        Index('ix_search_cache_expires', 'expires_at'),
        Index('ix_search_cache_hash', 'query_hash'),
        Index('ix_search_cache_query_text', 'query_text'),
        UniqueConstraint("query_hash"),
    )

    id = Column(Integer, primary_key=True)
    query_hash = Column(String(64), nullable=False)
    query_text = Column(String(500), nullable=False)
    vehicle_make = Column(String(50))
    vehicle_model = Column(String(100))
    vehicle_year = Column(Integer)
    results = Column(JSON, nullable=False)  # cached results
    result_count = Column(Integer, nullable=False)
    sources_queried = Column(JSON)  # which APIs were called
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    hit_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<SearchCache '{self.query_text}' ({self.result_count} results)>"


class APIRateLimit(Base):
    """Track API usage and rate limits"""
    __tablename__ = "api_rate_limits"
    __table_args__ = (
        Index('ix_api_rate_reset', 'reset_at'),
        Index('ix_api_rate_source', 'source'),
    )

    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)  # ebay, lazada, shopee
    endpoint = Column(String(200), nullable=False)
    call_count = Column(Integer, default=0)
    reset_at = Column(DateTime, nullable=False)
    daily_limit = Column(Integer)
    remaining = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<APIRateLimit {self.source} {self.call_count}/{self.daily_limit}>"


class WorkshopDocument(Base):
    __tablename__ = "workshop_documents"
    __table_args__ = (
        CheckConstraint("byte_size > 0", name="ck_workshop_document_size"),
        CheckConstraint("data_origin IN ('synthetic_demo', 'private_source')", name="ck_workshop_document_origin"),
        CheckConstraint("media_type IN ('image/jpeg', 'image/png')", name="ck_workshop_document_media"),
    )

    id = Column(Uuid, primary_key=True, default=uuid4)
    checksum = Column(String(64), nullable=False, unique=True)
    storage_key = Column(String(120), nullable=False, unique=True)
    # The file itself; NULL only for rows saved before files moved into the database (then read from the storage folder).
    content = deferred(Column(LargeBinary))
    media_type = Column(String(20), nullable=False)
    byte_size = Column(Integer, nullable=False)
    data_origin = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class WorkshopJob(Base):
    __tablename__ = "workshop_jobs"
    __table_args__ = (CheckConstraint("draft_version >= 1", name="ck_workshop_job_version"),)

    id = Column(Uuid, primary_key=True, default=uuid4)
    source_document_id = Column(Uuid, ForeignKey("workshop_documents.id"))
    draft = Column(JSON, nullable=False)
    draft_version = Column(Integer, nullable=False, default=1, server_default="1")
    # Letters and digits of the job no., upper case; the unique index is what stops two jobs sharing a number.
    job_number = Column(String(200), unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class WorkshopJobRevision(Base):
    __tablename__ = "workshop_job_revisions"
    __table_args__ = (
        UniqueConstraint("job_id", "version", name="uq_workshop_job_revision"),
        CheckConstraint("version >= 1", name="ck_workshop_revision_version"),
        CheckConstraint("reviewer_identity IN ('self_reported', 'authenticated')", name="ck_workshop_reviewer_identity"),
    )

    id = Column(Uuid, primary_key=True, default=uuid4)
    job_id = Column(Uuid, ForeignKey("workshop_jobs.id"), nullable=False)
    source_document_id = Column(Uuid, ForeignKey("workshop_documents.id"))
    version = Column(Integer, nullable=False)
    record = Column(JSON, nullable=False)
    reviewer = Column(String(200), nullable=False)
    reviewer_identity = Column(String(20), nullable=False, default="self_reported", server_default="self_reported")
    reviewed_at = Column(DateTime(timezone=True), nullable=False)


class WorkshopExport(Base):
    __tablename__ = "workshop_exports"
    __table_args__ = (
        UniqueConstraint("revision_id", "mapping_version", name="uq_workshop_export_identity"),
        CheckConstraint("byte_size > 0", name="ck_workshop_export_size"),
    )

    id = Column(Uuid, primary_key=True, default=uuid4)
    revision_id = Column(Uuid, ForeignKey("workshop_job_revisions.id"), nullable=False)
    mapping_version = Column(String(40), nullable=False)
    checksum = Column(String(64), nullable=False)
    storage_key = Column(String(120), nullable=False, unique=True)
    # The file itself; NULL only for rows saved before files moved into the database (then read from the storage folder).
    content = deferred(Column(LargeBinary))
    byte_size = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class WorkshopInvoice(Base):
    __tablename__ = "workshop_invoices"

    id = Column(Uuid, primary_key=True, default=uuid4)
    job_id = Column(Uuid, ForeignKey("workshop_jobs.id"), nullable=False, unique=True)
    revision_id = Column(Uuid, ForeignKey("workshop_job_revisions.id"), nullable=False)
    number = Column(String(200), nullable=False, unique=True)
    snapshot = Column(JSON, nullable=False)
    issued_by = Column(String(200), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    html = Column(Text, nullable=False)
    checksum = Column(String(64), nullable=False)


class WorkshopPayment(Base):
    """Money received or refunded against an invoice; entries are added, never edited."""
    __tablename__ = "workshop_payments"

    id = Column(Uuid, primary_key=True, default=uuid4)
    invoice_id = Column(Uuid, ForeignKey("workshop_invoices.id"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    method = Column(String(20), nullable=False)
    paid_on = Column(Date, nullable=False)
    note = Column(String(500), nullable=False)
    recorded_by = Column(String(200), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False)


class WorkshopCompany(Base):
    """The workshop's own details, typed once on first use and printed on every invoice."""
    __tablename__ = "workshop_company"
    __table_args__ = (CheckConstraint("id = 1", name="ck_workshop_company_single"),)

    id = Column(Integer, primary_key=True, default=1)
    name = Column(String(200), nullable=False)
    address = Column(String(2000), nullable=False)
    gst_registration_number = Column(String(200))
    phone = Column(String(200), nullable=False, default="", server_default="")
    # The blank job-sheet form as a PNG, uploaded in the app so a hosted copy needs no files on disk. Loaded only when printing.
    sheet_template = deferred(Column(LargeBinary))
    updated_by = Column(String(200), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class WorkshopGuidePicture(Base):
    """A page of the paper guide (part names, sample sheets), uploaded by an owner so a hosted copy needs no folder."""
    __tablename__ = "workshop_guide_pictures"

    name = Column(String(200), primary_key=True)
    media_type = Column(String(50), nullable=False)
    content = deferred(Column(LargeBinary, nullable=False))
    updated_by = Column(String(200), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class WorkshopExpense(Base):
    """Money paid out to a supplier or for running costs; entries are added, never edited."""
    __tablename__ = "workshop_expenses"

    id = Column(Uuid, primary_key=True, default=uuid4)
    spent_on = Column(Date, nullable=False, index=True)
    supplier = Column(String(200), nullable=False)
    category = Column(String(20), nullable=False)
    description = Column(String(500), nullable=False)
    supplier_invoice = Column(String(200), nullable=False)
    job_reference = Column(String(200), nullable=False)
    # Set when the expense is for one job; the foreign key means it can only name a job that exists.
    job_number = Column(String(200), ForeignKey("workshop_jobs.job_number", onupdate="CASCADE"), index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    gst = Column(Numeric(12, 2), nullable=False)
    recorded_by = Column(String(200), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False)


class WorkshopInvoiceCounter(Base):
    """Last invoice number used in each year. Taking the next one locks the row, so two invoices cannot share a number."""
    __tablename__ = "workshop_invoice_counters"

    year = Column(Integer, primary_key=True)
    last = Column(Integer, nullable=False)


class WorkshopUser(Base):
    """A staff login added by the owner. Logins are switched off, never deleted, because records keep the name."""
    __tablename__ = "workshop_users"
    __table_args__ = (CheckConstraint("role IN ('owner', 'staff')", name="ck_workshop_user_role"),)

    username = Column(String(50), primary_key=True)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(10), nullable=False)
    active = Column(Boolean, nullable=False, default=True, server_default="true")
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
