import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from utils import load_json, save_json, ensure_dir

class Database:
    def __init__(self):
        self.data_dir = "data"
        ensure_dir(self.data_dir)
        self.history_file = f"{self.data_dir}/history.json"
        self.favorites_file = f"{self.data_dir}/favorites.json"
        self.stats_file = f"{self.data_dir}/stats.json"
    
    # ========== HISTORY ==========
    def add_history(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Tambah entri ke history"""
        history = load_json(self.history_file, [])
        entry["timestamp"] = datetime.now().isoformat()
        history.insert(0, entry)
        
        # Batasi history 100 entri
        if len(history) > 100:
            history = history[:100]
        
        save_json(self.history_file, history)
        self._update_stats(entry["platform"])
        return {"success": True, "data": entry}
    
    def get_history(self, limit: int = 50, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get history dengan filter"""
        history = load_json(self.history_file, [])
        if platform:
            history = [h for h in history if h.get("platform") == platform]
        return history[:limit]
    
    def clear_history(self) -> Dict[str, Any]:
        """Hapus semua history"""
        save_json(self.history_file, [])
        return {"success": True, "message": "History cleared"}
    
    def delete_history_item(self, item_id: str) -> Dict[str, Any]:
        """Hapus satu item dari history"""
        history = load_json(self.history_file, [])
        history = [h for h in history if h.get("id") != item_id]
        save_json(self.history_file, history)
        return {"success": True, "message": f"Item {item_id} deleted"}
    
    # ========== FAVORITES ==========
    def add_favorite(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Tambah profil ke favorites"""
        favorites = load_json(self.favorites_file, [])
        
        # Cek duplikat
        for fav in favorites:
            if fav.get("username") == profile.get("username") and fav.get("platform") == profile.get("platform"):
                return {"success": False, "error": "Profil sudah ada di favorites"}
        
        profile["favorited_at"] = datetime.now().isoformat()
        favorites.append(profile)
        save_json(self.favorites_file, favorites)
        return {"success": True, "data": profile}
    
    def get_favorites(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get semua favorites"""
        favorites = load_json(self.favorites_file, [])
        if platform:
            favorites = [f for f in favorites if f.get("platform") == platform]
        return favorites
    
    def remove_favorite(self, username: str, platform: str) -> Dict[str, Any]:
        """Hapus dari favorites"""
        favorites = load_json(self.favorites_file, [])
        favorites = [f for f in favorites if not (f.get("username") == username and f.get("platform") == platform)]
        save_json(self.favorites_file, favorites)
        return {"success": True, "message": f"@{username} removed from favorites"}
    
    def is_favorited(self, username: str, platform: str) -> bool:
        """Cek apakah profil sudah di-favorite"""
        favorites = load_json(self.favorites_file, [])
        for fav in favorites:
            if fav.get("username") == username and fav.get("platform") == platform:
                return True
        return False
    
    # ========== STATS ==========
    def _update_stats(self, platform: str):
        """Update statistik penggunaan"""
        stats = load_json(self.stats_file, {"total_searches": 0, "ig_searches": 0, "tt_searches": 0, "last_updated": None})
        stats["total_searches"] += 1
        if platform == "instagram":
            stats["ig_searches"] += 1
        elif platform == "tiktok":
            stats["tt_searches"] += 1
        stats["last_updated"] = datetime.now().isoformat()
        save_json(self.stats_file, stats)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistik"""
        stats = load_json(self.stats_file, {"total_searches": 0, "ig_searches": 0, "tt_searches": 0, "last_updated": None})
        favorites = load_json(self.favorites_file, [])
        stats["total_favorites"] = len(favorites)
        stats["ig_favorites"] = len([f for f in favorites if f.get("platform") == "instagram"])
        stats["tt_favorites"] = len([f for f in favorites if f.get("platform") == "tiktok"])
        return stats
    
    def reset_stats(self) -> Dict[str, Any]:
        """Reset statistik"""
        save_json(self.stats_file, {"total_searches": 0, "ig_searches": 0, "tt_searches": 0, "last_updated": None})
        return {"success": True, "message": "Stats reset"}
