#!/usr/bin/env python3
"""
SQLite-Sync Tutorial Demo

Automated demonstration of basic sync concepts.

Usage:
    python demo.py
    python demo.py --with-cloud "your-connection-string" "your-api-key"
"""

import argparse
import time
from sync import SyncClient


def tutorial_demo(use_cloud=False, connection_string=None, api_key=None):
    """Simple demo showing SQLite-Sync basics."""
    print("🎯 SQLite-Sync Tutorial Demo")
    print("=" * 40)
    
    # Create two devices
    device_a = SyncClient("device-a")  
    device_b = SyncClient("device-b")
    
    try:
        # Setup cloud if requested
        if use_cloud and connection_string and api_key:
            print("\n☁️  Setting up cloud sync...")
            if device_a.setup_cloud(connection_string, api_key):
                device_b.setup_cloud(connection_string, api_key)
                print("✅ Both devices connected to cloud")
            else:
                print("❌ Cloud setup failed - continuing in local mode")
                use_cloud = False
        
        # Device A adds todos
        print("\n📱 Device A adding todos...")
        device_a.add_todo("Learn SQLite-Sync")
        device_a.add_todo("Build awesome app")
        device_a.list_todos()
        
        if use_cloud:
            print("\n🔄 Device A syncing to cloud...")
            device_a.sync()
            time.sleep(1)
        
        # Device B syncs
        print("\n📱 Device B checking for todos...")
        if use_cloud:
            device_b.sync()
            time.sleep(1)
            
        device_b.list_todos()
        
        # Device B adds todo
        print("\n📱 Device B adding a todo...")
        device_b.add_todo("Review sync demo")
        
        if use_cloud:
            device_b.sync()
            time.sleep(1)
            
            print("\n📱 Device A syncing again...")
            device_a.sync()
            device_a.list_todos()
        
        print("\n✨ Demo complete!")
        if use_cloud:
            print("🎉 Both devices now have the same todos!")
        else:
            print("💡 Try with --with-cloud to see real sync!")
    
    finally:
        device_a.close()
        device_b.close()


def main():
    """Run the tutorial demo."""
    parser = argparse.ArgumentParser(
        description="SQLite-Sync Tutorial Demo",
        epilog="""
Examples:
  python demo.py                                    # Local-only demo
  python demo.py --with-cloud "cloud-url" "api-key" # Real sync demo
        """
    )
    
    parser.add_argument('--with-cloud', nargs=2, metavar=('URL', 'KEY'),
                        help='Enable cloud sync with connection string and API key')
    
    args = parser.parse_args()
    
    try:
        if args.with_cloud:
            tutorial_demo(True, args.with_cloud[0], args.with_cloud[1])
        else:
            tutorial_demo(False)
    
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


if __name__ == '__main__':
    main()