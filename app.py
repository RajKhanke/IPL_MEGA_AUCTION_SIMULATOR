import os
import json
import random
import time
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__, template_folder='templates', static_folder='static')

# --- CONFIGURATION ---
API_KEY = os.getenv('API_KEY')
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=API_KEY)

# ─── IPL 2025 REALISTIC RETAINED SQUADS ───────────────────────────────────────
RETAINED_PLAYERS = {
    "CSK": [
        {"name": "Ravindra Jadeja",  "price": 1800, "role": "All-Rounder",  "is_overseas": False, "bat_style": "LHB", "bowl_style": "LA Slow Orthodox"},
        {"name": "Ruturaj Gaikwad",  "price": 1800, "role": "Batter",       "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Off Spin"},
        {"name": "Matheesha Pathirana","price":1300, "role": "Bowler",       "is_overseas": True,  "bat_style": "RHB", "bowl_style": "RA Fast"},
        {"name": "Shivam Dube",      "price": 1200, "role": "All-Rounder",  "is_overseas": False, "bat_style": "LHB", "bowl_style": "RA Fast Medium"},
         {"name": "MS Dhoni",         "price": 400, "role": "WK-Batter",    "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Medium"}
    ],
    "DC": [
        {"name": "Axar Patel",        "price": 1650, "role": "All-Rounder", "is_overseas": False, "bat_style": "LHB", "bowl_style": "LA Slow Orthodox"},
        {"name": "Kuldeep Yadav",     "price": 1350, "role": "Bowler",      "is_overseas": False, "bat_style": "LHB", "bowl_style": "LA Wrist Spin"},
        {"name": "Tristan Stubbs",    "price":  1000, "role": "WK-Batter",      "is_overseas": True,  "bat_style": "RHB", "bowl_style": ""},
        {"name": "Abhishek Porel",    "price":  400, "role": "WK-Batter",      "is_overseas": False,  "bat_style": "RHB", "bowl_style": ""}
    ],
    "GT": [
        {"name": "Rashid Khan",     "price": 1800, "role": "Bowler",       "is_overseas": True,  "bat_style": "RHB", "bowl_style": "RA Leg Spin"},
        {"name": "Shubman Gill",    "price": 1700, "role": "Batter",       "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Off Spin"},
        {"name": "Sai Sudharsan",   "price":  850, "role": "Batter",       "is_overseas": False, "bat_style": "LHB", "bowl_style": "LA Slow"},
        {"name": "Shahrukh Khan",   "price":  400, "role": "Batter",       "is_overseas": False, "bat_style": "RHB", "bowl_style": ""},
        {"name": "Rahul Tewatia",   "price":  400, "role": "All-Rounder",  "is_overseas": False, "bat_style": "LHB", "bowl_style": "RA Leg Spin"}
    ],
    "KKR": [
        {"name": "Rinku Singh",          "price": 1300, "role": "Batter",      "is_overseas": False, "bat_style": "LHB", "bowl_style": ""},
        {"name": "Varun Chakaravarthy",  "price": 1200, "role": "Bowler",      "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Mystery Spin"},
        {"name": "Sunil Narine",         "price": 1200, "role": "All-Rounder", "is_overseas": True,  "bat_style": "LHB", "bowl_style": "RA Off Spin"},
        {"name": "Andre Russell",        "price": 1200, "role": "All-Rounder", "is_overseas": True,  "bat_style": "RHB", "bowl_style": "RA Fast Medium"},
        {"name": "Harshit Rana",         "price":  400, "role": "Bowler",      "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Fast"},
        {"name": "Ramandeep Singh",      "price":  400, "role": "All-Rounder", "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Fast Medium"},
    ],
    "LSG": [
        {"name": "Nicholas Pooran", "price": 2100, "role": "WK-Batter",   "is_overseas": True,  "bat_style": "LHB", "bowl_style": ""},
        {"name": "Ravi Bishnoi",    "price": 1100, "role": "Bowler",      "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Leg Spin"},
        {"name": "Mayank Yadav",    "price": 1100, "role": "Bowler",      "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Fast"},
        {"name": "Mohsin Khan",     "price":  400, "role": "Bowler",      "is_overseas": False, "bat_style": "RHB", "bowl_style": "LA Fast Medium"},
        {"name": "Ayush Badoni",    "price":  400, "role": "Batter",      "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Off Spin"},
    ],
    "MI": [
        {"name": "Jasprit Bumrah",    "price": 1800, "role": "Bowler",      "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Fast"},
        {"name": "Suryakumar Yadav",  "price": 1635, "role": "Batter",     "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Medium"},
        {"name": "Hardik Pandya",     "price": 1635, "role": "All-Rounder","is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Fast Medium"},
        {"name": "Rohit Sharma",      "price": 1630, "role": "Batter",     "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Off Spin"},
        {"name": "Tilak Varma",       "price": 800, "role": "Batter",     "is_overseas": False, "bat_style": "LHB", "bowl_style": "LA Slow"},
    ],
    "PBKS": [
        {"name": "Shashank Singh",    "price":  500, "role": "Batter",     "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Off Spin"},
        {"name": "Prabhsimran Singh", "price":  400, "role": "WK-Batter",  "is_overseas": False, "bat_style": "RHB", "bowl_style": ""},
    ],
    "RCB": [
        {"name": "Virat Kohli",    "price": 2100, "role": "Batter",  "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Medium"},
        {"name": "Rajat Patidar", "price": 1100, "role": "Batter",  "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Off Spin"},
        {"name": "Yash Dayal",    "price":  500, "role": "Bowler",  "is_overseas": False, "bat_style": "LHB", "bowl_style": "LA Fast Medium"},
    ],
    "RR": [
        {"name": "Sanju Samson",    "price": 1800, "role": "WK-Batter",  "is_overseas": False, "bat_style": "RHB", "bowl_style": ""},
        {"name": "Yashasvi Jaiswal","price": 1800, "role": "Batter",     "is_overseas": False, "bat_style": "LHB", "bowl_style": "LA Slow"},
        {"name": "Riyan Parag",     "price": 1400, "role": "Batter",     "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Leg Spin"},
        {"name": "Dhruv Jurel",     "price": 1400, "role": "WK-Batter",  "is_overseas": False, "bat_style": "RHB", "bowl_style": ""},
        {"name": "Shimron Hetmyer", "price": 1100, "role": "Batter",     "is_overseas": True,  "bat_style": "LHB", "bowl_style": ""},
        {"name": "Sandeep Sharma",  "price": 400, "role": "Bowler",     "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Fast Medium"}
    ],
    "SRH": [
        {"name": "Heinrich Klaasen",     "price": 2300, "role": "WK-Batter",   "is_overseas": True,  "bat_style": "RHB", "bowl_style": ""},
        {"name": "Pat Cummins",          "price": 1800, "role": "Bowler",      "is_overseas": True,  "bat_style": "RHB", "bowl_style": "RA Fast"},
        {"name": "Travis Head",          "price": 1400, "role": "Batter",      "is_overseas": True,  "bat_style": "LHB", "bowl_style": "RA Off Spin"},
        {"name": "Abhishek Sharma",      "price": 1400, "role": "Batter",      "is_overseas": False, "bat_style": "LHB", "bowl_style": "LA Slow"},
        {"name": "Nitish Kumar Reddy",   "price":  600, "role": "All-Rounder", "is_overseas": False, "bat_style": "RHB", "bowl_style": "RA Fast Medium"},
    ],
}

# Realistic post-retention budgets (in Lakhs)
INITIAL_BUDGETS = {
    "CSK": 5500, "DC": 7300, "GT": 6900, "KKR": 5100,
    "LSG": 6900, "MI": 4500, "PBKS": 11050, "RCB": 8300,
    "RR": 4100, "SRH": 4500,
}

# Team colors for UI
TEAM_COLORS = {
    "CSK":  {"primary": "#F5C518", "secondary": "#0D3B76", "accent": "#F5C518"},
    "DC":   {"primary": "#0095D8", "secondary": "#FF5E5E", "accent": "#0095D8"},
    "GT":   {"primary": "#5E5B6B", "secondary": "#E6C200", "accent": "#E6C200"},
    "KKR":  {"primary": "#6B4C9A", "secondary": "#FFD700", "accent": "#FFD700"},
    "LSG":  {"primary": "#A0C3F1", "secondary": "#002147", "accent": "#A0C3F1"},
    "MI":   {"primary": "#0066CC", "secondary": "#FFD700", "accent": "#FFD700"},
    "PBKS": {"primary": "#ED1B24", "secondary": "#DCDDDF", "accent": "#DCDDDF"},
    "RCB":  {"primary": "#EC1C24", "secondary": "#000000", "accent": "#F7A721"},
    "RR":   {"primary": "#254AA5", "secondary": "#FF69B4", "accent": "#FF69B4"},
    "SRH":  {"primary": "#F26522", "secondary": "#000000", "accent": "#F26522"},
}

# ─── HOME GROUND + PITCH PROFILE ──────────────────────────────────────────────
# Influences spin vs pace weighting for each team - REAL IPL STADIUM CHARACTERISTICS
TEAM_PITCH_PROFILE = {
    "CSK":  {"ground": "Chepauk, Chennai",     "type": "spin_paradise",    "spin_pref": 0.90, "pace_pref": 0.50, "bat_first": True, "desc": "Spin graveyard, technical batsmen needed, 120-150 scores, 4 spinners normal"},
    "DC":   {"ground": "Arun Jaitley, Delhi",  "type": "spin_friendly",         "spin_pref": 0.75, "pace_pref": 0.65, "bat_first": False, "desc": "Spin-friendly with dew, mix of explosive + technical batsmen, batting depth critical"},
    "GT":   {"ground": "Narendra Modi, Ahmd",  "type": "big_ground_flat",     "spin_pref": 0.65, "pace_pref": 0.70, "bat_first": False, "desc": "Large boundaries, muscular power needed, flat with bounce, pace helpful"},
    "KKR":  {"ground": "Eden Gardens, Kolkata","type": "bowling_paradise",    "spin_pref": 0.60, "pace_pref": 0.85, "bat_first": False, "desc": "Swing/seam heaven, 140-150 scores, pace bowlers dominate, technical batsmen needed"},
    "LSG":  {"ground": "BRSABV, Lucknow",      "type": "unpredictable", "spin_pref": 0.70, "pace_pref": 0.70, "bat_first": False, "desc": "Unpredictable pitch - 200+ or 120-130, needs balanced team with all types"},
    "MI":   {"ground": "Wankhede, Mumbai",     "type": "dual_nature",    "spin_pref": 0.65, "pace_pref": 0.75, "bat_first": False, "desc": "Red soil=pace, Black soil=spin, large dew factor, 170-180 scores, chasing key"},
    "PBKS": {"ground": "IS Bindra, Mohali",     "type": "batting_heaven",        "spin_pref": 0.40, "pace_pref": 0.50, "bat_first": False, "desc": "Pure flat track, batting paradise, deadliest for bowlers, 200+ scores"},
    "RCB":  {"ground": "Chinnaswamy, Bengaluru","type":"batting_paradise",  "spin_pref": 0.50, "pace_pref": 0.60, "bat_first": False, "desc": "Explosive batters paradise, hard hitters crucial, death specialists needed"},
    "RR":   {"ground": "Sawai MS, Jaipur",     "type": "spin_to_win",         "spin_pref": 0.85, "pace_pref": 0.50, "bat_first": True, "desc": "Very large ground, spin to win is key, technical batsmen needed"},
    "SRH":  {"ground": "Rajiv Gandhi, Hydrbd", "type": "flat_high_scoring",    "spin_pref": 0.60, "pace_pref": 0.80, "bat_first": False, "desc": "Flat track, very high scoring, early bounce and swing, premium fast bowlers + explosive batters"},
}

# ─── PLAYING XI ROLE REQUIREMENTS ─────────────────────────────────────────────
# Each team's ideal XI composition they're building toward
# These are MINIMUM counts in the 25-man squad to support a balanced XI
SQUAD_COMPOSITION_TARGETS = {
    # role: (min_in_squad, max_in_squad, xi_slots, priority)
    "WK-Batter":    {"min": 2,  "max": 3,  "xi_slots": 1, "priority": "critical"},
    "Batter":       {"min": 5,  "max": 8,  "xi_slots": 4, "priority": "high"},
    "All-Rounder":  {"min": 3,  "max": 5,  "xi_slots": 2, "priority": "high"},
    "Bowler":       {"min": 5,  "max": 8,  "xi_slots": 4, "priority": "high"},
}

