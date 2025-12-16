"""Vulnerability correlation engine."""
import logging
from typing import List, Dict, Any
from collections import defaultdict


logger = logging.getLogger(__name__)


class CorrelationEngine:
    """
    Correlates vulnerabilities from multiple scanning tools.
    
    Identifies duplicate findings, merges related vulnerabilities,
    and enriches vulnerability data.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize correlation engine."""
        self.config = config
        self.correlation_config = config.get("correlation", {})
        self.enabled = self.correlation_config.get("enabled", True)
        self.confidence_threshold = self.correlation_config.get("confidence_threshold", 0.7)
    
    def correlate(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Correlate vulnerabilities from multiple sources.
        
        Args:
            vulnerabilities: List of raw vulnerability dictionaries
            
        Returns:
            List of correlated and deduplicated vulnerabilities
        """
        if not self.enabled:
            logger.info("Correlation disabled, returning raw results")
            return vulnerabilities
        
        logger.info(f"Correlating {len(vulnerabilities)} vulnerabilities")
        
        # Group by host and port
        grouped = self._group_vulnerabilities(vulnerabilities)
        
        # Find duplicates and merge
        correlated = []
        for key, vulns in grouped.items():
            if len(vulns) == 1:
                correlated.append(vulns[0])
            else:
                merged = self._merge_similar_vulnerabilities(vulns)
                correlated.extend(merged)
        
        logger.info(f"Correlation complete: {len(correlated)} unique vulnerabilities")
        return correlated
    
    def _group_vulnerabilities(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[tuple, List[Dict[str, Any]]]:
        """Group vulnerabilities by host and port."""
        grouped = defaultdict(list)
        
        for vuln in vulnerabilities:
            key = (
                vuln.get("host", ""),
                vuln.get("port", 0),
                vuln.get("service", ""),
            )
            grouped[key].append(vuln)
        
        return grouped
    
    def _merge_similar_vulnerabilities(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge similar vulnerabilities.
        
        Uses fuzzy matching on titles and descriptions to identify duplicates.
        """
        merged = []
        processed = set()
        
        for i, vuln in enumerate(vulnerabilities):
            if i in processed:
                continue
            
            similar = [vuln]
            for j, other in enumerate(vulnerabilities[i+1:], start=i+1):
                if j in processed:
                    continue
                
                if self._is_similar(vuln, other):
                    similar.append(other)
                    processed.add(j)
            
            if len(similar) > 1:
                merged_vuln = self._merge_vulnerabilities(similar)
                merged.append(merged_vuln)
            else:
                merged.append(vuln)
            
            processed.add(i)
        
        return merged
    
    def _is_similar(self, vuln1: Dict[str, Any], vuln2: Dict[str, Any]) -> bool:
        """
        Check if two vulnerabilities are similar.
        
        Uses multiple heuristics:
        - Same CVE IDs
        - Similar titles (fuzzy match)
        - Same port and service
        """
        # Check CVE IDs
        cve1 = set(vuln1.get("cve_ids", []))
        cve2 = set(vuln2.get("cve_ids", []))
        if cve1 and cve2 and cve1.intersection(cve2):
            return True
        
        # Check title similarity
        title1 = vuln1.get("title", "").lower()
        title2 = vuln2.get("title", "").lower()
        
        if title1 and title2:
            similarity = self._calculate_similarity(title1, title2)
            if similarity >= self.confidence_threshold:
                return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two strings.
        
        Simple Jaccard similarity based on word sets.
        """
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _merge_vulnerabilities(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge multiple similar vulnerabilities into one.
        
        Combines information from all sources.
        """
        # Use the first vulnerability as base
        merged = vulnerabilities[0].copy()
        
        # Collect all detecting tools
        detected_by = set([v.get("detected_by", "unknown") for v in vulnerabilities])
        merged["detected_by"] = ", ".join(sorted(detected_by))
        
        # Merge CVE IDs
        all_cves = set()
        for v in vulnerabilities:
            all_cves.update(v.get("cve_ids", []))
        merged["cve_ids"] = sorted(list(all_cves))
        
        # Merge CWE IDs
        all_cwes = set()
        for v in vulnerabilities:
            all_cwes.update(v.get("cwe_ids", []))
        merged["cwe_ids"] = sorted(list(all_cwes))
        
        # Use highest severity
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
        severities = [v.get("severity", "info").lower() for v in vulnerabilities]
        merged["severity"] = max(severities, key=lambda s: severity_order.get(s, 0))
        
        # Use highest CVSS score
        cvss_scores = [v.get("cvss_score") for v in vulnerabilities if v.get("cvss_score")]
        if cvss_scores:
            merged["cvss_score"] = max(cvss_scores)
        
        # Merge references
        all_refs = set()
        for v in vulnerabilities:
            all_refs.update(v.get("references", []))
        merged["references"] = sorted(list(all_refs))
        
        # Add correlation metadata
        merged["correlated"] = True
        merged["source_count"] = len(vulnerabilities)
        
        return merged
