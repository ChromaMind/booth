# ChromaMind Studio

A creative platform for builders and artists to design and experience audio-reactive brain entrainment "trips" using LED glasses. ChromaMind Studio generates synchronized light patterns that respond to music for enhanced meditation, focus, and relaxation experiences.

## 🧠 Overview

ChromaMind Studio is a creative platform that enables builders and artists to craft immersive brain entrainment experiences. The system analyzes music tempo, mood, and intensity to generate optimal blinking patterns for different brain states (alpha, beta, theta, gamma waves), creating unique "trips" that synchronize light with sound.

## ✨ Features

### Audio Analysis

- **Tempo Detection**: Real-time BPM analysis using librosa
- **Mood Analysis**: Spectral centroid, rolloff, and RMS energy analysis
- **Intensity Mapping**: Dynamic pattern selection based on audio characteristics

### Brain Entrainment Patterns

- **8 Arduino Modes**: Pre-programmed patterns for different brain states
- **Dynamic Timing**: 20-50ms blink intervals based on tempo
- **Safety Controls**: Maximum brightness of 20 for safe closed-eye viewing
- **Real-time Generation**: Continuous pattern updates during audio playback

### Hardware Integration

- **ESP8266/ESP32 Support**: WebSocket communication with LED device
- **2x16 LED Array**: Optimized for glasses form factor
- **Synchronized Playback**: Audio and LED patterns perfectly synchronized

### Creative Platform

- **Trip Creation**: Design unique brain entrainment experiences
- **Artist Tools**: Intuitive interface for creators and builders
- **Walrus Integration**: Decentralized storage of brain entrainment trips
- **JSON Export**: Rich metadata with frame information
- **Session Tracking**: Complete pattern history and analytics

## 🛠️ Installation

### Prerequisites

```bash
pip install PyQt6 pygame librosa numpy websocket-client requests
```

### Hardware Setup

1. Flash ESP8266/ESP32 with the provided Arduino code
2. Configure WiFi settings in the Arduino code
3. Note the device IP address (default: `10.151.240.37:81`)

### Software Setup

```bash
git clone <repository-url>
cd chromamind-studio
python led_viewer.py
```

## 🎵 Usage

### Creative Workflow

1. **Load Audio**: Upload MP3 file through the intuitive GUI
2. **Design Trip**: System analyzes audio and creates brain entrainment frames
3. **Preview Experience**: View generated patterns in the visualization window
4. **Experience Trip**: Send patterns to Arduino device via WebSocket
5. **Share & Store**: Upload trip data to Walrus for permanent storage and sharing

### Pattern Types

- **Mode 1**: Full strip flash (high activity, calm mood)
- **Mode 2**: Color transition (high activity, energetic mood)
- **Mode 3**: Edge only (edge-focused patterns)
- **Mode 4**: Expanding (moderate activity)
- **Mode 5**: Center out (moderate activity)
- **Mode 6**: Moving dot (low activity, energetic)
- **Mode 7**: Row toggle (low activity, calm)
- **Mode 8**: Snake (very low activity)

### Safety Features

- **Session Limits**: Maximum 30-minute sessions recommended
- **Brightness Control**: Capped at 20 for safe viewing
- **Emergency Stop**: Immediate pattern cessation
- **Health Warnings**: Built-in safety disclaimers

## 📁 Project Structure

```
chromamind-studio/
├── led_viewer.py          # Main ChromaMind Studio application
├── patterns.py            # Brain entrainment pattern definitions
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

### Arduino Settings

```cpp
#define LED_PIN     D4
#define NUM_PIXELS  32
#define WEBSOCKET_PORT 81
```

### WebSocket Protocol

```
Format: "mode;blink_interval;brightness"
Example: "3;25;15"
```

### Walrus Storage

- **Publisher**: `https://publisher.walrus-testnet.walrus.space`
- **Storage**: 10 epochs by default
- **Format**: JSON with metadata and trip data

## 🧪 Technical Details

### Audio Analysis Pipeline

1. **librosa Loading**: Native sample rate preservation
2. **Feature Extraction**: RMS, spectral centroid, rolloff, zero-crossing rate
3. **Tempo Detection**: Beat tracking with librosa
4. **Mood Calculation**: Normalized feature combination
5. **Pattern Selection**: Dynamic mode assignment based on audio characteristics

### Trip Generation

- **Frame Rate**: 50 FPS target
- **Duration**: Based on audio length
- **Synchronization**: Perfect audio-visual sync
- **Optimization**: Simplified data structure for Arduino compatibility

### WebSocket Communication

- **Protocol**: Text-based with semicolon separation
- **Retry Logic**: 3 attempts with exponential backoff
- **Error Handling**: Graceful failure recovery
- **Timing**: Adaptive delays based on blink intervals

## 🚀 Advanced Features

### Brain State Targeting

- **Alpha (8-13 Hz)**: Relaxation and calm focus
- **Beta (13-30 Hz)**: Active thinking and alertness
- **Theta (4-8 Hz)**: Meditation and creativity
- **Gamma (30-100 Hz)**: High-level processing

### Pattern Algorithms

- **Position-based Variation**: Wave-like effects across LED array
- **Mood Intensity Scaling**: Dynamic brightness and timing
- **Tempo Synchronization**: Beat-matched pattern changes
- **Cross-pattern Effects**: Enhanced entrainment through multiple frequencies

## 🔒 Safety & Compliance

### Usage Guidelines

- **Session Duration**: Maximum 30 minutes per session
- **Break Intervals**: 5-minute breaks between sessions
- **Eye Safety**: Designed for closed-eye viewing
- **Medical Disclaimer**: Not a medical device

### Technical Safety

- **Brightness Limits**: Maximum 20/255 brightness
- **Frequency Limits**: 1-30 Hz safe range
- **Emergency Controls**: Immediate stop functionality
- **Connection Monitoring**: Real-time status indicators

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Brain entrainment should be used responsibly and in consultation with healthcare professionals. The authors are not responsible for any adverse effects from the use of this software.

## 🔗 Links

- [ChromaMind Studio Documentation](link-to-docs)
- [Arduino Code Repository](link-to-arduino-code)
- [Walrus Documentation](https://docs.world.org/mini-apps/quick-start/installing)
- [librosa Documentation](https://librosa.org/)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython/)

## 📞 Support

For questions, issues, or contributions, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for the ChromaMind community of creators and artists**