# ─── DETAILED TEAM STRATEGIES ─────────────────────────────────────────────────
TEAM_STRATEGIES = {
    "CSK": {
        "persona": "Chennai Super Kings - 'Daddy's Army'. Trust experience over youth (30+). Chepauk is spin paradise. NZ overseas preference (coach influence). Budget-friendly, distribute evenly, never overpay. Complete 25-squad with domestic backups. All-rounders critical.",
        "home_pitch": "Chepauk SPIN TRACK - spin graveyard, 120-150 scores, 4 spinners normal, technical batsmen",
        "xi_template": "Technical openers + Experienced middle-order + Dhoni(WK/finisher) + Jadeja(spin AR) + 3-4 spinners + Pathirana + 1 pacer",
        "captain_profile": "Ruturaj Gaikwad is captain - experienced team, quality spinners, all-rounders.",
        "bidding_style": "conservative_experienced",
        "spend_philosophy": "Budget-friendly balanced distribution. Trust experience (30+ age). NZ overseas preference. Don't spend big on single player. Complete 25-member squad with domestic uncapped backups at base price. All-rounders are focus area.",
        "urgency_roles": ["Spinner", "All-Rounder", "Technical Batter", "NZ Player", "Experienced Player"],
        "avoid_roles": ["Overseas Pace Bowler", "Young Uncapped"],
        "overseas_preference": ["New Zealand", "Australia"],
        "budget_tiers": {"star": 1000, "quality": 600, "utility": 250, "filler": 40},
        "squad_target": 25,  # Always complete full squad
        "overseas_slots_remaining": None,
    },
    "DC": {
        "persona": "Delhi Capitals - Young Guns. Go for fancy young talented overseas players. Price spoilers - bid to ruin others' party even if not interested. Big Indian names, young firepower. Need captain desperately. All-rounder focus.",
        "home_pitch": "Delhi - spin-friendly with dew, explosive + technical batsmen mix, batting depth critical",
        "xi_template": "Explosive overseas openers + Young Indian stars + Axar(AR) + Kuldeep(spin) + Young Indian pacers + 1-2 overseas pace/spin",
        "captain_profile": "NEED CAPTAIN URGENTLY - Will overpay for leadership. Young team needs experienced head.",
        "bidding_style": "aggressive_rebuild",
        "spend_philosophy": "Aggressive for young overseas talent and big Indian names. Price spoiler tactics - bid to increase others' costs. Focus on all-rounders. Complete squad with cheap domestic backups.",
        "urgency_roles": ["Captain", "Young Overseas Talent", "All-Rounder", "Big Indian Name"],
        "avoid_roles": ["Daddy's Army (30+)"],
        "overseas_preference": ["England", "Australia", "New Zealand"],
        "budget_tiers": {"star": 1500, "quality": 800, "utility": 300, "filler": 50},
        "squad_target": 22,
        "overseas_slots_remaining": None,
    },
    "GT": {
        "persona": "Gujarat Titans - Nehra's Bowling Factory. Excellence in fast bowling variety (international + domestic). Spend heavy on bowling (BEST IN CLASS). Go for big Indian names, all-rounders, spinners. Moneyball for batting. Balanced to aggressive.",
        "home_pitch": "Ahmedabad - big ground, muscular power needed, flat with pace help, 180-200 scores",
        "xi_template": "Shubman(opener) + Muscular batters + Rashid(spin) + All-rounders + 4-5 quality pace bowlers (variety)",
        "captain_profile": "Shubman Gill captain. Need express pace, all-rounders, spinners.",
        "bidding_style": "balanced_aggressive",
        "spend_philosophy": "AGGRESSIVE on BOWLERS (top priority). Spend 60% on bowling attack. Big Indian names welcome. All-rounders critical. Moneyball for batting depth. Complete squad 20-23 players.",
        "urgency_roles": ["Fast Bowler", "All-Rounder", "Big Indian Name", "Spinner", "Death Specialist"],
        "avoid_roles": ["Pure Batter"],
        "overseas_preference": ["Pace Bowlers - any country"],
        "budget_tiers": {"star": 1200, "quality": 700, "utility": 250, "filler": 60},
        "squad_target": 22,
        "overseas_slots_remaining": None,
    },
    "KKR": {
        "persona": "Kolkata Knight Riders - Overseas WK + Muscular ARs. Eden is bowling paradise for pacers. Go ANY amount for ex-players (unbalanced). NEED CAPTAIN. Spinners are strength. Left-arm pacers priority. Hardly finish with 18-19 players.",
        "home_pitch": "Kolkata - bowling paradise, swing/seam, 140-150 scores, pace dominates",
        "xi_template": "Narine(opener/AR) + Overseas WK + Technical batters + Russell(AR/finisher) + Strong spinners + Left-arm pacers + Overseas pace",
        "captain_profile": "NEED CAPTAIN - will overpay. Ex-players loyalty at any cost.",
        "bidding_style": "ex_player_loyalty",
        "spend_philosophy": "UNBALANCED - 80% on playing XI. Overseas WK mandatory. Ex-KKR players at ANY price. Strong spinners investment. Left-arm pacers obsession. Muscular all-rounders. Squad 18-19 players only.",
        "urgency_roles": ["Overseas WK", "Captain", "Ex-KKR Player", "Muscular All-Rounder", "Strong Spinner", "Left-Arm Pacer"],
        "avoid_roles": ["Pure Batter"],
        "overseas_preference": ["West Indies", "England", "Australia"],
        "budget_tiers": {"star": 2000, "quality": 600, "utility": 200, "filler": 40},
        "squad_target": 19,  # Unbalanced squad
        "overseas_slots_remaining": None,
    },
    "LSG": {
        "persona": "Lucknow Super Giants - Marquee Obsession + Poor Auction. Spend 50% purse on 2-3 marquee stars (VERY UNBALANCED). Bold calls on injury-prone players. Maharashtra domestic talent. AUS/SA overseas focus. Experienced-middle-experience team. NEED CAPTAIN. 18-20 squad.",
        "home_pitch": "Lucknow - unpredictable (200+ or 120-130), needs balanced team with all types",
        "xi_template": "Marquee opener + Marquee middle-order + Technical anchor + All-rounders + Balanced bowling attack",
        "captain_profile": "NEED CAPTAIN DESPERATELY - will overpay for experienced leader.",
        "bidding_style": "marquee_unbalanced",
        "spend_philosophy": "UNBALANCED AUCTION - Spend 50% on 2-3 MARQUEE STARS. Bold injury gambles. Maharashtra talent focus. AUS/SA overseas. Build experienced team. Rush to complete 18-20 players with cheap backups.",
        "urgency_roles": ["Marquee Star", "Captain", "Experienced Player", "All-Rounder", "Maharashtra Player"],
        "avoid_roles": ["Young Uncapped"],
        "overseas_preference": ["Australia", "South Africa"],
        "budget_tiers": {"star": 2700, "quality": 500, "utility": 150, "filler": 40},
        "squad_target": 19,  # Unbalanced squad
        "overseas_slots_remaining": None,
    },
    "MI": {
        "persona": "Mumbai Indians - Time-Wasters + Ex-Player Loyalty. Wankhede dual nature (red=pace, black=spin). 80% time delaying at table. Focus on supporting previous year players. Bid ONLY for past MI players. Highly unbalanced team - 80% on XI. Pick weird domestic players and make them stars. SL/ENG/AUS/NZ overseas. 20-22 squad with many all-rounders.",
        "home_pitch": "Wankhede, Mumbai - dual nature (red soil=pace, black soil=spin), large dew, 170-180 scores, chasing key",
        "xi_template": "Rohit(opener) + Opener + Surya(middle) + Hardik(AR) + Tilak + Multiple ARs + Bumrah + Pace/spin",
        "captain_profile": "Hardik Pandya captain. Need ex-MI players back + weird domestic finds.",
        "bidding_style": "budget_snipers",
        "spend_philosophy": "TIGHT BUDGET - Max 600L per player. 80% time time-passing. Focus on ex-MI players ONLY. Will stretch for past MI players. Pick weird domestic and develop. Highly unbalanced - 80% on playing XI. Complete 20-22 squad with lots of all-rounders.",
        "urgency_roles": ["Ex-MI Player", "All-Rounder", "Weird Domestic Find", "Overseas Bowler"],
        "avoid_roles": ["Expensive Indian Star without MI history"],
        "overseas_preference": ["Sri Lanka", "England", "Australia", "New Zealand"],
        "budget_tiers": {"star": 1000, "quality":400, "utility": 100, "filler": 40},
        "squad_target": 21,  # 20-22 range
        "overseas_slots_remaining": None,
    },
    "PBKS": {
        "persona": "Punjab Kings - RICHEST (110Cr) + Fresh Start Every Auction. Mohali is pure flat track batting heaven, deadliest for bowlers. Build complete team with captain. Go for BIG FANCY MARQUEE STARS. Always complete 25-member squad (90%). Backup focus on Punjab/NE/Vidarbha talent. AUS overseas preference (coach). Equal focus all departments.",
        "home_pitch": "Mohali - pure flat track, batting paradise, 200+ scores, deadliest for bowlers",
        "xi_template": "2 aggressive openers + Captain + Middle-order hitters + WK + Multiple ARs + Quality pace + Spin variety",
        "captain_profile": "NEED CAPTAIN - Will pay 2500-3000L+ for Pant/Iyer/KL type leader.",
        "bidding_style": "ultra_aggressive_big_spender",
        "spend_philosophy": "SPEND BIG AGGRESSIVELY on MARQUEE STARS. 110Cr purse. Will dominate early sets. Enter every major war. Spend 60-70% on 4-5 stars, then complete 25-squad with cheap Punjab/NE/Vidarbha backups at base price. AUS overseas preference. Equal focus all departments.",
        "urgency_roles": ["Marquee Star", "Captain", "Fancy Big Name", "Opener", "Overseas Pacer", "WK-Batter"],
        "avoid_roles": [],  # Needs everything
        "overseas_preference": ["Australia", "England", "South Africa"],
        "budget_tiers": {"star": 2500, "quality": 1200, "utility": 400, "filler": 40},
        "squad_target": 25,  # Always completes full squad
        "overseas_slots_remaining": None,
    },
    "RCB": {
        "persona": "Royal Challengers Bengaluru - Budget-Friendly Balanced. Chinnaswamy is batting paradise (explosive batters, death specialists). ENG/WI firepower + Kannada domestic talent. Distribute money evenly, don't go by big names, make most balanced team. NEED CAPTAIN. All-rounders focus.",
        "home_pitch": "Chinnaswamy, Bengaluru - batting paradise, explosive batters crucial, death specialists needed, tiny boundaries",
        "xi_template": "Kohli + Explosive opener + No.3 + Power hitters + Captain AR + WK + Death bowlers + Variety",
        "captain_profile": "NEED CAPTAIN - budget-friendly leader, all-rounder preferred.",
        "bidding_style": "balanced_budget_friendly",
        "spend_philosophy": "Budget-friendly BALANCED distribution. Don't overpay for big names. Make most balanced team possible. ENG/WI overseas firepower. Kannada domestic talent. All-rounders critical focus area. Complete squad 22-24 players.",
        "urgency_roles": ["Captain", "All-Rounder", "Death Bowler", "Explosive Batter", "ENG Player", "WI Player", "Kannada Player"],
        "avoid_roles": ["Pure Spinner"],
        "overseas_preference": ["England", "West Indies"],
        "budget_tiers": {"star": 1200, "quality": 700, "utility": 300, "filler": 50},
        "squad_target": 23,
        "overseas_slots_remaining": None,
    },
    "RR": {
        "persona": "Rajasthan Royals - Sangakkara+Dravid Moneyball Mastery. Jaipur is huge ground, spin-to-win. Pure specialists focus (batters & bowlers), very less all-rounders. ENG/SA/AUS overseas. Target BBL/Hundred/U19 stars. Young team + invest big in established Indian youngsters (Samson, Parag types). ALWAYS 25-member squad. Moneyball but will break barriers like Namita of Shark Tank if needed. UNBALANCED - spend on 3-4 stars.",
        "home_pitch": "Jaipur - very large ground, spin-to-win is key, technical batsmen needed",
        "xi_template": "Samson(WK/opener) + Jaiswal(opener) + Parag + Pure batters + Pure bowlers (spinners priority) + Minimal ARs",
        "captain_profile": "Samson is captain. Young established Indian stars focus.",
        "bidding_style": "extreme_budget_save",
        "spend_philosophy": "UNBALANCED - spend 60-70% on 3-4 established Indian youngsters. Then moneyball for rest. Target BBL/Hundred/U19 emerging stars. Pure specialists (batters & bowlers), minimal ARs. ENG/SA/AUS overseas. Will break barriers if truly want someone (Namita style). ALWAYS complete 25-member squad. Spinners are critical focus.",
        "urgency_roles": ["Pure Specialist", "Established Indian Youngster", "Spinner", "BBL/Hundred Star", "U19 Star"],
        "avoid_roles": ["All-Rounder", "Daddy's Army"],
        "overseas_preference": ["England", "South Africa", "Australia"],
        "budget_tiers": {"star": 2000, "quality": 400, "utility": 150, "filler": 40},
        "squad_target": 25,  # Always full squad
        "overseas_slots_remaining": None,
    },
    "SRH": {
        "persona": "Sunrisers Hyderabad - DEVILS (Explosive Unbalanced Strategy). Hyderabad flat track, very high scoring, early bounce/swing. HIGHLY UNBALANCED - go for firepower ultra explosive batting + aggressive bowling. Spend 80% on playing XI with not much good backups. Prefer SHORT SQUAD 18-20 members. Overseas batters are PRIORITY (best overseas batting lineup). Refer real SRH devils style - all-out attack.",
        "home_pitch": "Rajiv Gandhi, Hyderabad - flat track, very high scoring ground, early bounce and swing, premium fast bowlers + explosive batters",
        "xi_template": "Explosive overseas openers + Firepower batters + Ultra-aggressive middle-order + Premium fast bowlers + Attacking variety",
        "captain_profile": "Need firepower captain or explosive overseas leader.",
        "bidding_style": "ultra_aggressive_unbalanced",
        "spend_philosophy": "DEVILS STRATEGY - HIGHLY UNBALANCED. Spend 80% on 4-5 EXPLOSIVE players. Prioritize overseas batters (best batting lineup). Aggressive bowling attack. Don't care about backups - SHORT SQUAD 18-20 players. All-out attack, no balance needed. Go big or go home.",
        "urgency_roles": ["Explosive Overseas Batter", "Premium Fast Bowler", "Firepower Player", "Aggressive All-Rounder"],
        "avoid_roles": ["Technical Anchor", "Backup Players"],
        "overseas_preference": ["Explosive batters - any country"],
        "budget_tiers": {"star": 2500, "quality": 800, "utility": 200, "filler": 40-30},
        "squad_target": 19-22,  # Short unbalanced squad
        "overseas_slots_remaining": None,
    },
}

def build_initial_teams():
    teams = {}
    for team, retained in RETAINED_PLAYERS.items():
        os_count = sum(1 for p in retained if p["is_overseas"])
        budget = INITIAL_BUDGETS[team]
        teams[team] = {
            "budget": budget,
            "overseas_count": os_count,
            "total_players": len(retained),
            "squad": retained.copy(),
            "colors": TEAM_COLORS[team],
            "strategy": TEAM_STRATEGIES[team],
            "pitch": TEAM_PITCH_PROFILE[team],
        }
    return teams

def load_players():
    csv_path = 'ipl_auction.csv'
    if not os.path.exists(csv_path):
        csv_path = '/mnt/user-data/uploads/ipl_auction.csv'
    if not os.path.exists(csv_path):
        return []
    
    df = pd.read_csv(csv_path).fillna('')
    
    # Build full-name set of all retained players for exact matching
    retained_full_names = set()
    for team, squad in RETAINED_PLAYERS.items():
        for p in squad:
            retained_full_names.add(p["name"].lower())
    
    players = []
    for _, row in df.iterrows():
        try:
            fname = str(row.get('First Name', '')).strip()
            lname = str(row.get('Surname', '')).strip()
            full_name = f"{fname} {lname}".strip()
            full_lower = full_name.lower()
            
            # Skip retained players (exact full name match)
            if full_lower in retained_full_names:
                continue
            # Also check first+last name match to avoid suffix variations
            skip = False
            for rname in retained_full_names:
                r_parts = rname.split()
                p_parts = full_lower.split()
                if len(r_parts) >= 2 and len(p_parts) >= 2:
                    if r_parts[-1] == p_parts[-1] and r_parts[0] == p_parts[0]:
                        skip = True
                        break
            if skip:
                continue
            
            # Base price
            price_col = next((c for c in df.columns if "Reserve" in c), None)
            raw_price = row[price_col] if price_col else ''
            try:
                base = int(float(str(raw_price))) if str(raw_price).strip() not in ('', 'nan') else 30
            except:
                base = 30
            
            country = str(row.get('Country', 'India')).strip()
            if not country or country == 'nan':
                country = 'India'
            
            specialism = str(row.get('Specialism', 'Player')).strip()
            role_map = {
                'BATTER': 'Batter', 'BOWLER': 'Bowler',
                'ALL-ROUNDER': 'All-Rounder', 'WICKETKEEPER': 'WK-Batter'
            }
            role = role_map.get(specialism.upper(), specialism)
            
            ipl_matches = str(row.get('IPL', '0')).strip()
            try:
                ipl_int = int(float(ipl_matches)) if ipl_matches not in ('', 'nan') else 0
            except:
                ipl_int = 0
            
            capped = str(row.get('C/U/A', '')).strip()
            is_capped = 'capped' in capped.lower() if capped else False
            
            bat_style = str(row.get('Unnamed: 10', '')).strip()
            bowl_style = str(row.get('Unnamed: 11', '')).strip()
            
            prev_teams = str(row.get('Previous IPLTeam(s)', '')).strip()
            last_team = str(row.get('2024\nTeam', '')).strip()
            if not last_team or last_team == 'nan':
                last_team = ''
            
            players.append({
                "id": int(row.get('List Sr.No.', 0)),
                "set": str(row.get('2025 Set', 'UNK')).strip(),
                "set_no": int(row.get('Set No.', 0)) if str(row.get('Set No.', '')).strip() not in ('', 'nan') else 0,
                "name": full_name,
                "country": country,
                "role": role,
                "base_price": base,
                "is_overseas": country.lower() != "india",
                "is_capped": is_capped,
                "bat_style": bat_style if bat_style not in ('nan', '') else 'RHB',
                "bowl_style": bowl_style if bowl_style not in ('nan', '') else '',
                "stats": {
                    "ipl_matches": ipl_int,
                    "prev_teams": prev_teams,
                    "last_team": last_team,
                },
                "age": str(row.get('Age', '')).strip(),
            })
        except Exception as e:
            continue
    
    from collections import defaultdict
    set_groups = defaultdict(list)
    for p in players:
        set_groups[p["set_no"]].append(p)
    
    ordered = []
    for set_no in sorted(set_groups.keys()):
        group = set_groups[set_no]
        random.shuffle(group)
        ordered.extend(group)
    
    return ordered

PLAYERS_POOL_MASTER = load_players()

# ─── GAME STATE ───────────────────────────────────────────────────────────────
# RTM Cards: 6 - retentions = RTM cards available
RETAINED_COUNTS = {"CSK": 5, "DC": 4, "GT": 5, "KKR": 6, "LSG": 5, "MI": 5, "PBKS": 2, "RCB": 3, "RR": 6, "SRH": 5}
RTM_CARDS_INITIAL = {team: max(0, 6 - count) for team, count in RETAINED_COUNTS.items()}

game_state = {
    "teams": build_initial_teams(),
    "players_pool": list(PLAYERS_POOL_MASTER),
    "current_player": None,
    "current_bid": 0,
    "current_bidder": None,
    "ai_valuations": {},
    "sold_history": [],
    "unsold_players": [],
    "additional_set": [],  # Unsold players come back at the end
    "auction_log_cards": [],  # Player cards for completed auctions
    "bid_history": [],
    "user_team": "RCB",
    "user_passed": False,
    "total_sold": 0,
    "total_unsold": 0,
    "auction_started": False,
    "round_num": 0,
    "rtm_cards_available": dict(RTM_CARDS_INITIAL),
    "rtm_in_progress": False,
    "rtm_eligible_team": None,
    "rtm_highest_bidder": None,
    "rtm_highest_bid": 0,
    "_prev_bidder": None,  # For tracking bidding battles
    "_battle_stall_rounds": 0,  # Counter for battle stalls
}

def get_increment(price):
    """
    IPL Auction Realistic Bid Increment System:
    Base < 200L: Increments of ₹10L (110, 120, 130...200)
    200L-500L: Increments of ₹25L (225, 250, 275, 300...500)  
    500L-1000L: Increments of ₹50L (550, 600, 650...1000)
    1000L+: Increments of ₹50L (1050, 1100, 1150...)
    """
    if price < 200:
        return 10
    elif price < 500:
        return 25
    elif price < 1000:
        return 50
    else:
        return 50

def create_player_card(player, winner, price, status="sold"):
    """Create a player card for auction log"""
    import datetime
    player_card = {
        "card_id": len(game_state['auction_log_cards']) + 1,
        "name":        player['name'],
        "role":        player['role'],
        "team":        winner or "UNSOLD",
        "price":       price if winner else 0,
        "base_price":  player['base_price'],
        "is_overseas": player['is_overseas'],
        "country":     player['country'],
        "set":         player.get('set', 'Unknown'),
        "status":      status,
        "color":       TEAM_COLORS.get(winner, {}).get("primary", "#666") if winner else "#666",
        "timestamp":   datetime.datetime.now().strftime('%H:%M:%S'),
        "player":      player,
        "bid_log":     [b for b in game_state.get('bid_history', []) if b.get('player_name') == player.get('name')],
    }
    game_state['auction_log_cards'].insert(0, player_card)  # Most recent first
    return player_card

