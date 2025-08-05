#!/bin/bash
# SQLite-AI Tutorial Setup Script
# Sets up everything needed for the AI tutorial demonstration

echo "🚀 Setting up SQLite-AI Tutorial Environment"
echo "============================================="

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

# Function to download SQLite-AI extension
download_extension() {
    echo ""
    echo "📦 SQLite-AI Extension Setup"
    echo "============================="
    
    # Check if extension already exists
    if [[ -f "sqlite-ai.so" || -f "sqlite-ai.dylib" || -f "sqlite-ai.dll" ]]; then
        echo "✅ SQLite-AI extension already exists"
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
        read -p "📥 Download SQLite-AI extension for this platform? (Y/n): " confirm
        confirm=${confirm:-Y}
        
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            echo "⏭️  Skipping extension download"
            return 0
        fi
    fi
    
    local extension=$(get_extension "$platform")
    
    echo "📡 Getting latest release information..."
    
    # Get the latest release info from GitHub API
    local api_url="https://api.github.com/repos/sqliteai/sqlite-ai/releases/latest"
    local release_info
    
    if ! release_info=$(curl -s "$api_url"); then
        echo "❌ Failed to fetch release information"
        echo "💡 You can manually download from: https://github.com/sqliteai/sqlite-ai/releases"
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
    local download_url="https://github.com/sqliteai/sqlite-ai/releases/download/${version}/sqlite-ai-${platform}-${version}.zip"
    local zip_filename="sqlite-ai-${platform}-${version}.zip"
    
    echo "📥 Downloading SQLite-AI extension..."
    echo "   URL: $download_url"
    
    if curl -L -o "$zip_filename" "$download_url"; then
        echo "✅ Downloaded: $zip_filename"
        
        # Extract the zip file
        echo "📂 Extracting extension..."
        if unzip -q "$zip_filename"; then
            echo "✅ Extracted successfully"
            
            # Find the extension file and rename it to the expected name
            local found_extension=""
            local target_filename="sqlite-ai.$extension"
            
            # Look for the extension file in common locations
            if [[ -f "sqlite-ai.$extension" ]]; then
                found_extension="sqlite-ai.$extension"
                echo "🔍 Found: sqlite-ai.$extension"
            elif [[ -f "libsqlite-ai.$extension" ]]; then
                found_extension="libsqlite-ai.$extension"
                echo "🔍 Found: libsqlite-ai.$extension"
            else
                # Search recursively for the extension file
                found_extension=$(find . -name "*sqlite-ai*.$extension" -type f | head -1)
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
                rm -rf sqlite-ai-${platform}-${version} 2>/dev/null || true
                
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

# Function to download models from Hugging Face
download_sample_models() {
    echo ""
    echo "🧠 Sample AI Models Setup"
    echo "========================="
    
    # Create models directory
    mkdir -p models/
    
    read -p "📥 Download sample AI models from Hugging Face? (y/N): " download_models
    download_models=${download_models:-N}
    
    if [[ ! "$download_models" =~ ^[Yy]$ ]]; then
        echo "⏭️  Skipping model download"
        echo "💡 You can add your own GGUF models to the ./models/ directory"
        echo "💡 Visit https://huggingface.co/models?library=ggml for more models"
        return 0
    fi
    
    echo "📡 Available models from Hugging Face:"
    echo "1) TinyLlama 1.1B Chat (Fast, good for testing) - ~637MB"
    echo "2) Phi-3.5 Mini Instruct (High quality, compact) - ~2.2GB"
    echo "3) Qwen2.5 0.5B Instruct (Very fast, tiny) - ~394MB"
    echo "4) Skip model download"
    
    while true; do
        read -p "Select a model to download (1-4): " model_choice
        case $model_choice in
            1)
                download_tinyllama
                break
                ;;
            2)
                download_phi3_mini
                break
                ;;
            3)
                download_qwen_mini
                break
                ;;
            4)
                echo "⏭️  Skipping model download"
                break
                ;;
            *)
                echo "❌ Invalid choice. Please enter 1-4."
                ;;
        esac
    done
}

# Function to download TinyLlama from Hugging Face
download_tinyllama() {
    local model_name="TinyLlama-1.1B-Chat-v1.0"
    local filename="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    local url="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/${filename}"
    local output_path="models/${filename}"
    
    echo "🔄 Downloading TinyLlama 1.1B Chat..."
    echo "   Source: ${url}"
    echo "   Size: ~637MB"
    echo "   This may take a few minutes..."
    
    # Check if file already exists
    if [[ -f "$output_path" ]]; then
        echo "✅ TinyLlama model already exists: ${filename}"
        return 0
    fi
    
    if curl -L --progress-bar --fail -o "$output_path" "$url"; then
        echo "✅ TinyLlama model downloaded: ${filename}"
        echo "🧠 Model ready for chat and text generation"
        
        # Verify file size (should be around 637MB)
        local file_size=$(stat -f%z "$output_path" 2>/dev/null || stat -c%s "$output_path" 2>/dev/null)
        if [[ -n "$file_size" && "$file_size" -gt 600000000 ]]; then
            echo "✅ File size verification passed"
        else
            echo "⚠️  Downloaded file seems smaller than expected - may be incomplete"
        fi
    else
        echo "❌ Failed to download TinyLlama model"
        echo "💡 You can manually download from: $url"
        rm -f "$output_path"  # Clean up partial download
    fi
}

