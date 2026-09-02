"""Dataset ingestion and graph projection for uploaded CICIDS2017 CSV files.

This service deliberately keeps source labels separate from model predictions.  A
label in CICIDS2017 is ground truth; it is not presented as an AI prediction.
"""
import asyncio
import csv
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException, status

from app.config.database import MongoDB
from app.config.settings import settings


NETWORK_GRAPH_COLUMNS = {"source ip", "destination ip"}
# CICIDS feature exports are commonly distributed without Flow ID/IP columns.
# These columns identify that export without pretending it contains topology.
FEATURE_ONLY_CICIDS_COLUMNS = {"destination port", "flow duration", "label"}

# Map common CICIDS2017 and Kdd99 column names to standard names
COLUMN_NAME_MAPPING = {
    # Source IP variations
    "source ip": ["source ip", "src ip", "sourceip", "src_ip", "source_ip", "id 1", "ipv4_src_addr"],
    # Destination IP variations
    "destination ip": ["destination ip", "dest ip", "destinationip", "dest_ip", "destination_ip", "id 2", "ipv4_dst_addr"],
    # Source port variations
    "source port": ["source port", "src port", "srcport", "src_port", "source_port", "src_port", "l4_src_port"],
    # Destination port variations
    "destination port": ["destination port", "dest port", "destport", "dest_port", "destination_port", "dest_port", "l4_dst_port"],
    # Protocol variations
    "protocol": ["protocol", "proto", "ip_proto", "ip_protocol", "prtcl"],
}

# Import settings to use consistent max upload bytes
from app.config.settings import settings
MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_BYTES


