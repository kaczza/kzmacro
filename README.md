# KzMacro 🎮

![KzMacro Screenshot](https://img.shields.io/badge/KzMacro-Pro_Studio-blueviolet)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

![KzMacro UI Preview](https://via.placeholder.com/800x450/1c252e/ffffff?text=KzMacro+Professional+Macro+Studio)

## ✨ Features

### 🎯 **Core Capabilities**
- 🎥 **Real-time Recording** - Record keyboard and mouse actions
- 🎮 **Multi-profile System** - Create and switch between macro profiles
- 🔑 **Global Hotkeys** - Assign macros to any key or mouse button
- 🖱️ **Full Mouse Support** - Left, Right, Middle, X1, X2 buttons
- ⏱️ **Timeline Editor** - Visual timeline with wait times
- 💾 **Save/Load System** - JSON format for easy backup and sharing

### 🎨 **Professional Interface**
- 🎨 **G-HUB Inspired Design** - Dark theme with modern styling
- 📁 **Sidebar Navigation** - Easy profile management
- 🧩 **Drag & Drop Blocks** - Visual macro building
- 📊 **Real-time Preview** - See your macro as you build it

### ⚡ **Advanced Features**
- 🌐 **Global Listener** - Works in any application
- 🔄 **Multi-threaded** - Smooth performance while recording
- 🛡️ **Error Handling** - Robust exception handling
- 📱 **Responsive UI** - Adapts to different screen sizes

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8 or higher
```

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/KzMacro.git
cd KzMacro

# Install dependencies
pip install PyQt6 pynput
```

### Running KzMacro
```bash
python main.py
```

## 📖 User Guide

### 1. Creating Your First Macro
1. Click **"Record Macro"** to start recording
2. Perform your actions (type, click, etc.)
3. Click **"Stop"** when finished
4. Your macro appears in the timeline

### 2. Assigning a Hotkey
1. Click **"Assign to Key/Mouse Button"**
2. Press any keyboard key or mouse button
3. The macro will now trigger with that button

### 3. Managing Profiles
- **New Profile**: Click "+ New Profile" in sidebar
- **Rename**: Select profile and click "Rename"
- **Delete**: Select profile and click "Delete" (cannot delete last profile)
- **Switch**: Click on profile name in sidebar

### 4. Saving & Loading
- **Save All**: Click "Save" to export all profiles to JSON
- **Load**: Click "Load" to import profiles from JSON file

## 🛠️ Technical Details

### Project Structure
```
KzMacro/
├── main.py              # Main application entry point
├── README.md            # This file
├── requirements.txt     # Python dependencies
└── profiles/           # Saved macro profiles (auto-created)
```

### Dependencies
```txt
PyQt6==6.5.0
pynput==1.7.6
```

### Architecture
- **MacroEditor**: Main application window
- **MacroProfile**: Profile data management
- **MacroBlock**: UI representation of macro actions
- **GlobalKeyListener**: Background thread for hotkey detection

## 🎮 Supported Actions

### Keyboard
- All standard keys (A-Z, 0-9, F1-F12)
- Special keys (Enter, Space, Tab, Escape)
- Modifier keys (Ctrl, Alt, Shift, Windows)

### Mouse
- Left Click (single/double)
- Right Click
- Middle Click (Scroll Wheel)
- Side Buttons (X1, X2)
- Click & Hold / Release

### Timing
- Automatic delay recording between actions
- Precise millisecond timing
- Visual wait time display

## 📁 File Format

Profiles are saved in JSON format:
```json
{
  "name": "My Macro",
  "assigned_button": "Key.f5",
  "assigned_label": "F5",
  "blocks": [
    {"text": "Key a", "wait": 100},
    {"text": "Button.left Down", "wait": 50},
    {"text": "Button.left Up", "wait": 200}
  ]
}
```

## 🚧 Known Limitations

1. **Administrator Rights**: May require admin rights for system-wide hotkeys
2. **Anti-Cheat Software**: Some games may block macro software
3. **Mouse Movement**: Currently records clicks but not cursor movement
4. **Complex Macros**: Very long macros may have timing issues

## 🔮 Future Roadmap

- [ ] Mouse movement recording
- [ ] Loop/repeat functionality
- [ ] Conditional macros
- [ ] Scripting support
- [ ] Auto startup

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup
```bash
# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install black flake8  # Optional: code formatting/linting
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by SteelSeries GG
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Uses [pynput](https://pypi.org/project/pynput/) for input monitoring
- Thanks to all contributors and testers!

## 🐛 Bug Reports & Feature Requests

Found a bug? Have an idea for a feature?

1. Check the [Issues](https://github.com/kaczaa/KzMacro/issues) page
2. If not reported, create a new issue
3. Include:
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - System information

## 📞 Support

- **GitHub Issues**: [Report Problems](https://github.com/kaczza/KzMacro/issues)
- **Documentation**: Check this README and code comments
- **Community**: Join our Discord (coming soon!)

---

<div align="center">
  
Made with ❤️ by the KzMacro Team

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/KzMacro&type=Date)](https://star-history.com/#yourusername/KzMacro&Date)

</div>

## ⚡ Quick Tips

1. **Recording Tip**: Wait a second before starting complex actions
2. **Hotkey Tip**: Use function keys (F1-F12) for global macros
3. **Profile Tip**: Name profiles descriptively (e.g., "Game-Combo-1")
4. **Performance**: Close other heavy applications while recording
5. **Backup**: Regularly save your profiles to avoid data loss

---

**Ready to automate? Start KzMacro now and boost your productivity!** 🚀
