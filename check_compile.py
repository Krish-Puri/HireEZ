import py_compile, sys
files = [
    "backend/main.py",
    "backend/ai/providers/gemini_provider.py",
    "backend/ranking/ranking_engine.py",
    "backend/pipeline/stages/ranking_stage.py",
    "backend/pipeline/stages/ai_stage.py",
]
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print("OK:", f)
    except Exception as e:
        print("ERROR:", f, e)
        sys.exit(1)
print("All OK")