# ─── SQUAD ANALYSIS HELPERS ───────────────────────────────────────────────────
def analyse_squad(team_name):
    """
    Deep analysis of current squad for a team.
    Returns gaps, counts, budget pressure, overseas status.
    """
    t = game_state['teams'][team_name]
    squad = t['squad']
    
    # Count by role
    wk_count   = sum(1 for p in squad if 'WK' in p.get('role', '') or p.get('role','') == 'WK-Batter')
    bat_count  = sum(1 for p in squad if p.get('role','') == 'Batter')
    ar_count   = sum(1 for p in squad if 'All-Rounder' in p.get('role',''))
    bowl_count = sum(1 for p in squad if p.get('role','') == 'Bowler')
    os_count   = t['overseas_count']
    total      = t['total_players']
    budget     = t['budget']
    remaining_spots = 25 - total
    remaining_os_spots = 8 - os_count
    
    # Bat-style diversity (LHB vs RHB)
    lhb_count = sum(1 for p in squad if 'LHB' in p.get('bat_style','') or 'Left' in p.get('bat_style',''))
    rhb_count = sum(1 for p in squad if 'RHB' in p.get('bat_style',''))
    
    # Bowling type breakdown
    spin_bowlers  = sum(1 for p in squad if any(k in p.get('bowl_style','') for k in ['Spin','spin','Off Spin','Leg Spin','Slow','Unorthodox','Orthodox']))
    pace_bowlers  = sum(1 for p in squad if any(k in p.get('bowl_style','') for k in ['Fast','Medium','Pace','pace']))
    
    # Batting role breakdown (total batting resources including WK and batting ARs)
    # Count primary batters (role=Batter or WK-Batter)
    pure_batters = sum(1 for p in squad if p.get('role','') in ['Batter', 'WK-Batter'])
    # Batting ARs who primarily add batting depth
    batting_ars = sum(1 for p in squad if 'All-Rounder' in p.get('role','') and p.get('bowl_style','') in ['', 'RIGHT ARM Off Spin', 'RIGHT ARM Leg Spin'])
    total_batting_depth = pure_batters + batting_ars  # Total batting resources for XI
    
    # Gaps vs SQUAD_COMPOSITION_TARGETS
    gaps = {}
    for role, targets in SQUAD_COMPOSITION_TARGETS.items():
        if role == "WK-Batter":   current = wk_count
        elif role == "Batter":    current = bat_count
        elif role == "All-Rounder": current = ar_count
        elif role == "Bowler":    current = bowl_count
        else: current = 0
        
        shortage = max(0, targets['min'] - current)
        gaps[role] = {
            "current": current,
            "min_needed": targets['min'],
            "max_wanted": targets['max'],
            "shortage": shortage,
            "priority": targets['priority'] if shortage > 0 else "none"
        }
    
    # Budget pressure: how much per remaining slot
    budget_per_slot = budget / remaining_spots if remaining_spots > 0 else 0
    budget_pressure = "critical" if budget_per_slot < 50 else "high" if budget_per_slot < 150 else "medium" if budget_per_slot < 400 else "low"
    
    # Critical gaps (roles where we're below minimum)
    critical_gaps = [role for role, g in gaps.items() if g['shortage'] > 0]
    
    return {
        "wk": wk_count, "batters": bat_count, "all_rounders": ar_count, "bowlers": bowl_count,
        "total": total, "overseas": os_count,
        "remaining_spots": remaining_spots, "remaining_os_spots": remaining_os_spots,
        "lhb": lhb_count, "rhb": rhb_count,
        "spin_bowlers": spin_bowlers, "pace_bowlers": pace_bowlers,
        "pure_batters": pure_batters, "batting_ars": batting_ars, "total_batting_depth": total_batting_depth,
        "budget": budget, "budget_per_slot": round(budget_per_slot),
        "budget_pressure": budget_pressure,
        "gaps": gaps, "critical_gaps": critical_gaps,
    }

def player_fits_xi_need(player, squad_analysis, team_name):
    """
    Score 0.0-3.0 of how critically this player fills a playing XI gap.
    Higher = more urgently needed.
    """
    role = player.get('role','')
    bat_style = player.get('bat_style','')
    bowl_style = player.get('bowl_style','')
    is_overseas = player.get('is_overseas', False)
    pitch = TEAM_PITCH_PROFILE[team_name]
    sa = squad_analysis
    strat = TEAM_STRATEGIES[team_name]
    
    score = 0.0
    
    # 1. Critical role gaps (shortage > 0)
    role_key = role if role in SQUAD_COMPOSITION_TARGETS else None
    if role_key and sa['gaps'].get(role_key, {}).get('shortage', 0) > 0:
        shortage = sa['gaps'][role_key]['shortage']
        score += 1.0 * shortage  # 1.0 per missing player in critical role
    
    # 2. Role fills urgent strategy need
    urgency_match = any(
        urg.lower() in (role + ' ' + bowl_style + ' ' + bat_style).lower()
        for urg in strat.get('urgency_roles', [])
    )
    if urgency_match:
        score += 0.8
    
    # 3. SQUAD SATURATION CHECKS - Don't bid if already have enough
    is_spinner = any(k in bowl_style for k in ['Spin','Slow','Orthodox','Unorthodox','Leg Spin','Off Spin'])
    is_pacer   = any(k in bowl_style for k in ['Fast','Medium','Pace'])
    is_batter  = role in ['Batter', 'WK-Batter'] or 'Batter' in role
    is_batting_ar = 'All-Rounder' in role and bowl_style in ['', 'RIGHT ARM Off Spin', 'RIGHT ARM Leg Spin']
    
    # Bowling type saturation - reduce score if already have too many
    if is_spinner and sa['spin_bowlers'] >= 4:
        score *= 0.3  # Already have 4+ spinners, don't need more
    elif is_spinner and sa['spin_bowlers'] >= 3:
        score *= 0.6  # Have 3 spinners, somewhat saturated
    
    if is_pacer and sa['pace_bowlers'] >= 6:
        score *= 0.3  # Already have 6+ pacers, don't need more
    elif is_pacer and sa['pace_bowlers'] >= 5:
        score *= 0.6  # Have 5 pacers, somewhat saturated
    
    # Batting depth saturation - XI needs ~7 batters (including WK and ARs)
    # Saturated if team has 8-9+ batting resources (playing XI set, now focusing on backups)
    if (is_batter or is_batting_ar) and sa['total_batting_depth'] >= 9:
        score *= 0.2  # Playing XI batting set, only backup needs
    elif (is_batter or is_batting_ar) and sa['total_batting_depth'] >= 8:
        score *= 0.4  # Nearly complete batting lineup, selective
    elif (is_batter or is_batting_ar) and sa['total_batting_depth'] >= 7:
        score *= 0.6  # Adequate batting depth, focus on quality backups
    
    # All-rounder saturation (bowling ARs separate from batting depth)
    if 'All-Rounder' in role and not is_batting_ar and sa['all_rounders'] >= 4:
        score *= 0.6  # Have 4+ bowling all-rounders, selective
    
    # 4. Pitch compatibility bonus (only if not saturated)
    if is_spinner and pitch['spin_pref'] > 0.7 and sa['spin_bowlers'] < 4:
        score += 0.6
    elif is_pacer and pitch['pace_pref'] > 0.7 and sa['pace_bowlers'] < 6:
        score += 0.6
    elif is_spinner and pitch['spin_pref'] > 0.55 and sa['spin_bowlers'] < 3:
        score += 0.3
    elif is_pacer and pitch['pace_pref'] > 0.55 and sa['pace_bowlers'] < 5:
        score += 0.3
    
    # 5. LHB/RHB balance (value LHB if team is too RHB heavy)
    if sa['lhb'] < 3 and 'LHB' in bat_style:
        score += 0.3
    if sa['rhb'] < 4 and 'RHB' in bat_style:
        score += 0.2
    
    # 6. Overseas slot efficiency
    if is_overseas and sa['remaining_os_spots'] == 1:
        # Last overseas slot - very selective
        score += 0.5 if role in ['Bowler','All-Rounder'] else 0.2
    elif is_overseas and sa['remaining_os_spots'] > 1:
        score += 0.2
    
    # 7. Budget pressure penalty - if critically low, reduce desire
    if sa['budget_pressure'] == 'critical':
        score *= 0.4
    elif sa['budget_pressure'] == 'high':
        score *= 0.7
    
    return min(score, 3.0)

def compute_market_value(player):
    """
    Compute a BASELINE technical market value for a player from their attributes.
    This is the floor value - AI will add brand, marquee, and captain premiums on top.
    Used as the anchor for AI valuations.
    """
    role = player.get('role','')
    is_overseas = player.get('is_overseas', False)
    is_capped = player.get('is_capped', False)
    ipl_matches = player.get('stats',{}).get('ipl_matches', 0)
    base_price = player.get('base_price', 30)
    set_no = player.get('set_no', 99)  # Get auction set number
    
    # Start from base price
    value = base_price
    
    # Capped international multiplier (technical value only)
    if is_capped and is_overseas:
        value = max(value, 400)  # overseas capped floor
        if ipl_matches > 50: value = max(value, 800)
        if ipl_matches > 80: value = max(value, 1200)
        if ipl_matches > 100: value = max(value, 1500)
    elif is_capped and not is_overseas:
        value = max(value, 150)   # Any capped Indian
        if ipl_matches > 30: value = max(value, 250)
        if ipl_matches > 50: value = max(value, 350)   # Solid regular: ~Tripathi tier
        if ipl_matches > 80: value = max(value, 500)   # Experienced but not marquee
        if ipl_matches > 120: value = max(value, 750)  # Veteran — AI adds marquee premium separately
    elif not is_capped:
        # Uncapped - stay near base
        value = min(value * 1.5, 200)
    
    # Basic role premiums (technical scarcity only)
    if 'WK' in role:
        value = int(value * 1.2)  # WK scarcity (only 2 per team)
    
    if 'All-Rounder' in role:
        value = int(value * 1.15)  # Versatility value
    
    # 🌟 MARQUEE SET PREMIUM - Early auction sets when teams have full budgets
    if set_no == 1:
        value = int(value * 1.8)  # Set 1: MEGA MARQUEE (80% premium)
    elif set_no == 2:
        value = int(value * 1.5)  # Set 2: MARQUEE (50% premium)
    elif set_no == 3:
        value = int(value * 1.3)  # Set 3: Featured (30% premium)
    # Sets 4+ use base value (teams' budgets depleting)
    
    # NOTE: Brand value, marquee premiums, captain bonuses will be added by AI expert
    return int(value)

