import sys
import os
import json
import subprocess
from pathlib import Path

# Add src to path so we can reuse the fetching engines
sys.path.append(str(Path(__file__).parent.parent / "src"))

from app.database import SessionLocal, engine, Base
from app.models import Discovery
from fetch_papers import fetch_all_papers
from fetch_clinical_trials import fetch_recent_oncology_trials
from v2_fetchers import fetch_v2_intelligence

def ingest_to_v3_db():
    print("="*60)
    print("🚀 V3 Ingestion Engine (Zig Core)")
    print("="*60)

    print("\n[1/3] Fetching global intelligence (Papers, Patents, Grants, Open Source, Clinical Trials)...")
    papers = fetch_all_papers()
    trials = fetch_recent_oncology_trials(days_back=7)
    v2_nodes = fetch_v2_intelligence()
    all_discoveries = papers + trials + v2_nodes

    print(f"\n[2/3] Passing {len(all_discoveries)} discoveries to the Zig Native Engine for significance scoring...")
    

    # Save JSON to a temporary file for Zig to read at compile-time
    zig_dir = Path(__file__).parent.parent / "zig_engine"
    input_file = zig_dir / "src" / "temp_input.json"
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(all_discoveries, f)
    
    # Run Zig engine (compiles and runs instantly)
    result = subprocess.run(
        ["zig", "build", "run"],
        capture_output=True,
        cwd=str(zig_dir)
    )
    
    if result.returncode != 0:
        print(f"❌ Zig engine failed: {result.stderr.decode('utf-8')}")
        return
        
    # Read output from Zig
    scored_json = result.stderr.decode('utf-8') if result.stdout == b'' else result.stdout.decode('utf-8')
    
    # Zig build run might prefix output with some build info, let's extract the JSON block
    try:
        if "{" in scored_json:
            scored_json = scored_json[scored_json.index("{"):]
            
        parsed_data = json.loads(scored_json)
        scored_nodes = parsed_data.get("nodes", [])
        graph_edges = parsed_data.get("edges", [])
    except json.JSONDecodeError:
        print("❌ Failed to parse output from Zig engine. Raw output:")
        print(scored_json)
        return

    # 3. Save to V2 Postgres/SQLite
    from app.models import KnowledgeEdge
    print(f"\n[3/3] Saving {len(scored_nodes)} nodes and {len(graph_edges)} edges to Knowledge Graph Database...")
    db = SessionLocal()
    try:
        new_count = 0
        updated_count = 0
        edge_count = 0
        seen_ids = set()
        
        # Ingest Nodes
        for item in scored_nodes:
            did = item.get("id")
            if not did: continue
            
            if did in seen_ids: continue
            seen_ids.add(did)
                
            existing = db.query(Discovery).filter(Discovery.id == did).first()
            score = item.get("score", 0.0)
            status = item.get("status", "Emerging")
            forecast_prob = item.get("forecast_probability", 0.05)
            
            if existing:
                existing.significance_score = score
                existing.status = status
                existing.forecast_probability = forecast_prob
                updated_count += 1
            else:
                new_d = Discovery(
                    id=did,
                    title=item.get("title", ""),
                    primary_domain="Global", 
                    significance_score=score,
                    status=status,
                    forecast_probability=forecast_prob
                )
                db.add(new_d)
                
                # Also insert as a Knowledge Node for the Graph
                from app.models import KnowledgeNode
                node_exists = db.query(KnowledgeNode).filter(KnowledgeNode.node_id == did).first()
                if not node_exists:
                    new_node = KnowledgeNode(
                        node_id=did,
                        node_name=item.get("title", "")[:100],
                        node_type="Discovery",
                        field="Global"
                    )
                    db.add(new_node)
                    
                new_count += 1
                
        # Ingest Edges
        for e in graph_edges:
            edge_id = f"{e.get('source')}_{e.get('target')}"
            
            # Simple deduplication in session
            if edge_id in seen_ids: continue
            seen_ids.add(edge_id)
            
            new_edge = KnowledgeEdge(
                edge_id=edge_id,
                source_node=e.get("source"),
                target_node=e.get("target"),
                relationship_type=e.get("relationship", "related_to"),
                weight=e.get("weight", 0.0)
            )
            db.merge(new_edge)
            edge_count += 1
                
        db.commit()
        print(f"✅ V3 Ingestion Complete: {new_count} new nodes, {updated_count} updated nodes, {edge_count} edges mapped.")
    except Exception as e:
        db.rollback()
        print(f"❌ Database error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    ingest_to_v3_db()
