"""First-time setup: the workshop's own details, and a set of example jobs to look around with."""
from datetime import date, datetime, time, timedelta, timezone
from io import BytesIO
from decimal import Decimal
from random import Random
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.workshop_auth import STAFF_PASSWORD_LENGTH, hash_password, valid_username
from app.db.models import WorkshopCompany, WorkshopExpense, WorkshopJob, WorkshopJobRevision, WorkshopPayment, WorkshopUser
from app.schemas.workshop import WorkshopReviewedDraft
from app.schemas.workshop_books import CompanyRequest, UserRequest
from app.schemas.workshop_invoice import InvoiceRequest
from app.services.workshop import job_number, number_key
from app.services.workshop_invoice import billing_supplier, store_invoice


def company(db: Session) -> dict | None:
    row = db.get(WorkshopCompany, 1)
    return None if row is None else {"name": row.name, "address": row.address, "phone": row.phone,
                                     "gst_registration_number": row.gst_registration_number}


def setup_state(db: Session) -> dict:
    uploaded = db.scalar(select(func.length(WorkshopCompany.sheet_template)).where(WorkshopCompany.id == 1))
    template = settings.WORKSHOP_SHEET_TEMPLATE
    return {"company": company(db), "jobs": db.scalar(select(func.count()).select_from(WorkshopJob)),
            "form": "uploaded" if uploaded else "file" if template and str(template) != "." and template.is_file() else None}


MAX_FORM_BYTES = 8 * 1024 * 1024


def save_form(db: Session, content: bytes, actor: str) -> dict:
    """Keep the blank job-sheet picture in the database, as a PNG, so printing works without files on the server."""
    row = db.get(WorkshopCompany, 1)
    if row is None:
        raise HTTPException(409, "Save the workshop details first")
    if not content or len(content) > MAX_FORM_BYTES:
        raise HTTPException(413, "The picture must be smaller than 8 MB")
    try:
        with Image.open(BytesIO(content)) as image:
            if image.format not in {"PNG", "JPEG"} or max(image.size) > 6000 or min(image.size) < 400:
                raise HTTPException(415, "Use a PNG or JPEG scan of the blank form, between 400 and 6000 pixels a side")
            output = BytesIO()
            image.convert("RGB").save(output, "PNG", optimize=True)
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError):
        raise HTTPException(422, "That file is not a picture the app can read") from None
    try:
        row.sheet_template, row.updated_by, row.updated_at = output.getvalue(), actor, datetime.now(timezone.utc)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    return setup_state(db)


def users(db: Session) -> list[dict]:
    built_in = {"username": settings.WORKSHOP_AUTH_USERNAME, "role": "owner", "active": True, "built_in": True}
    return [built_in, *({"username": user.username, "role": user.role, "active": user.active, "built_in": False}
                        for user in db.scalars(select(WorkshopUser).order_by(WorkshopUser.username)))]


def save_user(db: Session, request: UserRequest, actor: str) -> list[dict]:
    """Add a login, or give an existing one a new password and role and switch it back on."""
    if not valid_username(request.username) or request.username == settings.WORKSHOP_AUTH_USERNAME:
        raise HTTPException(422, "Use a short login name in plain letters and digits that is not the main owner login")
    try:
        encoded = hash_password(request.password, STAFF_PASSWORD_LENGTH)
    except ValueError:
        raise HTTPException(422, f"The password needs at least {STAFF_PASSWORD_LENGTH} plain letters, digits or symbols") from None
    try:
        user = db.get(WorkshopUser, request.username) or WorkshopUser(
            username=request.username, created_by=actor, created_at=datetime.now(timezone.utc))
        user.password_hash, user.role, user.active = encoded, request.role, True
        db.add(user)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    return users(db)


def switch_user(db: Session, username: str, active: bool) -> list[dict]:
    user = db.get(WorkshopUser, username)
    if user is None:
        raise HTTPException(404, "No such login")
    try:
        user.active = active
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    return users(db)


def save_company(db: Session, request: CompanyRequest, actor: str) -> dict:
    try:
        row = db.get(WorkshopCompany, 1) or WorkshopCompany(id=1)
        row.name, row.address, row.phone = request.name, request.address, request.phone.strip()
        row.gst_registration_number = request.gst_registration_number
        row.updated_by, row.updated_at = actor, datetime.now(timezone.utc)
        db.add(row)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    return setup_state(db)