def generate_ai_valuations(player):
    """
    MASTER AI VALUATION ENGINE.
    
    For each AI team, computes a max bid (in Lakhs) using:
    1. Squad composition analysis (what roles are missing)
    2. Playing XI template matching
    3. Home pitch preferences  
    4. Budget pressure / remaining slots
    5. Market value anchoring
    6. Team personality / bidding style
    
    Then sends a rich, structured prompt to Llama 3.1 for final numbers.
    """
    
    # ── Pre-compute squad analysis for all teams ──
    team_analyses = {}
    for team in game_state['teams']:
        if team == game_state['user_team']:
            continue
        team_analyses[team] = analyse_squad(team)
    
    # ── RTM Logic: Exclude previous team from bidding if they have RTM cards ──
    previous_team = (player.get('stats', {}).get('last_team') or '').strip()
    rtm_eligible_team = None
    if previous_team and previous_team in game_state['teams']:
        # Check if previous team has RTM cards available
        rtm_cards = game_state.get('rtm_cards_available', {}).get(previous_team, 0)
        if rtm_cards > 0:
            rtm_eligible_team = previous_team
            # Store for later RTM exercise
            game_state['rtm_eligible_team'] = previous_team
    
    # ── Compute base market value for this player ──
    market_value = compute_market_value(player)
    
    # ── Build per-team context ──
    teams_context = []
    hard_zeros = {}  # teams that definitively cannot/will not bid
    
    for team, sa in team_analyses.items():
        t_data = game_state['teams'][team]
        
        # RTM RULE: Previous team doesn't bid initially (waits for RTM)
        if rtm_eligible_team and team == rtm_eligible_team:
            hard_zeros[team] = 0
            continue
        strat = TEAM_STRATEGIES[team]
        pitch = TEAM_PITCH_PROFILE[team]
        
        # HARD RULE: Overseas player but no overseas slots
        if player['is_overseas'] and sa['remaining_os_spots'] <= 0:
            hard_zeros[team] = 0
            continue
        
        # HARD RULE: Squad full
        if sa['remaining_spots'] <= 0:
            hard_zeros[team] = 0
            continue
        
        # HARD RULE: Budget too low even for base price
        if t_data['budget'] < player['base_price']:
            hard_zeros[team] = 0
            continue
        
        # SOFT RULE: SRH won't bid for overseas
        if team == 'SRH' and player['is_overseas']:
            hard_zeros[team] = 0
            continue
        
        # SOFT RULE: Player role is in team's avoid list
        role_avoided = any(
            avoid.lower() in (player['role'] + ' ' + player.get('bowl_style','') + ' ' + ('Overseas' if player['is_overseas'] else 'Indian')).lower()
            for avoid in strat.get('avoid_roles', [])
        )
        if role_avoided:
            hard_zeros[team] = 0
            continue
        
        critical_gaps_str = ', '.join(sa['critical_gaps']) if sa['critical_gaps'] else 'None'

        # Compute per-team XI fit score for this player
        xi_score = round(player_fits_xi_need(player, sa, team), 2)

        # Bowling saturation label for this player
        is_p_spinner = any(k in player.get('bowl_style','') for k in ['Spin','Slow','Orthodox','Unorthodox','Leg Spin','Off Spin'])
        is_p_pacer   = any(k in player.get('bowl_style','') for k in ['Fast','Medium','Pace'])
        if is_p_spinner:
            if sa['spin_bowlers'] >= 4:   bowl_sat = 'SPIN_SATURATED'
            elif sa['spin_bowlers'] >= 3: bowl_sat = 'SPIN_ADEQUATE'
            else:                          bowl_sat = 'NONE'
        elif is_p_pacer:
            if sa['pace_bowlers'] >= 6:   bowl_sat = 'PACE_SATURATED'
            elif sa['pace_bowlers'] >= 5: bowl_sat = 'PACE_ADEQUATE'
            else:                          bowl_sat = 'NONE'
        else:
            bowl_sat = 'NONE'

        # Batting saturation label
        p_role_here = player.get('role','')
        is_p_batter_ctx = p_role_here in ['Batter','WK-Batter'] or 'Batter' in p_role_here
        if is_p_batter_ctx:
            if sa['total_batting_depth'] >= 9:   bat_sat = 'BAT_SATURATED'
            elif sa['total_batting_depth'] >= 8: bat_sat = 'BAT_ADEQUATE'
            elif sa['total_batting_depth'] >= 7: bat_sat = 'BAT_SUFFICIENT'
            else:                                 bat_sat = 'NONE'
        else:
            bat_sat = 'N/A'

        teams_context.append({
            "team": team,
            "budget_lakhs": sa['budget'],
            "budget_per_remaining_slot": round(sa['budget_per_slot']),
            "remaining_spots": sa['remaining_spots'],
            "overseas_spots_left": sa['remaining_os_spots'],
            "squad_total": sa['total'],
            "squad_composition": {
                "WK": sa['wk'],
                "Batters": sa['batters'],
                "All_Rounders": sa['all_rounders'],
                "Bowlers": sa['bowlers'],
                "Spinners": sa['spin_bowlers'],
                "Pacers": sa['pace_bowlers'],
                "Overseas": sa['overseas'],
                "BatDepth": sa['total_batting_depth'],
            },
            "gaps_needed": critical_gaps_str,
            "bidding_style": strat['bidding_style'],
            "xi_fit_score": xi_score,
            "bowling_saturation": bowl_sat,
            "batting_saturation": bat_sat,
            "home_pitch_type": pitch['type'],
            "home_ground": pitch['ground'],
            "spin_affinity": pitch['spin_pref'],
            "pace_affinity": pitch['pace_pref'],
        })
    
    # If all teams filtered out
    if not teams_context:
        result = dict(hard_zeros)
        for t in game_state['teams']:
            if t != game_state['user_team'] and t not in result:
                result[t] = 0
        return result

    # ── Build the Master Prompt ──
    ipl_matches = player['stats']['ipl_matches']
    age = int(player.get('age', 25)) if player.get('age') else 25
    
    # Determine brand value category
    if ipl_matches >= 150:
        brand_status = "🌟 MEGA STAR (150+ matches) - HIGH BRAND VALUE - Teams will overpay for marquee names"
    elif ipl_matches >= 100:
        brand_status = "⭐ ESTABLISHED STAR (100+ matches) - STRONG BRAND VALUE"
    elif ipl_matches >= 70:
        brand_status = "✨ POPULAR PLAYER (70+ matches) - GOOD BRAND VALUE"
    elif ipl_matches >= 50:
        brand_status = "Known Face (50+ matches) - Moderate brand value"
    else:
        brand_status = "Emerging/Uncapped - Limited brand value"
    
    # Captain material check
    captain_material = ""
    if 25 <= age <= 34 and ipl_matches >= 80 and player['is_capped']:
        captain_material = "💼 CAPTAIN MATERIAL - Experienced leader in prime age - Commands 25-40% PREMIUM for captain-needing teams"
    elif 25 <= age <= 34 and ipl_matches >= 100:
        captain_material = "💼 LEADERSHIP POTENTIAL - Veteran with experience - moderate captain premium"

    # Indian Raw Talent indicator
    indian_talent_bonus = ""
    if not player['is_overseas']:
        if not player['is_capped'] and ipl_matches >= 5 and (not player.get('age') or age <= 25):
            indian_talent_bonus = "🌱 INDIAN RAW TALENT BONUS - Young uncapped Indian with IPL exposure. Future star potential. Add 20-40% over base for talent-hungry teams (GT, RR, MI)."
        elif not player['is_capped'] and age <= 22:
            indian_talent_bonus = "🌱 FUTURE STAR - Very young Indian domestic talent. Long career ahead. BBL/U19 calibre. Teams developing pipeline pay premium."
        elif player['is_capped'] and age <= 27 and ipl_matches <= 50:
            indian_talent_bonus = "⭐ YOUNG CAPPED INDIAN - Rare: experienced international but early career. High ceiling. Add 15-25% youth premium."

    # All-Rounder / WK-Batter special bonus
    role_bonus = ""
    if 'All-Rounder' in player.get('role',''):
        if ipl_matches >= 60 and player['is_capped']:
            role_bonus = "🎯 PROVEN ALL-ROUNDER BONUS - Fills 2 XI slots (batting + bowling). MANDATORY for all teams. Add 30-50% dual-role premium. NEVER undervalue a genuine proven AR."
        else:
            role_bonus = "🎯 ALL-ROUNDER VALUE - Versatile player filling dual role. Add 15-25% versatility premium over equivalent specialist."
    elif 'WK' in player.get('role',''):
        if ipl_matches >= 50 and player['is_capped']:
            role_bonus = "🧤 ELITE WK-BATTER BONUS - Only 2 WK slots per 25-man squad. Extreme scarcity. EVERY team needs minimum 2 WKs. Add 30-60% WK premium. Teams missing WK should bid VERY aggressively."
        else:
            role_bonus = "🧤 WK-BATTER SCARCITY - Limited WK-Batter slots. Add 20-30% WK premium."

    # Demand indicator (how many teams critically need this player's role)
    teams_needing_role = sum(
        1 for ctx in teams_context
        if player.get('role','') in ctx.get('gaps_needed','')
    )
    if teams_needing_role >= 5:
        demand_indicator = f"🔥 EXTREME DEMAND - {teams_needing_role} teams critically need this role → Expect BIDDING WAR, prices will explode 2-3× market value"
    elif teams_needing_role >= 3:
        demand_indicator = f"⚡ HIGH DEMAND - {teams_needing_role} teams need this role urgently → Strong competition expected"
    elif teams_needing_role >= 1:
        demand_indicator = f"📈 MODERATE DEMAND - {teams_needing_role} team(s) have critical gap → Some competition"
    else:
        demand_indicator = "📉 LOW DEMAND - No team has a critical gap for this role → Risk of going near base price"
    
    # Determine auction set status
    set_no = player.get('set_no', 99)
    set_name = player.get('set', 'Unknown')
    if set_no == 1:
        set_status = "🌟 SET 1 - MEGA MARQUEE - Early auction, ALL teams have FULL BUDGETS, expect INTENSE BIDDING WARS for star players"
    elif set_no == 2:
        set_status = "⭐ SET 2 - MARQUEE - Early auction, teams still have HIGH budgets, expect AGGRESSIVE bidding"
    elif set_no == 3:
        set_status = "✨ SET 3 - Featured players, teams starting to be selective"
    elif set_no <= 5:
        set_status = f"Set {set_no} - Mid-auction, budget pressure building"
    else:
        set_status = f"Set {set_no} - Late auction, teams completing squads"
    
    prompt = f"""You are the world's most experienced IPL auction analyst simulating the IPL 2025 Mega Auction.

═══════════════════════════════════════════════════════
PLAYER ON THE BLOCK:
  Name         : {player['name']}
  Role         : {player['role']}
  Country      : {player['country']} ({'OVERSEAS' if player['is_overseas'] else 'INDIAN'})
  Age          : {age} years
  Base Price   : ₹{player['base_price']} Lakhs
  IPL Matches  : {ipl_matches}
  Status       : {'Capped International' if player['is_capped'] else 'Uncapped/State/Domestic'}
  Brand Value  : {brand_status}
  {captain_material if captain_material else ''}
  {role_bonus if role_bonus else ''}
  {indian_talent_bonus if indian_talent_bonus else ''}
  {demand_indicator}
  Batting Hand : {player.get('bat_style','Unknown')}
  Bowl Type    : {player.get('bowl_style','N/A')}
  Last IPL Team: {player['stats'].get('last_team','None') or 'None'}
  Auction Set  : {set_status}
  Market Value : ₹{market_value} Lakhs (includes marquee premium for early sets)
═══════════════════════════════════════════════════════

BIDDING TEAMS + THEIR REAL SITUATION:
{json.dumps(teams_context, indent=2)}

═══════════════════════════════════════════════════════
AUCTION RULES (NON-NEGOTIABLE):
1. Max valuation CANNOT exceed team's budget_lakhs
2. Teams with overseas_spots_left = 0 cannot bid for overseas player (already handled - not in list)
3. Teams with remaining_spots = 0 cannot bid (already handled - not in list)
4. A team with role_avoided = true should have valuation = 0 or near base price only
5. Teams with budget_pressure = "critical" cannot exceed budget_per_remaining_slot × 2

-check for the given player, which teams are likely to bid and at what price, based on their current squad composition, budget, and the player's fit for their needs.
-check the real 2025 ip auction prices for similar players to set realistic valuation benchmarks.
- teams like DC and  SRH spil the party of other teams by raising the prices to unrealistic levels for players that are not even a great fit for them, just to make it harder for others to buy them. This should be reflected in their valuations.
- teams like RR and MI are extreme budget savers and will only bid if the player is a perfect fit and within a very low price range.
- teams like PBKS and RCB are aggressive spenders and will bid for players who are a good fit even if it means stretching their budget, especially in the early sets when they have more money to spend.
- teams like CSK and LSG are more balanced and will bid for players who fit their needs but won't overpay for marquee players if they don't fit their squad composition.
- teams like GT and KKR are disciplined spenders and will focus on value picks that fit
- MI and KRR will go any for their ex players if they want and spend high on them to retain them or get them back if they are in the auction pool. This should be reflected in their valuations for such players.
REALISTIC BIDDING FRAMEWORK (TRULY DYNAMIC):
- ALL teams adjust their max bid based on CURRENT budget AND slot situation (not fixed personalities)
- Teams adapt their aggression throughout the auction based on multiple real-time factors
- Budget reality creates natural power shifts as auction progresses
- Team personality is just the BASE - actual aggression changes with budget and squad status
- **CRITICAL**: Teams with < 18 players MUST bid aggressively to complete minimum squad

DYNAMIC AGGRESSIVE FACTOR CALCULATION:
aggressive_factor = base_personality × budget_multiplier × slot_multiplier × budget_reality_cap

Base Personality (1.0-1.8):
- ultra_aggressive_big_spender (PBKS): 1.8 base
- emotional_fan_driven (RCB): 1.6 base
- aggressive_rebuild (DC): 1.5 base
- conservative_experienced (CSK): 1.3 base
- analytics_balanced (LSG): 1.3 base
- moneyball_disciplined (GT): 1.2 base
- budget_champion (KKR): 1.2 base
- budget_snipers (MI): 1.1 base
- extreme_budget_save (RR): 1.0 base

Budget Multiplier (based on % budget spent):
- < 30% spent (early auction): 1.4× (aggressive with full purse)
- 30-50% spent: 1.2× (still comfortable)
- 50-70% spent: 1.0× (normal)
- 70-85% spent: 0.7× (getting conservative)
- > 85% spent (running low): 0.4× (very conservative)

Slot Fill Multiplier (based on squad size):
- < 10 players (< 40% full): 1.3× (need many players)
- 10-15 players (40-60%): 1.1× (still building)
- 15-19 players (60-75%): 1.0× (normal)
- 19-22 players (75-88%): 0.8× (selective)
- 23+ players (> 88%): 0.5× (very selective)

Budget Reality Cap (based on budget per slot):
- < 40L per slot: 0.6× (must be very conservative)
- 40-80L per slot: 0.8× (limited flexibility)
- 80-150L per slot: 1.0× (normal)
- > 150L per slot: 1.2× (can afford aggression)

EXAMPLES:
- PBKS early (1.8 × 1.4 × 1.3 × 1.2) = 3.9× → capped at 2.5×
- PBKS late with low budget (1.8 × 0.4 × 0.5 × 0.6) = 0.22× → use 0.5× minimum
- RR early with budget (1.0 × 1.4 × 1.3 × 1.2) = 2.2× → aggressive despite conservative style
- RR late (1.0 × 0.7 × 0.8 × 0.8) = 0.45× → very conservative

MAX_BID = min(budget_lakhs, budget_per_slot × dynamic_aggressive_factor)

SQUAD COMPLETION URGENCY MULTIPLIER:
- If team has < 18 players: Apply urgency multiplier (1.5× to 3.0×) to MAX_BID
- Teams MUST complete minimum 18 players to have viable squad
- Reserve only 25L per remaining slot (late-auction base prices are 20-30L, NOT 100L)
- This overrides conservative bidding styles when squad completion is at risk

🚨 SQUAD DESPERATION OVERRIDE (ABSOLUTE RULE):
- Team with < 15 players: MUST bid on every eligible player at MINIMUM base_price
  Their effective max per player = budget_lakhs / remaining_spots × 1.5 (spend more on good fits)
  DO NOT set these teams to 0 unless they are truly ineligible (overseas full, role saturated etc)
- Team with < 12 players: bid_floor = budget_lakhs / remaining_spots (at minimum spend average share)
- Example: PBKS with 6 players, 19 slots empty, ₹1226L → avg ₹64L/player. Bid ₹50-150L on most players
- Example: DC with 10 players, 15 slots empty, ₹701L → avg ₹47L/player. Bid ₹30-100L on players

VALUATION WITHIN MAX BID:
- CRITICAL urgency (combined > 3.0 OR squad < 18): Bid 70-95% of MAX_BID
- VERY HIGH urgency (combined > 2.0): Bid 60-80% of MAX_BID
- HIGH urgency (combined 1.5-2.0): Bid 50-70% of MAX_BID
- MEDIUM urgency (combined 0.8-1.5): Bid 35-55% of MAX_BID
- LOW urgency (combined 0.4-0.8): Bid 20-40% of MAX_BID
- VERY LOW urgency (combined < 0.4): Pass or minimal bid

Combined urgency = xi_fit_score × position_urgency_multiplier
Position urgency multipliers:
- WK and team has < 2 WK: 2.5×
- Batter and team has < 5 batters: 2.0×
- Bowler and team has < 5 bowlers: 2.0×
- All-Rounder and team has < 2 AR: 1.8×
- Otherwise: 1.0×

CRITICAL SAFETY RULES:
- Never bid if it leaves < 25L per remaining slot to reach min 18 players
- If team has < 18 players: MUST bid to complete squad (override conservative style)
- Never bid if it leaves < 40L per remaining slot for teams with 18+ players
- If budget_pressure = "critical" AND squad >= 18: Reduce MAX_BID by 40%
- If bowling_saturation = "SPIN_SATURATED" or "PACE_SATURATED": Team should NOT bid (set 0)
- If bowling_saturation = "SPIN_ADEQUATE" or "PACE_ADEQUATE": Reduce valuation by 60%
- Create variety: Some stars unsold, some mid-tier overpaid, realistic competition

SQUAD SATURATION INTELLIGENCE (CRITICAL):
A. BOWLING SATURATION:
   - Each team shows bowling_saturation status for this player
   - SPIN_SATURATED (4+ spinners): Team should set valuation = 0 (already have enough spinners)
   - PACE_SATURATED (6+ pacers): Team should set valuation = 0 (already have enough pacers)
   - SPIN_ADEQUATE (3 spinners): Reduce spinner valuation by 50-70% (not urgent need)
   - PACE_ADEQUATE (5 pacers): Reduce pacer valuation by 50-70% (not urgent need)
   - Example: If CSK has 4 spinners and player is spinner, CSK should NOT bid at all

B. BATTING SATURATION (PLAYING XI COMPLETE):
   - Each team shows batting_saturation status AND "BatDepth" count in squad_summary
   - BatDepth = Total batting resources (pure batters + batting all-rounders)
   - Playing XI needs ~7 batters (WK + batters + ARs), so 8-9 means XI complete
   
   - BAT_SATURATED (9+ batters): Playing XI's batting COMPLETE - only bid for exceptional backup
     * Reduce batter/WK valuation by 80% (₹500L batter → ₹100L backup bid)
     * Teams with 9+ batters are NOW FOCUSING ON BOWLERS, not more batters
     * Example: PBKS with 9 batters should bid ₹0-200L for batters, normal for bowlers
   
   - BAT_ADEQUATE (8 batters): Nearly complete batting lineup - very selective
     * Reduce batter/WK valuation by 60% (only bid for star batters)
     * Example: CSK with 8 batters should skip average batters, only bid for exceptional names
   
   - BAT_SUFFICIENT (7 batters): Adequate batting depth - quality over quantity
     * Reduce batter/WK valuation by 40% (selective bidding)
     * Focus on quality additions, not filling spots
   
   - NONE (< 7 batters): Still building batting lineup - bid normally
     * Teams with < 7 batters actively need batting depth

SQUAD BALANCE INTELLIGENCE:
- xi_fit_score > 2.0 = Player directly fills a CRITICAL GAP in playing XI - bid aggressively
- xi_fit_score 1.0-2.0 = Player fills an important squad role - bid competitively
- xi_fit_score 0.5-1.0 = Useful depth player - bid conservatively
- xi_fit_score < 0.5 = Not really needed - consider 0 or base price only

BRAND VALUE & MARQUEE PLAYER INTELLIGENCE (USE YOUR EXPERTISE):
You are an expert - analyze player's attributes and decide appropriate brand premium:

🌟 MEGA STAR INDICATORS (150+ IPL matches):
- Household names that fill stadiums and drive viewership
- Teams will pay 30-50% EXTRA beyond technical value for brand power
- Examples: Rohit Sharma, Virat Kohli, MS Dhoni type players
- Fan following = jersey sales = sponsor value = worth the premium

⭐ ESTABLISHED STAR (100-149 IPL matches):
- Well-known faces with proven track record
- Apply 20-35% brand premium for established stars
- Reliable performers that fans recognize

✨ POPULAR PLAYER (70-99 IPL matches):
- Known in IPL circles, growing brand
- Apply 10-20% brand premium for popularity

💼 CAPTAIN MATERIAL BONUS (CRITICAL FOR TEAMS):
Analyze if player has leadership qualities:
- Age 25-34 (prime leadership age) + 80+ IPL matches + Capped international = potential captain
- Teams DESPERATE for leaders may pay 15-30% EXTRA for captaincy material
- Particularly valuable for teams without established captain
- Young teams (DC, GT, LSG, RCB) especially value leadership

🎯 MARQUEE ALL-ROUNDER / WK PREMIUM:
- 100+ matches + Capped + (All-Rounder OR WK) = MARQUEE player
- These are auction headliners - teams battle for them
- Can command 40-60% premium beyond base value
- Scarcity value: Only 2 WK per team, all-rounders fill multiple roles

🌟 AUCTION SET STRATEGY (CRITICAL FOR REALISTIC BIDDING):
**SET 1 - MEGA MARQUEE** (Early auction, full budgets):
- ALL teams have FULL budgets and are AGGRESSIVE for star players
- These are the headliner players everyone wants - expect INTENSE BIDDING WARS
- Even conservative teams (RR, MI, KKR) bid HIGH in Set 1 for marquee stars
- Teams will spend 20-30% of their budget on Set 1/Set 2 marquee players
- If Set 1 player: Increase valuation by 30-50% beyond technical value (already included in market value)
- Example: Mitchell Starc (Set 1, 100+ matches) - Market ₹1200L → Teams bid ₹1600-2400L

**SET 2 - MARQUEE** (Early auction, high budgets):
- Teams still have 70-90% budgets remaining, expect AGGRESSIVE bidding
- These are featured players that fill critical roles
- Teams compete strongly for Set 2 stars
- Example: Arshdeep Singh (Set 2) - Market ₹600L → Teams bid ₹900-1500L

**SET 3-5** (Mid-auction, selective bidding):
- Teams spent 30-50% of budgets, now becoming selective
- Quality players still get competitive bids
- Teams focus on filling specific gaps

**SET 6+** (Late auction, budget pressure):
- Teams completing minimum 18-squad with cheap backups
- Expect base price or slightly above for most players
- Only exceptional players get bidding wars

� POST-MARQUEE PRICE DISCIPLINE (SETS 3+) — ABSOLUTE HARD RULE:
After marquee sets (1-2), teams have already spent big. Remaining sets have REGULAR/DEPTH players.
STRICT PRICE CONTROL — NO EXCEPTIONS:
- TYPICAL range : ₹500–1000L (5–10 crore) for most players in sets 3+
- ABOVE AVERAGE : ₹1000–1500L (10–15 crore) ONLY for truly exceptional role fits
- ABSOLUTE MAXIMUM: ₹1500L (15 crore) — DO NOT OUTPUT ANY VALUE ABOVE THIS for sets 3+
- Teams that already spent heavily on marquee players MUST be even more conservative
- Budget left after marquee must cover ALL remaining sets, not blow on one player
- NEVER generate bidding-war prices for non-marquee depth players
Example: A decent Indian pacer in Set 4 → ₹300–700L, NOT ₹1600L
Example: If PBKS spent ₹2700L on Rishabh Pant, they bid ₹400–900L on later players

�📊 REAL IPL 2025 MEGA AUCTION RESULTS (November 2024) — MANDATORY CALIBRATION:
These are ACTUAL prices. Your valuations MUST reflect this reality:

🏆 MARQUEE WK / CAPTAIN TIER (₹1200L–₹2700L):
- Rishabh Pant (WK, 100+ IPL, Captain, Indian): ₹2700L → LSG — 4× base, bid wars
- Shreyas Iyer (Batter, 100+ IPL, Captain, Indian): ₹2675L → PBKS — captain premium exploded price
- KL Rahul (WK+Captain, 100+ IPL, Indian): ₹1400L → DC
- Ishan Kishan (WK, 100+ IPL, Indian): ₹1125L → PBKS
- Phil Salt (WK-Batter, Overseas, 80+ IPL): ₹1150L → KKR
- Jos Buttler (WK-Batter, Overseas, 100+ IPL): ₹1575L → GT

💪 ALL-ROUNDER TIER (₹600L–₹2000L):
- Axar Patel (AR/Spinner, 80+ IPL, Indian): ₹1625L → DC — dual role premium
- Mitchell Starc (Pace AR, 30+ IPL, Overseas): ₹1125L → KKR — overseas spearhead
- Washington Sundar (AR, 50+ IPL, Indian): ₹525L → SRH
- Krunal Pandya (AR, 100+ IPL, Indian): ₹550L → RCB

🎳 BOWLER TIER:
- Arshdeep Singh (Pacer, 60+ IPL, Indian capped): ₹1800L → PBKS — premier Indian pacer
- Yuzvendra Chahal (Leg-spin, 150+ IPL, Indian): ₹1800L → PBKS — supreme spinner brand
- Mohammed Shami (Pacer, 50+ IPL, Indian capped): ₹975L → GT
- Avesh Khan (Pacer, 60+ IPL, Indian capped): ₹240L — ordinary Indian pacer, low demand
- Harshit Rana (Pacer, 20+ IPL, Young Indian): ₹400L retained (KKR valued young pace)

🏏 BATTER TIER:
- Tilak Varma (Batter, 40+ IPL, Uncapped Indian, young): ₹1400L → MI — raw talent premium
- Mohammad Siraj (Pacer, 60+ IPL, Indian capped): ₹1225L → RCB
- Mayank Agarwal (Batter, 100+ IPL, Indian capped): ₹620L — experience but no WK/captain angle
- Rahul Tripathi (Batter, 80+ IPL, Indian capped, no WK/AR/captain): ₹200L — ordinary batter
- Manish Pandey (Batter, 100+ IPL, Indian capped): ₹200L — experience alone = no premium
- Devdutt Padikkal (Batter, 40+ IPL, Indian): ₹150L — uncapped batter near base
- Uncapped domestic specialist:  ₹30–75L (base or near)

🌱 INDIAN RAW TALENT (Young Uncapped Indians who impressed):
- Tilak Varma: ₹1400L — young talent > experienced ordinary player
- Riyan Parag (retained ₹1400L) — youngster with ceiling valued more than veterans
- Ayush Badoni, Nitish Reddy, Harshit Rana: ₹400-600L range for India-capped youngsters
- Unknown domestic find: ₹30-100L (base price discovery)

KEY INSIGHT FROM REAL AUCTION: Marquee Indians in high demand went 2×-4× their market value.
NON-MARQUEE ordinary capped Indians (batters/bowlers without WK/AR/captain angle) often sold near 100-300L.
Massive variance: stars go 2800L; solid journeymen go 150-300L. Do NOT overprice average players.

SMART VALUATION EXAMPLES (with REAL 2025 AUCTION outcomes):
- Rishabh Pant (WK, 100+ matches, Captain material): Real sold ₹2700L — teams bid ₹2200-2700L
- Shreyas Iyer (Batter, captain, 100+ matches): Real sold ₹2675L — captain-hungry teams go crazy
- Arshdeep Singh (Premier pacer, 60+ matches, Set 1): Real sold ₹1800L — top Indian pacers command this
- Axar Patel (All-Rounder, 80+ matches, Set 1): Real sold ₹1625L — WK/AR dual value earns premium
- KL Rahul (WK+captain, 100+ matches): Real sold ₹1400L — even at reduced demand, WK+captain = big money
- Rahul Tripathi (Batter only, 80+ matches, NOT WK/AR/captain): Real sold ₹200L — good player but no unique value driver
- Manish Pandey (Batter, 100+ matches): Real sold ₹200L — experience alone doesn’t command premium now
- Uncapped domestic youngster (5-20 matches): ₹30-100L base-price range

🇮🇳 MANDATORY MINIMUMS — ONLY FOR TRULY MARQUEE INDIAN PLAYERS:
These apply ONLY if the player has genuine marquee indicators, NOT ordinary batters:

✅ GENUINELY MARQUEE (apply minimum):
- Indian WK-Batter + 80+ matches + capped = MINIMUM ₹1200L (extreme scarcity, only 2 WK per team)
- Indian All-Rounder + 80+ matches + capped = MINIMUM ₹1100L (WK/AR dual utility)
- Captain-material Indian (age 25-35, 100+ matches, WK or top-order, capped) = MINIMUM ₹2000L for captain-hungry teams (DC/KKR/LSG/RCB)
- Premier Indian pacer with 30+ T20Is or 120+ IPL wickets = MINIMUM ₹1200L

❌ NOT MARQUEE (do NOT apply minimum — bid only if squad need exists):
- Pure batters with 80+ IPL matches but no WK/captain/AR angle = ₹150-500L range (Tripathi, Pandey tier)
- Spinners who aren’t Chahal/Ashwin tier (no marquee name) = ₹200-600L
- Middle-order domestic specialists = ₹75-300L regardless of match count

Pant/Iyer/KL Rahul tier = ₹2000-2800L — genuine headliners, bid wars guaranteed
Teams needing captains should pay 30-50% captain premium ONLY for actual leader candidates

USE YOUR JUDGMENT: Not all stars get premiums - consider team's budget, urgency, saturation!

🎲 VARIANCE & REALISM (CRITICAL — READ THIS):
Real auctions are UNPREDICTABLE. Do NOT make all players end up at the same price range:
- Some marquee players spark WARS (2 teams keep bidding, price explodes 2×-3× market value)
- Some quality players get OVERLOOKED (only 1 team interested → goes near base price)
- A team can go CRAZY for a player they desperately need (3× their normal ceiling)
- Another team might DROP OUT early even for a star (budget/saturation reasons)
- Introduce spread: In any given auction, 20% of players go cheap, 60% go market rate, 20% go expensive
- DO NOT cluster everyone at 1300-1500L — that's unrealistic!
- Some teams should bid 0 for players they don't need, others should far overbid for urgent needs
- Allow randomness: even similar teams can value the same player very differently (±30 variation is fine)
- Create exciting bidding wars for 2-3 players per set; let others pass cheaply

- Most Important tip : If teasm goes very high for one marquee player potential cadidate of captaincy exm: PBJS pant 25 crore then pbks will not go much hihg for other cap[taincy plaeyr like shreyas (will got only till 10-12  crore) okay so tema can spedn purse for other sets as welll like evenly ...not spending all orf its in earleir marquee sets
POSITION-BASED URGENCY (SQUAD MINIMUMS — USE xi_fit_score FROM EACH TEAM'S DATA):
- Each team in BIDDING TEAMS has an "xi_fit_score" field — use it!
  * xi_fit_score > 2.0 = CRITICAL gap filled → bid aggressively (60-90% of MAX_BID)
  * xi_fit_score 1.0-2.0 = important gap → bid competitively (40-70% of MAX_BID)
  * xi_fit_score 0.5-1.0 = useful depth → bid conservatively (20-40% of MAX_BID)
  * xi_fit_score < 0.5 = not needed → 0 or base price only
- critical_gaps contains "WK-Batter" OR xi_fit_score > 2.0 for WK = 2.5× urgency
- critical_gaps contains "All-Rounder" OR team arhas < 3 ARs = 1.8× urgency
- xi_fit_score × position_urgency = combined urgency (drives bid %)
- Teams MUST complete minimum 18 players — factor in remaining_spots and budget
- NEVER spend so much that team can't fill remaining_spots with 50L each

🏟️ HOME PITCH & STADIUM CONDITIONS (CRITICAL — EACH TEAM HAS home_pitch_type):
- Each team has home_pitch_type, spin_affinity (0-1), pace_affinity (0-1) in their data
- CSK: Chepauk SPIN PARADISE (spin_pref=0.9) → pay 30-40% extra for quality spinners
- RR: Jaipur BIG GROUND SPIN (spin_pref=0.85) → premium for spinners
- KKR: Eden PACE/SWING HEAVEN (pace_pref=0.85) → pay 20-35% extra for left-arm pacers
- SRH: Hyderabad HIGH-SCORING FLAT (pace_pref=0.80) → pay for pace + explosive batters
- MI: Wankhede DUAL NATURE (spin+pace) → balance needed, no extreme on either
- GT: Ahmedabad BIG GROUND (pace_pref=0.70) → pay for pace variety
- PBKS: Mohali BATTING HEAVEN (spin_pref=0.40) → barely value spinners, love pace+batters
- DC: Delhi SPIN-FRIENDLY (spin_pref=0.75) → value spinners moderately
- LSG: Lucknow UNPREDICTABLE → balanced team, value versatility
- RCB: Chinnaswamy BATTING PARADISE → value explosive batters + death bowlers

IF player is spinner AND team's spin_affinity > 0.7 AND bowling_saturation = 'NONE': Add 25-40% pitch bonus
IF player is pacer AND team's pace_affinity > 0.75 AND bowling_saturation = 'NONE': Add 20-35% pitch bonus
IF bowling_saturation = 'SPIN_SATURATED' or 'PACE_SATURATED': Team bids 0 (set in their data)

PITCH COMPATIBILITY BONUS:
- Team home_pitch is spin_dominant and player is quality spinner = +20-40% valuation bonus
- Team home_pitch is pace_dominant and player is pace bowler = +20-40% valuation bonus

OUTPUT FORMAT:
Return ONLY a raw valid JSON object. Zero markdown, zero explanation, zero extra text.
Keys = team abbreviations. Values = max bid in Lakhs (integer).
Example: {{"CSK": 850, "DC": 1400, "GT": 0, "KKR": 300}}

IMPORTANT: Only include teams present in BIDDING TEAMS list above."""

    # ── Simple fallback defaults (used if LLM fails) ──
    # Uses market_value × personality × budget availability × random variance
    default_result = dict(hard_zeros)
    bp = player['base_price']
    p_set_no = player.get('set_no', 99)

    PERSONALITY_MULT = {
        'ultra_aggressive_big_spender': 1.7,
        'emotional_fan_driven': 1.5,
        'aggressive_rebuild': 1.4,
        'conservative_experienced': 1.1,
        'analytics_balanced': 1.15,
        'moneyball_disciplined': 1.05,
        'budget_champion': 1.1,
        'budget_snipers': 0.85,
        'extreme_budget_save': 0.75,
        'overseas_saturated': 1.0,
    }

    for ctx in teams_context:
        team = ctx['team']
        t_data = game_state['teams'][team]
        sa = team_analyses[team]
        strat = TEAM_STRATEGIES[team]
        budget = t_data['budget']
        remaining_slots = ctx['remaining_spots']
        style = strat['bidding_style']

        if remaining_slots <= 0 or budget <= bp:
            default_result[team] = 0
            continue

        personality = PERSONALITY_MULT.get(style, 1.1)

        # Budget availability multiplier
        initial_budget = INITIAL_BUDGETS.get(team, 6000)
        budget_pct_remaining = budget / initial_budget
        if budget_pct_remaining > 0.7:
            budget_mult = 1.3
        elif budget_pct_remaining > 0.5:
            budget_mult = 1.1
        elif budget_pct_remaining > 0.3:
            budget_mult = 0.9
        else:
            budget_mult = 0.6

        # Squad completion urgency
        slots_to_18 = max(0, 18 - sa['total'])
        completion_mult = 1.5 if slots_to_18 > 5 else (1.2 if slots_to_18 > 0 else 1.0)

        val = int(market_value * personality * budget_mult * completion_mult)

        # Random variance
        variance = random.uniform(0.75, 1.30) if p_set_no <= 2 else (random.uniform(0.80, 1.20) if p_set_no <= 4 else random.uniform(0.88, 1.12))
        val = int(val * variance)

        # Safety: tiered reserve per slot based on squad size
        # >=10 players→*30, >=5→*50, <5→*25 (late-auction base prices ~20-30L)
        _reserve_mult = 30 if sa['total'] >= 10 else (50 if sa['total'] >= 5 else 25)
        safety_reserve = slots_to_18 * _reserve_mult
        safe_max = max(bp, budget - safety_reserve)
        if remaining_slots > 1:
            safe_max = min(safe_max, budget - (remaining_slots - 1) * _reserve_mult)
        val = min(val, safe_max, budget)
        default_result[team] = max(0, int(val))

        if default_result[team] > 0:
            print(f"  [{team}] MV:₹{market_value}L × pers:{personality} × budg:{budget_mult} × comp:{completion_mult:.1f} × var:{variance:.2f} → ₹{default_result[team]}L")

    
    # ── Call LLM ──
    print(f"\n{'='*80}")
    print(f"[PLAYER] {player['name']} | Role: {player['role']} | Base: ₹{player['base_price']}L | Market: ₹{market_value}L")
    print(f"[DYNAMIC FACTORS] Teams' aggressive factors adjusted by budget & slots:")
    
    try:
        completion = client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=350,
            timeout=10,
        )
        content = completion.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()
        start = content.find('{')
        end   = content.rfind('}') + 1
        if start >= 0 and end > start:
            parsed = json.loads(content[start:end])
            
            # Merge: use LLM values where available, fallback elsewhere
            merged = dict(default_result)
            for team, llm_val in parsed.items():
                if team in merged and team != game_state['user_team']:
                    t_data = game_state['teams'].get(team, {})
                    sa = team_analyses.get(team)
                    
                    # Enforce hard constraints on LLM output
                    llm_val = max(0, int(llm_val))
                    llm_val = min(llm_val, t_data.get('budget', 0))
                    if player['is_overseas'] and t_data.get('overseas_count', 0) >= 8:
                        llm_val = 0
                    if t_data.get('total_players', 0) >= 25:
                        llm_val = 0
                    if sa and sa['budget_pressure'] == 'critical':
                        llm_val = min(llm_val, sa['budget_per_slot'] * 2)
                    # SRH hard block on overseas
                    if team == 'SRH' and player['is_overseas']:
                        llm_val = 0
                    
                    merged[team] = llm_val
            
            # Make sure every non-user team has an entry
            for t in game_state['teams']:
                if t != game_state['user_team'] and t not in merged:
                    merged[t] = default_result.get(t, 0)
            
            # FINAL BUDGET RESERVE CHECK: Cap valuations to preserve squad completion budget
            for team in merged:
                if team != game_state['user_team']:
                    sa = team_analyses.get(team)
                    if sa:
                        slots_to_18 = max(0, 18 - sa['total'])
                        # Tiered reserve: >=10 players→*30, >=5→*50, <5→*25
                        _reserve_mult = 30 if sa['total'] >= 10 else (50 if sa['total'] >= 5 else 25)
                        min_reserve = slots_to_18 * _reserve_mult
                        max_safe_bid = max(player['base_price'], sa['budget'] - min_reserve)
                        merged[team] = min(merged[team], max_safe_bid)

            # POST-MARQUEE HARD CAP: Sets 3+ are non-marquee — max 1500L (15 crore) per team
            if player.get('set_no', 99) >= 3:
                for team in merged:
                    if team != game_state['user_team']:
                        merged[team] = min(merged[team], 1500)

            print(f"\n[AI Vals] {player['name']} | Market:₹{market_value}L | {json.dumps(merged)}")
            return merged
    
    except Exception as e:
        print(f"[AI Error] {e} — using fallback valuations")
    
    # Make sure every non-user team has a fallback value
    for t in game_state['teams']:
        if t != game_state['user_team'] and t not in default_result:
            default_result[t] = 0
    
    # FINAL BUDGET RESERVE CHECK: Cap valuations to preserve squad completion budget (fallback)
    for team in default_result:
        if team != game_state['user_team']:
            sa = team_analyses.get(team)
            if sa:
                slots_to_18 = max(0, 18 - sa['total'])
                # Tiered reserve: >=10 players→*30, >=5→*50, <5→*25
                _reserve_mult = 30 if sa['total'] >= 10 else (50 if sa['total'] >= 5 else 30)
                min_reserve = slots_to_18 * _reserve_mult
                max_safe_bid = max(player['base_price'], sa['budget'] - min_reserve)
                default_result[team] = min(default_result[team], max_safe_bid)

    # POST-MARQUEE HARD CAP (fallback): Sets 3+ are non-marquee — max 1500L (15 crore)
    if player.get('set_no', 99) >= 3:
        for team in list(default_result.keys()):
            if team != game_state.get('user_team'):
                default_result[team] = min(default_result[team], 1500)

    # Add per-team random variance to fallback valuations (±25%) for realistic spread
    p_set_fallback = player.get('set_no', 99)
    for team in list(default_result.keys()):
        if default_result[team] > 0 and team != game_state.get('user_team'):
            # Higher variance for earlier sets (more excitement), lower for late sets
            if p_set_fallback <= 2:
                variance = random.uniform(0.75, 1.30)  # ±30% for marquee sets
            elif p_set_fallback <= 4:
                variance = random.uniform(0.80, 1.20)  # ±20% for mid sets
            else:
                variance = random.uniform(0.88, 1.12)  # ±12% for late sets
            varied_val = int(default_result[team] * variance)
            sa_check = team_analyses.get(team)
            if sa_check:
                # Still cap to budget
                varied_val = min(varied_val, sa_check['budget'])
            default_result[team] = max(player['base_price'], varied_val) if default_result[team] >= player['base_price'] else varied_val
    print(f"\n[FALLBACK Vals] {player['name']} | Market:₹{market_value}L | {json.dumps(default_result)}")
    return default_result

