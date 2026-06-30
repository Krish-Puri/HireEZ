import py_compile, sys
for f in ["backend/main.py","backend/api/candidate_routes.py","backend/api/test_routes.py","backend/api/interview_routes.py","backend/services/import_service.py","backend/pipeline/stages/ai_stage.py","backend/pipeline/stages/github_stage.py","backend/pipeline/stages/ranking_stage.py"]:
    try:
        py_compile.compile(f, doraise=True)
        print(f"OK: {f}")
    except py_compile.PyCompileError as e:
        print(f"ERROR: {f}: {e}")
        sys.exit(1)
print("All files OK")