"""
Test script to demonstrate Step 2: Combined JSON configuration
This simulates the component configuration data and tests the combined JSON creation
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_combined_config():
    """Test the combined configuration functionality"""
    
    # Simulate test configuration data (what we get from the form)
    test_config = {
        'filename': 'youtube_focus_test',
        'url': 'https://www.youtube.com',
        'duration': '3',
        'created_at': datetime.now().isoformat(),
        'config_version': '1.0'
    }
    
    # Simulate component configuration data (what we get from browser element ranking)
    component_config = {
        'origin': 'https://www.youtube.com',
        'path': '/',
        'ranks': {
            '1': [
                {'selector': '#content-wrapper', 'tag': 'div'},
                {'selector': '.search-box', 'tag': 'input'}
            ],
            '2': [
                {'selector': '#guide-inner-content', 'tag': 'div'}
            ],
            '3': [
                {'selector': '.ytd-topbar-logo-renderer', 'tag': 'div'}
            ]
        },
        'saved_at': 1759037337426,
        'url': 'https://www.youtube.com/',
        'version': 1
    }
    
    # Create combined configuration (Step 2 implementation)
    combined_config = {
        'test_metadata': {
            'created_at': test_config['created_at'],
            'config_version': test_config['config_version'],
            'combined_config': True
        },
        'test_parameters': {
            'filename': test_config['filename'],
            'url': test_config['url'],
            'duration': test_config['duration']
        },
        'component_configuration': component_config,
        'file_structure': {
            'test_config_file': f"{test_config['filename']}_config.json",
            'component_config_file': f"{test_config['filename']}_components.json",
            'combined_config_file': f"{test_config['filename']}_combined.json"
        }
    }
    
    # Save to desktop for testing
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    if not os.path.exists(desktop_path):
        desktop_path = os.path.expanduser('~')  # Fallback to home directory
    
    # Save individual files
    test_file = os.path.join(desktop_path, f"{test_config['filename']}_config.json")
    component_file = os.path.join(desktop_path, f"{test_config['filename']}_components.json")
    combined_file = os.path.join(desktop_path, f"{test_config['filename']}_combined.json")
    
    try:
        # Save test config
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Test config saved: {test_file}")
        
        # Save component config
        with open(component_file, 'w', encoding='utf-8') as f:
            json.dump(component_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Component config saved: {component_file}")
        
        # Save combined config
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(combined_config, f, indent=2, ensure_ascii=False)
        print(f"🔗 Combined config saved: {combined_file}")
        
        print("\n" + "="*60)
        print("📋 STEP 2 DEMONSTRATION - COMBINED JSON STRUCTURE")
        print("="*60)
        
        print("\n🎯 Test Parameters:")
        for key, value in test_config.items():
            print(f"  • {key}: {value}")
            
        print("\n🎯 Component Configuration:")
        print(f"  • Origin: {component_config['origin']}")
        print(f"  • Total ranks: {len(component_config['ranks'])}")
        for rank, elements in component_config['ranks'].items():
            print(f"  • Rank {rank}: {len(elements)} elements")
            
        print("\n🎯 File Structure Created:")
        print(f"  • {os.path.basename(test_file)} (test parameters)")
        print(f"  • {os.path.basename(component_file)} (component config)")  
        print(f"  • {os.path.basename(combined_file)} (COMBINED - ready for use)")
        
        print("\n✅ Step 2 Complete: JSON merging and file structure working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test files: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Step 2: Component Config JSON Merging")
    test_combined_config()