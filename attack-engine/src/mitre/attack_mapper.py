"""Attack mapper for Member 5 - Attack Engine."""

from typing import List, Dict, Any, Optional
from datetime import datetime

from src.core.logging import get_logger
from src.mitre.technique_mapper import TechniqueMapper
from src.mitre.tactic_mapper import TacticMapper
from src.mitre.mitre_data import MitreData


class AttackMapper:
    """
    Main MITRE ATT&CK mapping engine.
    
    Features:
    - Map attacks to MITRE techniques
    - Map attacks to tactics
    - Generate MITRE reports
    - Confidence scoring for mapping
    """
    
    def __init__(self):
        """Initialize the attack mapper."""
        self.logger = get_logger("mitre.attack_mapper")
        self.technique_mapper = TechniqueMapper()
        self.tactic_mapper = TacticMapper()
        self.mitre_data = MitreData()
    
    def map_attack(
        self,
        events: List[Dict[str, Any]],
        attack_type: Optional[str] = None,
        confidence_threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Map an attack to MITRE ATT&CK.
        
        Args:
            events: List of events
            attack_type: Attack type
            confidence_threshold: Minimum confidence
            
        Returns:
            Dict[str, Any]: Mapping results
        """
        self.logger.info(f"Mapping attack with {len(events)} events")
        
        # Get techniques
        techniques = self.technique_mapper.get_techniques_for_incident(events, attack_type)
        
        # Get tactics
        tactics_result = self.tactic_mapper.get_tactics_for_incident(events, attack_type)
        
        # Calculate confidence
        confidence = self._calculate_confidence(techniques, events)
        
        # Generate report
        result = {
            "status": "success",
            "attack_type": attack_type or "unknown",
            "events_mapped": len(events),
            "techniques_found": len(techniques),
            "techniques": techniques,
            "tactics": tactics_result["tactics"],
            "tactic_coverage": tactics_result["tactic_coverage"],
            "tactic_chain": tactics_result["tactic_chain"],
            "attack_phase": self.tactic_mapper.get_attack_phase(tactics_result["all_tactics"]),
            "confidence": confidence,
            "confidence_level": self._get_confidence_level(confidence),
            "mitre_version": self.mitre_data._data.get("version", "unknown"),
            "mapped_at": datetime.utcnow().isoformat() + "Z",
        }
        
        self.logger.info(f"Mapping complete: {len(techniques)} techniques, {tactics_result['tactic_coverage']} tactics")
        return result
    
    def _calculate_confidence(self, techniques: List[Dict], events: List[Dict]) -> float:
        """
        Calculate confidence in the mapping.
        
        Args:
            techniques: Mapped techniques
            events: Events
            
        Returns:
            float: Confidence score (0-1)
        """
        if not techniques or not events:
            return 0.0
        
        # Factors:
        # 1. Number of techniques found vs expected
        technique_score = min(len(techniques) / 5, 1.0) * 0.3
        
        # 2. Event evidence strength
        evidence_score = min(len(events) / 10, 1.0) * 0.3
        
        # 3. Technique specificity (subtechniques vs main)
        subtech_count = sum(1 for t in techniques if t.get("is_subtechnique", False))
        specificity_score = min(subtech_count / max(len(techniques), 1), 1.0) * 0.2
        
        # 4. Tactic coverage
        tactics = set()
        for technique in techniques:
            tactics.update(technique.get("tactics", []))
        coverage_score = min(len(tactics) / 5, 1.0) * 0.2
        
        total = technique_score + evidence_score + specificity_score + coverage_score
        return round(min(total, 1.0), 2)
    
    def _get_confidence_level(self, confidence: float) -> str:
        """
        Get confidence level from score.
        
        Args:
            confidence: Confidence score
            
        Returns:
            str: Confidence level
        """
        if confidence >= 0.8:
            return "HIGH"
        elif confidence >= 0.6:
            return "MEDIUM"
        elif confidence >= 0.4:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def generate_report(self, mapping_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a human-readable MITRE report.
        
        Args:
            mapping_result: Mapping result
            
        Returns:
            Dict[str, Any]: Report
        """
        techniques = mapping_result.get("techniques", [])
        tactics = mapping_result.get("tactics", {})
        
        report = {
            "summary": {
                "attack_type": mapping_result.get("attack_type", "unknown"),
                "confidence": mapping_result.get("confidence", 0),
                "confidence_level": mapping_result.get("confidence_level", "LOW"),
                "attack_phase": mapping_result.get("attack_phase", "unknown"),
                "mitre_version": mapping_result.get("mitre_version", "unknown"),
            },
            "techniques": [
                {
                    "id": t.get("id"),
                    "name": t.get("name"),
                    "tactics": t.get("tactics", []),
                    "is_subtechnique": t.get("is_subtechnique", False),
                    "parent": t.get("parent"),
                }
                for t in techniques
            ],
            "tactics": {
                tactic: {
                    "techniques": tech_ids,
                    "count": len(tech_ids),
                    "description": self.tactic_mapper.get_tactic_description(tactic),
                }
                for tactic, tech_ids in tactics.items()
            },
            "tactic_chain": mapping_result.get("tactic_chain", []),
            "recommendations": self._generate_recommendations(mapping_result),
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
        
        return report
    
    def _generate_recommendations(self, mapping_result: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on mapping.
        
        Args:
            mapping_result: Mapping result
            
        Returns:
            List[str]: Recommendations
        """
        recommendations = []
        
        techniques = mapping_result.get("techniques", [])
        attack_type = mapping_result.get("attack_type", "")
        
        # Technique-specific recommendations
        tech_recommendations = {
            "T1110": "Implement account lockout policies and multi-factor authentication",
            "T1021": "Restrict remote access and monitor for unusual connections",
            "T1078": "Implement least privilege and regular account reviews",
            "T1068": "Keep systems patched and monitor for exploit attempts",
            "T1003": "Use credential protection and monitor for credential dumping",
            "T1486": "Implement backups and ransomware protection",
            "T1059": "Restrict script execution and monitor command-line activity",
            "T1046": "Implement network segmentation and monitor scans",
            "T1562": "Monitor for security control modifications",
            "T1083": "Monitor for unusual file access patterns",
            "T1133": "Monitor external connections and implement access controls",
            "T1190": "Keep applications patched and use WAF",
        }
        
        for technique in techniques:
            tech_id = technique.get("id")
            if tech_id in tech_recommendations:
                recommendations.append(tech_recommendations[tech_id])
        
        # General recommendations
        if "Lateral Movement" in mapping_result.get("all_tactics", []):
            recommendations.append("Implement network segmentation to limit lateral movement")
        
        if "Privilege Escalation" in mapping_result.get("all_tactics", []):
            recommendations.append("Review and restrict administrative privileges")
        
        if "Exfiltration" in mapping_result.get("all_tactics", []):
            recommendations.append("Monitor outbound traffic and implement DLP controls")
        
        # Remove duplicates
        return list(dict.fromkeys(recommendations[:10]))  # Limit to 10