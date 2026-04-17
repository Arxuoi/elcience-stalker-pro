import os
import re
import json
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from .utils import format_number, ensure_dir, generate_id

class TikTokOSINT:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.output_dir = "output/tt"
        ensure_dir(self.output_dir)
    
    def _parse_number(self, text: str) -> int:
        """Parse follower/likes count dari text"""
        if not text:
            return 0
        text = text.lower().replace(',', '').strip()
        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        elif 'm' in text:
            return int(float(text.replace('m', '')) * 1000000)
        elif 'b' in text:
            return int(float(text.replace('b', '')) * 1000000000)
        else:
            try:
                return int(text)
            except:
                return 0
    
    def get_profile(self, username: str) -> Dict[str, Any]:
        """Get TikTok profile information"""
        try:
            url = f"https://www.tiktok.com/@{username}"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return {"success": False, "error": f"Profil @{username} tidak ditemukan (HTTP {response.status_code})"}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data dari meta tags
            info = {
                "id": generate_id(username),
                "platform": "tiktok",
                "username": username,
                "url": url,
                "scraped_at": datetime.now().isoformat()
            }
            
            # Parse meta description
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                desc = meta_desc.get('content', '')
                info['description'] = desc
                
                # Parse followers dan likes
                followers_match = re.search(r'(\d+\.?\d*[KkMmBb]?)\s*Followers', desc)
                likes_match = re.search(r'(\d+\.?\d*[KkMmBb]?)\s*Likes', desc)
                
                if followers_match:
                    info['followers_text'] = followers_match.group(1)
                    info['followers'] = self._parse_number(followers_match.group(1))
                if likes_match:
                    info['likes_text'] = likes_match.group(1)
                    info['likes'] = self._parse_number(likes_match.group(1))
            
            # Parse JSON-LD
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if 'author' in data:
                        author = data['author']
                        info['nickname'] = author.get('name', '')
                        info['bio'] = author.get('description', '')
                        info['profile_pic'] = author.get('image', '')
                        info['verified'] = 'verified' in str(data).lower()
                except:
                    pass
            
            # Parse meta tags lainnya
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content', '')
                info['display_name'] = title.replace(f'@{username}', '').strip(' ()')
            
            og_image = soup.find('meta', property='og:image')
            if og_image:
                info['profile_pic_og'] = og_image.get('content', '')
            
            # Hitung engagement rate (estimasi)
            if 'followers' in info and 'likes' in info and info['followers'] > 0:
                info['engagement_rate'] = round((info['likes'] / info['followers']) * 100, 2)
            else:
                info['engagement_rate'] = 0
            
            return {"success": True, "data": info}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout - server TikTok lambat"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_videos(self, username: str, count: int = 10) -> Dict[str, Any]:
        """Get recent videos from TikTok profile (basic info)"""
        try:
            url = f"https://www.tiktok.com/@{username}"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return {"success": False, "error": "Profil tidak ditemukan"}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cari video data (TikTok menyimpan data di script tag)
            videos = []
            scripts = soup.find_all('script')
            
            for script in scripts:
                if script.string and '"video"' in script.string:
                    try:
                        # Extract JSON data
                        json_match = re.search(r'\{.*"video".*\}', script.string)
                        if json_match:
                            data = json.loads(json_match.group())
                            # Parse video info
                    except:
                        pass
            
            # Fallback: parse dari meta tags
            video_meta = soup.find_all('meta', property='og:video')
            for meta in video_meta[:count]:
                videos.append({
                    "url": meta.get('content', ''),
                    "title": meta.get('og:title', ''),
                })
            
            return {
                "success": True,
                "data": {
                    "username": username,
                    "count": len(videos),
                    "videos": videos,
                    "profile_url": url,
                    "note": "Untuk melihat video lengkap, buka profil di browser"
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def compare_profiles(self, username1: str, username2: str) -> Dict[str, Any]:
        """Compare two TikTok profiles"""
        profile1 = self.get_profile(username1)
        profile2 = self.get_profile(username2)
        
        if not profile1["success"] or not profile2["success"]:
            return {"success": False, "error": "Salah satu profil tidak ditemukan"}
        
        p1 = profile1["data"]
        p2 = profile2["data"]
        
        comparison = {
            "profiles": [p1, p2],
            "comparison": {
                "followers_diff": p1.get("followers", 0) - p2.get("followers", 0),
                "likes_diff": p1.get("likes", 0) - p2.get("likes", 0),
                "engagement_diff": round(p1.get("engagement_rate", 0) - p2.get("engagement_rate", 0), 2),
                "winner": {
                    "followers": p1["username"] if p1.get("followers", 0) > p2.get("followers", 0) else p2["username"],
                    "engagement": p1["username"] if p1.get("engagement_rate", 0) > p2.get("engagement_rate", 0) else p2["username"]
                }
            }
        }
        return {"success": True, "data": comparison}