# ---- example jobs ------------------------------------------------------------------------------
# Every person, vehicle number, phone number and address below is made up.
CARS = [("Toyota", "Vios"), ("Toyota", "Corolla Altis"), ("Honda", "Vezel"), ("Honda", "Civic"), ("Mazda", "3"),
        ("Hyundai", "Avante"), ("Nissan", "Qashqai"), ("Kia", "Cerato"), ("Mitsubishi", "Attrage"), ("Toyota", "Hiace"),
        ("BMW", "318i"), ("Mercedes-Benz", "C180"), ("Subaru", "Forester"), ("Volkswagen", "Golf")]
SURNAMES = ["Tan", "Lim", "Lee", "Ng", "Ong", "Wong", "Goh", "Chua", "Koh", "Teo", "Yeo", "Low", "Chan", "Ho", "Sim"]
GIVEN = ["Wei Ming", "Siew Hoon", "Bee Lian", "Chee Keong", "Jia Hui", "Kok Leong", "Boon Huat", "Mei Ling", "Kah Fai", "Pei Shan",
         "Chin Hock", "Li Ting", "Swee Lan", "Ah Seng", "Hui Min", "Jun Jie"]
OTHERS = ["Muhammad Faizal", "Nurul Aisyah", "Siti Rahimah", "Ahmad Zulkifli", "Rajesh Kumar", "Suresh Pillai", "Priya Nair",
          "Hafiz Rahman", "Kavitha Menon", "Daniel Pereira"]
JOBS_PER_MONTH = 30
STREETS = ["Ang Mo Kio Ave 4", "Bedok North St 2", "Jurong West St 52", "Tampines St 81", "Yishun Ring Rd", "Hougang Ave 8",
           "Bukit Batok St 31", "Woodlands Dr 14", "Toa Payoh Lor 5", "Clementi Ave 2"]
PANELS = ["front bumper", "rear bumper", "bonnet", "boot", "front left door", "rear left door", "front right fender",
          "rear right fender", "front right door", "roof"]
REPAIRS = [("Servicing", 128), ("Engine oil", 68), ("Radiator", 320), ("Fan motor", 180), ("Front oil seal", 95),
           ("Headlight", 240), ("Rear lamp", 150), ("Side mirror", 135), ("Brake pads", 160), ("Battery", 185),
           ("Windscreen replace", 380), ("Labour", 80)]
INSURERS = ["NTUC Income", "AIG", "Great Eastern", "MSIG", "Tokio Marine", "Singlife", "Liberty"]
SUPPLIERS = {"parts": ["Hock Seng Auto Parts", "Kim Huat Motor Spares", "Eastern Auto Supply"],
             "paint": ["Nippon Refinish Supply", "Colourtech Paints"], "subcontract": ["Ah Seng Windscreen", "Precision Wheel Alignment"]}
# (type, paid to, what for, amount, GST on the bill, day of the month it is paid)
FIXED = [("rent", "JTC Corporation", "Workshop unit rent", 3800, True, 1), ("wages", "Staff payroll", "Wages for the month", 7200, False, 28),
         ("utilities", "SP Services", "Electricity and water", 640, True, 15), ("tools", "Sin Hup Tools", "Sandpaper, masking tape, consumables", 215, True, 5)]
# Where each panel sits on the form's car outline, as percentages of the picture.
SPOTS = {"front bumper": (50, 10), "bonnet": (52, 27), "roof": (52, 45), "boot": (52, 63), "rear bumper": (52, 79),
         "front left door": (20, 38), "rear left door": (20, 52), "front right door": (82, 38),
         "front right fender": (82, 24), "rear right fender": (82, 64)}
CENT = Decimal("0.01")


def _plate(rng: Random) -> str:
    return f"S{rng.choice('GHJKLMN')}{rng.choice('ABCDEFGHJKLMNPRSTUXYZ')} {rng.randrange(1000, 9999)} {rng.choice('ABCDEGHJKLMPRSTUXYZ')}"


def _line(text: str, amount: int | None, section: str) -> dict:
    value = None if amount is None else f"{amount}.00"
    return {"section": section, "description_raw": text, "description": text, "description_state": "confirmed",
            "amount_raw": value or "", "amount": value, "amount_state": "confirmed" if value else "missing", "cancelled": False}


