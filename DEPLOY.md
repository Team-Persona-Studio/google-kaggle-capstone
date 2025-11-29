# Deployment Guide for Hugging Face Spaces

This guide explains how to deploy the Character AI application to Hugging Face Spaces (completely free, no credit card required).

## Prerequisites
- A [Hugging Face](https://huggingface.co/join) account
- A [TiDB Cloud](https://tidbcloud.com) account (free tier)
- A [Google AI Studio](https://aistudio.google.com/) API Key (free)

## Step 1: Database Setup (TiDB)

1. Log in to TiDB Cloud and create a free Serverless Cluster
2. Note down your connection details:
   - Host
   - Port (usually 4000)
   - Username
   - Password
   - Database name

3. Run the SQL initialization:
   - Connect to your TiDB cluster (using CLI or web SQL editor)
   - Execute the contents of `Backend/create.sql`
   - This creates the required tables: `users`, `persona_flow`, `persona_messages`

## Step 2: Create Organization (Recommended)

For a professional URL, create a Hugging Face Organization:

1. Go to [https://huggingface.co/organizations/new](https://huggingface.co/organizations/new)
2. Choose a name (e.g., `Team-Persona-Studio`)
3. Click **Create Organization**

## Step 3: Deploy Backend

1. **Create Backend Space:**
   - Go to [Hugging Face Spaces](https://huggingface.co/spaces/new)
   - Owner: Select your Organization
   - Space name: `character-ai-backend`
   - SDK: **Docker** (Blank)
   - Visibility: Public or Private
   - Click **Create Space**

2. **Upload Backend Files:**
   - Clone the Space: `git clone https://huggingface.co/spaces/YOUR-ORG/character-ai-backend`
   - Copy all files from `Backend/` folder into the cloned repository
   - Commit and push:
     ```bash
     cd character-ai-backend
     git add .
     git commit -m "Deploy backend"
     git push
     ```

3. **Set Environment Variables:**
   - Go to Space **Settings** → **Variables and secrets**
   - Add these **Secrets**:
     - `DB_HOST` - Your TiDB host
     - `DB_USER` - Your TiDB username
     - `DB_PASSWORD` - Your TiDB password
     - `DB_NAME` - Your database name
     - `DB_PORT` - `4000`
     - `GOOGLE_API_KEY` - Your Gemini API key

4. **Verify Backend:**
   - Wait for build to complete
   - Visit the Space URL
   - You should see: `{"message": "Character AI Backend is running"}`
   - Copy the backend URL (e.g., `https://your-org-character-ai-backend.hf.space`)

## Step 4: Deploy Frontend

1. **Create Frontend Space:**
   - Create another Space in your Organization
   - Space name: `character-ai-frontend`
   - SDK: **Docker** (Blank)

2. **Upload Frontend Files:**
   - Clone: `git clone https://huggingface.co/spaces/YOUR-ORG/character-ai-frontend`
   - Copy all files from `frontend/` folder
   - Commit and push:
     ```bash
     cd character-ai-frontend
     git add .
     git commit -m "Deploy frontend"
     git push
     ```

3. **Set Backend URL:**
   - Go to Space **Settings** → **Variables and secrets**
   - Add Variable:
     - `BACKEND_URL` - Your backend Space URL (no trailing slash)
     - Example: `https://your-org-character-ai-backend.hf.space`

4. **Verify Frontend:**
   - Wait for build to complete
   - Visit the Space URL
   - You should see the login/register page

## Step 5: Test the Application

1. Register a new user
2. Create a persona (character)
3. Start chatting!

## Troubleshooting

### Backend Issues
- **Database Connection Error**: Verify all DB credentials in Secrets
- **SSL Error**: Ensure `isrgrootx1.pem` is in the Backend folder
- **500 Error**: Check container logs in the Space

### Frontend Issues
- **Connection Refused**: Verify `BACKEND_URL` is set correctly
- **App won't start**: Check container logs for Python errors
- **Stuck on "Starting"**: Try Factory Rebuild in Settings

### General Tips
- Use **Factory Rebuild** if changes don't appear
- Check **Container logs** for detailed error messages
- Ensure both Spaces are in the same Organization for easier management

## Your Shareable Link

Once deployed, share this link with your team:
`https://huggingface.co/spaces/YOUR-ORG/character-ai-frontend`

Or the direct app link:
`https://your-org-character-ai-frontend.hf.space`
