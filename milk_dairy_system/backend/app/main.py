from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .config import settings
from .routers import auth, suppliers, milk, payments
from . import models, auth as auth_utils

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A secure and easy-to-use API for Dairy Owners to manage suppliers, milk logs, and payment ledgers.",
    version="1.0.0"
)

# Enable CORS so our Streamlit frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits access from any origin (e.g. mobile networks or localhost)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register our API routers
app.include_router(auth.router, prefix="/api")
app.include_router(suppliers.router, prefix="/api")
app.include_router(milk.router, prefix="/api")
app.include_router(payments.router, prefix="/api")

@app.on_event("startup")
def seed_admin_user():
    """Checks if the admin user exists in SQLite, creating them with default values if not."""
    db = SessionLocal()
    try:
        admin_user = db.query(models.User).filter(
            models.User.username == settings.DEFAULT_ADMIN_USER
        ).first()
        
        if not admin_user:
            print(f"[*] Seeding default admin user: '{settings.DEFAULT_ADMIN_USER}'")
            hashed_pw = auth_utils.get_password_hash(settings.DEFAULT_ADMIN_PASSWORD)
            new_admin = models.User(
                username=settings.DEFAULT_ADMIN_USER,
                hashed_password=hashed_pw
            )
            db.add(new_admin)
            db.commit()
            print("[+] Seeding completed successfully.")
        else:
            print("[*] Admin user already exists. Seeding skipped.")
    except Exception as e:
        print(f"[-] Error seeding admin user: {e}")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} Backend API!",
        "documentation": "/docs"
    }
