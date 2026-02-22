# 🏏 IPL 2026 Mega Auction Simulator

> **A fully AI-powered, real-time IPL auction simulator where you manage one of 10 franchises while 9 intelligent AI agents — each with unique personalities, strategies, and squad intelligence — compete against you in a live bidding environment.**

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technical Architecture](#️-technical-architecture)
- [The AI Agent System](#-the-ai-agent-system)
- [9 AI Teams — Personalities & Strategies](#-9-ai-teams--personalities--strategies)
- [Auction Mechanics](#-auction-mechanics)  
- [Dynamic Bidding Engine](#-dynamic-bidding-engine)
- [Squad Intelligence System](#-squad-intelligence-system)
- [Market Valuation Engine](#-market-valuation-engine)
- [RTM (Right to Match) System](#-rtm-right-to-match-system)
- [Tech Stack](#-tech-stack)
- [Installation & Setup](#-installation--setup)
- [Project Structure](#-project-structure)
- [Output Photos](#output=photos)
- [cotributing](#contributing)

---

## 🌟 Overview

This project simulates the **IPL 2026 Mega Auction** with full fidelity to real-world rules, team strategies, player valuations, and bidding dynamics. You pick one of 10 IPL franchises and participate in a live auction against 9 AI-driven opponents.

What makes this unique is the **multi-layer AI decision engine** — each AI team is not a simple rule-based bot. Instead, every player going under the hammer triggers a **full LLM-powered valuation call**, where the model is given:

- Real squad composition data for all 10 teams
- Budget remaining, overseas slots used, squad gaps
- Player stats, age, IPL experience, brand value
- Home pitch preferences for each ground
- Team personality and spending philosophy
- Real 2025 IPL auction prices as ground truth

The entire frontend is a **Flask Based web app** built with vanilla JavaScript, polling Flask APIs continuously to animate the auction live.

---

## ✨ Features

### 🎮 Gameplay
- **Play as any of 10 IPL franchises** with real 2025 retained squads and post-retention budgets
- **Live bidding interface** — place bids, pass, or watch AI teams battle
- **RTM (Right to Match) Cards** — each team gets RTMs based on how many players they retained (6 − retentions)
- **Player sets** — auction follows IPL format: Marquee Set 1 → Marquee Set 2 → Batters → Wicket-Keepers → All-Rounders → Pacers → Spinners → Additional
- **Unsold players return** in an Additional Set for a second chance
- **Squad limits enforced**: 18-25 players, 6-8 max overseas per team

### 🤖 AI Intelligence
- **9 unique AI agents**, one per team, each with distinct persona and bidding behaviour
- **LLM-powered valuations** using `meta/llama-3.1-70b-instruct` via NVIDIA NIM API
- **Fallback engine** if LLM call times out — purely algorithmic valuation using squad analysis × personality multipliers × budget factors × variance
- **Real-time squad analysis** before every bid decision — bowler saturation, batting depth, overseas slots, budget pressure, XI fit scoring
- **Dynamic aggression** — teams become more or less aggressive based on current budget spent %, squad fill %, and urgency

### 📊 UI & Information
- **Overview panel** — live budget, players, overseas count for all 10 teams
- **Squad viewer** — click any team card to instantly open their full squad
- **Bidding log** — live feed of every bid for the current player
- **HISTORY tab** — full sold/unsold record
- **Animated sold/unsold reveal** after each player
- **Team colour-coded UI** — each franchise has its own primary/secondary colour scheme
- **Player cards** — role badge, overseas flag, IPL stats, batting/bowling style, age, base price
- **Real-time bid increment system** — mirrors actual IPL auction increments (₹10L / ₹25L / ₹50L tiers)

---

## 🏗️ Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (SPA)                        │
│  - Vanilla JS polling Flask APIs every ~1.5s            │
│  - Bid controls, squad panel, log, overview             │
│  - Animated transitions for bidding/sold/unsold states  │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP (fetch/XHR)
┌──────────────────────────▼──────────────────────────────┐
│               Flask Backend (app.py)                    │
│                                                         │
│  /api/start_player   → Pop next player, run AI vals     │
│  /api/ai_bid         → AI bidding round logic           │
│  /api/place_bid      → User bid submission              │
│  /api/pass           → User passes                      │
│  /api/sold           → Finalize sale, award to winner   │
│  /api/unsold         → Mark unsold, queue for 2nd round │
│  /api/use_rtm        → RTM card exercise logic          │
│  /api/get_live_log   → Current player bid history       │
│  /api/get_auction_cards → Completed player log          │
│  /api/status         → Current auction state            │
└──────────┬─────────────────────────┬───────────────────┘
           │                         │
┌──────────▼──────────┐   ┌──────────▼──────────────────┐
│   game_state dict   │   │  generate_ai_valuations()   │
│                     │   │                             │
│  - teams{}          │   │  1. analyse_squad() ×9      │
│  - players_pool[]   │   │  2. player_fits_xi_need()   │
│  - current_player   │   │  3. compute_market_value()  │
│  - ai_valuations{}  │   │  4. Build LLM prompt        │
│  - sold_history[]   │   │  5. Call Llama 3.1 70B      │
│  - rtm_cards{}      │   │  6. Parse + enforce caps    │
│  - bid_history[]    │   │  7. Return per-team max bids│
└─────────────────────┘   └─────────────────────────────┘
                                      │
                         ┌────────────▼────────────────┐
                         │  NVIDIA NIM API             │
                         │  meta/llama-3.1-70b-instruct│
                         │  (IPL auction expert prompt) │
                         └─────────────────────────────┘
```

### Key Data Flows

1. **Player starts** → `start_player` pops from pool, calls `generate_ai_valuations()` which computes per-team max bids via LLM
2. **AI bidding** → `ai_bid` is polled by frontend. Backend selects the best candidate from teams whose `max_bid ≥ next_bid` and passes all safety checks
3. **User bids** → validated against budget, overseas slots, squad size, and tiered reserve requirements
4. **Sold** → squad/budget updated, player card created, RTM check triggered if applicable
5. **Frontend polling** → `status` API returns full game state; UI re-renders diff

---

## 🤖 The AI Agent System

Each player going under the hammer triggers a full AI valuation pipeline:

### Step 1 — Squad Analysis (`analyse_squad`)

For every AI team, a deep squad snapshot is computed:

| Metric | What it tracks |
|--------|---------------|
| `wk`, `batters`, `all_rounders`, `bowlers` | Role counts vs minimums |
| `spin_bowlers`, `pace_bowlers` | Bowling type split |
| `total_batting_depth` | Pure batters + WKs + batting ARs |
| `remaining_spots`, `remaining_os_spots` | Available slots |
| `budget_per_slot` | Budget ÷ empty slots |
| `budget_pressure` | `low / medium / high / critical` |
| `critical_gaps` | Roles below squad minimum |

### Step 2 — XI Fit Scoring (`player_fits_xi_need`)

Each player gets a **fit score (0.0 – 3.0)** per team, driven by:

- **Role gap urgency** — if team is short on WKs/bowlers/ARs, score goes up proportionally
- **Squad saturation** — if team has 4+ spinners, spinner score drops 70%; 6+ pacers → pacer score drops 70%
- **Home pitch compatibility** — Chepauk spinners get +0.6, Eden pacers get +0.6, etc.
- **Batting depth saturation** — teams that have 9+ batting resources defocus on batters
- **LHB/RHB balance** — rewards players filling the hand imbalance
- **Budget pressure penalty** — critical budget → multiply final score by 0.4
- **Overseas slot scarcity** — last overseas slot triggers higher XI score for bowling/AR

### Step 3 — Market Value Baseline (`compute_market_value`)

A **technical floor price** (not final bid) computed from:

```
value = base_price
→ Capped Indian floor: 150L → 750L (by IPL match count)  
→ Capped Overseas floor: 400L → 1500L (by IPL match count)
→ WK premium: ×1.2 (only 2 per team, extreme scarcity)
→ All-Rounder premium: ×1.15 (fills dual XI slot)
→ Set 1 (Mega Marquee): ×1.8
→ Set 2 (Marquee): ×1.5
→ Set 3 (Featured): ×1.3
```

This anchors the AI prompt with a realistic floor before brand/captain premiums.

### Step 4 — LLM Prompt Construction

A structured ~2000-token prompt is built per player containing:

- Full player profile (age, IPL matches, role, country, brand tier)
- 9-team JSON with squad composition, budget, XI fit scores, bowling saturation, batting saturation, pitch affinity
- Real 2025 IPL Mega Auction outcome data for calibration (Pant ₹2700L, Shreyas ₹2675L, Tripathi ₹200L, etc.)
- Extensive bidding framework: dynamic aggression factors, squad completion urgency, post-marquee price discipline
- Explicit squad desperation logic for teams with < 10 or < 5 players
- Hard rules: never exceed budget, overseas block, squad full block

### Step 5 — LLM Call & Constraint Enforcement

```python
# After LLM returns per-team max bids:
for team, llm_val in parsed.items():
    llm_val = min(llm_val, t_data['budget'])          # never exceed budget
    llm_val = 0 if overseas player + os_slots_full     # hard overseas block
    llm_val = 0 if squad already 25 players            # squad full block
    if budget_pressure == 'critical':
        llm_val = min(llm_val, budget_per_slot * 2)    # protect squad completion
    # Tiered reserve cap
    reserve_mult = 30 if players≥10 else 50 if players≥5 else 25
    max_safe = budget - (slots_to_18 × reserve_mult)
    llm_val = min(llm_val, max_safe)
    # Post-marquee hard cap (Sets 3+)
    if set_no >= 3:
        llm_val = min(llm_val, 1500)
```

### Step 6 — Fallback Algorithmic Engine

If LLM times out (10s limit), a purely coded fallback runs:

```
val = market_value × personality_mult × budget_mult × completion_mult × variance
```

| Factor | Range | Logic |
|--------|-------|-------|
| `personality_mult` | 0.75 – 1.8 | Fixed per team style |
| `budget_mult` | 0.6 – 1.3 | Based on % budget spent |
| `completion_mult` | 1.0 – 1.5 | Based on slots to 18 |
| `variance` | ±12–30% | Random spread for realism |

---

## 🏟️ 9 AI Teams — Personalities & Strategies

### 1. CSK — Chennai Super Kings  
**Style:** `conservative_experienced`  
**Persona:** "Daddy's Army." Trust experience (30+ age) over youth. Chepauk is a spin graveyard — 4 spinners normal. NZ overseas preference (coach influence). Distributes budget evenly, never overpays for one star. Targets 25-member squad with domestic backups.  
**Pitch:** Chepauk (spin paradise, 120-150 scores, 4 spinners regular)  
**Spend philosophy:** Balanced distribution. Max ~₹1000L on any star. Age 30+ < players prioritized.

---

### 2. DC — Delhi Capitals
**Style:** `aggressive_rebuild`  
**Persona:** "Young Guns + Price Spoilers." Desperately needs a captain. Goes for fancy young overseas talent. Also bids to **inflate prices** for rivals even on players they don't need — tactical price-ruining.  
**Pitch:** Arun Jaitley, Delhi (spin-friendly with dew, batting depth critical)  
**Spend philosophy:** Aggressive for young talent. Price spoiler tactics. All-rounder obsession.

---

### 3. GT — Gujarat Titans
**Style:** `balanced_aggressive`  
**Persona:** "Nehra's Bowling Factory." Spends 60% of budget on bowling attack alone — best pace variety in the league. Moneyball for batting depth. Big Indian names welcome, all-rounders critical. Rashid + 4-5 quality pacers is the XI template.  
**Pitch:** Narendra Modi Stadium, Ahmedabad (big ground, flat with bounce, 180-200 scores)  
**Spend philosophy:** Bowlers are #1 priority. Moneyball everything else.

---

### 4. KKR — Kolkata Knight Riders
**Style:** `ex_player_loyalty`  
**Persona:** Eden is a bowling paradise. KKR prioritizes an **overseas WK**, muscular all-rounders, strong spinners, and left-arm pacers. Goes **any amount for ex-KKR players** — unbalanced loyalty spending. Needs captain desperately. Typically ends with only 18-19 players.  
**Pitch:** Eden Gardens (swing/seam heaven, 140-150 scores, pace dominates)  
**Spend philosophy:** 80% on playing XI. Ex-KKR at ANY price. Squad 18-19 only.

---

### 5. LSG — Lucknow Super Giants
**Style:** `marquee_unbalanced`  
**Persona:** Marquee obsession — spends 50% of purse on 2-3 superstar signings then scrambles for cheap backups. Bold calls on injury-prone players. Maharashtra domestic talent focus. AUS/SA overseas preference. Desperately needs a captain.  
**Pitch:** BRSABV Ekana, Lucknow (unpredictable — can be 200+ or 120, needs all-round balance)  
**Spend philosophy:** 2-3 marquee stars at all costs. Cheap fill for remaining 15-16 slots.

---

### 6. MI — Mumbai Indians
**Style:** `budget_snipers`  
**Persona:** Tight budget. Spends 80% of time "delaying at the table" (realistic time-burn behaviour). **Bids ONLY on past MI players** or "weird domestic finds it wants to develop." Highly unbalanced — almost all budget goes to playing XI. SL/ENG/AUS/NZ overseas preference.  
**Pitch:** Wankhede (dual nature — red soil=pace, black soil=spin, heavy dew, 170-180 scores, chasing team)  
**Spend philosophy:** Max ₹1000L on any player. Ex-MI at any price. Squad 20-22 with lots of ARs.

---

### 7. PBKS — Punjab Kings
**Style:** `ultra_aggressive_big_spender`  
**Persona:** Richest team (₹110 Cr purse). Mohali is a batting paradise — deadliest for bowlers. Enters **every marquee war**, dominates early sets. Spends 60-70% on 4-5 stars then completes 25-member squad with cheap Punjab/NE/Vidarbha backups. AUS overseas preference (coach connection). Equal focus all departments.  
**Pitch:** IS Bindra, Mohali (pure flat track, batting heaven, 200+ scores, bowlers nightmare)  
**Spend philosophy:** Go BIG early. Complete full 25-squad always. Punjab domestic talent filler.

---

### 8. RCB — Royal Challengers Bengaluru
**Style:** `balanced_budget_friendly`  
**Persona:** Budget-friendly but balanced. Chinnaswamy favours explosive batters and death specialists — but RCB avoids overpaying for big names. Instead builds the **most balanced team possible**. ENG/WI overseas firepower. Kannada domestic talent. Needs captain + all-rounders.  
**Pitch:** Chinnaswamy (batting paradise, tiny boundaries, explosive batters and death bowlers critical)  
**Spend philosophy:** No single star for ₹2500L. Distribute evenly. All-rounders are #1.

---

### 9. RR — Rajasthan Royals
**Style:** `extreme_budget_save`  
**Persona:** Sangakkara/Dravid moneyball DNA. Jaipur's huge ground favours spin — spinners are priority. Pure specialists only (no all-rounders by choice). Targets BBL/Hundred/U19 overseas stars for value. Invests big in **established young Indian players** (Samson, Parag tier). Will "break barriers like Namita from Shark Tank" if they REALLY want someone. Always completes 25-squad.  
**Pitch:** Sawai Mansingh (massive ground, spin-to-win, technical batsmen needed)  
**Spend philosophy:** 60-70% on 3-4 Indian youngsters. Moneyball everything else. Always 25 players.

---

### 10. SRH — Sunrisers Hyderabad
**Style:** `ultra_aggressive_unbalanced`  
**Persona:** "DEVILS." Highly explosive, highly unbalanced. Hyderabad's flat track + early swing = explosive batters + premium pace. Overseas batters are **top priority** (best overseas batting lineup in the league). Spends 80% on 4-5 players, keeps short squad (18-20). No backups. All-out attack.  
**Pitch:** Rajiv Gandhi, Hyderabad (flat, very high-scoring, early bounce/swing, premium pace + explosive batters)  
**Spend philosophy:** Go big or go home. 4-5 explosive players dominate budget. Short squad 18-20 only.

---

## 🎯 Auction Mechanics

### Player Sets (IPL Format)
Players are auctioned in structured sets, randomized within each set:

| Set | Type | Price Multiplier |
|-----|------|-----------------|
| 1 | Mega Marquee | ×1.8 market premium |
| 2 | Marquee | ×1.5 premium |
| 3 | Featured Batters | ×1.3 premium |
| 4 | Featured WK-Batters | base |
| 5 | Featured All-Rounders | base |
| 6 | Featured Pacers | base |
| 7 | Featured Spinners | base |
| 8+ | Additional (unsold returns) | base |

### Bid Increment System
Mirrors real IPL auction increments:

| Price Band | Increment |
|-----------|-----------|
| < ₹200L | ₹10L |
| ₹200L – ₹500L | ₹25L |
| ₹500L – ₹1000L | ₹50L |
| ₹1000L+ | ₹50L |

### RTM (Right to Match) Cards
- Formula: `RTM Cards = 6 − number of players retained`
- CSK retained 5 → 1 RTM card; PBKS retained 2 → 4 RTM cards
- When a player's **previous team** has RTM cards, they sit out initial bidding and get the option to match the final highest bid
- Counter-raise mechanic: original highest bidder can respond to RTM, creating a final showdown

---

## ⚡ Dynamic Bidding Engine

The AI bidding loop (`/api/ai_bid`) runs every ~1.5s polled by the frontend:

```
For each bidding round:
  next_bid = current_bid + increment(current_bid)
  
  For each AI team with max_val >= next_bid:
    Check: has budget for next_bid?
    Check: bidding would still leave (slots_to_18 × reserve_mult) available?
    Check: overseas slot available if needed?
    Check: squad not full?
    
    If all pass → add to candidates with eagerness = max_val - next_bid
  
  Sort candidates by eagerness desc
  Select winner (weighted random among top candidates)
  Emit bid event → frontend updates in real time
```

### Post-Marquee Price Discipline (Sets 3+)

A critical rule preventing over-spending on depth players:

```
if set_no >= 3:
    all AI bids hard-capped at ₹1500L (15 crore)
```

Realistic range for non-marquee:
- Typical: ₹500L – ₹1000L (5-10 crore)
- Above average fit: ₹1000L – ₹1500L (only exceptional fits)
- Never: ₹1600L+ for non-Set-1/2 players

### Tiered Reserve System

Ensures desperate teams aren't blocked from bidding just because the naïve 100L-per-slot reserve made their budget appear insufficient:

```python
reserve_mult = (
    30  if team_players >= 10   # 10+ players → *30L per empty slot
    50  if team_players >= 5    # 5-9 players → *50L per empty slot  
    25  if team_players < 5     # <5 players → *25L per empty slot (most desperate)
)
max_safe_bid = budget - (slots_to_18 × reserve_mult)
```

This ensures a team like PBKS (6 players, ₹1226L budget) can bid up to ₹626L instead of being locked to ₹26L.

---

## 🔬 Squad Intelligence System

### Bowling Saturation
The system prevents illogical overbidding when a team already has enough of a bowling type:

| Status | Condition | Valuation impact |
|--------|-----------|-----------------|
| `SPIN_SATURATED` | 4+ spinners | Team bids ₹0 |
| `SPIN_ADEQUATE` | 3 spinners | Score ×0.6, valuation –50-70% |
| `PACE_SATURATED` | 6+ pacers | Team bids ₹0 |
| `PACE_ADEQUATE` | 5 pacers | Score ×0.6, valuation –50-70% |

### Batting Depth Saturation
Prevents every team from hoarding batters late in auction:

| Status | Batting Resources | Valuation impact |
|--------|------------------|-----------------|
| `BAT_SATURATED` | 9+ | –80% for batters |
| `BAT_ADEQUATE` | 8 | –60% for batters |
| `BAT_SUFFICIENT` | 7 | –40% for batters |
| `NONE` | < 7 | Normal bidding |

*Batting resources = pure batters + WK-batters + batting all-rounders*

### Budget Pressure Levels

| Level | Budget/slot | AI behaviour |
|-------|------------|--------------|
| `low` | > ₹400L | Full aggression allowed |
| `medium` | ₹150-400L | Normal bidding |
| `high` | ₹50-150L | Score penalty ×0.7 |
| `critical` | < ₹50L | Score ×0.4, capped at budget_per_slot ×2 |

---

## 💰 Market Valuation Engine

Real 2025 IPL Mega Auction data is embedded in the prompt as mandatory calibration:

| Player | Price | Why |
|--------|-------|-----|
| Rishabh Pant | ₹2700L | WK + Captain + 100+ IPL → bid wars |
| Shreyas Iyer | ₹2675L | Captain-hungry teams explode on leadership |
| Arshdeep Singh | ₹1800L | Premier Indian pacer, Set 1 marquee |
| Yuzvendra Chahal | ₹1800L | 150+ IPL, supreme brand + spin value |
| KL Rahul | ₹1400L | WK + Captain even with lower demand |
| Rahul Tripathi | ₹200L | 80+ IPL, pure batter, no WK/AR/captain → no premium |
| Manish Pandey | ₹200L | Experience alone ≠ premium in 2025 |

### Mandatory Minimums (genuinely marquee only)
- Indian WK-Batter + 80+ matches + capped → **min ₹1200L**
- Indian All-Rounder + 80+ matches + capped → **min ₹1100L**
- Captain-material Indian (WK/top-order, 100+ matches) → **min ₹2000L** from captain-hungry teams
- Premier Indian pacer (30+ T20Is or 120+ IPL wickets) → **min ₹1200L**

---

## 🔄 RTM (Right to Match) System

```
Normal bidding → final highest bidder established
   ↓
If player's previous team has RTM cards:
   Previous team can MATCH the final price
      ↓ YES → previous team gets player, uses 1 RTM card
      ↓ NO (or previous team passes) → highest bidder wins

Highest bidder can also COUNTER-RAISE after RTM is attempted:
   Highest bidder raises → previous team must decide again
   RTM team raises → final resolution
```

RTM cards per team:
| Team | Retained | RTM Cards |
|------|----------|-----------|
| CSK | 5 | 1 |
| DC | 4 | 2 |
| GT | 5 | 1 |
| KKR | 6 | 0 |
| LSG | 5 | 1 |
| MI | 5 | 1 |
| PBKS | 2 | 4 |
| RCB | 3 | 3 |
| RR | 6 | 0 |
| SRH | 5 | 1 |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10, Flask |
| **AI / LLM** | `meta/llama-3.1-70b-instruct` via NVIDIA NIM API |
| **LLM Client** | `openai` Python SDK (NVIDIA-compatible endpoint) |
| **Data** | Pandas — player pool loaded from `ipl_auction.csv` |
| **Player parsing** | `pdfplumber` — `auction_parser.py` can parse official auction PDFs |
| **Frontend** | Vanilla JS, HTML5, CSS3 (no framework) |
| **Communication** | REST polling (fetch API) |
| **Fonts** | Google Fonts — Bebas Neue, Inter |
| **Hosting** | Flask dev server (`python app.py`) |

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- pip
- NVIDIA LLM API key (free tier available at [build.nvidia.com](https://build.nvidia.com))

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ipl-auction-simulator.git
cd ipl-auction-simulator

# 2. Create and activate virtual environment
python -m venv myenv

# Windows
myenv\Scripts\activate

# macOS/Linux
source myenv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. INSERT your NVIDIA LLM API key
# Open .env and replace the API_KEY value on line 12:
API_KEY = "your-nvapi-key-here"

# 5. Run the app
python app.py

# 6. Open in browser
# http://127.0.0.1:5000
```

### First-time flow
1. Select your franchise on the setup screen
2. Read the rules modal (RTM rules, squad limits, bidding increments)
3. View retained players for your team
4. Click **START AUCTION**
5. First player appears — place bids or pass; watch 9 AI agents compete in real time

---

## 📁 Project Structure

```
ipl-auction-simulator/
│
├── app.py                  # Main Flask app —backend logic 
|
|
├── auction.pdf      # Full player list data of all 574 players registered for IPL AUCTION 2025 
│
├── auction_parser.py       # PDF parser for IPL auction documents (pdfplumber)
│
├── ipl_auction.csv         # Full player pool Data with stats, roles, countries, base prices
│
├── templates/
│   └── index.html          # Frontend (~3000 lines)
│                           # Setup screen → Team select → Auction UI
│                           # Real-time bidding controls, squad panels, logs
│
|
└── README.md               # This file
```

---


## OUTPUT PHOTOS

<img width="2749" height="1510" alt="image" src="https://github.com/user-attachments/assets/f70d9561-d36b-4e1d-8ad8-48d918257f58" />


<img width="2313" height="1368" alt="image" src="https://github.com/user-attachments/assets/38fe8602-c323-450e-89d8-5197a33cab7b" />


<img width="1341" height="1337" alt="image" src="https://github.com/user-attachments/assets/dcaca249-cba1-4e8d-8800-1476ae9c9371" />


<img width="2877" height="1504" alt="image" src="https://github.com/user-attachments/assets/ec80c8a5-b721-4980-99ee-5923af3a8e43" />


<img width="2834" height="1438" alt="image" src="https://github.com/user-attachments/assets/9401e0a3-739f-42d2-889b-c3c240c574a5" />


<img width="1692" height="1331" alt="image" src="https://github.com/user-attachments/assets/068909bb-6edc-4fbf-9b28-9c93af0f4055" />


<p align="center">
<img alt="image1" src="https://github.com/user-attachments/assets/4691e7d4-d1d3-4c99-b112-a9120cf3e5d1" width="45" /><img alt="image2" src="https://github.com/user-attachments/assets/888d1a2a-5236-4f10-b589-3b9b063bfc5f" width="45" />
</p>

<img width="985" height="471" alt="image" src="https://github.com/user-attachments/assets/36d7e0b2-1449-4b65-a875-74b98087ac56" />


## 👋 Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

- Fork the repository.

- Create a new branch (git checkout -b feature/your-feature-name).

- Make your changes.

- Commit your changes (git commit -m 'Add your feature').

- Push to the branch (git push origin feature/your-feature-name).

- Open a Pull Request.

- Please ensure your code adheres to the project's styling and includes necessary tests if applicable.



----


*Built with ❤️ for cricket fans by a Die-hard Cricket Fan ❤️ Inspired by the real IPL 2025 Mega Auction & 2026 Mini Auction*




