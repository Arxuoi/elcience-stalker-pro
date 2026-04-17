import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import instaloader
from .utils import format_number, ensure_dir, generate_id

class InstagramOSINT:
    def __init__(self):
        self.loader = instaloader.Instaloader(
            download_pictures=True,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=True,
            save_metadata=True,
            compress_json=False,
            post_metadata_txt_pattern="",
            max_connection_attempts=3,
            quiet=True
        )
        self.output_dir = "output/ig"
        ensure_dir(self.output_dir)
    
    def get_profile(self, username: str) -> Dict[str, Any]:
        """Get Instagram profile information"""
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            # Hitung engagement rate
            engagement_rate = 0
            if profile.followers > 0:
                total_likes = 0
                total_comments = 0
                post_count = 0
                for post in profile.get_posts():
                    if post_count >= 12:
                        break
                    total_likes += post.likes
                    total_comments += post.comments
                    post_count += 1
                if post_count > 0:
                    avg_interactions = (total_likes + total_comments) / post_count
                    engagement_rate = (avg_interactions / profile.followers) * 100
            
            # Analisis bio
            bio_keywords = []
            keywords = ['business', 'contact', 'shop', 'youtube', 'tiktok', 'twitter', 'snapchat']
            for kw in keywords:
                if kw in profile.biography.lower():
                    bio_keywords.append(kw)
            
            info = {
                "id": generate_id(username),
                "platform": "instagram",
                "username": profile.username,
                "full_name": profile.full_name,
                "biography": profile.biography,
                "followers": profile.followers,
                "followers_formatted": format_number(profile.followers),
                "following": profile.followees,
                "following_formatted": format_number(profile.followees),
                "posts_count": profile.mediacount,
                "is_private": profile.is_private,
                "is_verified": profile.is_verified,
                "is_business": profile.is_business_account,
                "business_category": profile.business_category_name,
                "external_url": profile.external_url,
                "profile_pic_url": profile.profile_pic_url,
                "profile_pic_hd": profile.profile_pic_url_no_iphone if hasattr(profile, 'profile_pic_url_no_iphone') else profile.profile_pic_url,
                "engagement_rate": round(engagement_rate, 2),
                "bio_keywords": bio_keywords,
                "scraped_at": datetime.now().isoformat()
            }
            return {"success": True, "data": info}
        except instaloader.exceptions.ProfileNotExistsException:
            return {"success": False, "error": f"Profil @{username} tidak ditemukan"}
        except instaloader.exceptions.LoginRequiredException:
            return {"success": False, "error": "Login diperlukan untuk mengakses profil ini"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_posts(self, username: str, count: int = 12) -> Dict[str, Any]:
        """Get recent posts from Instagram profile"""
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            target_dir = f"{self.output_dir}/{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ensure_dir(target_dir)
            
            posts = []
            for i, post in enumerate(profile.get_posts()):
                if i >= count:
                    break
                
                # Download post
                self.loader.download_post(post, target=target_dir)
                
                post_data = {
                    "id": post.shortcode,
                    "url": f"https://instagram.com/p/{post.shortcode}",
                    "type": "video" if post.is_video else "image",
                    "likes": post.likes,
                    "likes_formatted": format_number(post.likes),
                    "comments": post.comments,
                    "comments_formatted": format_number(post.comments),
                    "timestamp": post.date_utc.isoformat(),
                    "caption": post.caption[:500] if post.caption else "",
                    "hashtags": post.caption_hashtags if post.caption else [],
                    "mentions": post.caption_mentions if post.caption else [],
                    "location": str(post.location) if post.location else None,
                    "is_sponsored": post.is_sponsored if hasattr(post, 'is_sponsored') else False
                }
                posts.append(post_data)
            
            return {
                "success": True,
                "data": {
                    "username": username,
                    "count": len(posts),
                    "download_path": target_dir,
                    "posts": posts
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_stories(self, username: str) -> Dict[str, Any]:
        """Get current stories (jika ada)"""
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            stories = []
            for story in self.loader.get_stories(userids=[profile.userid]):
                for item in story.get_items():
                    story_data = {
                        "id": item.mediaid,
                        "type": "video" if item.is_video else "image",
                        "timestamp": item.date_utc.isoformat(),
                        "expires_at": item.expiring_utc.isoformat() if hasattr(item, 'expiring_utc') else None,
                        "url": item.url if hasattr(item, 'url') else item.video_url if item.is_video else item.url
                    }
                    stories.append(story_data)
            
            return {"success": True, "data": {"username": username, "stories_count": len(stories), "stories": stories}}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def compare_profiles(self, username1: str, username2: str) -> Dict[str, Any]:
        """Compare two Instagram profiles"""
        profile1 = self.get_profile(username1)
        profile2 = self.get_profile(username2)
        
        if not profile1["success"] or not profile2["success"]:
            return {"success": False, "error": "Salah satu profil tidak ditemukan"}
        
        p1 = profile1["data"]
        p2 = profile2["data"]
        
        comparison = {
            "profiles": [p1, p2],
            "comparison": {
                "followers_diff": p1["followers"] - p2["followers"],
                "following_diff": p1["following"] - p2["following"],
                "posts_diff": p1["posts_count"] - p2["posts_count"],
                "engagement_diff": round(p1["engagement_rate"] - p2["engagement_rate"], 2),
                "winner": {
                    "followers": p1["username"] if p1["followers"] > p2["followers"] else p2["username"],
                    "engagement": p1["username"] if p1["engagement_rate"] > p2["engagement_rate"] else p2["username"]
                }
            }
        }
        return {"success": True, "data": comparison}
