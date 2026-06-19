from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from ..models import Discovery, KnowledgeNode

router = APIRouter()

@router.get("/discoveries/", response_model=List[Dict[str, Any]])
def list_discoveries(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """API endpoint to list discoveries, ordered by significance."""
    discoveries = db.query(Discovery).order_by(Discovery.significance_score.desc()).offset(skip).limit(limit).all()
    # Simple dict conversion for MVP
    return [
        {
            "id": d.id,
            "title": d.title,
            "domain": d.primary_domain,
            "score": d.significance_score,
            "status": d.status
        }
        for d in discoveries
    ]

@router.get("/discoveries/{discovery_id}", response_model=Dict[str, Any])
def get_discovery(discovery_id: str, db: Session = Depends(get_db)):
    """API endpoint to get a specific discovery page details."""
    d = db.query(Discovery).filter(Discovery.id == discovery_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Discovery not found")
    return {
        "id": d.id,
        "title": d.title,
        "abstract": d.abstract,
        "domain": d.primary_domain,
        "score": d.significance_score,
        "momentum": d.momentum_score,
        "status": d.status,
        "sources": d.source_urls
    }

@router.get("/knowledge-graph/", response_model=Dict[str, Any])
def get_knowledge_graph(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    """API endpoint to explore Knowledge Graph Nodes and Edges for 3D Visualization."""
    from ..models import KnowledgeEdge
    
    nodes_db = db.query(KnowledgeNode).offset(skip).limit(limit).all()
    # We need to get edges that connect the nodes we just fetched
    node_ids = [n.node_id for n in nodes_db]
    
    edges_db = db.query(KnowledgeEdge).filter(
        KnowledgeEdge.source_node.in_(node_ids),
        KnowledgeEdge.target_node.in_(node_ids)
    ).all()
    
    nodes = [
        {"id": n.node_id, "name": n.node_name, "group": n.node_type} 
        for n in nodes_db
    ]
    
    links = [
        {"source": e.source_node, "target": e.target_node, "value": e.weight, "type": e.relationship_type}
        for e in edges_db
    ]
    
    return {"nodes": nodes, "links": links}
