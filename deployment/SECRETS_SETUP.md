# Environment Configuration

For the VM deployment, configuration is done through `.env` files in the `webapp/env/` directory.

## Setup

1. Navigate to the webapp directory on your VM:
   ```bash
   cd ~/artevoke/webapp
   ```

2. Create `.env` files from examples:
   ```bash
   cp env/.backend.env.example env/.backend.env
   cp env/.mysql.env.example env/.mysql.env
   cp env/.nginx.env.example env/.nginx.env  # if exists
   ```

3. Edit the `.env` files with your values:
   ```bash
   nano env/.backend.env
   nano env/.mysql.env
   ```

## Required Configuration

### `env/.backend.env`
```bash
DB_USER=admin
DB_PASSWORD=your_secure_password
DB_HOST=mysql  # Use 'mysql' as hostname (Docker Compose service name)
DB_PORT=3306
DB_NAME=artevoke
JWT_SECRET=your_jwt_secret_min_32_chars
MARITACA_API_KEY=your_maritaca_key
STATIC_DIR=/app/data/static
DATA_DIR=/app/data
DISABLE_EMBEDDING_MODEL=false
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### `env/.mysql.env`
```bash
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=artevoke
MYSQL_USER=admin
MYSQL_PASSWORD=your_secure_password  # Must match DB_PASSWORD in .backend.env
```

### `env/.nginx.env` (optional)
```bash
NGINX_CONFIG=nginx-local.conf  # or nginx-prod.conf for HTTPS
```

## Important Notes

- **DB_HOST**: Use `mysql` (the Docker Compose service name), not `localhost` or an IP address
- **DB_PASSWORD**: Must match between `env/.backend.env` and `env/.mysql.env`
- **DB_USER**: Must match between `env/.backend.env` and `env/.mysql.env`
- **JWT_SECRET**: Must be at least 32 characters long

## After Configuration

Restart services to apply changes:
```bash
cd ~/artevoke/webapp
docker compose down
docker compose up -d
```

## Security

- Never commit `.env` files to git
- Use strong passwords
- Consider using environment variables or secrets management for production
- Regularly rotate secrets
