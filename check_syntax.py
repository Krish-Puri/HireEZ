import py_compile
try:
    py_compile.compile('frontend/app.py', doraise=True)
    print("Frontend syntax: OK")
except py_compile.PyCompileError as e:
    print(f"ERROR: {e}")