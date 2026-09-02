from fastapi import APIRouter, HTTPException, Request

from app.config.database import MongoDB

router = APIRouter(prefix="/api/graph", tags=["graph"])


def _get_user_id(request: Request) -> str:
    return getattr(request.state, "user", {}).get("userId", "anonymous")


@router.get("")
@router.get("/")
async def get_graph(request: Request, dataset_id: str | None = None):
    db = MongoDB.get_db()
    if db is None:
        return {"success": True, "dataset_id": dataset_id or "sample_dataset", "nodes": [
            {"id": "10.0.0.1", "label": "10.0.0.1", "type": "host", "status": "Normal"},
            {"id": "10.0.0.2", "label": "10.0.0.2", "type": "host", "status": "Suspicious"},
            {"id": "10.0.0.3", "label": "10.0.0.3", "type": "host", "status": "Normal"}
        ], "edges": [
            {"id": "e1", "source": "10.0.0.1", "target": "10.0.0.2", "protocol": "TCP", "count": 15, "status": "Suspicious"},
            {"id": "e2", "source": "10.0.0.2", "target": "10.0.0.3", "protocol": "TCP", "count": 8, "status": "Normal"}
        ]}
    query = {"user_id": _get_user_id(request)}
    if dataset_id:
        query["dataset_id"] = dataset_id
    graph = await db.graphs.find_one(query, {"_id": 0}, sort=[("updated_at", -1)])
    if not graph:
        return {"success": True, "nodes": [], "edges": []}
    return {"success": True, "dataset_id": graph["dataset_id"], "nodes": graph.get("nodes", []), "edges": graph.get("edges", [])}


@router.get("/nodes")
async def get_graph_nodes(request: Request):
    graph = await get_graph(request)
    return graph.get("nodes", [])


@router.get("/edges")
async def get_graph_edges(request: Request):
    graph = await get_graph(request)
    return graph.get("edges", [])


@router.get("/node/{node_id}")
async def get_graph_node(node_id: str, request: Request):
    graph = await get_graph(request)
    nodes = graph.get("nodes", [])
    for node in nodes:
        if str(node.get("id")) == str(node_id):
            return node
    raise HTTPException(status_code=404, detail="Node not found")
