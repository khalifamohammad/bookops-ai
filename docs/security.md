# BookOps AI — Security

BookOps uses multiple security layers across the VPS, application, database and deployment pipeline.

## SSH

- non-root deployment user
- Ed25519 SSH keys
- root SSH login disabled
- password SSH login disabled
- public-key authentication enabled

## Firewall

UFW defaults to denying incoming connections.

Public ports:

```text
22   SSH
80   HTTP
443  HTTPS
