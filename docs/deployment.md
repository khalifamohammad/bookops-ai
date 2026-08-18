# VPS Deployment Checklist

1. Provision an Ubuntu VPS.
2. Create a non-root deployment user and add an SSH public key.
3. Enable the firewall for SSH, HTTP and HTTPS.
4. Install Docker Engine and the Compose plugin.
5. Clone the repository and copy `.env.example` to `.env`.
6. Replace passwords, `JWT_SECRET`, domain names and Caddy email.
7. Point the chosen Cloudflare DNS records to the VPS.
8. Run:

```bash
docker compose --profile production --profile monitoring up -d --build
```

9. Configure Uptime Kuma checks for:
   - `https://api.booking.example.com/api/health`
   - `https://booking.example.com`
10. Schedule the backup script with cron.
11. Test restore on a disposable database before relying on the backup.

Cloudflare should use a secure SSL mode after Caddy has obtained a certificate. Add rate limiting for the login and public booking paths at Cloudflare and at the application/reverse-proxy layer.
