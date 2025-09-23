# -----------------------------------------------------------------------------
# ARCHIVO: config.py (VERSIÓN DEFINITIVA)
# -----------------------------------------------------------------------------

# --- Llaves para la conexión con Supabase ---

# Esta es la URL de tu proyecto.
SUPABASE_URL = "https://ylolxyimkrmmcnitebjf.supabase.co"

# Esta es la llave pública (anon key). Se usa en el frontend (JavaScript).
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlsb2x4eWlta3JtbWNuaXRlYmpmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc4MzA2NjUsImV4cCI6MjA3MzQwNjY2NX0.CG8wwCNJKeOIRF7WmFjf6gQtqUx0wgVV-p-1xDUs5rg"

# --- La Llave Maestra (Service Role Key) ---
# Esta es la llave secreta. SOLO se usa en el backend (Python).
# Le da a nuestro servidor permisos de administrador sobre la base de datos.
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlsb2x4eWlta3JtbWNuaXRlYmpmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzgzMDY2NSwiZXhwIjoyMDczNDA2NjY1fQ.JG3TlMSusueywNyZ8qnTIF011sBJMcMp59qMZCDvdjw"