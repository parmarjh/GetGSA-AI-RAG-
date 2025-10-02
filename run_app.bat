@echo off
echo Starting GetGSA Streamlit App...
echo.
echo The app will open in your browser at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
python -m streamlit run app.py --server.port 8501
pause
