#!/usr/bin/env python3
"""
System Check Script
Verifies all prerequisites are met before starting the server
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_python_version():
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible (3.8+)")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_postgresql():
    print_header("Checking PostgreSQL")
    try:
        result = subprocess.run(['pg_isready'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL is running")
            print(result.stdout.strip())
            return True
        else:
            print("❌ PostgreSQL is not running")
            print("Start it with: brew services start postgresql@14")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL not found or not in PATH")
        print("Install it with: brew install postgresql@14")
        return False

def check_env_file():
    print_header("Checking Environment Variables")
    env_path = Path(".env")

    if env_path.exists():
        print(f"✅ .env file exists at {env_path.absolute()}")

        # Check for required variables
        with open(env_path) as f:
            content = f.read()
            required = ["DATABASE_URL", "GOOGLE_API_KEY", "GOOGLE_CSE_ID"]
            missing = []

            for var in required:
                if var in content and not content.count(f"{var}=\n"):
                    print(f"  ✅ {var} is set")
                else:
                    print(f"  ⚠️  {var} may not be set")
                    missing.append(var)

            return len(missing) == 0
    else:
        print("❌ .env file not found")
        print("Create it with the template in STARTUP_GUIDE.md")
        return False

def check_dependencies():
    print_header("Checking Python Dependencies")

    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',
        'alembic',
        'pydantic',
        'scikit-learn'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Install missing packages with:")
        print(f"pip install {' '.join(missing)}")
        return False

    return True

def check_database():
    print_header("Checking Database Connection")

    try:
        from app.db.session import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")

            # Check if tables exist
            result = conn.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()

            if table_count > 0:
                print(f"✅ Database has {table_count} tables")
            else:
                print("⚠️  No tables found - run migrations")

            return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nSteps to fix:")
        print("1. Ensure PostgreSQL is running")
        print("2. Create database: psql postgres -c 'CREATE DATABASE automotive_intelligence;'")
        print("3. Check DATABASE_URL in .env file")
        return False

def check_data():
    print_header("Checking Database Data")

    try:
        from app.db.session import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            # Check parts_catalog
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM parts_catalog"))
                count = result.scalar()

                if count > 0:
                    print(f"✅ parts_catalog has {count} records")
                else:
                    print("⚠️  parts_catalog is empty - run: python scripts/seed_data.py")
            except:
                print("⚠️  parts_catalog table doesn't exist - run migrations")

            return True

    except Exception as e:
        print(f"❌ Could not check data: {e}")
        return False

def check_fault_code_database():
    print_header("Checking Fault Code Database")

    try:
        from app.data.fault_codes_database import FAULT_CODE_DATABASE

        code_count = len(FAULT_CODE_DATABASE)
        print(f"✅ Fault code database loaded with {code_count} codes")

        # List codes
        print("Available codes:", ", ".join(FAULT_CODE_DATABASE.keys()))
        return True

    except Exception as e:
        print(f"❌ Could not load fault code database: {e}")
        return False

def check_services():
    print_header("Checking Services")

    try:
        from app.services.diagnostics_service import get_diagnostics_service
        from app.services.valuation_service import get_valuation_service
        from app.services.paint_code_service import get_paint_code_service

        print("✅ DiagnosticsService can be imported")
        print("✅ ValuationService can be imported")
        print("✅ PaintCodeService can be imported")

        # Try to instantiate
        diag = get_diagnostics_service()
        val = get_valuation_service()
        paint = get_paint_code_service()

        print("✅ All services instantiated successfully")
        return True

    except Exception as e:
        print(f"❌ Service import failed: {e}")
        return False

def check_port_available():
    print_header("Checking Port 8000")

    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()

        if result == 0:
            print("⚠️  Port 8000 is already in use")
            print("Kill existing process with: kill -9 $(lsof -ti:8000)")
            print("Or use a different port: uvicorn app.main:app --port 8001")
            return False
        else:
            print("✅ Port 8000 is available")
            return True

    except Exception as e:
        print(f"⚠️  Could not check port: {e}")
        return True  # Assume it's available

def main():
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   🤖 Automotive Intelligence System - Health Check         ║")
    print("╚════════════════════════════════════════════════════════════╝")

    checks = [
        ("Python Version", check_python_version),
        ("PostgreSQL", check_postgresql),
        ("Environment Variables", check_env_file),
        ("Python Dependencies", check_dependencies),
        ("Database Connection", check_database),
        ("Database Data", check_data),
        ("Fault Code Database", check_fault_code_database),
        ("Services", check_services),
        ("Port Availability", check_port_available),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results[name] = False

    # Summary
    print("\n")
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 All checks passed! You're ready to start the server.")
        print("\nRun: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("Then open: http://localhost:8000")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before starting.")
        print("\nRefer to STARTUP_GUIDE.md for detailed instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
