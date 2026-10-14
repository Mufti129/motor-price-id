import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resolve_db_path() -> str:
    env_path = os.environ.get("DB_PATH")
    if env_path:
        if os.path.isabs(env_path) and os.path.exists(env_path):
            return env_path
        joined = os.path.join(BASE_DIR, env_path)
        if os.path.exists(joined):
            return joined

    candidates = [
        os.path.join(BASE_DIR, "motor_bekas.db"),
        os.path.join(os.getcwd(), "motor_bekas.db"),
        "/mount/src/motor-price-id/motor_bekas.db",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return os.path.abspath(candidate)

    return os.path.join(BASE_DIR, "motor_bekas.db")

DB_PATH = resolve_db_path()
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30} if DATABASE_URL.startswith("sqlite") else {}
)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=30000")
            cursor.close()
        except Exception:
            pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from models.catalog import (
        MasterBrand, MasterModel, MasterVariant, ScrapedListing, MarketPriceStats,
        AuctionLot, WholesalePriceStats, ListingPriceHistory, VehicleHistoryReport,
        ListingImageAnalysis, B2BApiClient, ApiUsageLog, UserDealAlert
    )
    Base.metadata.create_all(bind=engine)
    
    # Auto-migration for SQLite to guarantee image_url column exists
    try:
        import sqlite3
        if DATABASE_URL.startswith("sqlite"):
            db_file = DB_PATH
            if os.path.exists(db_file):
                conn = sqlite3.connect(db_file, timeout=30)
                c = conn.cursor()
                
                c.execute("PRAGMA table_info(master_models)")
                cols_m = [r[1] for r in c.fetchall()]
                if cols_m and "image_url" not in cols_m:
                    c.execute("ALTER TABLE master_models ADD COLUMN image_url TEXT")
                    
                c.execute("PRAGMA table_info(master_variants)")
                cols_v = [r[1] for r in c.fetchall()]
                if cols_v and "image_url" not in cols_v:
                    c.execute("ALTER TABLE master_variants ADD COLUMN image_url TEXT")
                    
                conn.commit()
                conn.close()
    except Exception:
        pass
