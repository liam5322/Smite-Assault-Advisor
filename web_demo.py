#!/usr/bin/env python3
"""
🌐 SMITE 2 Assault Brain - Web Demo
Web interface for testing and team coordination
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import aiohttp
from aiohttp import web, WSMsgType
import aiohttp_cors
import logging

# Import our optimized system
import sys
sys.path.append('.')
from optimized_assault_brain import SmartDataManager, MatchAnalysis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebAssaultBrain:
    """Web interface for SMITE 2 Assault Brain"""
    
    def __init__(self):
        self.data_manager = SmartDataManager()
        self.websockets = set()
        self.analysis_history = []
        
        logger.info("✅ Web Assault Brain initialized")
    
    async def handle_index(self, request):
        """Serve main web interface"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 SMITE 2 Assault Brain</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #00ff88, #00aaff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .team-input {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 20px;
            margin-bottom: 30px;
            align-items: center;
        }
        
        .team-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .team-section h3 {
            margin-bottom: 15px;
            text-align: center;
            font-size: 1.3em;
        }
        
        .team1 h3 { color: #00ff88; }
        .team2 h3 { color: #ff4444; }
        
        .god-input {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .god-input input {
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 16px;
        }
        
        .god-input input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        
        .vs-section {
            text-align: center;
            font-size: 2em;
            font-weight: bold;
            color: #ffaa00;
        }
        
        .analyze-btn {
            display: block;
            width: 200px;
            margin: 0 auto 30px;
            padding: 15px;
            background: linear-gradient(45deg, #00ff88, #00aaff);
            border: none;
            border-radius: 25px;
            color: white;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .analyze-btn:hover {
            transform: scale(1.05);
        }
        
        .results {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .result-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .win-probability {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .win-prob-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin: 0 auto 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            position: relative;
        }
        
        .advice-list {
            list-style: none;
        }
        
        .advice-list li {
            padding: 10px;
            margin: 5px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            border-left: 4px solid #00ff88;
        }
        
        .history {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .history h3 {
            margin-bottom: 15px;
            color: #00aaff;
        }
        
        .history-item {
            padding: 10px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            font-size: 14px;
        }
        
        .status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
        }
        
        .status.connected {
            background: #00ff88;
            color: #000;
        }
        
        .status.disconnected {
            background: #ff4444;
            color: #fff;
        }
        
        @media (max-width: 768px) {
            .team-input {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            .results {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚔️ SMITE 2 Assault Brain</h1>
            <p>Real-time team analysis and strategic coaching</p>
        </div>
        
        <div class="team-input">
            <div class="team-section team1">
                <h3>🔵 Your Team</h3>
                <div class="god-input">
                    <input type="text" id="team1-god1" placeholder="God 1 (e.g., Zeus)" value="Zeus">
                    <input type="text" id="team1-god2" placeholder="God 2 (e.g., Ares)" value="Ares">
                    <input type="text" id="team1-god3" placeholder="God 3 (e.g., Neith)" value="Neith">
                    <input type="text" id="team1-god4" placeholder="God 4 (e.g., Ra)" value="Ra">
                    <input type="text" id="team1-god5" placeholder="God 5 (e.g., Ymir)" value="Ymir">
                </div>
            </div>
            
            <div class="vs-section">
                VS
            </div>
            
            <div class="team-section team2">
                <h3>🔴 Enemy Team</h3>
                <div class="god-input">
                    <input type="text" id="team2-god1" placeholder="God 1 (e.g., Loki)" value="Loki">
                    <input type="text" id="team2-god2" placeholder="God 2 (e.g., Aphrodite)" value="Aphrodite">
                    <input type="text" id="team2-god3" placeholder="God 3 (e.g., Kukulkan)" value="Kukulkan">
                    <input type="text" id="team2-god4" placeholder="God 4 (e.g., Thor)" value="Thor">
                    <input type="text" id="team2-god5" placeholder="God 5 (e.g., Sobek)" value="Sobek">
                </div>
            </div>
        </div>
        
        <button class="analyze-btn" onclick="analyzeTeams()">
            🎯 Analyze Matchup
        </button>
        
        <div class="results" id="results" style="display: none;">
            <div class="result-card">
                <div class="win-probability">
                    <div class="win-prob-circle" id="win-circle">
                        <span id="win-percentage">--</span>
                    </div>
                    <div id="confidence">Analyzing...</div>
                </div>
                
                <h4>🎤 Voice Summary</h4>
                <p id="voice-summary">--</p>
            </div>
            
            <div class="result-card">
                <h4>🧠 Strategic Advice</h4>
                <ul class="advice-list" id="advice-list">
                    <li>Analyzing team compositions...</li>
                </ul>
                
                <h4 style="margin-top: 20px;">🛡️ Item Priorities</h4>
                <ul class="advice-list" id="item-list">
                    <li>Calculating priorities...</li>
                </ul>
            </div>
        </div>
        
        <div class="history">
            <h3>📊 Analysis History</h3>
            <div id="history-list">
                <p>No analyses yet. Start by analyzing a team matchup!</p>
            </div>
        </div>
    </div>
    
    <div class="status disconnected" id="status">Connecting...</div>
    
    <script>
        let ws = null;
        let analysisCount = 0;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = function() {
                document.getElementById('status').textContent = 'Connected';
                document.getElementById('status').className = 'status connected';
            };
            
            ws.onclose = function() {
                document.getElementById('status').textContent = 'Disconnected';
                document.getElementById('status').className = 'status disconnected';
                setTimeout(connectWebSocket, 3000);
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'analysis') {
                    displayAnalysis(data.analysis);
                }
            };
        }
        
        function analyzeTeams() {
            const team1 = [];
            const team2 = [];
            
            for (let i = 1; i <= 5; i++) {
                const god1 = document.getElementById(`team1-god${i}`).value.trim();
                const god2 = document.getElementById(`team2-god${i}`).value.trim();
                
                if (god1) team1.push(god1);
                if (god2) team2.push(god2);
            }
            
            if (team1.length !== 5 || team2.length !== 5) {
                alert('Assault is 5v5! Please enter all 5 gods for each team.');
                return;
            }
            
            // Show loading state
            document.getElementById('results').style.display = 'grid';
            document.getElementById('win-percentage').textContent = '...';
            document.getElementById('confidence').textContent = 'Analyzing...';
            
            // Send analysis request
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'analyze',
                    team1: team1,
                    team2: team2
                }));
            } else {
                // Fallback to HTTP request
                fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({team1: team1, team2: team2})
                })
                .then(response => response.json())
                .then(data => displayAnalysis(data))
                .catch(error => {
                    console.error('Analysis failed:', error);
                    alert('Analysis failed. Please try again.');
                });
            }
        }
        
        function displayAnalysis(analysis) {
            const winProb = Math.round(analysis.win_probability * 100);
            
            // Update win probability
            document.getElementById('win-percentage').textContent = winProb + '%';
            document.getElementById('confidence').textContent = `${analysis.confidence} confidence`;
            
            // Color code the circle
            const circle = document.getElementById('win-circle');
            if (winProb >= 70) {
                circle.style.background = 'conic-gradient(#00ff88 0deg, #00ff88 ' + (winProb * 3.6) + 'deg, rgba(255,255,255,0.2) ' + (winProb * 3.6) + 'deg)';
            } else if (winProb >= 50) {
                circle.style.background = 'conic-gradient(#ffaa00 0deg, #ffaa00 ' + (winProb * 3.6) + 'deg, rgba(255,255,255,0.2) ' + (winProb * 3.6) + 'deg)';
            } else {
                circle.style.background = 'conic-gradient(#ff4444 0deg, #ff4444 ' + (winProb * 3.6) + 'deg, rgba(255,255,255,0.2) ' + (winProb * 3.6) + 'deg)';
            }
            
            // Update voice summary
            document.getElementById('voice-summary').textContent = analysis.voice_summary;
            
            // Update advice list
            const adviceList = document.getElementById('advice-list');
            adviceList.innerHTML = '';
            analysis.key_advice.forEach(advice => {
                const li = document.createElement('li');
                li.textContent = advice;
                adviceList.appendChild(li);
            });
            
            // Update item priorities
            const itemList = document.getElementById('item-list');
            itemList.innerHTML = '';
            if (analysis.item_priorities.length > 0) {
                analysis.item_priorities.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item;
                    itemList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'No specific item priorities identified';
                itemList.appendChild(li);
            }
            
            // Add to history
            addToHistory(analysis);
        }
        
        function addToHistory(analysis) {
            analysisCount++;
            const historyList = document.getElementById('history-list');
            
            if (analysisCount === 1) {
                historyList.innerHTML = '';
            }
            
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            const winProb = Math.round(analysis.win_probability * 100);
            const timestamp = new Date().toLocaleTimeString();
            
            historyItem.innerHTML = `
                <strong>#${analysisCount} - ${timestamp}</strong><br>
                Win Probability: ${winProb}% (${analysis.confidence})<br>
                Strategy: ${analysis.voice_summary}
            `;
            
            historyList.insertBefore(historyItem, historyList.firstChild);
            
            // Keep only last 10 analyses
            while (historyList.children.length > 10) {
                historyList.removeChild(historyList.lastChild);
            }
        }
        
        // Initialize
        connectWebSocket();
        
        // Allow Enter key to trigger analysis
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeTeams();
            }
        });
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def handle_analyze(self, request):
        """Handle analysis API request"""
        try:
            data = await request.json()
            team1 = data.get('team1', [])
            team2 = data.get('team2', [])
            
            if not team1 or not team2:
                return web.json_response({'error': 'Both teams required'}, status=400)
            
            logger.info(f"🔍 Web analysis: {team1} vs {team2}")
            
            # Perform analysis
            start_time = time.time()
            analysis = self.data_manager.quick_analyze(team1, team2)
            analysis_time = (time.time() - start_time) * 1000
            
            # Convert to dict for JSON response
            analysis_dict = {
                'win_probability': analysis.win_probability,
                'confidence': analysis.confidence,
                'key_advice': analysis.key_advice,
                'item_priorities': analysis.item_priorities,
                'voice_summary': analysis.voice_summary,
                'timestamp': analysis.timestamp,
                'analysis_time_ms': round(analysis_time, 2)
            }
            
            # Add to history
            self.analysis_history.append({
                'team1': team1,
                'team2': team2,
                'analysis': analysis_dict,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 50 analyses
            if len(self.analysis_history) > 50:
                self.analysis_history = self.analysis_history[-50:]
            
            logger.info(f"📊 Analysis complete in {analysis_time:.1f}ms - {analysis.win_probability*100:.0f}% win chance")
            
            return web.json_response(analysis_dict)
            
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_websocket(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        logger.info(f"📡 WebSocket connected. Total: {len(self.websockets)}")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        
                        if data.get('type') == 'analyze':
                            team1 = data.get('team1', [])
                            team2 = data.get('team2', [])
                            
                            if team1 and team2:
                                analysis = self.data_manager.quick_analyze(team1, team2)
                                
                                response = {
                                    'type': 'analysis',
                                    'analysis': {
                                        'win_probability': analysis.win_probability,
                                        'confidence': analysis.confidence,
                                        'key_advice': analysis.key_advice,
                                        'item_priorities': analysis.item_priorities,
                                        'voice_summary': analysis.voice_summary,
                                        'timestamp': analysis.timestamp
                                    }
                                }
                                
                                await ws.send_str(json.dumps(response))
                                
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({'error': 'Invalid JSON'}))
                    except Exception as e:
                        await ws.send_str(json.dumps({'error': str(e)}))
                        
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.websockets.discard(ws)
            logger.info(f"📡 WebSocket disconnected. Total: {len(self.websockets)}")
        
        return ws
    
    async def handle_history(self, request):
        """Get analysis history"""
        return web.json_response({
            'history': self.analysis_history[-20:],  # Last 20 analyses
            'total_analyses': len(self.analysis_history)
        })

def create_app():
    """Create web application"""
    brain = WebAssaultBrain()
    app = web.Application()
    
    # Setup CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Routes
    app.router.add_get('/', brain.handle_index)
    app.router.add_post('/api/analyze', brain.handle_analyze)
    app.router.add_get('/api/history', brain.handle_history)
    app.router.add_get('/ws', brain.handle_websocket)
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app

async def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🌐 SMITE 2 ASSAULT BRAIN WEB DEMO                        ║
║                     Real-time Analysis Web Interface                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    app = create_app()
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 9000)
    await site.start()
    
    print("🚀 Web demo started!")
    print("📱 Open in browser: http://localhost:9000")
    print("🌐 Network access: http://0.0.0.0:9000")
    print("⚡ Features:")
    print("   - Real-time team analysis")
    print("   - WebSocket live updates")
    print("   - Analysis history")
    print("   - Mobile-friendly interface")
    print("   - Discord-ready results")
    print("\n🎯 Ready for testing!")
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down web demo...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())