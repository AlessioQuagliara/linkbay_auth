# LinkBay-Auth v0.2.1

[![License](https://img.shields.io/badge/license-MIT-blue)]() [![Python](https://img.shields.io/badge/python-3.8+-blue)]() [![Tests](https://img.shields.io/badge/tests-20/20-green)]()

LinkBay-Auth fornisce un set completo di endpoint JWT per FastAPI senza imporre alcun modello di database. È ideale per progetti interni, MVP e applicazioni con requisiti di sicurezza standard. Prima di usarla in scenari enterprise critici, pianifica audit esterni, MFA e monitoring dedicato.

## Prima di iniziare

- ✅ Pro: architettura pulita, async-first, nessun vincolo sui tuoi modelli.
- ⚠️ Contro: niente MFA/SSO integrati, nessun audit indipendente.
- 🎯 Usa questa libreria per ridurre il boilerplate di registrazione/login mantenendo pieno controllo sui dati.

## Installazione

```bash
pip install linkbay-auth==0.2.0
```

Oppure l'ultima versione dal repository:

```bash
pip install git+https://github.com/AlessioQuagliara/linkbay_auth.git
```

## Come funziona (3 passi)

### 1. Implementa il servizio utente

```python
from datetime import datetime
from linkbay_auth import UserServiceProtocol

class MyUserService(UserServiceProtocol):
    def __init__(self, db):
        self.db = db

    async def get_user_by_email(self, email: str):
        return await self.db.get_user_by_email(email)

    async def get_user_by_id(self, user_id: int):
        return await self.db.get_user(user_id)

    async def create_user(self, email: str, hashed_password: str):
        return await self.db.create_user(email=email, hashed_password=hashed_password)

    async def update_user_password(self, email: str, hashed_password: str):
        return await self.db.update_password(email, hashed_password)

    async def save_refresh_token(self, user_id: int, token: str, expires_at: datetime):
        return await self.db.store_refresh_token(user_id, token, expires_at)

    async def get_refresh_token(self, token: str):
        return await self.db.get_refresh_token(token)

    async def revoke_refresh_token(self, token: str) -> bool:
        return await self.db.revoke_refresh_token(token)

    async def revoke_all_user_tokens(self, user_id: int):
        await self.db.revoke_all_tokens(user_id)
```

> ℹ️ Sostituisci i metodi `db.*` con il tuo ORM o servizio preferito.

### 2. Configura FastAPI

```python
from fastapi import FastAPI, Depends
from linkbay_auth import (
    AuthCore,
    create_auth_router,
    create_get_current_user,
    create_get_current_active_user,
)

app = FastAPI()
user_service = MyUserService(db_session)

auth_core = AuthCore(
    user_service=user_service,
    secret_key="cambia-questa-chiave",
    access_token_expire_minutes=15,
    refresh_token_expire_days=30,
)

auth_router = create_auth_router(auth_core)
app.include_router(auth_router)

get_current_user = create_get_current_user(auth_core)
get_current_active_user = create_get_current_active_user(auth_core, get_current_user)

@app.get("/me")
async def whoami(current_user = Depends(get_current_active_user)):
    return {"email": current_user.email}
```

### 3. Avvia e testa

```bash
uvicorn main:app --reload
```

Endpoint inclusi:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/logout-all`
- `GET /auth/me`
- `POST /auth/password-reset-request`
- `POST /auth/password-reset-confirm`

## Esempio avanzato (opzionale)

Abilita funzioni extra di sicurezza quando il tuo progetto richiede policy più rigide.

```python
from linkbay_auth import PasswordPolicy

policy = PasswordPolicy(
    min_length=10,
    require_uppercase=True,
    require_lowercase=True,
    require_numbers=True,
    require_special=True,
    blacklist=["password", "123456", "qwerty"],
)

auth_core = AuthCore(
    user_service=user_service,
    secret_key=env.SECRET_KEY,
    access_token_expire_minutes=10,
    refresh_token_expire_days=15,
    password_policy=policy,
    enable_token_blacklist=True,
)
```

Per sfruttare blacklist, rate limiting e logging estendi il servizio utente con:

```python
async def log_security_event(self, event_type: str, user_id: int | None, details: dict):
    ...  # salva nel tuo sistema di logging

async def check_login_attempts(self, email: str) -> bool:
    ...  # True se l'utente può tentare ancora, False per bloccarlo

async def record_failed_login(self, email: str):
    ...  # incrementa il contatore di tentativi

async def reset_failed_logins(self, email: str):
    ...  # resetta il contatore dopo login riuscito
```

## Caratteristiche principali

- JWT access e refresh token con scadenze configurabili.
- Hashing password con `bcrypt>=4.0.0` (nessuna dipendenza da passlib).
- Async-first e privo di opinioni sui tuoi modelli.
- Reset password con token temporanei.
- Possibilità di revocare singoli refresh token o interi set utente.

## Sicurezza opzionale inclusa

| Feature | Come abilitarla | Cosa devi implementare |
| --- | --- | --- |
| Password policy | `password_policy=PasswordPolicy(...)` | Nessun extra |
| Token blacklist | `enable_token_blacklist=True` | Storage condiviso (es. Redis) |
| Brute force guard | `check_login_attempts`, `record_failed_login`, `reset_failed_logins` | Persistenza contatori |
| Security logging | `log_security_event` | Destinazione log centralizzata |
| Device tracking | Salva user agent/IP nei tuoi modelli | Endpoint di gestione sessioni |

## Testing

```bash
python3 test_basic.py              # flusso auth core
python3 test_security_features.py  # feature opzionali di sicurezza
```

Entrambe le suite devono terminare con `✅ TUTTI I TEST SUPERATI`.

## Limitazioni note

- Mancano MFA, SSO/OAuth social, gestione dispositivi con UI.
- Nessun audit di sicurezza esterno eseguito.
- La blacklist di default è in-memory: per produzione usa Redis o altro store condiviso.
- Non fornisce metriche/monitoring: integrazione Prometheus/Grafana a carico tuo.

## Roadmap consigliata

1. Security audit indipendente.
2. Espandere la test suite (edge case, fuzzing, integrazione DB reali).
3. Aggiungere MFA (TOTP/email) e device management.
4. Documentare runbook operativi per incident response e backup/restore.

## Licenza

MIT. Puoi usarla e modificarla liberamente, assicurandoti di valutarne i rischi nel tuo contesto.

## Supporto

- Issues: https://github.com/AlessioQuagliara/linkbay_auth/issues
- Email: quagliara.alessio@gmail.com

Contribuisci, apri una issue o raccontaci come stai usando la libreria 🧡
