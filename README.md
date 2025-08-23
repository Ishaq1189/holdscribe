# HoldScribe 🎤

A push-to-talk voice transcription tool that uses AI for accurate speech-to-text conversion. Hold a key, speak, release to transcribe and automatically paste the text at your cursor position.

## 🚀 Quick Install with Homebrew

```bash
brew tap ishaq1189/holdscribe
brew install holdscribe
holdscribe
```

Hold **Right Alt**, speak, release to transcribe!

## ✨ Features

- **Push-to-talk functionality** - Hold key to record, release to transcribe
- **High accuracy** - Uses OpenAI Whisper AI models for precise transcription
- **Multiple trigger keys** - Support for function keys, modifier keys, and more
- **Cross-platform pasting** - Automatically types transcribed text at cursor position
- **Multiple Whisper models** - Choose between speed and accuracy
- **Real-time feedback** - Visual indicators for recording and processing states
- **Terminal friendly** - Works great with terminals like Ghostty, iTerm2, Terminal.app

## 📖 Usage

### Basic Commands

```bash
# Start with Right Alt key (default)
holdscribe

# Use different trigger keys
holdscribe --key f8
holdscribe --key f9

# Choose AI models for speed vs accuracy
holdscribe --model tiny    # Fastest
holdscribe --model base    # Balanced (default)
holdscribe --model large   # Most accurate

# Background mode (runs continuously)
holdscribe --background

# Enhanced security (prompts before each recording)
holdscribe --prompt-permissions
```

### Available Trigger Keys

- **Function keys**: `f1`, `f2`, `f3`, `f4`, `f5`, `f6`, `f7`, `f8`, `f9`, `f10`, `f11`, `f12`
- **Modifier keys**: `alt_r`, `cmd_r`, `shift_r`, `ctrl`, `space`
- **Other keys**: `caps_lock`, `tab`, `home`, `end`, `page_up`, `page_down`

### Background Mode

```bash
# Run in background (keeps running after closing terminal)
holdscribe --background

# True daemon mode (completely detached)
holdscribe --daemon

# Stop background process
pkill -f holdscribe
```

### AI Models

Choose between speed and accuracy:

```bash
# Fastest processing
holdscribe --model tiny

# Good balance (default)
holdscribe --model base

# More accurate
holdscribe --model medium

# Most accurate
holdscribe --model large
```

| Model  | Speed | Accuracy | Size |
|--------|-------|----------|------|
| tiny   | ⚡⚡⚡ | ⭐⭐   | ~39MB |
| base   | ⚡⚡   | ⭐⭐⭐ | ~74MB |
| small  | ⚡     | ⭐⭐⭐⭐ | ~244MB |
| medium | 🐌     | ⭐⭐⭐⭐⭐ | ~769MB |
| large  | 🐌🐌   | ⭐⭐⭐⭐⭐ | ~1550MB |

## ⚙️ Configuration

### macOS Permissions

**Required**: Grant accessibility permissions for keyboard monitoring.

1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Click the **lock** 🔒 and authenticate  
3. Click **+** and add your terminal app (Terminal.app, Ghostty, iTerm2, etc.)
4. Enable the checkbox for your terminal

### Enhanced Security Mode

```bash
# Prompt for permission before each recording
holdscribe --prompt-permissions

# Combine with other options
holdscribe --key f8 --prompt-permissions --model tiny
```

This prompts for explicit consent before each recording session.

### Recommended Keys

- **`alt_r` (Right Alt)** - Doesn't interfere with typing
- **`f8`, `f9`, `f10`** - Great for terminal use
- **Avoid `space`** - Will type spaces during normal use

## 🎯 How It Works

1. **Hold trigger key** - Starts audio recording from your microphone
2. **Speak naturally** - Audio is captured while key is held down
3. **Release trigger key** - Recording stops, processing begins
4. **Whisper transcription** - OpenAI Whisper converts speech to text
5. **Auto-paste** - Transcribed text is typed at your cursor position

## 🚨 Troubleshooting

### "This process is not trusted" Error

You need to grant accessibility permissions:
- System Settings → Privacy & Security → Accessibility
- Add your terminal app and enable it

### Permission Issues

HoldScribe handles permissions gracefully:
1. **First run**: Prompts to grant accessibility permissions
2. **Enhanced security**: Use `--prompt-permissions` for consent before each recording
3. **Graceful fallback**: Continues with limited functionality if permissions denied

### Key Not Detected

Some keys may not work on all systems:
- **Right Alt not working?** Try `f8` or `f9`
- **Right Control not working?** Use `alt_r` or function keys
- Test with debug output to see what keys are detected

### Audio Issues

- Ensure microphone permissions are granted
- Check your default audio input device
- Try running with `sudo` temporarily to test

### Whisper Model Loading

First run downloads the Whisper model (~74MB for base model). This is normal and only happens once.

## 💡 Tips

- **Terminal Usage**: Function keys like `F8` work great in terminals
- **Text Editors**: Right Alt key is perfect for coding/writing
- **Longer Speech**: Hold key for entire sentence/paragraph for best results
- **Background Noise**: Whisper handles reasonable background noise well
- **Multiple Languages**: Whisper supports many languages automatically

## 🔒 Privacy

- **All processing is local** - No data sent to external servers
- **No audio storage** - Recordings are temporary and deleted immediately
- **Open source** - Full code available for inspection

## 📋 System Requirements

- **OS**: macOS 10.15+ (tested on macOS 14+)
- **Python**: 3.8 or higher
- **Memory**: 2GB+ RAM recommended
- **Storage**: 1GB for Whisper models
- **Microphone**: Any built-in or USB microphone

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features  
- Submit pull requests
- Improve documentation

## 📄 License

This project is open source. Use it however you'd like!

---

**Happy transcribing!** 🎤✨