# ─── ROUTES (ALL ORIGINAL ROUTES PRESERVED) ───────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html',
                           teams=game_state['teams'],
                           team_colors=TEAM_COLORS)

@app.route('/api/init', methods=['GET'])
def api_init():
    return jsonify({
        "teams": {k: {
            "budget": v["budget"],
            "overseas_count": v["overseas_count"],
            "total_players": v["total_players"],
            "squad": v["squad"],
            "colors": v["colors"],
        } for k, v in game_state['teams'].items()},
        "team_colors": TEAM_COLORS,
        "total_players_pool": len(game_state['players_pool']),
    })

@app.route('/api/set_team', methods=['POST'])
def set_team():
    data = request.json
    game_state['user_team'] = data['team']
    return jsonify({"status": "ok", "team": data['team']})

@app.route('/api/start_player', methods=['POST'])
def start_player():
    # Check if main pool is empty
    if not game_state['players_pool']:
        # Try additional set (unsold players)
        if game_state['additional_set']:
            player = game_state['additional_set'].pop(0)
            game_state['current_player'] = player
            game_state['current_bid'] = player['base_price']
            game_state['current_bidder'] = None
            game_state['user_passed'] = False
            game_state['_prev_bidder'] = None  # Reset bidding battle state
            game_state['_battle_stall_rounds'] = 0
            game_state['round_num'] += 1
            game_state['auction_started'] = True
        else:
            # Auction complete
            return jsonify({"status": "game_over", "sold": game_state['total_sold'], "unsold": game_state['total_unsold']})
    else:
        player = game_state['players_pool'].pop(0)
        game_state['current_player'] = player
        game_state['current_bid'] = player['base_price']
        game_state['current_bidder'] = None
        game_state['user_passed'] = False
        game_state['_prev_bidder'] = None  # Reset bidding battle state
        game_state['_battle_stall_rounds'] = 0
        game_state['round_num'] += 1
        game_state['auction_started'] = True

    # Generate AI valuations via full intelligence engine
    game_state['ai_valuations'] = generate_ai_valuations(player)
    
    # Check RTM eligibility
    rtm_eligible_team = None
    rtm_cards_available = 0
    last_team_clean = (player.get('stats', {}).get('last_team') or '').strip()
    if last_team_clean and last_team_clean in game_state['teams']:
        rtm_cards = game_state['rtm_cards_available'].get(last_team_clean, 0)
        if rtm_cards > 0:
            rtm_eligible_team = last_team_clean
            rtm_cards_available = rtm_cards
    
    return jsonify({
        "status": "active",
        "player": player,
        "base_price": player['base_price'],
        "rtm_eligible_team": rtm_eligible_team,
        "rtm_cards_available": rtm_cards_available,
        "teams": {k: {
            "budget": v["budget"],
            "overseas_count": v["overseas_count"],
            "total_players": v["total_players"],
            "squad": v["squad"],
            "colors": v["colors"],
        } for k, v in game_state['teams'].items()},
        "players_remaining": len(game_state['players_pool']),
        "round_num": game_state['round_num'],
        "ai_valuations_summary": {k: v for k, v in game_state['ai_valuations'].items()},
    })

