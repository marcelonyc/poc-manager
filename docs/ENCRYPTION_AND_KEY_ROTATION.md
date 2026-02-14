# Encryption System — Setup, Usage & Key Rotation

## Architecture Overview

The POC Manager encrypts sensitive data **at rest** using Fernet symmetric encryption (AES-128-CBC with HMAC-SHA256 via the `cryptography` library).

### Components

| File | Responsibility |
|---|---|
| `app/utils/encryption.py` | `EncryptionManager` — low-level encrypt / decrypt / key derivation |
| `app/utils/encrypted_field.py` | SQLAlchemy event listeners + helpers (`is_encrypted_value`, `encrypt_value`, `decrypt_value`) |
| `app/config.py` | Reads `ENCRYPTION_KEY` and `ENCRYPTION_LEGACY_KEYS` from environment |
| `app/database.py` | Calls `setup_encryption()` at startup to register ORM event listeners |
| `app/models/tenant.py` | Registers `custom_mail_password`, `custom_mail_username`, `ollama_api_key` |
| `app/models/integration.py` | Registers `config_data` (JSON blob with tokens/passwords) |
| `app/models/encryption_key.py` | DB model for tracking key versions and rotation metadata |
| `app/services/encryption_service.py` | CRUD for `EncryptionKey` records |
| `app/services/key_rotation_service.py` | Bulk re-encryption during key rotation |
| `app/routers/encryption.py` | REST API for Platform Admins (`/api/encryption/*`) |
| `scripts/encryption_management.py` | CLI tool for key generation, rotation, verification |

### Encrypted Fields Registry

Any model field can be registered for automatic encryption:

```python
# In the model file, after the class definition:
from app.utils.encrypted_field import register_encrypted_field

register_encrypted_field(Tenant, "custom_mail_password")
register_encrypted_field(Tenant, "custom_mail_username")
register_encrypted_field(Tenant, "ollama_api_key")
register_encrypted_field(TenantIntegration, "config_data")
```

### How It Works (Data Flow)

```
┌──────────────────────────────────────────────────────────┐
│  Application writes plaintext to model attribute         │
│  e.g. tenant.ollama_api_key = "sk-abc123"                │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│  before_flush listener detects the field is registered   │
│  and the value is NOT already encrypted                  │
│  → calls EncryptionManager.encrypt(plaintext)            │
│  → stores base64(ENC_V1 + Fernet(plaintext))             │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│  Database stores the base64-encoded ciphertext           │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│  On read (after_insert / after_update Mapper events)     │
│  → detects is_encrypted_value(value) == True             │
│  → calls EncryptionManager.decrypt(ciphertext)           │
│  → sets plaintext back on the in-memory object           │
└──────────────────────────────────────────────────────────┘
```

**Important:** The stored value in the database is a base64 string (e.g. `RU5DX1Yx...`), **not** a string starting with literal `ENC_V`. The `is_encrypted_value()` function handles this by base64-decoding first.

---

## First-Time Setup

### 1. Generate an Encryption Key

```bash
cd backend
python scripts/encryption_management.py generate-key
```

This prints a Fernet key like:
```
Key:
dGhpcyBpcyBhIHRlc3Qga2V5...
```

### 2. Set the Key in Your Environment

Add to your `.env` file (or Docker Compose environment):

```env
ENCRYPTION_KEY=dGhpcyBpcyBhIHRlc3Qga2V5...
ENCRYPTION_LEGACY_KEYS=
```

If you don't set `ENCRYPTION_KEY`, the default `"your-encryption-key-change-in-production"` from `config.py` is used — **this is insecure for production**.

### 3. Start / Restart the Application

```bash
docker compose restart backend
```

On startup, `setup_encryption()` in `database.py` registers the SQLAlchemy event listeners. All subsequent INSERT / UPDATE operations on registered fields encrypt automatically.

### 4. Encrypt Existing Plaintext Data

If you already have unencrypted data in the database:

```bash
python scripts/encryption_management.py re-encrypt
```

