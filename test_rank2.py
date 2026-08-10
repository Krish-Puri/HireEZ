import sys
sys.path.insert(0, '.')
from backend.database.connection import SessionLocal
from backend.ranking.ranking_engine import ranking_engine
from backend.models.candidate import Candidate

db = SessionLocal()
try:
    candidates = db.query(Candidate).all()
    print("Total candidates:", len(candidates))
    for c in candidates:
        result = ranking_engine.rank_candidate(db, c)
        print(f"  {c.id} {c.name}: result={result is not None}, score={result.final_score if result else None}")
        if result:
            c.final_score = result.final_score
            c.candidate_rank = 0  # temporary
            db.commit()
    print("Done")
finally:
    db.close()