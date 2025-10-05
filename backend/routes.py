from flask import request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import os
import time
from functools import lru_cache

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '5f573c9620494bae87890c0f08a60293')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '212476d9b0f3472eaa762d90b19b0ba8')

# Initialize Spotify client
try:
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
    )
except Exception as e:
    print(f"Error initializing Spotify client: {e}")
    sp = None

# Video URL cache for faster downloads
video_cache = {}

@lru_cache(maxsize=100)
def get_cached_video_url(track_name, track_artist):
    """Get cached video URL for faster downloads"""
    cache_key = f"{track_name} {track_artist}".lower()
    
    if cache_key in video_cache:
        return video_cache[cache_key]
    
    search_query = f"{track_name} {track_artist}"
    search_opts = {
        'quiet': True, 
        'no_warnings': True, 
        'extract_flat': True,
        'max_downloads': 1
    }
    
    try:
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
            
            if not search_results or not search_results.get('entries'):
                return None
                
            video_info = search_results['entries'][0]
            video_url = video_info.get('webpage_url') or video_info.get('url')
            
            if not video_url and 'id' in video_info:
                video_url = f"https://www.youtube.com/watch?v={video_info['id']}"
            
            if video_url:
                video_cache[cache_key] = video_url
                return video_url
                
    except Exception as e:
        print(f"Error getting video URL: {e}")
    
    return None

def build_search_query(query, filters):
    """Build advanced search query with filters"""
    search_query = query
    
    if filters.get('genre'):
        search_query += f" genre:{filters['genre']}"
    if filters.get('year'):
        search_query += f" year:{filters['year']}"
    if filters.get('language'):
        search_query += f" language:{filters['language']}"
    
    # Add mood filter (using audio features)
    mood = filters.get('mood')
    if mood == 'happy':
        search_query += " valence:0.7-1.0"
    elif mood == 'sad':
        search_query += " valence:0.0-0.3"
    elif mood == 'energetic':
        search_query += " energy:0.7-1.0"
    elif mood == 'calm':
        search_query += " energy:0.0-0.3"
    
    return search_query

def apply_track_filters(track, filters):
    """Apply additional filters to track"""
    # Popularity filter
    if filters.get('popularityMin'):
        if track['popularity'] < int(filters['popularityMin']):
            return False
    if filters.get('popularityMax'):
        if track['popularity'] > int(filters['popularityMax']):
            return False
    
    # Duration filter
    duration_seconds = track['duration_ms'] // 1000
    if filters.get('durationMin'):
        if duration_seconds < int(filters['durationMin']):
            return False
    if filters.get('durationMax'):
        if duration_seconds > int(filters['durationMax']):
            return False
    
    # Explicit filter
    if not filters.get('explicit', False) and track.get('explicit', False):
        return False
    
    return True