def _example_job(rng: Random, number: int, day_in: date, customer: tuple, stage: str) -> dict:
    owner, phone, plate, (make, model) = customer
    damaged = rng.sample(PANELS, rng.choice((0, 1, 1, 2, 2, 3)))
    items = [_line(f"Knock {panel}", rng.choice((120, 150, 180, 200, 250)), "knock") for panel in damaged]
    items += [_line(text, price, "repair") for text, price in rng.sample(REPAIRS, rng.choice((1, 1, 2, 3)) if damaged else rng.choice((2, 3, 4)))]
    items += [_line(f"Spray {panel}", rng.choice((180, 220, 250, 280)), "spray") for panel in damaged]
    accident = None
    if len(damaged) >= 2 and rng.random() < 0.45:
        kind = rng.choice(("own_damage", "third_party", "private_settlement", "report_only"))
        other = kind != "own_damage"
        accident = {"claim_type": kind, "accident_date": (day_in - timedelta(days=rng.randrange(1, 4))).isoformat(),
                    "accident_place": rng.choice(("PIE towards Changi, near Eunos exit", "Car park at Blk 210 Hougang St 21",
                                                  "Junction of Yishun Ave 2 and Ave 5", "CTE towards SLE, before Braddell")),
                    "insurer": rng.choice(INSURERS), "policy_number": f"MV{rng.randrange(10**7, 10**8)}",
                    "report_number": f"GIA-{day_in.year}-{rng.randrange(10**5, 10**6)}",
                    "other_vehicle": _plate(rng) if other else None, "other_party": rng.choice(OTHERS) if other else None,
                    "other_insurer": rng.choice(INSURERS) if kind == "third_party" else None,
                    "excess": f"{rng.choice((500, 600, 800, 1000))}.00" if kind == "own_damage" else None,
                    "notes": {"own_damage": "Claiming own insurer. Customer pays the excess.", "third_party": "Claiming against the other party's insurer.",
                              "private_settlement": "Other driver pays directly. Report filed for record.",
                              "report_only": "Report for record only; customer paying for the repair."}[kind]}
    header = {"job_reference": str(number), "customer_reference": owner, "vehicle_reference": plate, "make": make, "model": model,
              "date_in": day_in.isoformat(), "date_out": None if stage != "completed_work" else (day_in + timedelta(days=rng.randrange(1, 6))).isoformat(),
              "quotation_date": day_in.isoformat(), "currency": "SGD"}
    return {"data_origin": "synthetic_demo", "manual_provenance": "Example job added by the app at set-up; not a real customer.",
            "record_stage": stage, **header, "contact": phone, "fuel_level": rng.choice(("1/5", "2/5", "3/5", "4/5", "full")),
            "items": items, "accident": accident,
            "diagram_marks": [{"x": SPOTS[panel][0], "y": SPOTS[panel][1], "note": f"{panel} dent"} for panel in damaged],
            "field_states": {name: "confirmed" for name, value in header.items() if value}}