This iterates over all `Tenant` and `TenantIntegration` rows, detects plaintext (values that are NOT already encrypted), encrypts them with the current primary key, and commits.

### 5. Verify

```bash
python scripts/encryption_management.py verify
```

Reports how many encrypted fields exist, how many can be successfully decrypted, and flags any failures.

---

## Key Rotation

### When to Rotate

- **Scheduled maintenance** — rotate every 90 days as a best practice
- **Key compromise** — rotate immediately if the key is exposed
- **Personnel change** — rotate when someone with key access leaves

### Rotation Procedure

#### Step 1 — Generate and Register the New Key

**Option A: CLI** (recommended for production)

```bash
python scripts/encryption_management.py rotate --reason "scheduled Q1 rotation"
```

The output shows the new key value and version number.

**Option B: API** (Platform Admin only)

```
POST /api/encryption/rotate
{
  "reason": "scheduled Q1 rotation"
}
```

#### Step 2 — Update Environment Variables

```env
# Set the NEW key as primary
ENCRYPTION_KEY=<new-key-from-step-1>

# Add the OLD primary to legacy keys (comma-separated if multiple)
ENCRYPTION_LEGACY_KEYS=<old-key-1>,<old-key-2>
```

**Do NOT remove old keys from `ENCRYPTION_LEGACY_KEYS` until all data has been re-encrypted.** During the transition period the system uses legacy keys for decryption.

#### Step 3 — Restart the Application

```bash
docker compose restart backend
```

The `EncryptionManager` now uses the new primary key for encryption and falls back to legacy keys for decryption of older ciphertext.

#### Step 4 — Re-encrypt All Data

```bash
python scripts/encryption_management.py re-encrypt
```

This decrypts every encrypted field (using primary or legacy keys) and re-encrypts with the new primary key.

#### Step 5 — Verify

```bash
python scripts/encryption_management.py verify
```

Confirm zero decryption failures.

#### Step 6 — Remove Old Legacy Keys (Optional)

Once you've verified all data is re-encrypted:

```env
ENCRYPTION_LEGACY_KEYS=
```

Restart again. Old keys are no longer needed.

### Rotation API Endpoints (Platform Admin Only)

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/encryption/keys` | List all key versions |
| `POST` | `/api/encryption/rotate` | Generate & register a new primary key |
| `GET` | `/api/encryption/status` | Encryption system health stats |

---

## Adding Encryption to a New Field

1. **Register the field** at the bottom of your model file:

```python
from app.utils.encrypted_field import register_encrypted_field

class MyModel(Base):
    __tablename__ = "my_table"
    secret_token = Column(String, nullable=True)

register_encrypted_field(MyModel, "secret_token")
```

2. **Update `key_rotation_service.py`** to include the new model/field in `re_encrypt_all()` and `verify_encryption_data()`.

3. **Encrypt existing rows** — run `re-encrypt` or write a one-off migration.

4. **When reading the field outside the ORM** (e.g. passing to an external API), use `decrypt_value()`:

```python
from app.utils import decrypt_value

plaintext = decrypt_value(model_instance.secret_token)
```

---

## How Encrypted Detection Works

The `is_encrypted_value(value)` function:

1. Attempts `base64.urlsafe_b64decode(value)`
2. Checks if the decoded bytes start with `b"ENC_V"`
3. Returns `True` only if both succeed

This is used everywhere: the `before_flush` listener (to avoid double-encryption), the `after_insert`/`after_update` listeners (to trigger decryption), `decrypt_value()`, and the verification/rotation services.

---

## Security Notes

- **No plaintext keys are stored in the database.** The `encryption_keys` table only stores SHA-256 hashes for verification.
- **Fernet provides authenticated encryption** — tampering is detected on decrypt.
- **Key derivation** — if you supply a raw passphrase instead of a proper Fernet key, PBKDF2-HMAC-SHA256 with 100,000 iterations derives a valid 32-byte key. A fixed salt (`b"poc-manager-salt"`) is used for deterministic derivation from the same passphrase. For production, prefer generated Fernet keys.
- **Never log decrypted values.** The `mask_sensitive_data()` helper is available for safe logging.
