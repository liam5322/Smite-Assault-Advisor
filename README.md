# 🎮 SMITE 2 Assault Brain - AI-Powered Game Assistant

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/liam5322/Smite-Assault-Advisor)

> **Hardware-adaptive AI companion for SMITE 2 Assault mode with real-time analysis, smart build suggestions, and smooth thematic UI**

![SMITE 2 Assault Brain Demo](https://via.placeholder.com/800x400/1a1a1a/FFD700?text=SMITE+2+ASSAULT+BRAIN)

## ✨ Features

### 🔧 **Hardware-Adaptive Performance**
- **Minimal Tier**: CPU-only OCR, basic analysis (4GB+ RAM, 2+ cores)
- **Standard Tier**: GPU-accelerated OCR, full analysis (8GB+ RAM, 4+ cores) 
- **Maximum Tier**: All features, ML predictions (16GB+ RAM, 8+ cores, GPU)

### 🎨 **Smooth & Thematic UI**
- **Divine Dark Theme**: SMITE-inspired gold/blue color scheme
- **Celestial Light Theme**: Accessibility-focused light mode
- **Pantheon Contrast**: High contrast for visibility
- **60fps Animations**: Smooth fade/slide/bounce effects with easing functions

### 🔍 **Advanced OCR System**
- **Dual Backend**: Tesseract (lightweight) + EasyOCR (advanced)
- **Fuzzy Matching**: 80%+ accuracy for god name detection
- **Adaptive Regions**: Auto-scaling for different resolutions
- **Real-time Detection**: Loading screen, TAB screen, in-game states

### 📊 **Intelligent Analysis**
- **Team Composition Analysis**: Role balance, damage split, synergies
- **Win Probability Calculation**: Meta-aware matchup analysis
- **Contextual Build Suggestions**: Counter-picks, situational items
- **Priority Recommendations**: Critical vs optional items

### ⚡ **Performance Optimizations**
- **Dynamic Loading**: Only installs needed dependencies
- **Memory Efficient**: Configurable image scaling and caching
- **Rate Limiting**: Adaptive update rates based on hardware
- **Background Processing**: Non-blocking UI with async operations

## 🚀 Quick Start

### 1. **Clone Repository**
```bash
git clone https://github.com/liam5322/Smite-Assault-Advisor.git
cd Smite-Assault-Advisor
```

### 2. **Run Setup Wizard**
```bash
python src/main.py --setup
```
The setup wizard will:
- Detect your hardware capabilities
- Recommend optimal performance tier
- Show installation commands
- Configure settings automatically

### 3. **Install Dependencies**

**For Minimal Systems (CPU-only):**
```bash
pip install -r requirements-minimal.txt
```

**For Standard Systems (Mid-range):**
```bash
pip install -r requirements.txt
```

**For Maximum Performance (High-end + GPU):**
```bash
pip install -r requirements.txt -r requirements-gpu.txt
```

### 4. **Launch Application**
```bash
python src/main.py
```

## 🎯 Usage

1. **Start SMITE 2** and queue for Assault mode
2. **Launch Assault Brain** - overlay appears in top-right corner
3. **Enter Loading Screen** - teams are automatically detected
4. **View Analysis** - win probability, strengths/weaknesses, build tips
5. **Use Hotkeys**:
   - `F1` - Toggle overlay visibility
   - `F2` - Force refresh analysis
   - `F3` - Cycle overlay position
   - `F4` - Toggle theme (Dark/Light/Contrast)

## 📋 System Requirements

### Minimum (Minimal Tier)
- **OS**: Windows 10+, Linux, macOS
- **CPU**: 2+ cores, 2.0+ GHz
- **RAM**: 4+ GB
- **Python**: 3.8+
- **Features**: Basic OCR, simple analysis

### Recommended (Standard Tier)
- **OS**: Windows 10+, Linux, macOS
- **CPU**: 4+ cores, 2.5+ GHz
- **RAM**: 8+ GB
- **Python**: 3.9+
- **Features**: GPU OCR, full analysis, real-time tracking

### Optimal (Maximum Tier)
- **OS**: Windows 10+, Linux, macOS
- **CPU**: 8+ cores, 3.0+ GHz
- **RAM**: 16+ GB
- **GPU**: NVIDIA/AMD with 4+ GB VRAM
- **Python**: 3.10+
- **Features**: All features, ML predictions, voice output

## ⚙️ Configuration

### Automatic Configuration
The application automatically detects your hardware and configures optimal settings. Manual overrides available in `config/settings.yaml`:

```yaml
# Performance settings
performance_tier: "auto"  # auto, minimal, standard, maximum
ocr_engine: "auto"        # auto, tesseract, easyocr
gpu_acceleration: "auto"  # auto, true, false

# Display settings
theme: "divine_dark"      # divine_dark, celestial_light, pantheon_contrast
overlay_position: "top-right"
overlay_opacity: 0.85

# OCR settings
ocr_confidence: 0.7
fuzzy_match_threshold: 80
```

### Theme Customization
Three built-in themes with smooth transitions:

- **🌙 Divine Dark**: SMITE-inspired with gold accents
- **☀️ Celestial Light**: Clean light mode for accessibility  
- **⚡ Pantheon Contrast**: High contrast for visibility

## 🏗️ Architecture

```
smite2-assault-brain/
├── src/
│   ├── core/                 # Core system components
│   │   ├── hardware_detector.py  # Hardware detection & performance tiers
│   │   └── config_manager.py     # Configuration management
│   ├── vision/               # Computer vision & OCR
│   │   ├── screen_capture.py     # Screen capture with optimization
│   │   └── ocr_engine.py         # Adaptive OCR with multiple backends
│   ├── analysis/             # Game analysis components
│   │   ├── comp_analyzer.py      # Team composition analysis
│   │   └── build_suggester.py    # Intelligent build suggestions
│   ├── ui/                   # User interface components
│   │   ├── themes.py             # Thematic color schemes
│   │   ├── animations.py         # Smooth animation system
│   │   └── overlay.py            # Main overlay window
│   └── main.py               # Application entry point
├── assets/                   # Game data
│   ├── gods.json            # God database with stats
│   └── items.json           # Item database with effects
├── config/                   # Configuration
│   └── settings.yaml        # User settings
└── requirements*.txt         # Dependencies for different tiers
```

## 🎨 UI Themes

### Divine Dark (Default)
```python
primary="#FFD700"     # Divine Gold
secondary="#4A90E2"   # Mystic Blue  
accent="#FF6B35"      # Phoenix Orange
background="#0A0A0A"  # Deep Black
```

### Celestial Light
```python
primary="#1E3A8A"     # Royal Blue
secondary="#7C3AED"   # Purple
accent="#DC2626"      # Red
background="#F8FAFC"  # Light Gray
```

### Pantheon Contrast
```python
primary="#00FFFF"     # Cyan
secondary="#FF00FF"   # Magenta
accent="#FFFF00"      # Yellow
background="#000000"  # Black
```

## 🔧 Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/liam5322/Smite-Assault-Advisor.git
cd Smite-Assault-Advisor

# Install development dependencies
pip install -r requirements.txt
pip install pytest black

# Run tests
pytest tests/

# Format code
black src/
```

### Adding New Features
1. **God Data**: Update `assets/gods.json` with new god stats
2. **Items**: Add new items to `assets/items.json`
3. **Themes**: Create new themes in `src/ui/themes.py`
4. **Analysis**: Extend analysis logic in `src/analysis/`

## 🐛 Troubleshooting

### Common Issues

**OCR Not Working**
```bash
# Install Tesseract
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
```

**GPU Acceleration Issues**
```bash
# Check CUDA installation
nvidia-smi

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Performance Issues**
- Lower `performance_tier` in settings
- Reduce `image_scale` for memory constraints
- Increase `update_rate` for slower systems

### Debug Mode
Enable debug mode in `config/settings.yaml`:
```yaml
debug_mode: true
save_screenshots: true
log_level: "DEBUG"
```

## 📈 Roadmap

### Phase 2 - Advanced Features
- [ ] TAB screen item detection
- [ ] Voice coaching system
- [ ] Discord integration
- [ ] Match history tracking
- [ ] Performance analytics

### Phase 3 - ML Integration
- [ ] Advanced prediction models
- [ ] Meta trend analysis
- [ ] Personalized recommendations
- [ ] Replay analysis

### Phase 4 - Community Features
- [ ] Build sharing
- [ ] Team finder
- [ ] Tournament mode
- [ ] Coaching tools

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution
- **God Database**: Expand god stats and abilities
- **Item Database**: Add new items and effects
- **OCR Accuracy**: Improve text detection
- **UI/UX**: Design improvements and new themes
- **Performance**: Optimization and new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hi-Rez Studios** for creating SMITE
- **EasyOCR Team** for excellent OCR capabilities
- **OpenCV Community** for computer vision tools
- **Python Community** for amazing libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/liam5322/Smite-Assault-Advisor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/liam5322/Smite-Assault-Advisor/discussions)
- **Discord**: [Join our Discord](https://discord.gg/smite-assault-brain)

---

<div align="center">

**⚔️ May the gods favor your battles! ⚔️**

Made with ❤️ for the SMITE community

</div>