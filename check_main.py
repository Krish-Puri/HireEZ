import sys
sys.path.insert(0, '.')
try:
    import backend.main
    print("Backend OK")
except Exception as e:
    print("ERROR:", e)