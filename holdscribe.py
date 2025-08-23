#!/usr/bin/env python3
"""
HoldScribe - Push-to-Talk Voice Transcription Tool
Hold a key to record, release to transcribe and paste at cursor
"""

__version__ = "1.3.4"

import pyaudio
import wave
import threading
import queue
import time
import tempfile
import os
import sys
from pynput import keyboard
from pynput.keyboard import Key
import whisper
import pyperclip
import subprocess
import platform

# macOS accessibility permission handling
if platform.system() == "Darwin":
    try:
        import objc
        
        # Load ApplicationServices framework
        bundle_path = '/System/Library/Frameworks/ApplicationServices.framework'
        ApplicationServices = objc.loadBundle('ApplicationServices', 
                                            globals(), 
                                            bundle_path=bundle_path)
        
        # Load the AXIsProcessTrustedWithOptions function
        objc.loadBundleFunctions(ApplicationServices, globals(), 
                               [('AXIsProcessTrustedWithOptions', b'Z@')])
        
        AXIsProcessTrustedWithOptions = globals().get('AXIsProcessTrustedWithOptions')
        
    except ImportError:
        # Fallback if objc not available
        AXIsProcessTrustedWithOptions = None

def check_accessibility_permissions(interactive=True):
    """Check and request accessibility permissions on macOS"""
    if platform.system() != "Darwin":
        return True
    
    if AXIsProcessTrustedWithOptions is None:
        if interactive:
            print("⚠️  Cannot check accessibility permissions - objc not available")
            print("Please manually grant accessibility permissions in System Settings")
            response = input("Do you want to continue anyway? (y/N): ").strip().lower()
            return response == 'y' or response == 'yes'
        return False
    
    # Check if already trusted
    trusted = AXIsProcessTrustedWithOptions({})
    if trusted:
        print("✅ Accessibility permissions already granted")
        return True
    
    if interactive:
        print("\n🔐 HoldScribe needs accessibility permissions to monitor key presses.")
        print("This allows it to detect when you press and release the trigger key.")
        print("\nDo you want to grant these permissions? (y/N): ", end="")
        response = input().strip().lower()
        
        if response != 'y' and response != 'yes':
            print("❌ Permissions denied by user")
            return False
    
    print("🔐 Requesting accessibility permissions...")
    print("A system dialog will appear - please click 'Open System Settings'")
    print("Then add this application to Accessibility and enable it.")
    
    # Request permissions with automatic dialog
    options = {
        'AXTrustedCheckOptionPrompt': True
    }
    
    # This will trigger the macOS permission dialog
    trusted = AXIsProcessTrustedWithOptions(options)
    
    if trusted:
        print("✅ Accessibility permissions granted!")
        return True
    else:
        print("❌ Accessibility permissions not granted")
        print("Please go to System Settings → Privacy & Security → Accessibility")
        print("and add this application to the list.")
        if interactive:
            print("\nDo you want to continue without permissions? (y/N): ", end="")
            response = input().strip().lower()
            return response == 'y' or response == 'yes'
        return False

