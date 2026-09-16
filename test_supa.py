from supabase_client import supabase

if supabase:
    try:
        res = supabase.table('instrument_profiles').select('*').limit(1).execute()
        print("Success! Data:", res.data)
    except Exception as e:
        print("Error connecting to Supabase:", str(e))
else:
    print("Supabase client not initialized")
