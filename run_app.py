import sys
import os
import streamlit.web.cli as stcli

def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(basedir, path)

if __name__ == "__main__":
    # Ensure environment is set up correctly
    if getattr(sys, "frozen", False):
        # In PyInstaller bundle
        # Adjust sys.path to ensure local modules can be imported if needed
        # (Though PyInstaller usually handles imports via its internal mechanism)
        pass

    # Setup arguments for streamlit
    # We point to the bundled app.py
    app_path = resolve_path("app.py")
    
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    
    sys.exit(stcli.main())
