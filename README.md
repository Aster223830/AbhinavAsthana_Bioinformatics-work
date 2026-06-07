# ADME Tier 2 Platemap Automation Tool

A Python command-line pipeline for automating Janus instrument file 
generation for ADME Tier 2 compound plating workflows at NCATS/NIH.

## Status
Active development — core pipeline functional, repeat/set logic 
and final platemap output in progress.

## Background
Each Tier 2 compound plating order has a unique layout — different 
numbers of compounds, repeats, empty wells, and skipped sections. 
Previously, generating the Janus instrument CSV and final platemap 
required manual interpretation of every order, taking over an hour 
per run and requiring significant institutional knowledge to perform 
correctly. This pipeline automates that process.

## Pipeline

### Step 1 — Clean the Order Platemap
`coverter_v3.py`

Takes the raw Store Order Platemap Excel file and:
- Removes unnecessary columns (Order ID, eLN, User, Description, Note)
- Adds a sequential Number column (1–N per plate)
- Adds a Set column for repeat group logic (in progress)
- Saves a cleaned Excel file ready for Janus generation

```bash
python3 "coverter v3.py"
```

### Step 2 — Generate Janus CSV
`janus_generator_sets_repeats.py`

Takes the cleaned platemap and generates:
- A Janus-compatible CSV with Source, Well, Dest, Well, Volume
- Correct compound orientation mapped to 384-well destination plate

```bash
python3 janus_generator_sets_repeats.py
```

## Roadmap
- [ ] Gap and empty well handling
- [ ] Repeat/set compound logic
- [ ] Final platemap output with compound metadata (MW, formula, 
      well locations)
- [ ] Direct intake from DMPK order format — fully automated 
      end-to-end pipeline

## Dependencies
- Python 3.9+
- pandas
- openpyxl

## Author
Abhi Asthana — Compound Management Scientist, NCATS/NIH
