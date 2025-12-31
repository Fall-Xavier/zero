from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

#SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_URL = "https://ashxuohxbxinakwajhdz.supabase.co"
#SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzaHh1b2h4YnhpbmFrd2FqaGR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2Njk3MTYsImV4cCI6MjA2MTI0NTcxNn0.x35lYxTNgMEDTGi8sLU1iH15syC4VBDo28fx4yVNsmM"
SUPABASE_BUCKET = "profile_photos"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)