class HoldScribe:
    def __init__(self, trigger_key=Key.alt_r, model_size="base", background_mode=False, prompt_permissions=False):
        self.trigger_key = trigger_key
        self.background_mode = background_mode
        self.prompt_permissions = prompt_permissions
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recording_thread = None
        self.permission_granted = True  # Track current permission state
        
        # Audio settings
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # Whisper works best with 16kHz
        
        # Initialize audio
        self.audio = pyaudio.PyAudio()
        
        # Load Whisper model
        if not self.background_mode:
            print(f"Loading AI model '{model_size}'...")
        self.model = whisper.load_model(model_size)
        if not self.background_mode:
            print("Model loaded successfully!")
        
        # Keyboard listener
        self.listener = None
        
    def start_recording(self):
        """Start audio recording"""
        if self.is_recording:
            return
        
        # Check permissions before each recording if prompt_permissions is enabled
        if self.prompt_permissions and not self.background_mode:
            if not self._check_runtime_permissions():
                print("❌ Recording cancelled - permissions denied")
                return
            
        self.is_recording = True
        self.audio_queue = queue.Queue()
        
        print("🎤 Recording started...")
        
        # Start recording thread
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
    def stop_recording(self):
        """Stop recording and process audio"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        print("⏹️  Recording stopped, processing...")
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=2)
        
        # Process the recorded audio
        self._process_audio()
        
    def _record_audio(self):
        """Record audio in a separate thread"""
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            while self.is_recording:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.audio_queue.put(data)
                except Exception as e:
                    print(f"Error recording: {e}")
                    break
                    
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Failed to initialize audio stream: {e}")
            self.is_recording = False
            
    def _process_audio(self):
        """Process recorded audio and transcribe"""
        if self.audio_queue.empty():
            print("No audio recorded")
            return
            
        # Collect all audio data
        audio_data = []
        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())
            
        if not audio_data:
            print("No audio data to process")
            return
            
        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name
            
        try:
            # Write WAV file
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(audio_data))
            
            # Transcribe with AI
            print("🤖 Transcribing...")
            result = self.model.transcribe(temp_filename, language="en")
            text = result["text"].strip()
            
            if text:
                print(f"📝 Transcribed: '{text}'")
                self._paste_text(text)
            else:
                print("No speech detected")
                
        except Exception as e:
            print(f"Error processing audio: {e}")
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_filename)
            except:
                pass
                
    def _paste_text(self, text):
        """Paste text at current cursor position"""
        try:
            # Method 1: Try direct typing (works in most applications)
            if platform.system() == "Darwin":  # macOS
                # Use AppleScript for reliable pasting on macOS
                script = f'''
                tell application "System Events"
                    keystroke "{text}"
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=True)
                
            elif platform.system() == "Linux":
                # Use xdotool for Linux
                subprocess.run(["xdotool", "type", text], check=True)
                
            else:  # Windows fallback
                # Copy to clipboard and paste
                pyperclip.copy(text)
                time.sleep(0.1)
                # Simulate Ctrl+V
                from pynput.keyboard import Controller
                kbd = Controller()
                with kbd.pressed(Key.ctrl):
                    kbd.press('v')
                    kbd.release('v')
                    
        except (subprocess.CalledProcessError, Exception) as e:
            # Fallback: copy to clipboard
            if isinstance(e, subprocess.CalledProcessError):
                print("Direct typing failed, copied to clipboard instead")
            else:
                print(f"Error pasting text: {e}")
            pyperclip.copy(text)
            print("📋 Text copied to clipboard - paste with Cmd+V")
    
    def on_key_press(self, key):
        """Handle key press events"""
        if key == self.trigger_key:
            self.start_recording()
            
    def on_key_release(self, key):
        """Handle key release events"""
        if key == self.trigger_key:
            self.stop_recording()
        elif key == Key.esc and not self.background_mode:
            print("Exiting...")
            return False  # Stop listener
            
    def start_listener(self):
        """Start the keyboard listener"""
        if not self.background_mode:
            print(f"HoldScribe ready! 🎤")
            print(f"Hold {self.trigger_key} to record, release to transcribe")
            print("Press ESC to exit")
        else:
            # In background mode, minimal output
            print(f"HoldScribe running in background 🎤")
            print(f"Trigger key: {self.trigger_key}")
            print(f"Stop with: killall Python or pkill -f holdscribe")
        
        try:
            with keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release,
                suppress=False  # Don't suppress other key events
            ) as listener:
                self.listener = listener
                listener.join()
        except Exception as e:
            if not self.background_mode:
                print(f"Error starting listener: {e}")
            # In background mode, fail silently or log to a file
            
    def cleanup(self):
        """Clean up resources"""
        self.is_recording = False
        if self.audio:
            self.audio.terminate()
    
    def _check_runtime_permissions(self):
        """Check permissions at runtime with user prompt"""
        if platform.system() != "Darwin":
            return True
        
        # Check if we have accessibility permissions
        has_accessibility = True
        if AXIsProcessTrustedWithOptions is not None:
            has_accessibility = AXIsProcessTrustedWithOptions({})
        
        # Check if we need microphone permissions (PyAudio handles this)
        print(f"\n🔐 HoldScribe Permission Check")
        print(f"Accessibility: {'✅ Granted' if has_accessibility else '❌ Not granted'}")
        print(f"Microphone: Will be requested by PyAudio if needed")
        
        if not has_accessibility:
            print("\n⚠️  Some features may not work without accessibility permissions.")
        
        print(f"\nDo you want to allow HoldScribe to:")
        print(f"  • Monitor keyboard for trigger key ({self.trigger_key})")
        print(f"  • Record audio when key is held")
        print(f"  • Transcribe speech using AI")
        print(f"  • Paste text at cursor position")
        
        response = input(f"\nAllow these actions? (y/N): ").strip().lower()
        granted = response == 'y' or response == 'yes'
        
        if granted:
            print("✅ User granted permissions for this session")
        else:
            print("❌ User denied permissions")
            
        return granted


def main():
    import argparse
    
    # Check if script is executable (for debugging installation issues)
    import stat
    script_path = os.path.abspath(__file__)
    try:
        file_stat = os.stat(script_path)
        if not (file_stat.st_mode & stat.S_IEXEC):
            print("⚠️  Warning: Script may not have execute permissions")
            print(f"Script path: {script_path}")
            print("If installed via Homebrew, try: brew reinstall holdscribe")
    except Exception:
        pass  # Ignore stat errors
    
    parser = argparse.ArgumentParser(
        description=f"HoldScribe v{__version__} - Push-to-talk voice transcription",
        epilog="Hold your trigger key, speak, release to transcribe and paste!"
    )
    parser.add_argument("--version", action="version", version=f"HoldScribe {__version__}")
    parser.add_argument("--key", default="alt_r", 
                       help="Trigger key (default: alt_r, options: f1-f12, space, ctrl_r)")
    parser.add_argument("--model", default="base",
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="AI model size (default: base)")
    parser.add_argument("--background", action="store_true",
                       help="Run in background mode (fork process)")
    parser.add_argument("--prompt-permissions", action="store_true",
                       help="Prompt for permissions before each recording (enhanced security)")
    parser.add_argument("--daemon", action="store_true",
                       help="True daemon mode (completely detach from terminal)")
    
    args = parser.parse_args()
    
    # For background mode, spawn a new detached process and exit parent
    if args.background:
        if platform.system() != "Darwin":
            print("❌ Background mode only supported on macOS") 
            sys.exit(1)
        print("🔄 Starting HoldScribe in background mode...")
        print("💡 Use 'pkill -f holdscribe' to stop")
        
        # Spawn a new detached process using subprocess
        import subprocess
        
        # Build command without --background flag to avoid recursion
        cmd_args = [sys.executable, __file__]
        for arg in sys.argv[1:]:
            if arg != '--background':
                cmd_args.append(arg)
        
        # Start detached background process
        process = subprocess.Popen(
            cmd_args,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
        
        print(f"✅ HoldScribe started in background (PID: {process.pid})")
        sys.exit(0)  # Parent exits, child continues detached
    
    elif args.daemon:
        if platform.system() != "Darwin":
            print("❌ Background/daemon mode only supported on macOS")
            sys.exit(1)
        print("🚀 Starting HoldScribe daemon...")
        # Daemon mode uses same subprocess approach as background mode
        import subprocess
        cmd_args = [sys.executable, __file__]
        for arg in sys.argv[1:]:
            if arg != '--daemon':
                cmd_args.append(arg)
        process = subprocess.Popen(
            cmd_args,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
        print(f"✅ HoldScribe daemon started (PID: {process.pid})")
        sys.exit(0)
    
    # Now check permissions (after fork for background mode)
    if args.daemon or args.background:
        # Check permissions for background/daemon modes (non-interactive)
        if not check_accessibility_permissions(interactive=False):
            # In background/daemon mode, exit silently if no permissions
            sys.exit(1)
        # Debug: confirm we passed permission check
        if args.background and not args.daemon:
            print("✅ Background process: permissions OK")
    else:
        # Interactive mode permission check
        if not check_accessibility_permissions(interactive=True):
            print("\n⚠️  HoldScribe will run with limited functionality.")
            print("Key monitoring may not work properly without accessibility permissions.")
            print("You can grant permissions later in System Settings → Privacy & Security → Accessibility")
            
            response = input("\nDo you want to continue anyway? (y/N): ").strip().lower()
            if response != 'y' and response != 'yes':
                print("Exiting...")
                sys.exit(1)
            
            print("\n⚠️  Running with limited permissions - some features may not work correctly.")
    
    # Map key string to Key object
    key_map = {
        # Function keys
        "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
        "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
        "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
        
        # Modifier keys
        "space": Key.space,
        "alt": Key.alt, "alt_r": Key.alt_r, "right_alt": Key.alt_r,
        "ctrl": Key.ctrl, "ctrl_r": Key.ctrl_r, "right_ctrl": Key.ctrl_r,
        "cmd": Key.cmd, "cmd_r": Key.cmd_r, "right_cmd": Key.cmd_r,
        "shift": Key.shift, "shift_r": Key.shift_r, "right_shift": Key.shift_r,
        
        # Other useful keys
        "caps_lock": Key.caps_lock,
        "tab": Key.tab,
        "home": Key.home,
        "end": Key.end,
        "page_up": Key.page_up,
        "page_down": Key.page_down,
        
        # Arrow keys
        "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right
    }
    
    trigger_key = key_map.get(args.key.lower(), Key.alt_r)
    
    holdscribe = HoldScribe(
        trigger_key=trigger_key, 
        model_size=args.model, 
        background_mode=args.background or args.daemon,
        prompt_permissions=args.prompt_permissions
    )
    
    # Show tip only in interactive mode
    if not args.background and not args.daemon:
        print(f"\n💡 \033[1m\033[36mTIP:\033[0m To run in background: \033[33mholdscribe --background\033[0m")
        print(f"   This lets you use other apps while HoldScribe runs.")
        print(f"   Stop with: \033[31mkillall Python\033[0m or \033[31mpkill -f holdscribe\033[0m")
        print(f"\n🚀 \033[1m\033[36mDAEMON:\033[0m For true daemon mode: \033[33mholdscribe --daemon\033[0m")
        print(f"   Completely detaches from terminal (no output)")
        if not args.prompt_permissions:
            print(f"\n🔐 \033[1m\033[36mSECURITY:\033[0m For enhanced security: \033[33mholdscribe --prompt-permissions\033[0m")
            print(f"   This prompts for permission before each recording.")
        print()
    
    try:
        holdscribe.start_listener()
    except KeyboardInterrupt:
        if not args.background and not args.daemon:
            print("\nInterrupted by user")
    except Exception as e:
        if not args.background and not args.daemon:
            print(f"\n❌ Error: {e}")
        # In background/daemon mode, fail silently or log to file
        import traceback
        if args.background or args.daemon:
            # Could log to a file here in the future
            pass
        else:
            traceback.print_exc()
    finally:
        holdscribe.cleanup()

if __name__ == "__main__":
    main()