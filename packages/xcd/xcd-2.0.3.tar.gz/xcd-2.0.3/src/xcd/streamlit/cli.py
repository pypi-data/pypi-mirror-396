def main():
    from pathlib import Path
    import sys
    from streamlit.web import cli as strcli

    app = Path(__file__).with_name("app.py")
    sys.argv = ["streamlit", "run", str(app)]
    strcli.main()