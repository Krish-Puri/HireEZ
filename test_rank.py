import sys
sys.path.insert(0, '.')
from backend.database.connection import SessionLocal
from backend.ranking.ranking_engine import ranking_engine

db = SessionLocal()
try:
    ranking = ranking_engine.rank_all_candidates(db)
    print("Ranked:", len(ranking))
    for c, r in ranking[:3]:
        print(f"  {c.id} {c.name}: score={r.final_score} rank={r.rank}")
finally:
    db.close()