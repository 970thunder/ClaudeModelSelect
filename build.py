#!/usr/bin/env python3
"""
Cross-platform build script for Claude Model Manager
"""

import os
import sys
import subprocess
import platform
import shutil

def clean_build_artifacts():
    """Clean up build and dist directories"""
    print("🧹 Cleaning up build artifacts...")
    dirs_to_clean = ['build', 'dist']
    for d in dirs_to_clean:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                print(f"   Removed {d}/")
            except Exception as e:
                print(f"   Failed to remove {d}/: {e}")

def build_windows():
    """Build for Windows"""
    print("🪟 Starting Windows build...")
    try:
        # Use PyInstaller with the Windows spec file
        subprocess.check_call(['pyinstaller', '--clean', '--noconfirm', 'build_windows.spec'])
        print("✅ Windows build completed successfully!")
        print("   Executable is located at: dist/ClaudeModelManager.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Windows build failed: {e}")
        sys.exit(1)

def build_macos():
    """Build for macOS"""
    print("🍎 Starting macOS build...")
    try:
        # Use PyInstaller with the macOS spec file
        subprocess.check_call(['pyinstaller', '--clean', '--noconfirm', 'build_macos.spec'])
        print("✅ macOS build completed successfully!")
        print("   App bundle is located at: dist/ClaudeModelManager.app")
        
        # Optional: Check for create-dmg
        if shutil.which('create-dmg'):
            print("\n📦 Found create-dmg, creating disk image...")
            dmg_name = "ClaudeModelManager.dmg"
            if os.path.exists(dmg_name):
                os.remove(dmg_name)
                
            cmd = [
                'create-dmg',
                '--volname', 'ClaudeModelManager',
                '--window-pos', '200', '120',
                '--window-size', '800', '400',
                '--icon-size', '100',
                '--icon', 'ClaudeModelManager.app', '200', '190',
                '--hide-extension', 'ClaudeModelManager.app',
                '--app-drop-link', '600', '185',
                dmg_name,
                'dist/ClaudeModelManager.app'
            ]
            try:
                subprocess.check_call(cmd)
                print(f"✅ DMG created successfully: {dmg_name}")
            except subprocess.CalledProcessError:
                print("⚠️ Failed to create DMG (but the .app is fine)")
        else:
            print("\nℹ️ create-dmg not found. Skipping DMG creation.")
            print("   To enable DMG creation: brew install create-dmg")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ macOS build failed: {e}")
        sys.exit(1)

def main():
    """Main build entry point"""
    # Ensure we're in the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    clean_build_artifacts()
    
    system = platform.system().lower()
    
    if system == 'windows':
        build_windows()
    elif system == 'darwin':
        build_macos()
    else:
        print(f"⚠️ Unsupported platform: {system}")
        print("   Attempting Linux build (using Windows spec as base)...")
        # Linux usually works with similar settings to Windows (one-file) or Mac (one-dir)
        # We'll default to the Windows spec (one-file) for simplicity on Linux
        try:
            subprocess.check_call(['pyinstaller', '--clean', '--noconfirm', 'build_windows.spec'])
            print("✅ Linux build completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Linux build failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
