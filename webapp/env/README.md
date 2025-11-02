# Environment Variables Configuration

This folder contains all environment variable files for the ArtEvoke application.

## 🚀 Quick Setup

### Step 1: Create Environment Files

Create the actual environment files by copying the example files:

```bash
cd /home/augustovillar/ArtEvoke/webapp/env

# Copy all example files to actual env files
cp .backend.env.example .backend.env
cp .mysql.env.example .mysql.env
cp .phpmyadmin.env.example .phpmyadmin.env
cp .nginx.env.example .nginx.env
```

### Step 2: Update Values

Edit each file with your actual credentials:

```bash
nano .mysql.env        # Database credentials
nano .backend.env      # Backend/API configuration
nano .phpmyadmin.env   # PHPMyAdmin access
nano .nginx.env        # Nginx configuration
```

### Step 3: Restart Services

```bash
cd /home/augustovillar/ArtEvoke/webapp
docker-compose down
docker-compose up -d
```

---

## 📁 File Descriptions

### `.backend.env`
Backend (FastAPI) configuration including:
- Database connection settings
- Qdrant vector database settings
- API configuration
- Security keys
- OpenAI/LLM API keys
- CORS settings

### `.mysql.env`
MySQL database configuration:
- Root password
- Database name
- Application user credentials
- Character set and collation

### `.phpmyadmin.env`
PHPMyAdmin configuration:
- Database connection details
- Authentication credentials
- Upload and memory limits

### `.nginx.env`
Nginx configuration:
- Configuration file selection (local vs prod)
- Domain settings

---

## 🔒 Security Notes

1. **NEVER commit actual .env files to git**
   - Only `.example` files should be in version control
   - Actual env files (without `.example`) are in `.gitignore`

2. **Change all default passwords**
   - All example files contain placeholder passwords
   - Update them before deploying to production

3. **Protect your API keys**
   - Keep OpenAI and other API keys secure
   - Rotate them regularly

4. **Use strong passwords**
   - Use at least 16 characters
   - Mix uppercase, lowercase, numbers, and symbols
   - Example: `MyS3cur3P@ssw0rd!2024`

---

## 🔄 Synchronization - CRITICAL!

**⚠️ IMPORTANT:** These values MUST match across multiple files or your application will not work!

| Value | Files That Must Match |
|-------|----------------------|
| **Database Name** | `.mysql.env` (`MYSQL_DATABASE`) = `.backend.env` (`DB_NAME`) |
| **Database User** | `.mysql.env` (`MYSQL_USER`) = `.backend.env` (`DB_USER`) = `.phpmyadmin.env` (`PMA_USER`) |
| **Database Password** | `.mysql.env` (`MYSQL_PASSWORD`) = `.backend.env` (`DB_PASSWORD`) = `.phpmyadmin.env` (`PMA_PASSWORD`) |

### Quick Reference:
- **Database Name**: `artevoke` (must be the same in `.mysql.env` and `.backend.env`)
- **Database User**: `appuser` (must be the same in `.mysql.env`, `.backend.env`, and `.phpmyadmin.env`)
- **Database Password**: `changeme_app` (must be the same in `.mysql.env`, `.backend.env`, and `.phpmyadmin.env`)

**💡 Tip:** When updating passwords, update all three files at the same time!

---

## ✅ Verification

After setup, verify your configuration:

```bash
# Check if env files exist
ls -la /home/augustovillar/ArtEvoke/webapp/env/.*.env

# Verify docker-compose can read them
cd /home/augustovillar/ArtEvoke/webapp
docker-compose config

# Check services are running
docker-compose ps
```

---

## 📋 Checklist

Before deploying to production:

- [ ] All `.example` files copied to actual `.env` files
- [ ] All default passwords changed
- [ ] MySQL root password updated
- [ ] MySQL application user password updated
- [ ] Backend SECRET_KEY generated (use: `openssl rand -hex 32`)
- [ ] API keys configured (OpenAI, etc.)
- [ ] CORS origins updated for your domain
- [ ] Nginx configuration set correctly (local vs prod)
- [ ] Database credentials synchronized across files
- [ ] PHPMyAdmin credentials match MySQL user
- [ ] All services restart successfully

---

## 🆘 Troubleshooting

### "Error: .env file not found"
```bash
# Make sure you copied the example files
cd /home/augustovillar/ArtEvoke/webapp/env
cp .backend.env.example .backend.env
# ... repeat for other files
```

### "Connection refused" errors
- Check that database credentials match in `.mysql.env` and `.backend.env`
- Ensure services are running: `docker-compose ps`

### "Authentication failed"
- Verify passwords match across configuration files
- Check for extra spaces or special characters in passwords

---

## 🔐 Password Generation

Generate secure passwords:

```bash
# Generate a secure random password
openssl rand -base64 32

# Generate a hex secret key (for SECRET_KEY)
openssl rand -hex 32
```

---

**Last Updated**: November 2, 2025

