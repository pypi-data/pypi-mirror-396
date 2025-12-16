"""Checkpoint system for resuming interrupted scans."""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class ScanCheckpoint:
    """Manages scan checkpoints for resume capability."""
    
    def __init__(self, checkpoint_dir: Optional[Path] = None):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoints (default: .dutVulnScanner/checkpoints)
        """
        if checkpoint_dir is None:
            checkpoint_dir = Path.home() / ".dutVulnScanner" / "checkpoints"
        
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_checkpoint_id(self, target: str, profile: str) -> str:
        """
        Generate unique checkpoint ID based on target and profile.
        
        Args:
            target: Target host/domain
            profile: Profile name
            
        Returns:
            Checkpoint ID (hash)
        """
        key = f"{target}:{profile}"
        return hashlib.md5(key.encode()).hexdigest()[:12]
    
    def _get_checkpoint_path(self, checkpoint_id: str) -> Path:
        """Get path to checkpoint file."""
        return self.checkpoint_dir / f"{checkpoint_id}.json"
    
    def save_checkpoint(
        self,
        target: str,
        profile: str,
        completed_tools: List[str],
        remaining_tools: List[str],
        results: Dict[str, Any],
        scan_id: str,
        start_time: datetime
    ) -> str:
        """
        Save scan checkpoint.
        
        Args:
            target: Target being scanned
            profile: Profile being used
            completed_tools: Tools that have finished
            remaining_tools: Tools yet to run
            results: Results collected so far
            scan_id: Unique scan ID
            start_time: When scan started
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = self._get_checkpoint_id(target, profile)
        checkpoint_path = self._get_checkpoint_path(checkpoint_id)
        
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "scan_id": scan_id,
            "target": target,
            "profile": profile,
            "start_time": start_time.isoformat(),
            "checkpoint_time": datetime.utcnow().isoformat(),
            "completed_tools": completed_tools,
            "remaining_tools": remaining_tools,
            "results": results,
            "status": "interrupted"
        }
        
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        return checkpoint_id
    
    def load_checkpoint(self, target: str, profile: str) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint for target and profile.
        
        Args:
            target: Target host/domain
            profile: Profile name
            
        Returns:
            Checkpoint data or None if not found
        """
        checkpoint_id = self._get_checkpoint_id(target, profile)
        checkpoint_path = self._get_checkpoint_path(checkpoint_id)
        
        if not checkpoint_path.exists():
            return None
        
        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return None
    
    def delete_checkpoint(self, target: str, profile: str) -> bool:
        """
        Delete checkpoint after successful completion.
        
        Args:
            target: Target host/domain
            profile: Profile name
            
        Returns:
            True if deleted, False if not found
        """
        checkpoint_id = self._get_checkpoint_id(target, profile)
        checkpoint_path = self._get_checkpoint_path(checkpoint_id)
        
        if checkpoint_path.exists():
            checkpoint_path.unlink()
            return True
        return False
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.
        
        Returns:
            List of checkpoint summaries
        """
        checkpoints = []
        
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    checkpoints.append({
                        "checkpoint_id": data["checkpoint_id"],
                        "target": data["target"],
                        "profile": data["profile"],
                        "start_time": data["start_time"],
                        "checkpoint_time": data["checkpoint_time"],
                        "completed": len(data["completed_tools"]),
                        "remaining": len(data["remaining_tools"]),
                        "total": len(data["completed_tools"]) + len(data["remaining_tools"])
                    })
            except Exception:
                continue
        
        return sorted(checkpoints, key=lambda x: x["checkpoint_time"], reverse=True)
    
    def clear_all_checkpoints(self) -> int:
        """
        Clear all checkpoints.
        
        Returns:
            Number of checkpoints deleted
        """
        count = 0
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            checkpoint_file.unlink()
            count += 1
        return count
