# Soundify - Music Discovery & Download Platform

A comprehensive web application for discovering, previewing, and downloading music tracks using Spotify's API and YouTube integration.

## Features

### Core Functionality
- **Advanced Search**: Search for songs, artists, and albums with intelligent filtering
- **Music Preview**: Play 30-second previews directly in the browser
- **Track Download**: Download full tracks as high-quality audio files
- **Smart Recommendations**: Get personalized track recommendations based on your selections
- **Search Suggestions**: Real-time search suggestions as you type

### Advanced Features
- **Advanced Filtering**: Filter by genre, year, language, mood, popularity, and duration
- **Caching System**: Intelligent video URL caching for instant downloads
- **Progress Tracking**: Real-time progress bars for downloads and playback
- **Error Handling**: Comprehensive error pages (400, 403, 404, 500)
- **Responsive Design**: Modern UI with Tailwind CSS and Phosphor icons

### Technical Features
- **YouTube Integration**: Uses yt-dlp for high-quality audio extraction
- **Spotify API**: Full integration with Spotify's Web API
- **Flask Backend**: Modular Flask application with proper routing
- **Client Credentials**: No user authentication required

## Project Structure

```
spotify backup/
├── backend/                 # Flask backend application
│   ├── __init__.py         # Package initialization
│   ├── app.py              # Main Flask app with error handlers
│   ├── routes.py           # API routes and business logic
│   └── models.py           # Data models (currently empty)
├── templates/              # HTML templates
│   ├── base.html           # Base template with Tailwind CSS
│   ├── index.html          # Main application interface
│   └── errors/             # Error page templates
│       ├── 400.html
│       ├── 403.html
│       ├── 404.html
│       └── 500.html
├── static/                 # Static assets
│   ├── css/               # Custom CSS files
│   └── js/                # JavaScript files
├── scripts/               # Utility scripts
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Installation

1. **Clone the repository**:
```bash
git clone (https://github.com/zensage/Spotify-Downloader)
cd spotify-downloader
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (optional):
```bash
export SPOTIFY_CLIENT_ID=your_client_id
export SPOTIFY_CLIENT_SECRET=your_client_secret
```

4. **Run the application**:
```bash
python run.py
```

5. **Open your browser**:
```
http://localhost:5000
```

## Usage

### Basic Search
1. Enter a song name, artist, or album in the search box
2. Browse through the results displayed as cards
3. Click on any track to play the 30-second preview
4. Use play/pause controls to manage playback

### Advanced Features
1. **Download Tracks**: Click the download button to get full audio files
2. **Get Recommendations**: Use the recommendations feature for similar tracks
3. **Apply Filters**: Use advanced filters for refined search results
4. **Search Suggestions**: Get real-time suggestions as you type

### API Endpoints
- `POST /search` - Search for tracks with advanced filtering
- `POST /recommendations` - Get track recommendations
- `POST /download` - Download track audio files
- `POST /search-suggestions` - Get search suggestions
- `POST /prewarm-cache` - Pre-cache popular tracks for faster downloads

## Dependencies

- **Flask 2.3.3** - Web framework
- **spotipy 2.23.0** - Spotify Web API client
- **yt-dlp** - YouTube video/audio downloader
- **Tailwind CSS** - Utility-first CSS framework
- **Phosphor Icons** - Modern icon library

## Configuration

The application uses embedded Spotify API credentials by default. For production use, set your own credentials:

```bash
export SPOTIFY_CLIENT_ID=your_client_id
export SPOTIFY_CLIENT_SECRET=your_client_secret
```

## Key Features Explained

### Smart Caching
- Video URLs are cached for instant downloads
- Pre-warming system for popular tracks
- LRU cache with configurable size limits

### Advanced Search
- Genre, year, and language filtering
- Mood-based filtering using audio features
- Popularity and duration range filters
- Explicit content filtering

### Download System
- High-quality audio extraction (M4A/MP4)
- Optimized download options for speed
- Automatic filename sanitization
- Progress tracking and error handling

## Error Handling

The application includes comprehensive error handling with custom error pages:
- **400 Bad Request** - Invalid search parameters
- **403 Forbidden** - Access denied
- **404 Not Found** - Page or resource not found
- **500 Internal Server Error** - Server-side errors

## Browser Compatibility

- Modern browsers with JavaScript support
- Responsive design for mobile and desktop
- Progressive enhancement for better performance
