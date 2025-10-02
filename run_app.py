#!/usr/bin/env python3
"""
Simple launcher for the GetGSA Streamlit app
"""
import subprocess
import sys
import os

def main():
    """Launch the Streamlit app"""
    try:
        # Change to the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        print("Starting GetGSA Streamlit App...")
        print("=" * 50)
        print("The app will open in your browser at: http://localhost:8501")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying alternative method...")
        
        # Alternative: direct import and run
        try:
            import streamlit.web.cli as stcli
            import sys
            
            sys.argv = ["streamlit", "run", "app.py", "--server.port", "8501"]
            stcli.main()
        except Exception as e2:
            print(f"Alternative method also failed: {e2}")

if __name__ == "__main__":
    main()
