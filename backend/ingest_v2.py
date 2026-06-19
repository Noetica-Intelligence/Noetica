import sys
import os
from pathlib import Path

# Add src to path so we can reuse the scoring and fetching engines
sys.path.append(str(Path(__file__).parent.parent / "src"))

from app.database import SessionLocal, engine, Base
from app.models import Discovery
from fetch_papers import fetch_all_papers
from v2_fetchers import fetch_v2_intelligence
from score_papers import score_and_rank

def ingest_to_v2_db():
    print("="*60)
    print("🚀 V2 Ingestion Engine")
    print("="*60)

    # 1. Fetch
    print("\n[1/3] Fetching global intelligence (Papers, Patents, Grants, Open Source)...")
    papers = fetch_all_papers()
    v2_nodes = fetch_v2_intelligence()
    
    all_discoveries = papers + v2_nodes

    # 2. Score
    print(f"\n[2/3] Scoring and ranking {len(all_discoveries)} discoveries...")
    scored = score_and_rank(all_discoveries, top_n=len(all_discoveries))

    # 3. Save to V2 Postgres/SQLite
    print(f"\n[3/3] Saving to V2 Database...")
    db = SessionLocal()
    try:
        new_count = 0
        updated_count = 0
        seen_ids = set()
        
        for item in scored:
            did = item.get("id")
            if not did:
                continue
            
            # Simple deduplication within the loop to prevent double insertions in the same session
            if did in seen_ids:
                continue
            seen_ids.add(did)
                
            existing = db.query(Discovery).filter(Discovery.id == did).first()
            score = item.get("scores", {}).get("composite", 0.0)
            
            urls = [item.get("url", "")] + item.get("cluster_urls", [])
            
            if existing:
                existing.significance_score = score
                existing.status = item.get("status", "Emerging")
                updated_count += 1
            else:
                new_d = Discovery(
                    id=did,
                    title=item.get("title", ""),
                    abstract=item.get("abstract", ""),
                    primary_domain=item.get("domain", ""),
                    significance_score=score,
                    status=item.get("status", "Emerging"),
                    source_urls=urls,
                    authors=item.get("authors", [])
                )
                db.add(new_d)
                new_count += 1
                
        db.commit()
        print(f"✅ Ingestion Complete: {new_count} new, {updated_count} updated.")
    except Exception as e:
        db.rollback()
        print(f"❌ Database error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    ingest_to_v2_db()
