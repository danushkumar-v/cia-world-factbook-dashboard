"""
Safe app runner with detailed error reporting
"""
import sys
import traceback

try:
    print("=" * 60)
    print("Starting Global Insights Explorer...")
    print("=" * 60)
    
    import app
    
    print("\n✓ App loaded successfully")
    print("✓ Starting server...\n")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("❌ ERROR DURING STARTUP")
    print("=" * 60)
    print(f"\nError type: {type(e).__name__}")
    print(f"Error message: {str(e)}\n")
    print("Full traceback:")
    print("-" * 60)
    traceback.print_exc()
    print("-" * 60)
    sys.exit(1)