def init_routes(app):
    @app.route('/search', methods=['POST'])
    def search():
        data = request.json
        query = data.get('query', '')
        filters = data.get('filters', {})
        
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        try:
            limit = int(data.get('limit', 20))
            offset = int(data.get('offset', 0))
            
            # Build advanced search query
            search_query = build_search_query(query, filters)
            
            results = sp.search(q=search_query, type='track', limit=limit, offset=offset)
            tracks = []
            
            for track in results['tracks']['items']:
                # Apply additional filters
                if apply_track_filters(track, filters):
                    tracks.append({
                        'id': track['id'],
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'album': track['album']['name'],
                        'cover_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                        'preview_url': track['preview_url'],
                        'duration': track['duration_ms'] // 1000,
                        'popularity': track['popularity'],
                        'explicit': track['explicit'],
                        'external_urls': track['external_urls']
                    })
            
            return jsonify({
                'tracks': tracks,
                'total': results['tracks']['total']
            })
            
        except Exception as e:
            return jsonify({'error': f'Search failed: {str(e)}'}), 500
    
    @app.route('/recommendations', methods=['POST'])
    def get_recommendations():
        data = request.json
        seed_track_id = data.get('seed_track_id', '')
        
        if not seed_track_id:
            return jsonify({'error': 'No seed track provided'}), 400
        
        try:
            limit = int(data.get('limit', 20))
            
            # Get recommendations based on the seed track
            recommendations = sp.recommendations(seed_tracks=[seed_track_id], limit=limit)
            tracks = []
            
            for track in recommendations['tracks']:
                tracks.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'cover_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'preview_url': track['preview_url'],
                    'duration': track['duration_ms'] // 1000,
                    'popularity': track['popularity'],
                    'explicit': track['explicit'],
                    'external_urls': track['external_urls']
                })
            
            return jsonify({
                'tracks': tracks,
                'total': len(tracks)
            })
            
        except Exception as e:
            return jsonify({'error': f'Recommendations failed: {str(e)}'}), 500
    
    @app.route('/download', methods=['POST'])
    def download_track():
        try:
            data = request.json
            track_name = data.get('name', '')
            track_artist = data.get('artist', '')
            
            if not track_name or not track_artist:
                return jsonify({'error': 'Track name and artist required'}), 400
            
            # Use cached video URL for instant response
            video_url = get_cached_video_url(track_name, track_artist)
            
            if not video_url:
                # Fallback to direct search if not cached
                search_query = f"{track_name} {track_artist}"
                search_opts = {
                    'quiet': True, 
                    'no_warnings': True, 
                    'extract_flat': True,
                    'max_downloads': 1
                }
                
                with yt_dlp.YoutubeDL(search_opts) as ydl:
                    search_results = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
                    
                    if not search_results or not search_results.get('entries'):
                        raise Exception('No video found')
                    
                    video_info = search_results['entries'][0]
                    video_url = video_info.get('webpage_url') or video_info.get('url')
                    
                    if not video_url and 'id' in video_info:
                        video_url = f"https://www.youtube.com/watch?v={video_info['id']}"
                    
                    if not video_url:
                        raise Exception('Could not get video URL')
            
            # Ultra-fast download options for instant response
            download_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp4]/bestaudio',
                'quiet': True,
                'no_warnings': True,
                'no_check_certificate': True,
                'prefer_insecure': True,
                'socket_timeout': 10,
                'retries': 1,
                'fragment_retries': 1,
                'http_chunk_size': 10485760,  # 10MB chunks for faster streaming
            }
            
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                if not info or 'url' not in info:
                    return jsonify({'error': 'Could not get download URL'}), 500
                
                filename = f"{track_name} - {track_artist}.m4a"
                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                
                return jsonify({
                    'download_url': info['url'],
                    'filename': filename,
                    'title': info.get('title', track_name),
                    'duration': info.get('duration', 0),
                    'cached': video_url in video_cache
                })
            
        except Exception as e:
            return jsonify({'error': f'Download failed: {str(e)}'}), 500
    
    @app.route('/search-suggestions', methods=['POST'])
    def get_search_suggestions():
        try:
            data = request.json
            query = data.get('query', '')
            limit = int(data.get('limit', 8))
            
            if not query or len(query) < 2:
                return jsonify({'suggestions': []})
            
            # Search for tracks with minimal data for speed
            results = sp.search(q=query, type='track', limit=limit)
            
            suggestions = []
            for track in results['tracks']['items']:
                suggestions.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'id': track['id']
                })
            
            return jsonify({
                'suggestions': suggestions
            })
            
        except Exception as e:
            return jsonify({'error': f'Failed to get suggestions: {str(e)}'}), 500
    
    @app.route('/prewarm-cache', methods=['POST'])
    def prewarm_cache():
        """Pre-warm cache with popular tracks for instant downloads"""
        try:
            data = request.json
            tracks = data.get('tracks', [])
            
            if not tracks:
                return jsonify({'error': 'No tracks provided'}), 400
            
            cached_count = 0
            for track in tracks[:10]:  # Limit to 10 tracks to avoid overload
                track_name = track.get('name', '')
                track_artist = track.get('artist', '')
                
                if track_name and track_artist:
                    # Pre-cache the video URL
                    get_cached_video_url(track_name, track_artist)
                    cached_count += 1
            
            return jsonify({
                'message': f'Pre-warmed cache with {cached_count} tracks',
                'cached_tracks': cached_count
            })
            
        except Exception as e:
            return jsonify({'error': f'Pre-warming failed: {str(e)}'}), 500