@app.route('/api/place_bid', methods=['POST'])
def place_bid():
    team = game_state['user_team']
    t_data = game_state['teams'][team]
    p = game_state['current_player']
    
    # Safety check
    if not p:
        return jsonify({"status": "fail", "msg": "No active player to bid on"})
    
    current = game_state['current_bid']
    
    # What the next bid should be
    if game_state['current_bidder'] is None:
        new_bid = current  # Opening bid at base price
    else:
        new_bid = current + get_increment(current)
    
    # Validations
    if new_bid > t_data['budget']:
        return jsonify({"status": "fail", "msg": f"Not enough budget! You have ₹{t_data['budget']}L"})
    
    # BUDGET RESERVE CHECK: Warn if bid would compromise squad completion
    slots_to_18 = max(0, 18 - t_data['total_players'])
    # Tiered reserve: >=10 players→*30, >=5→*50, <5→*25
    _reserve_mult = 30 if t_data['total_players'] >= 10 else (50 if t_data['total_players'] >= 5 else 25)
    min_reserve = slots_to_18 * _reserve_mult
    if t_data['total_players'] < 18 and (t_data['budget'] - new_bid) < min_reserve:
        return jsonify({"status": "fail", "msg": f"⚠️ This bid would leave insufficient budget to complete minimum 18-player squad! You need ₹{min_reserve}L reserved for {slots_to_18} more slots."})
    
    if t_data['total_players'] >= 25:
        return jsonify({"status": "fail", "msg": "Squad is full! (25 players max)"})
    if p['is_overseas'] and t_data['overseas_count'] >= 8:
        return jsonify({"status": "fail", "msg": "Overseas slots full! (8 max)"})

    game_state['current_bid'] = new_bid
    game_state['current_bidder'] = team
    
    # Track bid in history
    import datetime
    game_state['bid_history'].append({
        'player_name': p['name'],
        'team': team,
        'price': new_bid,
        'timestamp': datetime.datetime.now().strftime('%H:%M:%S')
    })
    
    return jsonify({"status": "success", "bid": new_bid, "bidder": team})

@app.route('/api/user_pass', methods=['POST'])
def user_pass():
    game_state['user_passed'] = True
    return jsonify({"status": "ok"})

@app.route('/api/poll', methods=['POST'])
def poll_auction():
    """
    Core auction engine. Called every 1s by frontend.
    Determines if any AI wants to bid based on pre-computed valuations.
    Uses weighted random selection + realistic timing.
    """
    # Safety check if no active player
    if not game_state['current_player']:
        return jsonify({"action": "wait"})
    
    current_bid    = game_state['current_bid']
    current_bidder = game_state['current_bidder']
    
    if current_bidder is None:
        next_bid = current_bid
    else:
        next_bid = current_bid + get_increment(current_bid)

    # ── Find valid AI bidders ──
    candidates = []
    for team, max_val in game_state['ai_valuations'].items():
        if team == current_bidder:
            continue
        if team == game_state['user_team']:
            continue
        
        t_data = game_state['teams'][team]
        p      = game_state['current_player']
        
        # BUDGET RESERVE CHECK: Ensure team can complete minimum 18 players
        remaining_slots = 25 - t_data['total_players']
        slots_to_18 = max(0, 18 - t_data['total_players'])
        
        # Reserve per slot based on squad size: >=10→*30, >=5→*50, <5→*25
        _reserve_mult = 30 if t_data['total_players'] >= 10 else (50 if t_data['total_players'] >= 5 else 25)
        min_reserve_for_squad = slots_to_18 * _reserve_mult
        
        # Team must have budget for: this bid + reserve for minimum squad
        can_afford_safely = (next_bid <= t_data['budget']) and (t_data['budget'] - next_bid >= min_reserve_for_squad)
        
        wants_it    = next_bid <= max_val
        has_space   = t_data['total_players'] < 25
        os_valid    = not (p['is_overseas'] and t_data['overseas_count'] >= 8)
        
        if can_afford_safely and wants_it and has_space and os_valid:
            eagerness = max_val - next_bid  # how much headroom they have
            candidates.append((team, eagerness, max_val))
    
    # ── SQUAD COMPLETION FALLBACK: Force teams with < 18 players to bid if no one else will ──
    if not candidates or len(candidates) < 2:
        # Check if any team needs squad completion and can afford base price
        for team in game_state['ai_valuations']:
            if team == current_bidder or team == game_state['user_team']:
                continue
            
            t_data = game_state['teams'][team]
            p = game_state['current_player']
            
            if t_data['total_players'] < 18:  # MUST complete squad
                slots_to_18 = max(0, 18 - t_data['total_players'])
                _reserve_mult = 30 if t_data['total_players'] >= 10 else (50 if t_data['total_players'] >= 5 else 25)
                min_reserve_for_squad = slots_to_18 * _reserve_mult
                
                # Check if they can afford base price + reserve
                can_afford_base = t_data['budget'] >= p['base_price'] and (t_data['budget'] - p['base_price'] >= min_reserve_for_squad)
                has_space = t_data['total_players'] < 25
                os_valid = not (p['is_overseas'] and t_data['overseas_count'] >= 8)
                
                if can_afford_base and has_space and os_valid and team not in [t for t, _, _ in candidates]:
                    # Force this team to bid - they MUST complete squad
                    candidates.append((team, 1.0, p['base_price']))
                    break  # Just one for this round
    
    if not candidates:
        return jsonify({"action": "wait"})
    
    # ── Bid timing realism ──
    # Opening bid: someone should jump in quickly (high chance)
    # Counter-bid: simulate thinking time (moderate chance)
    # Near max value: hesitation increases (lower chance per tick)
    max_eagerness = max(e for _, e, _ in candidates) + 1

    # Teams close to their max are more hesitant
    adjusted_candidates = []
    for team, eagerness, max_val in candidates:
        # closeness_to_max: 1.0 = lots of headroom, 0.0 = at their absolute ceiling
        closeness_to_max = (max_val - next_bid) / max(max_val, 1)
        adjusted_candidates.append((team, eagerness, closeness_to_max))

    if current_bidder is None:
        # First bid on a player — someone should step in immediately
        bid_chance = 0.95
    else:
        # Use the MOST EAGER team's headroom to set bid pace.
        # The team with the most room should drive the auction forward.
        best_closeness = max(c for _, _, c in adjusted_candidates)
        # best_closeness ~1.0 (plenty of room)  → bid_chance ~0.93
        # best_closeness ~0.3 (near max)         → bid_chance ~0.75
        # best_closeness ~0.0 (at absolute max)  → bid_chance ~0.62
        # This ensures teams reliably bid to 90-95% of their valuation.
        bid_chance = 0.62 + (best_closeness * 0.31)

    if random.random() > bid_chance:
        return jsonify({"action": "wait"})
    
    # ── REALISTIC BIDDING BATTLES: Two teams fight, others join only if battle stalls ──
    # Track ongoing battle between top 2 bidders
    # After 3+ rounds of same bidder, open to new teams (battle stalled)
    prev_bidder = game_state.get('_prev_bidder')
    if current_bidder != prev_bidder:
        game_state['_prev_bidder'] = current_bidder
        game_state['_battle_stall_rounds'] = 0
    else:
        game_state['_battle_stall_rounds'] += 1
    
    battle_is_stalled = game_state['_battle_stall_rounds'] >= 3
    
    # ── Weighted selection: bidding battle preferrence ──
    # If we have top 2 candidates and battle not stalled, keep them fighting
    if len(adjusted_candidates) >= 2 and not battle_is_stalled and current_bidder:
        # Sort by eagerness to find top 2
        sorted_candidates = sorted(adjusted_candidates, key=lambda x: x[1], reverse=True)
        top_2_teams = {sorted_candidates[0][0], sorted_candidates[1][0]}
        
        # Prefer to keep battle between top 2 (80% chance)
        if current_bidder in top_2_teams and random.random() < 0.80:
            # Current bidder's opponent should raise
            for team, _, _ in sorted_candidates:
                if team != current_bidder and team in top_2_teams:
                    winner = team
                    break
        else:
            # 20% chance or new candidates to enter
            weights = [max(0.05, e / max_eagerness) for _, e, _ in adjusted_candidates]
            total_w = sum(weights)
            r = random.random() * total_w
            cumulative = 0.0
            winner = adjusted_candidates[0][0]
            for (team, eagerness, _), w in zip(adjusted_candidates, weights):
                cumulative += w
                if r <= cumulative:
                    winner = team
                    break
    else:
        # Normal weighted selection when battle not active or stalled
        weights = [max(0.05, e / max_eagerness) for _, e, _ in adjusted_candidates]
        total_w = sum(weights)
        r = random.random() * total_w
        cumulative = 0.0
        winner = adjusted_candidates[0][0]
        for (team, eagerness, _), w in zip(adjusted_candidates, weights):
            cumulative += w
            if r <= cumulative:
                winner = team
                break
    
    game_state['current_bid']    = next_bid
    game_state['current_bidder'] = winner
    
    # Track AI bid in history
    import datetime
    if game_state['current_player']:
        game_state['bid_history'].append({
            'player_name': game_state['current_player']['name'],
            'team': winner,
            'price': next_bid,
            'timestamp': datetime.datetime.now().strftime('%H:%M:%S')
        })
    
    # Check if user can still counter
    user_next = next_bid + get_increment(next_bid)
    user_can_bid = (
        user_next <= game_state['teams'][game_state['user_team']]['budget'] and
        not game_state['user_passed']
    )
    
    return jsonify({
        "action": "bid",
        "team": winner,
        "amount": next_bid,
        "team_color": TEAM_COLORS.get(winner, {}).get("primary", "#fff"),
        "user_can_counter": user_can_bid,
    })

@app.route('/api/finalize', methods=['POST'])
def finalize_player():
    winner = game_state['current_bidder']
    price  = game_state['current_bid']
    player = game_state['current_player']
    
    # Safety check if player is None
    if not player:
        return jsonify({
            "status": "error",
            "msg": "No player to finalize",
            "teams": {k: {
                "budget":         v["budget"],
                "overseas_count": v["overseas_count"],
                "total_players":  v["total_players"],
                "squad":          v["squad"],
                "colors":         v["colors"],
            } for k, v in game_state['teams'].items()},
            "history":           game_state['sold_history'][:20],
            "players_remaining": len(game_state['players_pool']),
        })
    
    # Check RTM eligibility
    rtm_eligible_team = game_state.get('rtm_eligible_team')
    rtm_cards = game_state.get('rtm_cards_available', {}).get(rtm_eligible_team, 0) if rtm_eligible_team else 0
    
    # If RTM is applicable and there's a winning bid
    if winner and rtm_eligible_team and rtm_cards > 0:
        # RTM team has the option to match
        t_rtm = game_state['teams'].get(rtm_eligible_team)
        if t_rtm and t_rtm['budget'] >= price:
            # Can afford - trigger RTM flow
            game_state['rtm_in_progress'] = True
            game_state['rtm_highest_bidder'] = winner
            game_state['rtm_highest_bid'] = price
            
            # Check if RTM team is user or AI
            is_rtm_user_team = (rtm_eligible_team == game_state.get('user_team'))
            
            if is_rtm_user_team:
                # User is RTM team - show UI for user to decide match/raise/pass
                return jsonify({
                    "status": "rtm_pending",
                    "rtm_team": rtm_eligible_team,
                    "is_user_rtm": True,
                    "rtm_cards_left": rtm_cards,
                    "highest_bidder": winner,
                    "highest_bid": price,
                    "player_name": player['name'],
                    "can_afford": True,
                    "msg": f"🎯 You have RTM! Match at ₹{price}L, raise higher, or pass?",
                })
            else:
                # AI is RTM team - will auto-decide
                return jsonify({
                    "status": "rtm_ai_pending",
                    "rtm_team": rtm_eligible_team,
                    "is_user_rtm": False,
                    "rtm_cards_left": rtm_cards,
                    "highest_bidder": winner,
                    "highest_bid": price,
                    "player_name": player['name'],
                    "msg": f"🤖 {rtm_eligible_team} is evaluating RTM... (auto-deciding)",
                    "teams": {k: {
                        "budget": v["budget"],
                        "overseas_count": v["overseas_count"],
                        "total_players": v["total_players"],
                        "squad": v["squad"],
                        "colors": v["colors"],
                    } for k, v in game_state['teams'].items()},
                })
    
    # No RTM or RTM not triggered - proceed with normal finalization
    if winner:
        t = game_state['teams'][winner]
        t['budget']       -= price
        t['total_players'] += 1
        if player['is_overseas']:
            t['overseas_count'] += 1
        t['squad'].append({
            "name":        player['name'],
            "price":       price,
            "role":        player['role'],
            "is_overseas": player['is_overseas'],
            "country":     player['country'],
            "bat_style":   player.get('bat_style',''),
            "bowl_style":  player.get('bowl_style',''),
        })
        game_state['total_sold'] += 1
        msg    = f"SOLD to {winner} for ₹{price}L"
        status = "sold"
    else:
        # UNSOLD - Move to additional set (will come back at the end)
        game_state['total_unsold'] += 1
        game_state['unsold_players'].append(player)
        game_state['additional_set'].append(player)  # Add to additional set pool
        msg    = "UNSOLD"
        status = "unsold"
    
    # Create player card for auction log
    create_player_card(player, winner, price, status)
    
    history_entry = {
        "name":        player['name'],
        "role":        player['role'],
        "team":        winner or "UNSOLD",
        "price":       price if winner else 0,
        "is_overseas": player['is_overseas'],
        "country":     player['country'],
        "status":      status,
        "color":       TEAM_COLORS.get(winner, {}).get("primary", "#666") if winner else "#666",
        "player":      player,
    }
    game_state['sold_history'].insert(0, history_entry)
    
    # Reset bidding state for next player
    game_state['current_player'] = None
    game_state['current_bidder'] = None
    game_state['current_bid'] = 0
    game_state['user_passed'] = False
    game_state['rtm_eligible_team'] = None
    
    return jsonify({
        "status":          "completed",
        "result_status":   status,
        "msg":             msg,
        "winner":          winner,
        "price":           price,
        "teams": {k: {
            "budget":         v["budget"],
            "overseas_count": v["overseas_count"],
            "total_players":  v["total_players"],
            "squad":          v["squad"],  # Include squad for auto-update
            "colors":         v["colors"],
        } for k, v in game_state['teams'].items()},
        "history":           game_state['sold_history'][:20],
        "players_remaining": len(game_state['players_pool']),
        "additional_set_count": len(game_state.get('additional_set', [])),
    })