def add_example_data(db: Session, actor: str) -> dict:
    """Three months of made-up jobs, invoices, payments and expenses, issued in the saved workshop's name."""
    supplier = billing_supplier(db)
    if supplier is None:
        raise HTTPException(409, "Save the workshop details first")
    if db.scalar(select(func.count()).select_from(WorkshopJob)):
        raise HTTPException(409, "Example jobs can only be added while the app has no jobs")
    rng, today = Random(2026), datetime.now(ZoneInfo("Asia/Singapore")).date()
    owners = rng.sample([f"{surname} {given}" for surname in SURNAMES for given in GIVEN], 50) + OTHERS
    customers = [(owner, f"{rng.choice('89')}{rng.randrange(1000):03d} {rng.randrange(10**4):04d}", _plate(rng), rng.choice(CARS))
                 for owner in owners]
    first = (today.replace(day=1) - timedelta(days=40)).replace(day=1)
    days = [first + timedelta(days=offset) for offset in range((today - first).days + 1)]
    work_days = sorted(rng.choice([day for day in days if day.weekday() < 6]) for _ in range(len(days) * JOBS_PER_MONTH // 30))
    try:
        for number, day_in in enumerate(work_days, 1001):
            recent = (today - day_in).days < 6
            stage = rng.choice(("quote", "approved_scope")) if recent or rng.random() < 0.08 else "completed_work"
            # Some jobs are returning cars, so "this car has been here before" has something to show.
            customer = rng.choice(customers[:6]) if rng.random() < 0.15 else rng.choice(customers)
            record = WorkshopReviewedDraft.model_validate(_example_job(rng, number, day_in, customer, stage))
            draft = record.model_dump(mode="json")
            job = WorkshopJob(draft=draft, job_number=job_number(record))
            db.add(job)
            db.flush()
            reviewed_at = datetime.combine(record.date_out or day_in, time(9, 30), tzinfo=timezone.utc)
            revision = WorkshopJobRevision(job_id=job.id, version=1, record=draft, reviewer=actor, reviewed_at=reviewed_at,
                                           reviewer_identity="authenticated")
            db.add(revision)
            db.flush()
            if stage != "completed_work" or record.date_out > today:
                continue
            invoice = store_invoice(db, job.id, revision, InvoiceRequest(
                supplier=supplier, invoice_date=record.date_out, pricing_basis="inclusive",
                discount=rng.choice((0, 0, 0, 0, 20, 50)),
                customer={"name": customer[0], "address": f"Blk {rng.randrange(100, 900)} {rng.choice(STREETS)} #{rng.randrange(2, 15):02d}-{rng.randrange(100, 400)}"},
            ), actor, reviewed_at)
            total, luck = invoice.preview.total, rng.random()
            # What this job cost: parts and paint bought for it, so each job shows its own profit.
            category = "paint" if any(item.section == "spray" for item in record.items) and rng.random() < 0.5 else "parts"
            _expense(db, day_in + timedelta(days=1) if day_in < today else day_in, rng.choice(SUPPLIERS[category]), category,
                     "Paint and materials" if category == "paint" else "Parts", (total * Decimal(rng.randrange(22, 42)) / 100).quantize(Decimal(1)),
                     Decimal("9") / Decimal("109"), actor, f"SI-{rng.randrange(10**4, 10**5)}", record.job_reference)
            paid = total if luck < 0.72 else (total / 2).quantize(CENT) if luck < 0.86 else Decimal(0)
            if (today - record.date_out).days < 3 and luck > 0.4:
                paid = Decimal(0)
            if paid:
                db.add(WorkshopPayment(invoice_id=invoice.id, amount=paid, method=rng.choice(("cash", "nets", "paynow", "paynow", "bank")),
                                       paid_on=min(today, record.date_out + timedelta(days=rng.randrange(0, 4))),
                                       note="" if paid == total else "Part payment, balance to follow", recorded_by=actor, recorded_at=reviewed_at))
        registered = Decimal("9") / Decimal("109")
        month = first
        while month <= today:
            for category, name, what, amount, gst, day in FIXED:
                if month.replace(day=day) <= today:
                    _expense(db, month.replace(day=day), name, category, what, Decimal(amount), registered if gst else 0, actor)
            month = (month + timedelta(days=32)).replace(day=1)
        for day in days[::9]:
            category = rng.choice(("parts", "paint", "subcontract"))
            what = {"parts": "Workshop stock: oil, filters, bulbs", "paint": "Thinner, primer and clear coat stock", "subcontract": "Wheel alignment machine servicing"}[category]
            _expense(db, day, rng.choice(SUPPLIERS[category]), category, what, Decimal(rng.randrange(180, 950)), registered, actor,
                     f"SI-{rng.randrange(10**4, 10**5)}")
        db.commit()
    except (SQLAlchemyError, HTTPException):
        db.rollback()
        raise
    return setup_state(db)


def _expense(db: Session, day: date, supplier: str, category: str, what: str, amount: Decimal, gst_share, actor: str, bill: str = "",
             job: str = "") -> None:
    db.add(WorkshopExpense(spent_on=day, supplier=supplier, category=category, description=what, supplier_invoice=bill, job_reference=job,
                           job_number=number_key(job),
                           amount=amount, gst=(amount * gst_share).quantize(CENT), recorded_by=actor,
                           recorded_at=datetime.combine(day, time(10), tzinfo=timezone.utc)))
