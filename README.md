# NoteMate - AI-Powered YouTube Transcript Generator

A full-stack application that converts YouTube videos into intelligent transcripts with AI-powered summaries and bullet points.

## 🏗️ Project Structure

```
NoteMate/
├── backend/                 # Python Flask Backend
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── apikey.env         # Environment variables (API keys)
│   ├── temp_audio/        # Temporary audio files
│   ├── whisper_cache/     # Whisper model cache
│   ├── transcript.txt     # Sample transcript
│   └── react.mp3          # Sample audio file
├── frontend/               # React Frontend
│   ├── src/               # React source code
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   └── tailwind.config.js # Tailwind CSS config
├── node_modules/          # Node.js dependencies (root level)
├── package.json           # Root package.json
└── README.md              # This file
```

## 🚀 Features

- **YouTube Audio Download**: Automatically downloads audio from YouTube URLs
- **Whisper Transcription**: Converts audio to text using OpenAI Whisper
- **AI-Powered Analysis**: Uses Google Gemini AI for intelligent processing
- **Multiple Formats**: Full transcript, bullet points, timestamps, AI bullets, and AI summary
- **Modern UI**: Beautiful React interface with Tailwind CSS
- **Copy & Download**: Easy sharing and saving of results

## 🛠️ Tech Stack

### Backend
- **Python Flask**: Web framework
- **OpenAI Whisper**: Speech-to-text transcription
- **Google Gemini AI**: Intelligent text processing
- **yt-dlp**: YouTube audio downloader

### Frontend
- **React**: Frontend framework
- **Tailwind CSS**: Styling
- **Modern UI**: Responsive design with animations

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API key
- OpenAI API key (for Whisper)

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Add your API keys to apikey.env
python app.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 3. Access the App
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:5000

## 🔧 Configuration

1. **API Keys Setup**:
   ```bash
   # Copy the template file
   cp backend/apikey.env.template backend/apikey.env
   
   # Edit the file with your actual API keys
   # NEVER commit apikey.env to version control!
   ```

2. **Environment Variables** (for deployment):
   - Set `GEMINI_API_KEY` in your deployment platform's environment variables
   - Set `OPENAI_API_KEY` if using OpenAI services
   - The app will automatically load from environment variables

3. **Security Note**: 
   - The `apikey.env` file is in `.gitignore` to prevent accidental commits
   - Always use environment variables in production deployments

2. **Environment**: The app automatically handles YouTube download with multiple fallback methods.

## 📁 File Organization

- **Backend**: All Python/Flask code, models, and temporary files
- **Frontend**: All React code, components, and static assets
- **Root**: Project documentation and shared dependencies

## 🎯 Usage

1. Enter a YouTube URL in the frontend
2. Wait for audio download and transcription
3. View results in multiple formats:
   - Full transcript
   - Bullet points
   - Timestamped version
   - AI-generated bullets
   - AI-generated summary
4. Copy or download any format

## 🔄 Development

The project is organized for easy development:
- Backend runs on Flask debug mode
- Frontend runs on React development server
- Hot reloading enabled for both
- CORS configured for cross-origin requests

## 📝 License

This project is for educational and personal use.