# Function to download Phi-3.5 Mini from Hugging Face
download_phi3_mini() {
    local model_name="Phi-3.5-mini-instruct"
    local filename="Phi-3.5-mini-instruct-Q4_K_M.gguf"
    local url="https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/${filename}"
    local output_path="models/${filename}"
    
    echo "🔄 Downloading Phi-3.5 Mini Instruct..."
    echo "   Source: ${url}"
    echo "   Size: ~2.2GB"
    echo "   This may take 10-15 minutes..."
    
    # Check if file already exists
    if [[ -f "$output_path" ]]; then
        echo "✅ Phi-3.5 Mini model already exists: ${filename}"
        return 0
    fi
    
    if curl -L --progress-bar --fail -o "$output_path" "$url"; then
        echo "✅ Phi-3.5 Mini model downloaded: ${filename}"
        echo "🧠 High-quality model ready for advanced tasks"
        
        # Verify file size (should be around 2.2GB)
        local file_size=$(stat -f%z "$output_path" 2>/dev/null || stat -c%s "$output_path" 2>/dev/null)
        if [[ -n "$file_size" && "$file_size" -gt 2000000000 ]]; then
            echo "✅ File size verification passed"
        else
            echo "⚠️  Downloaded file seems smaller than expected - may be incomplete"
        fi
    else
        echo "❌ Failed to download Phi-3.5 Mini model"
        echo "💡 You can manually download from: $url"
        rm -f "$output_path"  # Clean up partial download
    fi
}

# Function to download Qwen2.5 0.5B from Hugging Face
download_qwen_mini() {
    local model_name="Qwen2.5-0.5B-Instruct"
    local filename="qwen2.5-0.5b-instruct-q4_k_m.gguf"
    local url="https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/${filename}"
    local output_path="models/${filename}"
    
    echo "🔄 Downloading Qwen2.5 0.5B Instruct..."
    echo "   Source: ${url}"
    echo "   Size: ~394MB"
    echo "   This may take a few minutes..."
    
    # Check if file already exists
    if [[ -f "$output_path" ]]; then
        echo "✅ Qwen2.5 0.5B model already exists: ${filename}"
        return 0
    fi
    
    if curl -L --progress-bar --fail -o "$output_path" "$url"; then
        echo "✅ Qwen2.5 0.5B model downloaded: ${filename}"
        echo "🧠 Ultra-fast model ready for quick responses"
        
        # Verify file size (should be around 394MB)
        local file_size=$(stat -f%z "$output_path" 2>/dev/null || stat -c%s "$output_path" 2>/dev/null)
        if [[ -n "$file_size" && "$file_size" -gt 350000000 ]]; then
            echo "✅ File size verification passed"
        else
            echo "⚠️  Downloaded file seems smaller than expected - may be incomplete"
        fi
    else
        echo "❌ Failed to download Qwen2.5 model"
        echo "💡 You can manually download from: $url"
        rm -f "$output_path"  # Clean up partial download
    fi
}

# Download SQLite-AI extension
download_extension

# Download sample models
download_sample_models

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
mkdir -p data/

echo ""
echo "✅ Setup complete!"
echo ""

# Check if extension was downloaded
extension_status=""
if [[ -f "sqlite-ai.so" || -f "sqlite-ai.dylib" || -f "sqlite-ai.dll" ]]; then
    extension_status="🤖 SQLite-AI extension: Ready for AI magic!"
else
    extension_status="📱 SQLite-AI extension: Not installed (demo mode)"
fi

echo "$extension_status"

# Check for models
model_count=$(find models/ -name "*.gguf" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$model_count" -gt 0 ]]; then
    echo "🧠 AI Models: $model_count model(s) available"
else
    echo "🧠 AI Models: No models installed (add to ./models/ directory)"
fi

echo ""
echo "🎯 To start the tutorial:"
echo "   source venv/bin/activate"
echo "   python ai.py --client-id my-app --interactive"
echo ""
echo "💡 With a model:"
if [[ -f "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf" ]]; then
    echo "   python ai.py --client-id chatbot --model-path ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --interactive"
elif [[ -f "models/qwen2.5-0.5b-instruct-q4_k_m.gguf" ]]; then
    echo "   python ai.py --client-id chatbot --model-path ./models/qwen2.5-0.5b-instruct-q4_k_m.gguf --interactive"
elif [[ -f "models/Phi-3.5-mini-instruct-Q4_K_M.gguf" ]]; then
    echo "   python ai.py --client-id chatbot --model-path ./models/Phi-3.5-mini-instruct-Q4_K_M.gguf --interactive"
else
    first_model=$(find models/ -name "*.gguf" -exec basename {} \; 2>/dev/null | head -1)
    if [[ -n "$first_model" ]]; then  
        echo "   python ai.py --client-id chatbot --model-path ./models/$first_model --interactive"
    else
        echo "   python ai.py --client-id chatbot --model-path ./models/your-model.gguf --interactive"
    fi
fi
echo ""
if [[ -f "sqlite-ai.so" || -f "sqlite-ai.dylib" || -f "sqlite-ai.dll" ]]; then
    echo "🌟 Ready for intelligent database applications!"
else
    echo "🌟 Ready to learn AI concepts in demo mode!"
    echo "💡 Re-run ./setup.sh to download the extension later"
fi