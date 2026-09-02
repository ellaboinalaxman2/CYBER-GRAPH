"""MITRE routes for Member 5 - Attack Engine."""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.core.logging import get_logger
from src.mitre.attack_mapper import AttackMapper
from src.mitre.technique_mapper import TechniqueMapper
from src.mitre.tactic_mapper import TacticMapper
from src.mitre.mitre_data import MitreData
from src.core.exceptions import MitreError

router = APIRouter()
logger = get_logger("api.mitre")

attack_mapper = AttackMapper()
technique_mapper = TechniqueMapper()
tactic_mapper = TacticMapper()
mitre_data = MitreData()


@router.post("/map")
async def map_attack(
    events: List[Dict[str, Any]],
    attack_type: Optional[str] = None,
    confidence_threshold: float = Query(0.5, ge=0, le=1),
):
    """
    Map an attack to MITRE ATT&CK.
    
    Args:
        events: List of events
        attack_type: Attack type
        confidence_threshold: Minimum confidence
        
    Returns:
        dict: Mapping results
    """
    try:
        result = attack_mapper.map_attack(events, attack_type, confidence_threshold)
        
        # Generate report
        report = attack_mapper.generate_report(result)
        
        return {
            "status": "success",
            "data": result,
            "report": report,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except MitreError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"MITRE mapping failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"MITRE mapping failed: {str(e)}")


@router.post("/map/sample")
async def map_sample_attack():
    """
    Map a sample attack to MITRE ATT&CK.
    
    Returns:
        dict: Sample mapping results
    """
    # Sample events
    sample_events = [
        {
            "event_id": "EVT-001",
            "event_type": "LOGIN_FAILURE",
            "source_ip": "192.168.1.50",
            "destination_ip": "192.168.1.20",
            "message": "Failed password for admin from 192.168.1.50",
        },
        {
            "event_id": "EVT-002",
            "event_type": "LOGIN_FAILURE",
            "source_ip": "192.168.1.50",
            "destination_ip": "192.168.1.20",
            "message": "Failed password for admin from 192.168.1.50",
        },
        {
            "event_id": "EVT-003",
            "event_type": "LOGIN_SUCCESS",
            "source_ip": "192.168.1.50",
            "destination_ip": "192.168.1.20",
            "message": "Successful login for admin from 192.168.1.50",
        },
        {
            "event_id": "EVT-004",
            "event_type": "NETWORK_CONNECTION",
            "source_ip": "192.168.1.20",
            "destination_ip": "192.168.1.30",
            "protocol": "SSH",
            "message": "SSH connection from 192.168.1.20 to 192.168.1.30",
        },
        {
            "event_id": "EVT-005",
            "event_type": "FILE_ACCESS",
            "source_ip": "192.168.1.30",
            "destination_ip": "192.168.1.40",
            "message": "Database access from 192.168.1.30",
        },
    ]
    
    result = attack_mapper.map_attack(sample_events, "lateral_movement")
    report = attack_mapper.generate_report(result)
    
    return {
        "status": "success",
        "sample_events": sample_events,
        "data": result,
        "report": report,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/techniques")
async def get_techniques(
    tactic: Optional[str] = Query(None, description="Filter by tactic"),
    search: Optional[str] = Query(None, description="Search by name or description"),
):
    """
    Get MITRE ATT&CK techniques.
    
    Args:
        tactic: Filter by tactic
        search: Search query
        
    Returns:
        dict: Techniques
    """
    try:
        if search:
            techniques = mitre_data.search_techniques(search)
        elif tactic:
            techniques = mitre_data.get_techniques_by_tactic(tactic)
        else:
            techniques = mitre_data.get_all_techniques()
        
        return {
            "status": "success",
            "techniques": techniques,
            "total": len(techniques),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Failed to get techniques: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/techniques/{technique_id}")
async def get_technique(technique_id: str):
    """
    Get a specific MITRE ATT&CK technique.
    
    Args:
        technique_id: Technique ID
        
    Returns:
        dict: Technique details
    """
    try:
        technique = mitre_data.get_technique(technique_id)
        
        if not technique:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Technique {technique_id} not found")
        
        return {
            "status": "success",
            "technique": technique,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get technique: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tactics")
async def get_tactics():
    """
    Get all MITRE ATT&CK tactics.
    
    Returns:
        dict: Tactics
    """
    try:
        tactics = mitre_data.get_all_tactics()
        
        return {
            "status": "success",
            "tactics": tactics,
            "total": len(tactics),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Failed to get tactics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tactics/{tactic}")
async def get_tactic_techniques(tactic: str):
    """
    Get techniques for a specific tactic.
    
    Args:
        tactic: Tactic name
        
    Returns:
        dict: Techniques for tactic
    """
    try:
        techniques = mitre_data.get_techniques_by_tactic(tactic)
        
        return {
            "status": "success",
            "tactic": tactic,
            "techniques": techniques,
            "total": len(techniques),
            "description": tactic_mapper.get_tactic_description(tactic),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Failed to get tactic techniques: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/mapping-rules")
async def get_mapping_rules():
    """
    Get mapping rules.
    
    Returns:
        dict: Mapping rules
    """
    return {
        "status": "success",
        "rules": technique_mapper.mapping_rules,
        "total": len(technique_mapper.mapping_rules),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/mapping-rules")
async def add_mapping_rule(event_type: str, technique_ids: List[str]):
    """
    Add a mapping rule.
    
    Args:
        event_type: Event type
        technique_ids: Technique IDs
        
    Returns:
        dict: Added rule
    """
    try:
        technique_mapper.add_mapping_rule(event_type, technique_ids)
        
        return {
            "status": "success",
            "event_type": event_type,
            "technique_ids": technique_ids,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Failed to add mapping rule: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))