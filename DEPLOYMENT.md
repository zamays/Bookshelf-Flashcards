# Deployment Guide for Render.com

This guide will walk you through deploying Bookshelf Flashcards to Render.com.

## Prerequisites

- A GitHub account
- A Render.com account (free tier available)
- (Optional) A Google AI Studio API key for AI-generated summaries

## Step-by-Step Deployment

### 1. Fork the Repository

1. Go to https://github.com/zamays/Bookshelf-Flashcards
2. Click the "Fork" button in the top-right corner
3. This creates a copy of the repository in your GitHub account

### 2. Sign Up for Render.com

1. Go to https://render.com
2. Sign up using your GitHub account
3. Authorize Render to access your GitHub repositories

### 3. Create a New Web Service

1. From your Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your forked repository
   - If you don't see your repository, click "Configure GitHub App" to grant access
4. Select your forked `Bookshelf-Flashcards` repository

### 4. Configure Your Service

Render will automatically detect the `render.yaml` configuration file. You can either:

**Option A: Use Blueprint (Recommended)**
- Render will detect `render.yaml` and pre-configure everything
- Click "Apply" to use the blueprint settings

**Option B: Manual Configuration**
- Name: `bookshelf-flashcards` (or your preferred name)
- Runtime: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT web_app:app`

### 5. Set Environment Variables (Optional)

If you want AI-generated summaries:

1. In your web service settings, go to "Environment"
2. Add a new environment variable:
   - Key: `GOOGLE_AI_API_KEY`
   - Value: Your Google AI Studio API key
3. Click "Save Changes"

**How to get a Google AI Studio API key:**
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it into Render

### 6. Deploy

1. Click "Create Web Service" (or "Apply" if using Blueprint)
2. Render will:
   - Build your application
   - Install dependencies
   - Start the web server
3. Wait for the deployment to complete (usually 2-5 minutes)

### 7. Access Your Application

Once deployed, your application will be available at:
```
https://your-service-name.onrender.com
```

You can find the URL in your Render dashboard.

## Post-Deployment

### Testing Your Deployment

1. Visit your application URL
2. Try adding a book manually
3. Test the flashcard mode
4. Upload a file with book titles (use the example_books.txt format)

### Monitoring

- **Health Check**: Visit `https://your-app.onrender.com/health` to check if the app is running
- **Logs**: View logs in the Render dashboard under "Logs"
- **Metrics**: Check performance metrics in the Render dashboard

## Troubleshooting

### Application Won't Start

**Check the logs in Render dashboard:**
- Look for Python import errors
- Verify all dependencies installed correctly
- Check that the start command is correct

### Database Issues

The SQLite database file (`bookshelf.db`) will be stored in the container's filesystem. Note:
- **Free tier**: Database will reset when the service restarts or sleeps
- **Paid tier**: Consider using persistent disk storage for data persistence

To add persistent storage on paid tiers:
1. Go to your web service settings
2. Add a "Disk" under "Disks"
3. Mount path: `/opt/render/project/src`
4. This will persist your database across deployments

### AI Summaries Not Working

1. Verify your `GOOGLE_AI_API_KEY` is set correctly in Environment Variables
2. Check logs for any API errors
3. Ensure your API key has not exceeded quota limits
4. Visit `https://your-app.onrender.com/health` to check if `ai_service` is `true`

### Free Tier Limitations

Render's free tier has some limitations:
- Service spins down after 15 minutes of inactivity
- First request after spin-down will be slow (cold start)
- Database resets when service spins down
- 750 hours per month free (31.25 days)

Consider upgrading to a paid tier for:
- Always-on service (no cold starts)
- Persistent disk storage
- Custom domains
- Better performance

## Updating Your Deployment

When you make changes to your repository:

1. Commit and push changes to your GitHub repository
2. Render will automatically detect the changes
3. If auto-deploy is enabled (default with render.yaml), it will redeploy automatically
4. Otherwise, click "Manual Deploy" → "Deploy latest commit"

## Custom Domain

To use a custom domain:

1. Go to your web service settings
2. Click "Custom Domain"
3. Add your domain name
4. Follow the instructions to configure DNS records
5. Wait for DNS propagation (can take up to 48 hours)

## Security Best Practices

1. **Always set a strong SECRET_KEY**: Set it in environment variables, don't use the default
2. **Protect your API keys**: Never commit API keys to your repository
3. **Enable HTTPS**: Render provides free SSL certificates automatically
4. **Monitor logs**: Regularly check logs for unusual activity
5. **Keep dependencies updated**: Regularly update requirements.txt

## Cost Optimization

### Free Tier Tips
- Use the free tier for personal projects and testing
- Be aware of the 750-hour monthly limit
- Database will reset on spin-down

### Paid Tier Benefits
- Starting at $7/month
- Always-on service (no cold starts)
- Persistent disk storage available
- Better performance and reliability

## Support

- **Render Documentation**: https://render.com/docs
- **GitHub Issues**: Report issues on the repository
- **Render Community**: https://community.render.com

## Alternative Deployment Options

While this guide focuses on Render.com, you can also deploy to:

- **Heroku**: Similar process, use `Procfile` instead
- **Railway**: Auto-detects Flask apps
- **PythonAnywhere**: Good for small Flask apps
- **AWS/Google Cloud/Azure**: More complex but more control
- **DigitalOcean App Platform**: Similar to Render

The Flask application (`web_app.py`) is designed to work on any platform that supports Python web applications.
