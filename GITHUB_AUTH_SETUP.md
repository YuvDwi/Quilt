# GitHub Authentication Setup Guide

## 🔧 Step 1: Create GitHub OAuth App

1. **Go to GitHub Developer Settings:**
   - Visit: https://github.com/settings/developers
   - Click "New OAuth App"

2. **Fill in the OAuth App details:**
   ```
   Application name: Quilt
   Homepage URL: https://your-frontend-domain.vercel.app
   Authorization callback URL: https://your-frontend-domain.vercel.app/auth/callback
   ```

3. **After creation, note down:**
   - **Client ID** (public, can be in frontend)
   - **Client Secret** (private, backend only)

## 🌐 Step 2: Set Environment Variables

### **For Vercel (Frontend):**
1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add these variables:

```env
NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_oauth_client_id
NEXT_PUBLIC_QUILT_API_URL=https://your-railway-backend.railway.app
```

### **For Railway (Backend):**
1. Go to your Railway project dashboard
2. Navigate to Variables
3. Add these variables:

```env
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_client_secret
PORT=8005
```

## 🔒 Step 3: Security Considerations

### **Important Security Notes:**
- **Never put `GITHUB_CLIENT_SECRET` in frontend code**
- **Use `NEXT_PUBLIC_` prefix only for public variables**
- **Client Secret should only be on your backend/server**

### **Current Setup Analysis:**
Your current auth flow is secure because:
- ✅ Frontend gets auth code from GitHub
- ✅ Frontend exchanges code for token directly with GitHub (this is allowed)
- ✅ Token is only used temporarily and passed to backend
- ✅ No client secret exposed in frontend

## 🚀 Step 4: Update Your Frontend Environment

In your `src/app/page.tsx`, update the GitHub OAuth URL:

```typescript
const handleGitHubLogin = () => {
  setIsLoading(true)
  const clientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID
  const redirectUri = encodeURIComponent(window.location.origin + '/auth/callback')
  const scope = 'repo'
  const state = Math.random().toString(36).substring(7)
  
  window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}&state=${state}`
}
```

## ✅ Step 5: Test the Flow

1. **Deploy your changes** to both Vercel and Railway
2. **Visit your frontend** 
3. **Click "Get Started for Free"**
4. **Authorize with GitHub**
5. **Should redirect to dashboard** with your repositories

## 🔧 Step 6: Backend OAuth Token Exchange (Alternative)

If you want to move token exchange to backend for extra security:

1. **Update frontend** to send auth code to your backend
2. **Backend exchanges code** for token using client secret
3. **Backend returns user data** and stores token securely

Your current setup works fine, but this would be more secure for production.

## 🎯 Current Flow Summary

1. User clicks "Get Started for Free"
2. Redirects to GitHub OAuth
3. User authorizes your app
4. GitHub redirects to `/auth/callback` with auth code
5. Frontend exchanges code for access token
6. Frontend gets user info from GitHub API
7. Redirects to dashboard with token and user info
8. Dashboard fetches user repositories
9. User can deploy repositories to Quilt

## 🚀 You're Ready!

Your authentication system is already well-built! Just:
1. Create the GitHub OAuth app
2. Set the environment variables  
3. Deploy and test

The flow will work seamlessly with your existing dashboard and deployment system.
