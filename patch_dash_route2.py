import re

with open('app/routes/inspector.py', 'r') as f:
    content = f.read()

new_supa_update = """                        supabase.table('verification_sessions').update({
                            'cert_number': cert_number,
                            'pdf_hash': pdf_hash,
                            'overall_status': overall_status,
                            'completed_at': completed_at
                        }).eq('id', session_id).execute()"""

better_supa_update = """                        from datetime import datetime, timezone
                        supabase.table('verification_sessions').update({
                            'cert_number': cert_number,
                            'pdf_hash': pdf_hash,
                            'overall_status': overall_status,
                            'completed_at': datetime.now(timezone.utc).isoformat()
                        }).eq('id', session_id).execute()"""

content = content.replace(new_supa_update, better_supa_update)

with open('app/routes/inspector.py', 'w') as f:
    f.write(content)