@app.route('/api/rtm_exercise', methods=['POST'])
def rtm_exercise():
    """RTM team decides whether to use RTM card or pass"""
    data = request.get_json() or {}
    use_rtm = data.get('use_rtm', False)
    
    rtm_team = game_state.get('rtm_eligible_team')
    if not rtm_team or not game_state.get('rtm_in_progress'):
        return jsonify({"status": "error", "msg": "No RTM in progress"}), 400
    
    # Only allow if user is RTM team
    if rtm_team != game_state.get('user_team'):
        return jsonify({"status": "error", "msg": "Only RTM team can exercise RTM"}), 400
    
    player = game_state['current_player']
    highest_bidder = game_state.get('rtm_highest_bidder')
    highest_bid = game_state.get('rtm_highest_bid', 0)
    
    if use_rtm:
        # RTM team uses the card
        game_state['rtm_cards_available'][rtm_team] -= 1
        
        # RTM team can decide to raise or just match
        rtm_raise_price = data.get('rtm_raise_price', highest_bid)  # Default: match current price
        if rtm_raise_price < highest_bid:
            rtm_raise_price = highest_bid  # Can't lower the price
        
        t_rtm = game_state['teams'][rtm_team]
        if rtm_raise_price > t_rtm['budget']:
            return jsonify({"status": "error", "msg": f"RTM raise price ₹{rtm_raise_price}L exceeds your budget ₹{t_rtm['budget']}L"}), 400
        
        # Check budget reserve
        slots_to_18 = max(0, 18 - t_rtm['total_players'])
        _reserve_mult = 30 if t_rtm['total_players'] >= 10 else (50 if t_rtm['total_players'] >= 5 else 25)
        min_reserve = slots_to_18 * _reserve_mult
        if t_rtm['budget'] - rtm_raise_price < min_reserve:
            return jsonify({"status": "error", "msg": f"RTM raise would compromise squad completion. Need ₹{min_reserve}L reserved."}), 400
        
        # Update the bid to RTM team's raise price
        game_state['rtm_highest_bid'] = rtm_raise_price
        
        return jsonify({
            "status": "rtm_used",
            "rtm_team": rtm_team,
            "msg": f"{rtm_team} used RTM card and {'raised to' if rtm_raise_price > highest_bid else 'matched'} ₹{rtm_raise_price}L!",
            "highest_bidder": highest_bidder,
            "current_price": rtm_raise_price,
            "rtm_cards_left": game_state['rtm_cards_available'][rtm_team],
            "awaiting_counter": True,  # Highest bidder now decides if they counter-raise
            "teams": {k: {
                "budget": v["budget"],
                "overseas_count": v["overseas_count"],
                "total_players": v["total_players"],
                "squad": v["squad"],
                "colors": v["colors"],
            } for k, v in game_state['teams'].items()},
        })
    else:
        # RTM team passes - player goes to highest bidder
        game_state['rtm_in_progress'] = False
        game_state['rtm_eligible_team'] = None
        
        # Finalize to highest bidder
        t = game_state['teams'][highest_bidder]
        t['budget'] -= highest_bid
        t['total_players'] += 1
        if player['is_overseas']:
            t['overseas_count'] += 1
        t['squad'].append({
            "name": player['name'],
            "price": highest_bid,
            "role": player['role'],
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "bat_style": player.get('bat_style',''),
            "bowl_style": player.get('bowl_style',''),
        })
        
        # Create player card
        create_player_card(player, highest_bidder, highest_bid, "sold")
        
        game_state['sold_history'].insert(0, {
            "name": player['name'],
            "role": player['role'],
            "team": highest_bidder,
            "price": highest_bid,
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "status": "sold",
            "color": TEAM_COLORS.get(highest_bidder, {}).get("primary", "#666"),
            "player": player,
        })
        
        # Reset state
        game_state['current_player'] = None
        game_state['current_bidder'] = None
        game_state['current_bid'] = 0
        game_state['user_passed'] = False
        
        return jsonify({
            "status": "rtm_passed",
            "msg": f"{rtm_team} passed on RTM",
            "winner": highest_bidder,
            "price": highest_bid,
            "teams": {k: {
                "budget": v["budget"],
                "overseas_count": v["overseas_count"],
                "total_players": v["total_players"],
                "squad": v["squad"],
                "colors": v["colors"],
            } for k, v in game_state['teams'].items()},
            "history": game_state['sold_history'][:20],
            "players_remaining": len(game_state['players_pool']),
        })

@app.route('/api/rtm_increment', methods=['POST'])
def rtm_increment():
    """Highest bidder decides whether to raise bid after RTM is used"""
    data = request.get_json() or {}
    raise_bid = data.get('raise_bid', False)
    new_price = data.get('new_price', 0)
    
    if not game_state.get('rtm_in_progress'):
        return jsonify({"status": "error", "msg": "No RTM in progress"}), 400
    
    player = game_state['current_player']
    rtm_team = game_state.get('rtm_eligible_team')
    highest_bidder = game_state.get('rtm_highest_bidder')
    current_price = game_state.get('rtm_highest_bid', 0)
    
    if raise_bid and new_price > current_price:
        # Bidder raises - RTM team gets final chance to match
        game_state['rtm_highest_bid'] = new_price
        game_state['current_bid'] = new_price
        
        # Check if RTM team can afford the new price
        t_rtm = game_state['teams'][rtm_team]
        can_afford = t_rtm['budget'] >= new_price
        
        return jsonify({
            "status": "bid_raised",
            "msg": f"{highest_bidder} raised bid to ₹{new_price}L",
            "new_price": new_price,
            "rtm_team": rtm_team,
            "highest_bidder": highest_bidder,
            "can_rtm_afford": can_afford,
            "awaiting_final_rtm": True,
            "teams": {k: {
                "budget": v["budget"],
                "overseas_count": v["overseas_count"],
                "total_players": v["total_players"],
                "squad": v["squad"],
                "colors": v["colors"],
            } for k, v in game_state['teams'].items()},
        })
    else:
        # Bidder doesn't raise - player goes to RTM team at original price
        game_state['rtm_in_progress'] = False
        game_state['rtm_eligible_team'] = None
        
        t_rtm = game_state['teams'][rtm_team]
        t_rtm['budget'] -= current_price
        t_rtm['total_players'] += 1
        if player['is_overseas']:
            t_rtm['overseas_count'] += 1
        t_rtm['squad'].append({
            "name": player['name'],
            "price": current_price,
            "role": player['role'],
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "bat_style": player.get('bat_style',''),
            "bowl_style": player.get('bowl_style',''),
        })
        
        # Create player card
        create_player_card(player, rtm_team, current_price, "sold_rtm")
        
        game_state['sold_history'].insert(0, {
            "name": player['name'],
            "role": player['role'],
            "team": rtm_team,
            "price": current_price,
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "status": "sold_rtm",
            "color": TEAM_COLORS.get(rtm_team, {}).get("primary", "#666"),
            "player": player,
        })
        
        # Reset state
        game_state['current_player'] = None
        game_state['current_bidder'] = None
        game_state['current_bid'] = 0
        game_state['user_passed'] = False
        
        return jsonify({
            "status": "rtm_success",
            "msg": f"{rtm_team} retained via RTM for ₹{current_price}L",
            "winner": rtm_team,
            "price": current_price,
            "teams": {k: {
                "budget": v["budget"],
                "overseas_count": v["overseas_count"],
                "total_players": v["total_players"],
                "squad": v["squad"],
                "colors": v["colors"],
            } for k, v in game_state['teams'].items()},
            "history": game_state['sold_history'][:20],
            "players_remaining": len(game_state['players_pool']),
        })

@app.route('/api/rtm_final_match', methods=['POST'])
def rtm_final_match():
    """RTM team's final decision to match raised bid or pass"""
    data = request.get_json() or {}
    match_bid = data.get('match_bid', False)
    
    if not game_state.get('rtm_in_progress'):
        return jsonify({"status": "error", "msg": "No RTM in progress"}), 400
    
    player = game_state['current_player']
    rtm_team = game_state.get('rtm_eligible_team')
    highest_bidder = game_state.get('rtm_highest_bidder')
    final_price = game_state.get('rtm_highest_bid', 0)
    
    game_state['rtm_in_progress'] = False
    game_state['rtm_eligible_team'] = None
    
    if match_bid:
        # RTM team matches the raised bid
        t_rtm = game_state['teams'][rtm_team]
        t_rtm['budget'] -= final_price
        t_rtm['total_players'] += 1
        if player['is_overseas']:
            t_rtm['overseas_count'] += 1
        t_rtm['squad'].append({
            "name": player['name'],
            "price": final_price,
            "role": player['role'],
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "bat_style": player.get('bat_style',''),
            "bowl_style": player.get('bowl_style',''),
        })
        
        create_player_card(player, rtm_team, final_price, "sold_rtm")
        game_state['sold_history'].insert(0, {
            "name": player['name'],
            "role": player['role'],
            "team": rtm_team,
            "price": final_price,
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "status": "sold_rtm",
            "color": TEAM_COLORS.get(rtm_team, {}).get("primary", "#666"),
            "player": player,
        })
        
        winner = rtm_team
        msg = f"{rtm_team} matched RTM for ₹{final_price}L!"
    else:
        # RTM team passes - player goes to highest bidder
        t = game_state['teams'][highest_bidder]
        t['budget'] -= final_price
        t['total_players'] += 1
        if player['is_overseas']:
            t['overseas_count'] += 1
        t['squad'].append({
            "name": player['name'],
            "price": final_price,
            "role": player['role'],
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "bat_style": player.get('bat_style',''),
            "bowl_style": player.get('bowl_style',''),
        })
        
        create_player_card(player, highest_bidder, final_price, "sold")
        game_state['sold_history'].insert(0, {
            "name": player['name'],
            "role": player['role'],
            "team": highest_bidder,
            "price": final_price,
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "status": "sold",
            "color": TEAM_COLORS.get(highest_bidder, {}).get("primary", "#666"),
            "player": player,
        })
        
        winner = highest_bidder
        msg = f"{rtm_team} couldn't match - {highest_bidder} wins for ₹{final_price}L"
    
    # Reset state
    game_state['current_player'] = None
    game_state['current_bidder'] = None
    game_state['current_bid'] = 0
    game_state['user_passed'] = False
    
    return jsonify({
        "status": "completed",
        "msg": msg,
        "winner": winner,
        "price": final_price,
        "teams": {k: {
            "budget": v["budget"],
            "overseas_count": v["overseas_count"],
            "total_players": v["total_players"],
            "squad": v["squad"],
            "colors": v["colors"],
        } for k, v in game_state['teams'].items()},
        "history": game_state['sold_history'][:20],
        "players_remaining": len(game_state['players_pool']),
    })

@app.route('/api/rtm_ai_decide', methods=['POST'])
def rtm_ai_decide():
    """AI RTM team decides to use/pass RTM. If user is highest bidder, return decision point. If AI vs AI, return complete result."""
    if not game_state.get('rtm_in_progress'):
        return jsonify({"status": "error", "msg": "No RTM in progress"}), 400
    
    player = game_state['current_player']
    rtm_team = game_state.get('rtm_eligible_team')
    highest_bidder = game_state.get('rtm_highest_bidder')
    price = game_state.get('rtm_highest_bid', 0)
    
    t_rtm = game_state['teams'][rtm_team]
    
    # AI decision: Use RTM based on realistic factors (50-50 decision framework)
    use_rtm = False
    sa = analyse_squad(rtm_team)
    
    if t_rtm['budget'] >= price:
        needs_squad_completion = sa['total'] < 18
        has_critical_gap = len(sa['critical_gaps']) > 0
        xi_fit = player_fits_xi_need(player, sa, rtm_team)
        
        if needs_squad_completion:
            use_rtm = True
        elif xi_fit > 0.7 and price <= sa['budget'] * 0.3:
            use_rtm = random.random() < 0.6
        elif has_critical_gap and price <= sa['budget_per_slot'] * 1.5:
            use_rtm = random.random() < 0.55
        elif sa['total'] < 8 and TEAM_STRATEGIES[rtm_team].get('bidding_style','').startswith('ultra') or 'aggressive' in TEAM_STRATEGIES[rtm_team].get('bidding_style',''):
            use_rtm = random.random() < 0.5
        else:
            use_rtm = random.random() < 0.25
    
    rtm_used = use_rtm
    
    # Check if highest bidder is user
    is_user_bidder = (highest_bidder == game_state.get('user_team'))
    
    if use_rtm:
        # RTM team deducts card
        game_state['rtm_cards_available'][rtm_team] -= 1
        rtm_cards_left = game_state['rtm_cards_available'][rtm_team]
        
        # RTM team raises the price
        new_price = price + get_increment(price)
        game_state['rtm_highest_bid'] = new_price
        
        if is_user_bidder:
            # User needs to decide counter-raise - return decision point 
            # Frontend will show increment modal
            return jsonify({
                "status": "rtm_ai_used_awaiting_user",
                "rtm_team": rtm_team,
                "highest_bidder": highest_bidder,
                "rtm_raised_price": new_price,
                "original_price": price,
                "rtm_cards_left": rtm_cards_left,
                "msg": f"🎯 {rtm_team} used RTM and raised to ₹{new_price}L! Your decision needed.",
                "awaiting_user_counter": True
            })
        else:
            # AI vs AI - AI highest bidder decides to counter-raise or not
            t_bidder = game_state['teams'][highest_bidder]
            sa_bidder = analyse_squad(highest_bidder)
            
            bid_raised = False
            final_price = new_price
            counter_price = new_price  # Track for step display
            final_winner = rtm_team  # Default: RTM team wins
            
            # AI logic: Raise if budget allows and player is valuable
            if t_bidder['budget'] >= new_price + 100:
                slots_to_18_bidder = max(0, 18 - t_bidder['total_players'])
                min_reserve_bidder = slots_to_18_bidder * 100
                can_afford_raise = (t_bidder['budget'] - new_price - 100 >= min_reserve_bidder)
                
                if sa_bidder.get('budget_pressure') not in ['critical', 'high'] and can_afford_raise:
                    # Raise by 10-20% of current price
                    increment = max(50, int(new_price * 0.15))
                    counter_price = new_price + increment
                    if counter_price <= t_bidder['budget']:
                        bid_raised = True
                        final_price = counter_price
                        game_state['rtm_highest_bid'] = final_price
            
            if bid_raised:
                # AI highest bidder raised - now RTM team makes final decision
                if t_rtm['budget'] >= final_price:
                    # Match if still within budget and valuable
                    if final_price <= sa.get('budget_per_slot', 0) * 2.5:
                        # Match - RTM team wins
                        final_winner = rtm_team
                    else:
                        # Too expensive - let go
                        final_winner = highest_bidder
                else:
                    # Can't afford - highest bidder wins
                    final_winner = highest_bidder
            # else: RTM team wins at raised price
            
            # Build RTM steps for frontend animation
            rtm_steps = [{"text": f"<b>{rtm_team}</b> uses RTM → raises bid to <b>₹{new_price}L</b>", "color": "#FF6B35"}]
            if bid_raised:
                rtm_steps.append({"text": f"<b>{highest_bidder}</b> counter-bids to <b>₹{counter_price}L</b>", "color": "#3B82F6"})
                if final_winner == rtm_team:
                    rtm_steps.append({"text": f"<b>{rtm_team}</b> MATCHES — player retained via RTM at <b>₹{final_price}L</b>", "color": "#22C55E"})
                else:
                    rtm_steps.append({"text": f"<b>{rtm_team}</b> backs down — <b>{highest_bidder}</b> wins at <b>₹{final_price}L</b>", "color": "#EF4444"})
            else:
                rtm_steps.append({"text": f"<b>{highest_bidder}</b> passes — <b>{rtm_team}</b> wins via RTM at <b>₹{new_price}L</b>", "color": "#22C55E"})
            
            # Finalize the sale
            game_state['rtm_in_progress'] = False
            game_state['rtm_eligible_team'] = None
            
            t_winner = game_state['teams'][final_winner]
            t_winner['budget'] -= final_price
            t_winner['total_players'] += 1
            if player['is_overseas']:
                t_winner['overseas_count'] += 1
            t_winner['squad'].append({
                "name": player['name'],
                "price": final_price,
                "role": player['role'],
                "is_overseas": player['is_overseas'],
                "country": player['country'],
                "bat_style": player.get('bat_style',''),
                "bowl_style": player.get('bowl_style',''),
            })
            
            status_type = "sold_rtm" if final_winner == rtm_team else "sold"
            create_player_card(player, final_winner, final_price, status_type)
            game_state['sold_history'].insert(0, {
                "name": player['name'],
                "role": player['role'],
                "team": final_winner,
                "price": final_price,
                "is_overseas": player['is_overseas'],
                "country": player['country'],
                "status": status_type,
                "color": TEAM_COLORS.get(final_winner, {}).get("primary", "#666"),
                "player": player,
            })
            
            # Reset state
            game_state['current_player'] = None
            game_state['current_bidder'] = None
            game_state['current_bid'] = 0
            game_state['user_passed'] = False
            
            return jsonify({
                "status": "completed",
                "msg": f"{final_winner} wins for ₹{final_price}L",
                "winner": final_winner,
                "price": final_price,
                "rtm_steps": rtm_steps,
                "teams": {k: {
                    "budget": v["budget"],
                    "overseas_count": v["overseas_count"],
                    "total_players": v["total_players"],
                    "squad": v["squad"],
                    "colors": v["colors"],
                } for k, v in game_state['teams'].items()},
                "history": game_state['sold_history'][:20],
                "players_remaining": len(game_state['players_pool']),
            })
    else:
        # RTM team passes - highest bidder wins
        rtm_steps = [{"text": f"<b>{rtm_team}</b> passes RTM — <b>{highest_bidder}</b> wins at <b>₹{price}L</b>", "color": "#EF4444"}]
        
        game_state['rtm_in_progress'] = False
        game_state['rtm_eligible_team'] = None
        
        t_winner = game_state['teams'][highest_bidder]
        t_winner['budget'] -= price
        t_winner['total_players'] += 1
        if player['is_overseas']:
            t_winner['overseas_count'] += 1
        t_winner['squad'].append({
            "name": player['name'],
            "price": price,
            "role": player['role'],
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "bat_style": player.get('bat_style',''),
            "bowl_style": player.get('bowl_style',''),
        })
        
        create_player_card(player, highest_bidder, price, "sold")
        game_state['sold_history'].insert(0, {
            "name": player['name'],
            "role": player['role'],
            "team": highest_bidder,
            "price": price,
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "status": "sold",
            "color": TEAM_COLORS.get(highest_bidder, {}).get("primary", "#666"),
            "player": player,
        })
        
        # Reset state
        game_state['current_player'] = None
        game_state['current_bidder'] = None
        game_state['current_bid'] = 0
        game_state['user_passed'] = False
        
        return jsonify({
            "status": "completed",
            "msg": f"{rtm_team} passed on RTM",
            "winner": highest_bidder,
            "price": price,
            "rtm_steps": rtm_steps,
            "teams": {k: {
                "budget": v["budget"],
                "overseas_count": v["overseas_count"],
                "total_players": v["total_players"],
                "squad": v["squad"],
                "colors": v["colors"],
            } for k, v in game_state['teams'].items()},
            "history": game_state['sold_history'][:20],
            "players_remaining": len(game_state['players_pool']),
        })

