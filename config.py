# Configuration file for Momentum Tracker
import os

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'your_supabase_url_here')
SUPABASE_SERVICE_ROLE_KEY = (
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    or os.getenv('SUPABASE_KEY')
    or 'your_supabase_service_role_key_here'
)
SUPABASE_KEY = SUPABASE_SERVICE_ROLE_KEY
