from backend.database.connection import SessionLocal
from backend.ranking.ranking_engine import ranking_engine

db = SessionLocal()

ranking = ranking_engine.rank_all_candidates(db)

for candidate, result in ranking:

    print(
        f"{result.rank}. "
        f"{candidate.name} "
        f"-> {result.final_score}"
    )

db.close()