@app.route('/api/rtm_ai_counter', methods=['POST'])
def rtm_ai_counter():
    """AI highest bidder decides whether to raise counter-bid"""
    if not game_state.get('rtm_in_progress'):
        return jsonify({"status": "error", "msg": "No RTM in progress"}), 400
    
    player = game_state['current_player']
    rtm_team = game_state.get('rtm_eligible_team')
    highest_bidder = game_state.get('rtm_highest_bidder')
    current_price = game_state.get('rtm_highest_bid', 0)
    
    t_bidder = game_state['teams'][highest_bidder]
    sa_bidder = analyse_squad(highest_bidder)
    
    raise_bid = False
    new_price = current_price
    
    # AI logic: Raise if budget allows and player is valuable
    if t_bidder['budget'] >= current_price + get_increment(current_price):
        if sa_bidder.get('budget_pressure') not in ['critical', 'high']:
            new_price = current_price + get_increment(current_price)
            if new_price <= t_bidder['budget']:
                raise_bid = True
    
    if raise_bid:
        game_state['rtm_highest_bid'] = new_price
        return jsonify({
            "status": "bid_raised",
            "msg": f"{highest_bidder} raised bid to ₹{new_price}L",
            "new_price": new_price,
            "rtm_team": rtm_team,
            "can_rtm_afford": game_state['teams'][rtm_team]['budget'] >= new_price,
            "awaiting_final_rtm": True
        })
    else:
        # Bidder doesn't raise - RTM team wins
        game_state['rtm_in_progress'] = False
        game_state['rtm_eligible_team'] = None
        
        t_rtm = game_state['teams'][rtm_team]
        t_rtm['budget'] -= current_price
        t_rtm['total_players'] += 1
        if player['is_overseas']:
            t_rtm['overseas_count'] += 1
        t_rtm['squad'].append({
            "name": player['name'],
            "price": current_price,
            "role": player['role'],
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "bat_style": player.get('bat_style',''),
            "bowl_style": player.get('bowl_style',''),
        })
        
        # Create player card
        create_player_card(player, rtm_team, current_price, "sold_rtm")
        
        game_state['sold_history'].insert(0, {
            "name": player['name'],
            "role": player['role'],
            "team": rtm_team,
            "price": current_price,
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "status": "sold_rtm",
            "color": TEAM_COLORS.get(rtm_team, {}).get("primary", "#666"),
            "player": player,
        })
        
        # Reset state
        game_state['current_player'] = None
        game_state['current_bidder'] = None
        game_state['current_bid'] = 0
        game_state['user_passed'] = False
        
        return jsonify({
            "status": "completed",
            "msg": f"{rtm_team} retained via RTM for ₹{current_price}L",
            "winner": rtm_team,
            "price": current_price,
            "teams": {k: {
                "budget": v["budget"],
                "overseas_count": v["overseas_count"],
                "total_players": v["total_players"],
                "squad": v["squad"],
                "colors": v["colors"],
            } for k, v in game_state['teams'].items()},
            "history": game_state['sold_history'][:20],
            "players_remaining": len(game_state['players_pool']),
        })

@app.route('/api/rtm_ai_final', methods=['POST'])
def rtm_ai_final():
    """AI RTM team makes final decision after counter-raise"""
    if not game_state.get('rtm_in_progress'):
        return jsonify({"status": "error", "msg": "No RTM in progress"}), 400
    
    player = game_state['current_player']
    rtm_team = game_state.get('rtm_eligible_team')
    highest_bidder = game_state.get('rtm_highest_bidder')
    final_price = game_state.get('rtm_highest_bid', 0)
    
    t_rtm = game_state['teams'][rtm_team]
    sa_rtm = analyse_squad(rtm_team)
    
    # AI decision: Match if affordable and within reasonable limit
    match_bid = False
    if t_rtm['budget'] >= final_price:
        if final_price <= sa_rtm.get('budget_per_slot', 0) * 2.5:
            match_bid = True
    
    game_state['rtm_in_progress'] = False
    game_state['rtm_eligible_team'] = None
    
    if match_bid:
        winner = rtm_team
        t_rtm['budget'] -= final_price
        t_rtm['total_players'] += 1
        if player['is_overseas']:
            t_rtm['overseas_count'] += 1
        t_rtm['squad'].append({
            "name": player['name'],
            "price": final_price,
            "role": player['role'],
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "bat_style": player.get('bat_style',''),
            "bowl_style": player.get('bowl_style',''),
        })
        status_type = "sold_rtm"
    else:
        winner = highest_bidder
        t_bidder = game_state['teams'][highest_bidder]
        t_bidder['budget'] -= final_price
        t_bidder['total_players'] += 1
        if player['is_overseas']:
            t_bidder['overseas_count'] += 1
        t_bidder['squad'].append({
            "name": player['name'],
            "price": final_price,
            "role": player['role'],
            "is_overseas": player['is_overseas'],
            "country": player['country'],
            "bat_style": player.get('bat_style',''),
            "bowl_style": player.get('bowl_style',''),
        })
        status_type = "sold"
    
    # Create player card
    create_player_card(player, winner, final_price, status_type)
    
    game_state['sold_history'].insert(0, {
        "name": player['name'],
        "role": player['role'],
        "team": winner,
        "price": final_price,
        "is_overseas": player['is_overseas'],
        "country": player['country'],
        "status": status_type,
        "color": TEAM_COLORS.get(winner, {}).get("primary", "#666"),
        "player": player,
    })
    
    # Reset state
    game_state['current_player'] = None
    game_state['current_bidder'] = None
    game_state['current_bid'] = 0
    game_state['user_passed'] = False
    
    return jsonify({
        "status": "completed",
        "msg": f"{winner} wins for ₹{final_price}L",
        "winner": winner,
        "price": final_price,
        "teams": {k: {
            "budget": v["budget"],
            "overseas_count": v["overseas_count"],
            "total_players": v["total_players"],
            "squad": v["squad"],
            "colors": v["colors"],
        } for k, v in game_state['teams'].items()},
        "history": game_state['sold_history'][:20],
        "players_remaining": len(game_state['players_pool']),
    })

@app.route('/api/team_squad/<team_name>', methods=['GET'])
def get_team_squad(team_name):
    if team_name not in game_state['teams']:
        return jsonify({"error": "Team not found"}), 404
    t = game_state['teams'][team_name]
    return jsonify({
        "team":           team_name,
        "budget":         t['budget'],
        "squad":          t['squad'],
        "overseas_count": t['overseas_count'],
        "total_players":  t['total_players'],
        "colors":         t['colors'],
    })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    global PLAYERS_POOL_MASTER
    PLAYERS_POOL_MASTER              = load_players()
    game_state['teams']              = build_initial_teams()
    game_state['players_pool']       = list(PLAYERS_POOL_MASTER)
    game_state['current_player']     = None
    game_state['current_bid']        = 0
    game_state['current_bidder']     = None
    game_state['ai_valuations']      = {}
    game_state['sold_history']       = []
    game_state['unsold_players']     = []
    game_state['user_team']          = "RCB"
    game_state['user_passed']        = False
    game_state['total_sold']         = 0
    game_state['total_unsold']       = 0
    game_state['auction_started']    = False
    game_state['round_num']          = 0
    game_state['bid_history']        = []
    game_state['rtm_cards_available']= dict(RTM_CARDS_INITIAL)
    game_state['rtm_in_progress']    = False
    game_state['rtm_eligible_team']  = None
    game_state['rtm_highest_bidder'] = None
    game_state['rtm_highest_bid']    = 0
    return jsonify({"status": "reset_ok"})

@app.route('/api/get_sets_data', methods=['GET'])
def get_sets_data():
    """Return players grouped by set with navigation support"""
    from collections import defaultdict
    
    # Get requested set (default to current player's set)
    requested_set = request.args.get('set', None)
    
    # Get current player info
    current_player_name = game_state.get('current_player', {}).get('name') if game_state.get('current_player') else None
    current_player_set = game_state.get('current_player', {}).get('set', 'Unknown') if game_state.get('current_player') else None
    
    # Track processed players to avoid duplicates
    processed_names = set()
    sets_data = defaultdict(list)
    all_set_names = set()
    
    # Add sold players (prioritize sold status over remaining)
    # BUT skip unsold players - they'll appear in Additional Set only
    for entry in game_state.get('sold_history', []):
        player = entry['player']
        # Skip unsold players - they're handled in Additional Set
        if entry['team'] == 'UNSOLD' or entry.get('status') == 'unsold':
            continue
        
        set_name = player.get('set', 'Unknown')
        all_set_names.add(set_name)
        if player['name'] not in processed_names:
            processed_names.add(player['name'])
            sets_data[set_name].append({
                'name': player['name'],
                'role': player['role'],
                'country': player['country'],
                'base_price': player['base_price'],
                'status': 'SOLD',
                'sold_to': entry['team'],  # Use sold_to for frontend
                'sold_price': entry['price'],  # Use sold_price for frontend
                'is_current': False
            })
    
    # Add current player being auctioned
    if game_state.get('current_player'):
        player = game_state['current_player']
        set_name = player.get('set', 'Unknown')
        all_set_names.add(set_name)
        if player['name'] not in processed_names:
            processed_names.add(player['name'])
            sets_data[set_name].append({
                'name': player['name'],
                'role': player['role'],
                'country': player['country'],
                'base_price': player['base_price'],
                'status': 'CURRENT',
                'sold_to': None,
                'sold_price': None,
                'is_current': True
            })
    
    # Add remaining players in pool (not yet auctioned)
    for player in game_state.get('players_pool', []):
        set_name = player.get('set', 'Unknown')
        all_set_names.add(set_name)
        if player['name'] not in processed_names:
            processed_names.add(player['name'])
            sets_data[set_name].append({
                'name': player['name'],
                'role': player['role'],
                'country': player['country'],
                'base_price': player['base_price'],
                'status': 'REMAINING',
                'sold_to': None,
                'sold_price': None,
                'is_current': False
            })
    
    # Add unsold players in additional set (will come back later)
    if game_state.get('additional_set'):
        all_set_names.add('Additional')
        for player in game_state.get('additional_set', []):
            if player['name'] not in processed_names:
                processed_names.add(player['name'])
                sets_data['Additional'].append({
                    'name': player['name'],
                    'role': player['role'],
                    'country': player['country'],
                    'base_price': player['base_price'],
                    'status': 'UNSOLD',
                    'sold_to': None,
                    'sold_price': None,
                    'is_current': False
                })
    
    # Sort all set names by set_no (from players data)
    # Build a map of set_name -> set_no
    set_order_map = {}
    for player_list in sets_data.values():
        for p_info in player_list:
            # We need to look up the original player to get set_no
            pass
    
    # Alternative: get set info from players_pool and sold_history
    for player in game_state.get('players_pool', []):
        set_name = player.get('set', 'Unknown')
        set_no = player.get('set_no', 999)
        if set_name not in set_order_map or set_no < set_order_map[set_name]:
            set_order_map[set_name] = set_no
    
    for entry in game_state.get('sold_history', []):
        player = entry['player']
        set_name = player.get('set', 'Unknown')
        set_no = player.get('set_no', 999)
        if set_name not in set_order_map or set_no < set_order_map[set_name]:
            set_order_map[set_name] = set_no
    
    for player in game_state.get('additional_set', []):
        set_name = player.get('set', 'Unknown')
        set_no = player.get('set_no', 999)
        if set_name not in set_order_map or set_no < set_order_map[set_name]:
            set_order_map[set_name] = set_no
    
    # Sort sets by set_no, then alphabetically for unknown sets
    sorted_sets = sorted(
        [s for s in all_set_names if s != 'Additional'],
        key=lambda s: (set_order_map.get(s, 999), s)
    )
    if 'Additional' in all_set_names:
        sorted_sets.append('Additional')
    
    # Determine which set to display (default to current player's set)
    display_set = requested_set if requested_set else current_player_set
    if not display_set or display_set not in sorted_sets:
        display_set = sorted_sets[0] if sorted_sets else None
    
    # Find prev/next sets for navigation
    current_index = sorted_sets.index(display_set) if display_set in sorted_sets else 0
    prev_set = sorted_sets[current_index - 1] if current_index > 0 else None
    next_set = sorted_sets[current_index + 1] if current_index < len(sorted_sets) - 1 else None
    
    # Return only the requested set with navigation info
    set_display_name = display_set if display_set else 'Unknown'
    if display_set == 'Additional':
        set_display_name = 'Additional Set (Unsold)'
    
    return jsonify({
        'current_set': {
            'set_name': set_display_name,
            'players': sets_data.get(display_set, [])
        },
        'navigation': {
            'prev_set': prev_set,
            'next_set': next_set,
            'all_sets': sorted_sets,
            'current_index': current_index,
            'total_sets': len(sorted_sets)
        },
        'is_current_player_set': (display_set == current_player_set)
    })

@app.route('/api/get_auction_cards', methods=['GET'])
def get_auction_cards():
    """Return player cards for completed auctions (chronological log)"""
    return jsonify({
        'cards': game_state.get('auction_log_cards', []),
        'total_cards': len(game_state.get('auction_log_cards', []))
    })

@app.route('/api/get_live_log', methods=['GET'])
def get_live_log():
    """Return live bidding log for current auction"""
    log = []
    
    # Add entries from bid history (last 50 bids)
    bid_history = game_state.get('bid_history', [])
    for entry in bid_history[-50:]:
        log.append({
            'player_name': entry.get('player_name', 'Unknown'),
            'team': entry.get('team', 'Unknown'),
            'price': entry.get('price', 0),
            'action': 'BID',
            'timestamp': entry.get('timestamp', '')
        })
    
    # Add sold entries
    for entry in game_state.get('sold_history', [])[-20:]:
        log.append({
            'player_name': entry['player']['name'],
            'team': entry['team'],
            'price': entry['price'],
            'action': 'SOLD',
            'timestamp': entry.get('timestamp', '')
        })
    
    # Sort by timestamp if available, otherwise keep order
    log.sort(key=lambda x: x.get('timestamp', ''), reverse=False)
    
    return jsonify({
        'log': log,
        'total_entries': len(log)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
