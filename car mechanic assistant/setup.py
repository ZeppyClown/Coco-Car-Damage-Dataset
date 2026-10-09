"""
Setup script for Car Mechanic RAG Assistant
"""
import subprocess
import sys
from pathlib import Path


def main():
    """Main setup function"""
    print("="*80)
    print("CAR MECHANIC RAG ASSISTANT - SETUP")
    print("="*80)

    # Step 1: Check Python version
    print("\n1. Checking Python version...")
    if sys.version_info < (3, 12):
        print("   ❌ Python 3.12 or higher required")
        return
    print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Step 2: Install dependencies
    print("\n2. Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("   ✓ Dependencies installed")
    except subprocess.CalledProcessError:
        print("   ❌ Failed to install dependencies")
        return

    # Step 3: Check for API key
    print("\n3. Checking for API key...")
    env_file = Path(".env")
    if not env_file.exists():
        print("   ⚠ .env file not found")
        print("   Creating .env from .env.example...")
        example_file = Path(".env.example")
        if example_file.exists():
            env_file.write_text(example_file.read_text())
            print("   ✓ .env file created")
            print("\n   ⚠ IMPORTANT: Edit .env and add your GOOGLE_API_KEY")
        else:
            print("   ❌ .env.example not found")
    else:
        # Check if API key is set
        env_content = env_file.read_text()
        if "your_gemini_api_key_here" in env_content or "GOOGLE_API_KEY=" not in env_content:
            print("   ⚠ GOOGLE_API_KEY not configured in .env")
            print("   Please edit .env and add your API key")
        else:
            print("   ✓ API key configured")

    # Step 4: Build vector database
    print("\n4. Building vector database...")
    response = input("   Build vector database now? This will process all knowledge base files. (y/n): ")
    if response.lower() == 'y':
        print("\n   Starting database build...")
        try:
            subprocess.check_call([sys.executable, "-m", "src.vector_store", "--output", "runtime/releases/initial"])
            print("   ✓ Vector database built successfully")
        except subprocess.CalledProcessError:
            print("   ❌ Failed to build vector database")
            print("   You can build it later by running: python -m src.vector_store --output runtime/releases/initial")
    else:
        print("   ⊘ Skipped. You can build it later by running: python -m src.vector_store --output runtime/releases/initial")

    # Done
    print("\n" + "="*80)
    print("SETUP COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Make sure your GOOGLE_API_KEY is set in .env")
    print("2. Build the vector database: python -m src.vector_store --output runtime/releases/initial")
    print("3. Test the system: CHROMA_PERSIST_DIRECTORY=runtime/releases/initial python -m src.test_rag")
    print("4. Run interactive mode: CHROMA_PERSIST_DIRECTORY=runtime/releases/initial python app.py")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
