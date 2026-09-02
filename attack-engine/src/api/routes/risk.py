"""Risk routes for Member 5 - Attack Engine."""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.core.logging import get_logger
from src.risk.risk_engine import RiskEngine
from src.risk.risk_scoring import RiskScorer
from src.risk.severity import SeverityCalculator, SeverityLevel
from src.risk.asset_criticality import AssetCriticalityManager
from src.risk.risk_rules import RiskRulesEngine

router = APIRouter()
logger = get_logger("api.risk")

risk_engine = RiskEngine()
risk_scorer = RiskScorer()
severity_calculator = SeverityCalculator()
asset_criticality = AssetCriticalityManager()
risk_rules = RiskRulesEngine()


@router.post("/assess")
async def assess_risk(
    incident: Dict[str, Any],
    events: List[Dict[str, Any]],
    predictions: Optional[List[Dict[str, Any]]] = None,
):
    """
    Assess risk for an incident.
    
    Args:
        incident: Incident data
        events: List of events
        predictions: AI predictions
        
    Returns:
        dict: Risk assessment results
    """
    try:
        result = risk_engine.assess(incident, events, predictions)
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Risk assessment failed: {str(e)}")


@router.post("/assess/sample")
async def assess_sample_risk():
    """
    Assess risk for a sample incident.
    
    Returns:
        dict: Sample risk assessment
    """
    # Sample incident
    incident = {
        "incident_id": "INC-SAMPLE-001",
        "attack_type": "lateral_movement",
        "severity": "HIGH",
        "nodes": ["192.168.1.50", "192.168.1.20", "192.168.1.30", "192.168.1.40"],
        "attack_path": [
            {"from": "192.168.1.50", "to": "192.168.1.20"},
            {"from": "192.168.1.20", "to": "192.168.1.30"},
            {"from": "192.168.1.30", "to": "192.168.1.40"},
        ],
    }
    
    # Sample events
    events = [
        {"event_id": "EVT-001", "event_type": "LOGIN_FAILURE", "source_ip": "192.168.1.50"},
        {"event_id": "EVT-002", "event_type": "LOGIN_FAILURE", "source_ip": "192.168.1.50"},
        {"event_id": "EVT-003", "event_type": "LOGIN_SUCCESS", "source_ip": "192.168.1.50"},
        {"event_id": "EVT-004", "event_type": "NETWORK_CONNECTION", "source_ip": "192.168.1.20"},
        {"event_id": "EVT-005", "event_type": "FILE_ACCESS", "source_ip": "192.168.1.30"},
    ]
    
    # Sample predictions
    predictions = [
        {"node_id": "192.168.1.50", "anomaly_score": 0.85},
        {"node_id": "192.168.1.20", "anomaly_score": 0.90},
        {"node_id": "192.168.1.30", "anomaly_score": 0.75},
        {"node_id": "192.168.1.40", "anomaly_score": 0.95},
    ]
    
    result = risk_engine.assess(incident, events, predictions)
    
    return {
        "status": "success",
        "sample_incident": incident,
        "sample_events": events,
        "sample_predictions": predictions,
        "data": result,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/severity")
async def get_severity_thresholds():
    """
    Get severity thresholds.
    
    Returns:
        dict: Severity thresholds
    """
    return {
        "status": "success",
        "thresholds": {
            level.value: {
                "threshold": severity_calculator.get_threshold(level),
                "color": severity_calculator.get_severity_color(level),
                "icon": severity_calculator.get_severity_icon(level),
            }
            for level in SeverityLevel
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/criticality")
async def get_asset_criticality():
    """
    Get asset criticality definitions.
    
    Returns:
        dict: Asset criticality definitions
    """
    return {
        "status": "success",
        "criticalities": asset_criticality.get_all_criticalities(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/criticality")
async def add_asset_criticality(
    asset_type: str,
    criticality_score: int,
    description: str,
    tags: Optional[List[str]] = None,
):
    """
    Add or update asset criticality.
    
    Args:
        asset_type: Asset type
        criticality_score: Criticality score (1-100)
        description: Description
        tags: Tags
        
    Returns:
        dict: Updated criticality
    """
    try:
        from src.risk.asset_criticality import AssetCriticality
        
        if not 1 <= criticality_score <= 100:
            raise ValueError("Criticality score must be between 1 and 100")
        
        criticality = AssetCriticality(
            asset_type=asset_type,
            criticality_score=criticality_score,
            description=description,
            tags=tags or [],
        )
        
        asset_criticality.add_criticality(asset_type, criticality)
        
        return {
            "status": "success",
            "asset_type": asset_type,
            "criticality": criticality_score,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add criticality: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/rules")
async def get_risk_rules():
    """
    Get risk rules.
    
    Returns:
        dict: Risk rules
    """
    return {
        "status": "success",
        "rules": risk_rules.get_rules(),
        "total": len(risk_rules.get_rules()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/rules")
async def add_risk_rule(
    name: str,
    description: str,
    condition: Dict[str, Any],
    score_modifier: float,
    severity: str = "MEDIUM",
    tags: Optional[List[str]] = None,
):
    """
    Add a risk rule.
    
    Args:
        name: Rule name
        description: Rule description
        condition: Rule condition
        score_modifier: Score modifier
        severity: Severity level
        tags: Tags
        
    Returns:
        dict: Added rule
    """
    try:
        from src.risk.risk_rules import RiskRule
        
        rule = RiskRule(
            name=name,
            description=description,
            condition=condition,
            score_modifier=score_modifier,
            severity=severity,
            tags=tags or [],
        )
        
        risk_rules.add_rule(rule)
        
        return {
            "status": "success",
            "rule": {
                "name": name,
                "description": description,
                "condition": condition,
                "score_modifier": score_modifier,
                "severity": severity,
                "tags": tags or [],
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Failed to add rule: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/rules/{rule_name}")
async def remove_risk_rule(rule_name: str):
    """
    Remove a risk rule.
    
    Args:
        rule_name: Rule name
        
    Returns:
        dict: Removal status
    """
    try:
        removed = risk_rules.remove_rule(rule_name)
        
        if not removed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule '{rule_name}' not found")
        
        return {
            "status": "success",
            "removed": rule_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove rule: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/score")
async def calculate_risk_score(
    anomaly_score: float = Query(..., ge=0, le=1, description="Anomaly score"),
    nodes: List[str] = Query(..., description="Node IDs"),
    attack_type: Optional[str] = Query(None, description="Attack type"),
    event_severity: Optional[str] = Query(None, description="Event severity"),
):
    """
    Calculate risk score.
    
    Args:
        anomaly_score: AI anomaly score
        nodes: Node IDs
        attack_type: Attack type
        event_severity: Event severity
        
    Returns:
        dict: Risk score calculation
    """
    try:
        result = risk_scorer.calculate(
            anomaly_score=anomaly_score,
            nodes=nodes,
            attack_type=attack_type,
            event_severity=event_severity,
        )
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Risk score calculation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))