import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
res = supabase.table('verification_sessions').select('*').limit(1).execute()
print("verification_sessions columns:", list(res.data[0].keys()) if res.data else "No rows to infer columns")
