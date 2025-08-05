#!/bin/bash
# SQLite-Sync Tutorial Setup Script
# Sets up everything needed for the tutorial demonstration

echo "🚀 Setting up SQLite-Sync Tutorial Environment"
echo "=============================================="

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo "❌ curl is required but not installed"
    exit 1
fi

# Check if unzip is available
if ! command -v unzip &> /dev/null; then
    echo "❌ unzip is required but not installed"
    exit 1
fi

# Function to detect platform
detect_platform() {
    local os=$(uname -s)
    local arch=$(uname -m)
    
    case "$os" in
        "Darwin")
            echo "macos"  # macOS releases are universal
            ;;
        "Linux")
            case "$arch" in
                "x86_64") echo "linux-x86_64" ;;
                "aarch64"|"arm64") echo "linux-arm64" ;;
                *) echo "unknown" ;;
            esac
            ;;
        "MINGW"*|"MSYS"*|"CYGWIN"*)
            echo "windows-x86_64"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Function to get file extension for platform
get_extension() {
    local platform=$1
    case "$platform" in
        macos-*) echo "dylib" ;;
        linux-*) echo "so" ;;
        windows-*) echo "dll" ;;
        *) echo "so" ;;
    esac
}

# Function to download SQLite-Sync extension
download_extension() {
    echo ""
    echo "📦 SQLite-Sync Extension Setup"
    echo "==============================="
    
    # Check if extension already exists
    if [[ -f "cloudsync.so" || -f "cloudsync.dylib" || -f "cloudsync.dll" ]]; then
        echo "✅ SQLite-Sync extension already exists"
        return 0
    fi
    
    local detected_platform=$(detect_platform)
    local platform=""
    
    if [[ "$detected_platform" == "unknown" ]]; then
        echo "❓ Unable to auto-detect your platform."
        echo "Please select your platform:"
        echo "1) macOS (Universal)"
        echo "2) Linux x86_64"
        echo "3) Linux ARM64"
        echo "4) Windows x86_64"
        echo "5) Skip extension download"
        
        while true; do
            read -p "Enter your choice (1-5): " choice
            case $choice in
                1) platform="macos"; break ;;
                2) platform="linux-x86_64"; break ;;
                3) platform="linux-arm64"; break ;;
                4) platform="windows-x86_64"; break ;;
                5) echo "⏭️  Skipping extension download"; return 0 ;;
                *) echo "❌ Invalid choice. Please enter 1-5." ;;
            esac
        done
    else
        platform="$detected_platform"
        echo "🔍 Detected platform: $platform"
        read -p "📥 Download SQLite-Sync extension for this platform? (Y/n): " confirm
        confirm=${confirm:-Y}
        
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            echo "⏭️  Skipping extension download"
            return 0
        fi
    fi
    
    local extension=$(get_extension "$platform")
    
    echo "📡 Getting latest release information..."
    
    # Get the latest release info from GitHub API
    local api_url="https://api.github.com/repos/sqliteai/sqlite-sync/releases/latest"
    local release_info
    
    if ! release_info=$(curl -s "$api_url"); then
        echo "❌ Failed to fetch release information"
        echo "💡 You can manually download from: https://github.com/sqliteai/sqlite-sync/releases"
        return 1
    fi
    
    # Extract the version from the release info
    local version
    version=$(echo "$release_info" | grep -o '"tag_name": "[^"]*"' | sed 's/"tag_name": "//; s/"//')
    
    if [[ -z "$version" ]]; then
        echo "❌ Could not extract version information"
        return 1
    fi
    
    echo "📦 Latest version: $version"
    
    # Construct download URL for the zip file
    local download_url="https://github.com/sqliteai/sqlite-sync/releases/download/${version}/cloudsync-${platform}-${version}.zip"
    local zip_filename="cloudsync-${platform}-${version}.zip"
    
    echo "📥 Downloading SQLite-Sync extension..."
    echo "   URL: $download_url"
    
    if curl -L -o "$zip_filename" "$download_url"; then
        echo "✅ Downloaded: $zip_filename"
        
        # Extract the zip file
        echo "📂 Extracting extension..."
        if unzip -q "$zip_filename"; then
            echo "✅ Extracted successfully"
            
            # Find the extension file and rename it to the expected name
            local found_extension=""
            local target_filename="cloudsync.$extension"
            
            # Look for the extension file in common locations
            if [[ -f "cloudsync.$extension" ]]; then
                found_extension="cloudsync.$extension"
                echo "🔍 Found: cloudsync.$extension"
            elif [[ -f "libcloudsync.$extension" ]]; then
                found_extension="libcloudsync.$extension"
                echo "🔍 Found: libcloudsync.$extension"
            else
                # Search recursively for the extension file
                found_extension=$(find . -name "*cloudsync*.$extension" -type f | head -1)
                if [[ -n "$found_extension" ]]; then
                    echo "🔍 Found: $found_extension"
                fi
            fi
            
            if [[ -n "$found_extension" && -f "$found_extension" ]]; then
                # Move/rename to expected location
                if [[ "$found_extension" != "$target_filename" ]]; then
                    mv "$found_extension" "$target_filename"
                fi
                
                # Set executable permissions
                chmod +x "$target_filename"
                
                echo "✅ Extension ready: $target_filename"
                echo "🔍 File permissions: $(ls -la "$target_filename")"
                
                # Clean up
                rm -f "$zip_filename"
                rm -rf cloudsync-${platform}-${version} 2>/dev/null || true
                
                return 0
            else
                echo "❌ Could not find extension file in archive"
                echo "💡 Contents of archive:"
                unzip -l "$zip_filename" | head -20
                rm -f "$zip_filename"
                return 1
            fi
        else
            echo "❌ Failed to extract archive"
            rm -f "$zip_filename"
            return 1
        fi
    else
        echo "❌ Failed to download extension"
        echo "💡 You can manually download from: $download_url"
        return 1
    fi
}

# Download SQLite-Sync extension
download_extension

echo ""
echo "🐍 Python Environment Setup"
echo "============================"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

echo ""
echo "✅ Setup complete!"
echo ""

# Check if extension was downloaded
extension_status=""
if [[ -f "cloudsync.so" || -f "cloudsync.dylib" || -f "cloudsync.dll" ]]; then
    extension_status="🔄 SQLite-Sync extension: Ready for real sync!"
else
    extension_status="📱 SQLite-Sync extension: Not installed (local-only mode)"
fi

echo "$extension_status"
echo ""
echo "🎯 To start the tutorial:"
echo "   source venv/bin/activate"
echo "   python sync.py --client-id device-a --interactive"
echo ""
echo "💡 Open another terminal and run:"
echo "   source venv/bin/activate" 
echo "   python sync.py --client-id device-b --interactive"
echo ""
if [[ -f "cloudsync.so" || -f "cloudsync.dylib" || -f "cloudsync.dll" ]]; then
    echo "🌟 Ready for real multi-device sync!"
else
    echo "🌟 Ready to learn sync concepts in local-only mode!"
    echo "💡 Re-run ./setup.sh to download the extension later"
fi