"""
Snapshot Testing System
=======================
Save "golden" outputs and detect regressions with semantic awareness.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime
import difflib


@dataclass
class Snapshot:
    """A saved snapshot of expected output"""
    name: str
    content: str
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    version: int
    hash: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Snapshot':
        """Create from dictionary"""
        return cls(**data)


class SnapshotManager:
    """
    Manages snapshot storage and comparison.
    
    Features:
    - File-based storage
    - Semantic comparison (not just exact match)
    - Version tracking
    - Diff generation
    - Update mode for reviewing changes
    """
    
    def __init__(
        self,
        snapshot_dir: str = ".snapshots",
        update_mode: bool = False,
        semantic_threshold: float = 0.9
    ):
        self.snapshot_dir = Path(snapshot_dir)
        self.update_mode = update_mode
        self.semantic_threshold = semantic_threshold
        
        # Create snapshot directory
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_snapshot_path(self, name: str) -> Path:
        """Get path to snapshot file"""
        # Sanitize name for filesystem
        safe_name = "".join(c for c in name if c.isalnum() or c in "._- ")
        return self.snapshot_dir / f"{safe_name}.json"
    
    def _hash_content(self, content: str) -> str:
        """Generate hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def save_snapshot(
        self,
        name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Snapshot:
        """
        Save a snapshot.
        
        Args:
            name: Snapshot name
            content: Content to save
            metadata: Optional metadata
            
        Returns:
            Snapshot object
        """
        path = self._get_snapshot_path(name)
        
        # Load existing snapshot if it exists
        version = 1
        created_at = datetime.now().isoformat()
        
        if path.exists():
            try:
                existing = self.load_snapshot(name)
                version = existing.version + 1
                created_at = existing.created_at
            except:
                pass
        
        snapshot = Snapshot(
            name=name,
            content=content,
            metadata=metadata or {},
            created_at=created_at,
            updated_at=datetime.now().isoformat(),
            version=version,
            hash=self._hash_content(content)
        )
        
        # Save to file
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(snapshot.to_dict(), f, indent=2, ensure_ascii=False)
        
        return snapshot
    
    def load_snapshot(self, name: str) -> Optional[Snapshot]:
        """
        Load a snapshot.
        
        Args:
            name: Snapshot name
            
        Returns:
            Snapshot object or None if not found
        """
        path = self._get_snapshot_path(name)
        
        if not path.exists():
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Snapshot.from_dict(data)
        except Exception as e:
            print(f"Error loading snapshot {name}: {e}")
            return None
    
    def compare(
        self,
        name: str,
        actual_content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare actual content with saved snapshot.
        
        Args:
            name: Snapshot name
            actual_content: Content to compare
            metadata: Optional metadata
            
        Returns:
            Comparison result dict with keys:
            - matched: bool
            - diff: str (if not matched)
            - similarity: float
            - snapshot_exists: bool
        """
        snapshot = self.load_snapshot(name)
        
        if not snapshot:
            # No snapshot exists - save it in update mode
            if self.update_mode:
                self.save_snapshot(name, actual_content, metadata)
                return {
                    "matched": True,
                    "snapshot_exists": False,
                    "message": "Snapshot created (update mode)"
                }
            else:
                return {
                    "matched": False,
                    "snapshot_exists": False,
                    "message": "No snapshot found. Run with --update to create."
                }
        
        # Compare content
        if snapshot.content == actual_content:
            return {
                "matched": True,
                "snapshot_exists": True,
                "exact_match": True,
                "similarity": 1.0
            }
        
        # Calculate similarity
        similarity = self._calculate_similarity(snapshot.content, actual_content)
        
        # Check if semantically similar
        if similarity >= self.semantic_threshold:
            if self.update_mode:
                # Update snapshot
                self.save_snapshot(name, actual_content, metadata)
                return {
                    "matched": True,
                    "snapshot_exists": True,
                    "exact_match": False,
                    "similarity": similarity,
                    "message": "Snapshot updated (semantic match + update mode)"
                }
            else:
                return {
                    "matched": True,
                    "snapshot_exists": True,
                    "exact_match": False,
                    "similarity": similarity,
                    "message": "Semantic match (similar enough)"
                }
        
        # Content differs significantly
        diff = self._generate_diff(snapshot.content, actual_content)
        
        if self.update_mode:
            # Update snapshot even on mismatch
            self.save_snapshot(name, actual_content, metadata)
            return {
                "matched": True,
                "snapshot_exists": True,
                "exact_match": False,
                "similarity": similarity,
                "diff": diff,
                "message": "Snapshot updated (forced update mode)"
            }
        
        return {
            "matched": False,
            "snapshot_exists": True,
            "exact_match": False,
            "similarity": similarity,
            "diff": diff,
            "message": "Content differs from snapshot"
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Use SequenceMatcher for quick similarity
        return difflib.SequenceMatcher(None, text1, text2).ratio()
    
    def _generate_diff(self, expected: str, actual: str) -> str:
        """Generate human-readable diff"""
        expected_lines = expected.splitlines(keepends=True)
        actual_lines = actual.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            expected_lines,
            actual_lines,
            fromfile="snapshot",
            tofile="actual",
            lineterm=""
        )
        
        return "".join(diff)
    
    def list_snapshots(self) -> List[str]:
        """List all snapshot names"""
        return [
            p.stem for p in self.snapshot_dir.glob("*.json")
        ]
    
    def delete_snapshot(self, name: str) -> bool:
        """
        Delete a snapshot.
        
        Args:
            name: Snapshot name
            
        Returns:
            True if deleted, False if not found
        """
        path = self._get_snapshot_path(name)
        
        if path.exists():
            path.unlink()
            return True
        return False
    
    def clear_all(self) -> int:
        """
        Delete all snapshots.
        
        Returns:
            Number of snapshots deleted
        """
        count = 0
        for path in self.snapshot_dir.glob("*.json"):
            path.unlink()
            count += 1
        return count
    
    def assert_matches_snapshot(
        self,
        name: str,
        actual_content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Assert that content matches snapshot.
        Raises AssertionError if not matched.
        
        Args:
            name: Snapshot name
            actual_content: Content to compare
            metadata: Optional metadata
        """
        result = self.compare(name, actual_content, metadata)
        
        if not result["matched"]:
            error_msg = f"Snapshot mismatch: {name}\n"
            error_msg += f"Similarity: {result.get('similarity', 0):.2%}\n"
            
            if "diff" in result:
                error_msg += f"\nDiff:\n{result['diff'][:500]}\n"
            
            error_msg += f"\n{result['message']}"
            
            raise AssertionError(error_msg)


# Convenience function for quick snapshot testing
def match_snapshot(
    name: str,
    content: str,
    snapshot_dir: str = ".snapshots",
    update: bool = False
) -> bool:
    """
    Quick snapshot matching.
    
    Args:
        name: Snapshot name
        content: Content to compare
        snapshot_dir: Directory for snapshots
        update: Update mode
        
    Returns:
        True if matched
        
    Raises:
        AssertionError if not matched
    """
    manager = SnapshotManager(snapshot_dir=snapshot_dir, update_mode=update)
    manager.assert_matches_snapshot(name, content)
    return True
