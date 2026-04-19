# Profitability Intelligence — PI-v1.0

Three-bot Telegram system giving subscribers automated daily performance updates across three trading products.

| Bot | Code | Description |
|-----|------|-------------|
| P1 Signals Bot  | `signals-bot`  | VIP channel listener + daily pip reports |
| P2 Copy Bot     | `copy-bot`     | MT4 API + compounding engine + personalised reports |
| P3 Funded Bot   | `funded-bot`   | Manual admin input + challenge status reports |

---

## Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3.12                         |
| Bots       | python-telegram-bot v21 (async)     |
| Admin API  | FastAPI + Uvicorn                   |
| Database   | PostgreSQL 16                       |
| Cache      | Redis 7                             |
| Deployment | Docker Compose (6 containers)       |
| MT4        | MetaAPI.cloud (investor/read-only)  |

---

## Folder Structure

```
profitability-intelligence/
  shared/              Shared DB, logger, i18n (EN + DE), schema.sql
  signals_bot/         P1 — channel listener + daily report bot
  copy_bot/            P2 — MT4 API + compounding engine + report bot
  funded_bot/          P3 — manual admin input + challenge status bot
  admin/               FastAPI REST API (port 4000, localhost only)
  docker-compose.yml   All 6 services
  .env.example         Copy to .env and fill in all values
```

---

## Deployment

### 1. Prerequisites
- Ubuntu 22.04 LTS or 24.04 LTS
- Docker + Docker Compose installed
- Git access to the repository

### 2. Clone & configure
```bash
git clone <REPO_URL> profitability-intelligence
cd profitability-intelligence
cp .env.example .env
nano .env   # fill in all REPLACE_WITH_... values
```

### 3. Create log directories
```bash
mkdir -p logs/signals logs/copy logs/funded logs/admin
```

### 4. Start all services
```bash
docker compose up -d
```

### 5. Verify
```bash
docker compose ps
docker compose logs -f signals-bot
curl http://localhost:4000/health
```

---

## Credentials Needed

### Telegram Bots — via @BotFather
Create three separate bots. Copy each token to `.env`:
- `SIGNALS_BOT_TOKEN`
- `COPY_BOT_TOKEN`
- `FUNDED_BOT_TOKEN`

### VIP Channel
1. Add the Signals Bot as Admin to the VIP channel (needs "Post Messages")
2. Forward any channel message to @userinfobot to get the channel ID
3. Set `SIGNALS_VIP_CHANNEL_ID` (negative number, e.g. `-1001234567890`)

### MetaAPI (MT4 connection)
1. Register at https://app.metaapi.cloud
2. Create a MetaAPI account — MT4, enter broker server + account number + **investor password** (read-only)
3. Copy `META_API_TOKEN` and `MT4_ACCOUNT_ID` to `.env`
4. MT4 credentials (account number, investor password, broker server) provided by Ben via WhatsApp

---

## Admin API

**Base URL:** `http://localhost:4000`  
**Auth header:** `X-Admin-Secret: <your ADMIN_SECRET>`

### Endpoints

#### Funded Accounts
| Method | Path | Description |
|--------|------|-------------|
| GET | `/funded` | List all funded accounts |
| POST | `/funded` | Create account |
| PATCH | `/funded/{id}` | Update daily figures |
| DELETE | `/funded/{id}` | Deactivate account |

**POST /funded body:**
```json
{
  "telegram_id": 123456789,
  "account_size": 100000,
  "profit_target": 10.0,
  "max_daily_loss": 5.0,
  "max_overall_loss": 10.0,
  "phase": "challenge"
}
```

**PATCH /funded/{id} body:**
```json
{
  "current_gain": 3.5,
  "used_daily_loss": 1.2,
  "used_overall_loss": 3.5,
  "phase": "challenge"
}
```

> ⚠️ The user **must /start the funded bot** before you can create an account. Their Telegram ID must exist in the users table.

#### Signal Snapshots
| Method | Path | Description |
|--------|------|-------------|
| GET | `/signals/snapshots` | Last 90 daily snapshots |
| POST | `/signals/snapshots` | Set today's snapshot |
| GET | `/signals` | Last 100 parsed signals |
| PATCH | `/signals/{id}` | Manually close a signal |

**POST /signals/snapshots body:**
```json
{
  "pips_closed": 142.5,
  "pips_floating": 30.0,
  "pips_week": 380.0,
  "pips_month": 1200.0,
  "closed_count": 8,
  "open_count": 3
}
```

#### Master Snapshots (P2 fallback)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/copy/snapshots` | Last 90 master snapshots |
| POST | `/copy/snapshots` | Manual override |

#### Health
| Method | Path |
|--------|------|
| GET | `/health` |

---

## Bot Commands

### All Bots
| Command | Description |
|---------|-------------|
| `/start` | Welcome + register user |
| `/subscribe` | Subscribe to reports |
| `/unsubscribe` | Stop reports |
| `/setlang en\|de` | Set language |
| `/help` | List commands |

### P1 Signals Bot
| Command | Description |
|---------|-------------|
| `/daily` | Today's report on demand |
| `/performance` | Latest snapshot |
| `/setlot 0.1` | Set personal lot size |

### P2 Copy Bot
| Command | Description |
|---------|-------------|
| `/daily` | Today's personalised report |
| `/projection` | 12-month compounding projection |
| `/setdeposit 5000` | Set deposit in USD |
| `/setrisk 1.0` | Set risk multiplier (0.1–3.0) |

### P3 Funded Bot
| Command | Description |
|---------|-------------|
| `/status` | Current challenge status + rule buffers |
| `/performance` | Same as /status |

---

## Automated Schedule

| Time (UTC) | Action |
|------------|--------|
| Every 1h | Copy Bot: fetch MT4 master account, store snapshot |
| 20:00 | Signals Bot: broadcast daily report |
| 20:00 | Copy Bot: broadcast personalised report |
| 20:30 | Funded Bot: broadcast challenge status |

---

## Rule Buffers (P3)

Colour indicators based on % of limit consumed:

| Colour | Condition |
|--------|-----------|
| 🟢 Green | < 50% of limit used |
| 🟡 Amber | 50% – 80% of limit used |
| 🔴 Red | > 80% of limit used |

---

## Ground Rules

- **Never commit `.env`** — it contains all secrets
- **Never expose port 4000 publicly** — use nginx with auth if needed
- All report messages include the compliance footer (in i18n templates)
- Do not modify `shared/schema.sql` without confirming with Ben first
- All code changes go through the repo — no direct edits on VM in production
- If MT4 connection fails, copy bot logs a warning and skips the snapshot — **fix credentials, do not patch the fallback**
- User must `/start` the funded bot before admin can create their account

---

## Contact

| | |
|-|------|
| Project lead | Ben — via WhatsApp |
| Questions | WhatsApp first, always |
| Updates | Daily progress updates during active development |

---

*Profitability Intelligence — Confidential. Do not distribute.*
"# Telegram_bots" 
