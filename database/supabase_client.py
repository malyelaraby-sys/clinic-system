from supabase import create_client

# ✅ Your Supabase project URL
SUPABASE_URL = "https://jshtdemzdkrwmvsxuvln.supabase.co"

# ✅ Your publishable (anon) key
SUPABASE_KEY = "sb_publishable_LX4ts31q1i69mOLHwCyTrg_-4sX-HRE"

# ✅ Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)