"""
Custom font registration for Phoenix CRM
"""
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
import os

# Get the directory where fonts are stored
FONTS_DIR = os.path.dirname(os.path.abspath(__file__))
resource_add_path(FONTS_DIR)

print(f"\n📁 Font directory: {FONTS_DIR}")

# List all files in the fonts directory
try:
    if os.path.exists(FONTS_DIR):
        all_files = os.listdir(FONTS_DIR)
        font_files = [f for f in all_files if f.endswith(('.ttf', '.otf'))]
        print(f"📂 Font files found: {font_files}")
    else:
        print("⚠️  Fonts directory does not exist!")
        font_files = []
except Exception as e:
    print(f"⚠️  Error listing fonts directory: {e}")
    font_files = []

# ALWAYS register the fonts with fallback to avoid crashes
def safe_register_font(name, variants):
    """Safely register a font with fallback to default."""
    registered = False
    
    for regular, bold in variants:
        regular_path = os.path.join(FONTS_DIR, regular)
        bold_path = os.path.join(FONTS_DIR, bold)
        
        if os.path.exists(regular_path):
            try:
                LabelBase.register(
                    name=name,
                    fn_regular=regular_path,
                    fn_bold=bold_path if os.path.exists(bold_path) else regular_path,
                )
                print(f"✅ {name} registered: {regular}")
                registered = True
                return True
            except Exception as e:
                print(f"⚠️  Error registering {regular}: {e}")
    
    # If no variant worked, use default font
    if not registered:
        try:
            print(f"⚠️  {name} not found, registering with system default font")
            # Just don't register it - let Kivy use the default
            # This avoids the "File not found" error
            return False
        except Exception as e:
            print(f"⚠️  Error with fallback: {e}")
            return False

# Try to register Cormorant Garamond
cormorant_variants = [
    ('CormorantGaramond-Regular.ttf', 'CormorantGaramond-Bold.ttf'),
    ('CormorantGaramond-SemiBold.ttf', 'CormorantGaramond-Bold.ttf'),
    ('Cormorant_Garamond/CormorantGaramond-Regular.ttf', 'Cormorant_Garamond/CormorantGaramond-Bold.ttf'),
    ('static/CormorantGaramond-Regular.ttf', 'static/CormorantGaramond-Bold.ttf'),
]

cormorant_ok = safe_register_font('CormorantGaramond', cormorant_variants)

# Try to register Inter
inter_variants = [
    ('Inter-Regular.ttf', 'Inter-SemiBold.ttf'),
    ('Inter-Regular.ttf', 'Inter-Bold.ttf'),
    ('Inter/Inter-Regular.ttf', 'Inter/Inter-SemiBold.ttf'),
    ('static/Inter-Regular.ttf', 'static/Inter-SemiBold.ttf'),
]

inter_ok = safe_register_font('Inter', inter_variants)

print("\n💡 Font registration summary:")
print(f"   - CormorantGaramond: {'✅ Custom' if cormorant_ok else '⚠️  Using system default'}")
print(f"   - Inter: {'✅ Custom' if inter_ok else '⚠️  Using system default'}")
print("\n📥 To use custom fonts, download from Google Fonts and place in:")
print(f"   {FONTS_DIR}")
print("   Required files:")
print("   - CormorantGaramond-Regular.ttf")
print("   - CormorantGaramond-Bold.ttf")
print("   - Inter-Regular.ttf")
print("   - Inter-SemiBold.ttf\n")
