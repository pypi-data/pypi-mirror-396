# PACMAN Security & Privacy

## Privacy Guarantees

PACMAN is designed with privacy-first principles. These are not just documentation - they are enforced at runtime.

### Core Guarantees

| Guarantee | Status | Description |
|-----------|--------|-------------|
| **NO_NETWORK** | Enforced | PACMAN never makes network requests |
| **NO_TELEMETRY** | Enforced | No usage data is collected |
| **NO_CLOUD_STORAGE** | Enforced | All data stays on your device |
| **NO_EXTERNAL_APIS** | Enforced | No external API calls |
| **AUDITABLE_SOURCE** | Yes | Open source, fully auditable |

### How These Are Enforced

1. **Import Blocking**: Network-capable modules (requests, httpx, socket, etc.) are blocked from being imported within PACMAN context.

2. **No Dependencies**: Core functionality has no network-capable dependencies.

3. **Open Source**: All code is auditable under AGPL-3.0.

## Verification

You can verify these guarantees by:

### 1. Command Line Check
```bash
pacman --privacy
```

### 2. Network Monitoring
Run PACMAN while monitoring network traffic:
```bash
# Linux
sudo tcpdump -i any host not localhost &
pacman categorize
```

### 3. Source Code Audit
Review the privacy module:
```
src/pacman/core/privacy.py
```

## Data Storage

- **Location**: `~/.pacman/` or project directory
- **Format**: JSON and YAML files
- **Encryption**: Optional AES-256 encryption (Phase 2)

### What Is Stored

| File | Contents | Sensitive? |
|------|----------|------------|
| `config.yaml` | Project settings | Low |
| `transactions.json` | Your transactions | **High** |
| `export/*.xlsx` | Tax calculations | **High** |

### Data Never Leaves Your Device

- No cloud sync
- No automatic backups
- No crash reports
- No analytics

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT open a public issue**
2. Email: [security contact]
3. We will respond within 48 hours

## Third-Party Dependencies

PACMAN uses these dependencies, none of which have network capabilities in our usage:

| Dependency | Purpose | Network? |
|------------|---------|----------|
| pydantic | Data validation | No |
| typer | CLI framework | No |
| pyyaml | YAML parsing | No |
| pandas | Data processing | No |
| openpyxl | Excel files | No |
| rich | Terminal output | No |

## Optional: Encrypted Storage (Phase 2)

When enabled, sensitive files are encrypted with AES-256:

- Password-based key derivation (PBKDF2)
- Files stored with `.pacman` extension
- Decrypted only in memory

## License

This security documentation is part of PACMAN, licensed under AGPL-3.0.