def _clean_column(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def _pick(row: Dict[str, Any], *names: str, default=None):
    for name in names:
        value = row.get(_clean_column(name))
        if value not in (None, ""):
            return value.strip() if isinstance(value, str) else value
    return default


def _number(value: Any, default=0):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


class DatasetService:
    _dataset_store: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def set_dataset_state(dataset_id: str, user_id: str, status: str, progress: int, **extra: Any) -> Dict[str, Any]:
        entry = DatasetService._dataset_store.setdefault(dataset_id, {"dataset_id": dataset_id, "user_id": user_id, "status": "UPLOADED", "progress": 0})
        entry.update({"dataset_id": dataset_id, "user_id": user_id, "status": status, "progress": progress, **extra})
        return entry

    @staticmethod
    def get_dataset_state(dataset_id: str) -> Optional[Dict[str, Any]]:
        return DatasetService._dataset_store.get(dataset_id)

    @staticmethod
    def list_datasets_for_user(user_id: str) -> List[Dict[str, Any]]:
        return [entry for entry in DatasetService._dataset_store.values() if entry.get("user_id") == user_id]

    @staticmethod
    def validate_upload(filename: str, content_type: Optional[str], size: int) -> None:
        if not filename or Path(filename).suffix.lower() != ".csv":
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload a CSV file.")
        if size <= 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        if size > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="File exceeds maximum allowed size.")
        if content_type and content_type not in {"text/csv", "application/csv", "application/vnd.ms-excel", "application/octet-stream"}:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

    @staticmethod
    def validate_csv_header(path: str) -> List[str]:
        try:
            with open(path, "r", encoding="utf-8-sig", newline="") as source:
                header = next(csv.reader(source), None)
        except (OSError, UnicodeDecodeError, csv.Error):
            raise HTTPException(status_code=400, detail="Invalid CSV format.")
        normalized = [_clean_column(item) for item in (header or [])]
        if not normalized:
            raise HTTPException(status_code=400, detail="CSV file is empty.")
        
        has_topology = DatasetService.has_topology_columns(normalized)
        is_feature_only_cicids = FEATURE_ONLY_CICIDS_COLUMNS.issubset(set(normalized))
        if not has_topology and not is_feature_only_cicids:
            raise HTTPException(
                status_code=400,
                detail=("CSV is not a supported CICIDS2017 export. Include Source IP and Destination IP for a "
                        "network graph, or the CICIDS feature columns Destination Port, Flow Duration, and Label "
                        "for feature-only analysis.")
            )
        
        return normalized

    @staticmethod
    def has_topology_columns(columns: List[str]) -> bool:
        available = set(columns)
        return (any(name in available for name in COLUMN_NAME_MAPPING["source ip"]) and
                any(name in available for name in COLUMN_NAME_MAPPING["destination ip"]))

    @staticmethod
    def normalize_row(row: Dict[str, Any], dataset_id: str, user_id: str, topology_available: bool) -> Optional[Dict[str, Any]]:
        # Use alternative column names for flexibility
        source_ip = _pick(row, *COLUMN_NAME_MAPPING["source ip"])
        destination_ip = _pick(row, *COLUMN_NAME_MAPPING["destination ip"])
        if topology_available and (not source_ip or not destination_ip):
            return None
        raw_label = _pick(row, "label", "class", "classification", "attack", default="UNKNOWN")
        label = str(raw_label).strip()
        is_attack = label.upper() not in {"BENIGN", "NORMAL", "", "background"}
        event = {
            "dataset_id": dataset_id,
            "user_id": user_id,
            "source_ip": source_ip if topology_available else None,
            "destination_ip": destination_ip if topology_available else None,
            "source_port": int(_number(_pick(row, *COLUMN_NAME_MAPPING["source port"]))),
            "destination_port": int(_number(_pick(row, *COLUMN_NAME_MAPPING["destination port"]))),
            "protocol": str(_pick(row, *COLUMN_NAME_MAPPING["protocol"], default="UNKNOWN")),
            "timestamp": _pick(row, "timestamp", "time", "date", default=None),
            "duration": _number(_pick(row, "flow duration", "flow_duration", "duration", "dur")),
            "packet_count": int(_number(_pick(row, "total forward packets", "total fwd packets", "fwd pkt", "total packets", "pkts"))),
            "byte_count": _number(_pick(row, "total length of fwd packets", "total fwd bytes", "total bytes", "bytes", "tot bytes")),
            "label": "ATTACK" if is_attack else "NORMAL",
            "attack_type": label if is_attack else None,
            "ground_truth_label": label,
            "created_at": datetime.utcnow(),
        }
        if not topology_available:
            # Retain feature vectors for real ML inference, without fabricating host identity.
            event["features"] = {
                key: _number(value, default=value) for key, value in row.items()
                if key not in {"label", "class", "classification", "attack"}
            }
            event["topology_available"] = False
        return event

    @staticmethod
    async def process_dataset(dataset_id: str, user_id: str, path: str) -> None:
        db = MongoDB.get_db()
        if db is None:
            with open(path, "r", encoding="utf-8-sig", newline="") as source:
                reader = csv.DictReader(source)
                columns = [_clean_column(name) for name in (reader.fieldnames or [])]
                reader.fieldnames = columns
                topology_available = DatasetService.has_topology_columns(columns)
                total = normal = attack = invalid = 0
                categories = Counter()
                for raw in reader:
                    total += 1
                    event = DatasetService.normalize_row({_clean_column(key): value for key, value in raw.items() if key}, dataset_id, user_id, topology_available)
                    if not event:
                        invalid += 1
                        continue
                    if event["label"] == "ATTACK":
                        attack += 1
                        categories[event["attack_type"] or "Unknown attack"] += 1
                    else:
                        normal += 1
            nodes = [{"id": f"dataset:{dataset_id}", "label": "CICIDS2017 dataset", "type": "dataset", "status": "Normal"}]
            edges = []
            for attack_type, count in categories.items():
                node_id = f"attack:{dataset_id}:{attack_type}"
                nodes.append({"id": node_id, "label": attack_type, "type": "attack_category", "status": "Suspicious", "count": count})
                edges.append({"id": f"{dataset_id}:{attack_type}", "source": f"dataset:{dataset_id}", "target": node_id, "status": "Suspicious", "attack_type": attack_type, "count": count})
            DatasetService.set_dataset_state(dataset_id, user_id, "VALIDATING", 10)
            await asyncio.sleep(0.2)
            DatasetService.set_dataset_state(dataset_id, user_id, "INGESTING", 35, total_records=total, processed_records=total - invalid, invalid_records=invalid, normal_records=normal, attack_records=attack, topology_available=topology_available)
            await asyncio.sleep(0.3)
            DatasetService.set_dataset_state(dataset_id, user_id, "ANALYZING", 65, ml={"status": "NOT_RUN", "reason": "AI service unavailable; accepted in local pipeline."})
            await asyncio.sleep(0.2)
            DatasetService.set_dataset_state(dataset_id, user_id, "GRAPH_BUILDING", 90, nodes=nodes, edges=edges)
            await asyncio.sleep(0.2)
            DatasetService.set_dataset_state(dataset_id, user_id, "COMPLETED", 100, completed_at=datetime.utcnow().isoformat())
            return

        try:
            await db.datasets.update_one({"dataset_id": dataset_id, "user_id": user_id}, {"$set": {"status": "INGESTING", "progress": 25}})
            total = valid = invalid = normal = attack = 0
            events = []
            with open(path, "r", encoding="utf-8-sig", newline="") as source:
                reader = csv.DictReader(source)
                if not reader.fieldnames:
                    raise ValueError("Invalid CSV format")
                reader.fieldnames = [_clean_column(name) for name in reader.fieldnames]
                topology_available = DatasetService.has_topology_columns(reader.fieldnames)
                for raw in reader:
                    total += 1
                    row = {_clean_column(key): value for key, value in raw.items() if key is not None}
                    event = DatasetService.normalize_row(row, dataset_id, user_id, topology_available)
                    if not event:
                        invalid += 1
                        continue
                    valid += 1
                    if event["label"] == "ATTACK":
                        attack += 1
                    else:
                        normal += 1
                    events.append(event)
                    if len(events) >= 1000:
                        await db.events.insert_many(events)
                        events = []
                if events:
                    await db.events.insert_many(events)

            await db.datasets.update_one(
                {"dataset_id": dataset_id, "user_id": user_id},
                {"$set": {"status": "ANALYZING", "progress": 65, "total_records": total, "processed_records": valid,
                          "invalid_records": invalid, "normal_records": normal, "attack_records": attack, "topology_available": topology_available}},
            )
            inference = await DatasetService.request_inference(dataset_id, user_id)
            await db.datasets.update_one(
                {"dataset_id": dataset_id, "user_id": user_id},
                {"$set": {"status": "GRAPH_BUILDING", "progress": 85, "ml": inference}},
            )
            await DatasetService.build_graph_projection(dataset_id, user_id)
            await db.datasets.update_one(
                {"dataset_id": dataset_id, "user_id": user_id},
                {"$set": {"status": "COMPLETED", "progress": 100, "completed_at": datetime.utcnow()}},
            )
        except Exception:
            await db.datasets.update_one(
                {"dataset_id": dataset_id, "user_id": user_id},
                {"$set": {"status": "FAILED", "progress": 100, "error": "Unable to parse and process network traffic data."}},
            )

    @staticmethod
    async def request_inference(dataset_id: str, user_id: str) -> Dict[str, Any]:
        payload = {"dataset_id": dataset_id, "user_id": user_id}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(f"{settings.AI_ENGINE_URL.rstrip('/')}/api/prediction/dataset", json=payload)
                response.raise_for_status()
                return {"status": "COMPLETED", "result": response.json()}
        except Exception:
            return {"status": "NOT_RUN", "reason": "AI inference service is unavailable or has no dataset inference endpoint."}

    @staticmethod
    async def build_graph_projection(dataset_id: str, user_id: str) -> None:
        """Build a Mongo graph projection used by the existing Cytoscape UI.

        It is derived from source traffic/labels and is intentionally not an ML claim.
        """
        db = MongoDB.get_db()
        cursor = db.events.find({"dataset_id": dataset_id, "user_id": user_id}, {"source_ip": 1, "destination_ip": 1, "protocol": 1, "destination_port": 1, "label": 1, "attack_type": 1, "topology_available": 1}).limit(5000)
        nodes, edges = {}, {}
        async for event in cursor:
            if not event.get("source_ip") or not event.get("destination_ip"):
                # Feature-only CICIDS exports have no network identity. Grouping by
                # known labels produces an honest dataset-to-attack-category view.
                dataset_node = f"dataset:{dataset_id}"
                nodes.setdefault(dataset_node, {"id": dataset_node, "label": "CICIDS2017 dataset", "type": "dataset", "status": "Normal", "dataset_id": dataset_id})
                attack_type = event.get("attack_type") or "Normal traffic"
                category_node = f"category:{dataset_id}:{attack_type}"
                nodes.setdefault(category_node, {"id": category_node, "label": attack_type, "type": "attack_category", "status": "Suspicious" if event.get("label") == "ATTACK" else "Normal", "dataset_id": dataset_id})
                key = (dataset_node, category_node)
                edge = edges.setdefault(key, {"id": "|".join(key), "source": dataset_node, "target": category_node, "count": 0, "status": "Suspicious" if event.get("label") == "ATTACK" else "Normal", "attack_type": event.get("attack_type"), "dataset_id": dataset_id})
                edge["count"] += 1
                continue
            for ip in (event["source_ip"], event["destination_ip"]):
                nodes.setdefault(ip, {"id": ip, "label": ip, "type": "host", "ip": ip, "status": "Normal", "dataset_id": dataset_id})
            key = (event["source_ip"], event["destination_ip"], str(event.get("protocol")), event.get("destination_port"))
            edge = edges.setdefault(key, {"id": "|".join(map(str, key)), "source": event["source_ip"], "target": event["destination_ip"], "protocol": event.get("protocol"), "port": event.get("destination_port"), "count": 0, "status": "Normal", "attack_type": None, "dataset_id": dataset_id})
            edge["count"] += 1
            if event.get("label") == "ATTACK":
                edge["status"] = "Suspicious"
                edge["attack_type"] = event.get("attack_type")
                nodes[event["source_ip"]]["status"] = "Suspicious"
                nodes[event["destination_ip"]]["status"] = "Suspicious"
        await db.graphs.replace_one({"dataset_id": dataset_id, "user_id": user_id}, {"dataset_id": dataset_id, "user_id": user_id, "nodes": list(nodes.values()), "edges": list(edges.values()), "updated_at": datetime.utcnow()}, upsert=True)
