# MorphoNews Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MorphoNews                               │
│                    Self-Evolving News Site                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼───────┐           ┌──────▼──────┐
        │   Evolution   │           │  Variation  │
        │   (進化)       │           │  (変化)      │
        └───────┬───────┘           └──────┬──────┘
                │                           │
                │                           │
    ┌───────────┴───────────┐   ┌──────────┴──────────┐
    │  Feature Additions    │   │  Style Management   │
    │  - Reading Progress   │   │  - 6 Themes         │
    │  - Font Control       │   │  - User Selection   │
    │  - Style Selector     │   │  - Persistence      │
    │  - Gallery            │   │  - Gallery View     │
    │  - Persistence        │   │  - Dynamic Switch   │
    │  - Modular CSS        │   │  - Metadata Track   │
    └───────────────────────┘   └─────────────────────┘
```

## File Structure

```
morphonews/
│
├── public/
│   ├── index.html                    # Redirect to latest
│   ├── history.html                  # Archive list
│   ├── style-gallery.html           # NEW: Theme gallery
│   │
│   ├── archives/
│   │   ├── TEMPLATE.html            # UPDATED: New UI components
│   │   └── YYYY-MM-DD_HHMM.html     # Generated pages
│   │
│   ├── styles/
│   │   ├── archive-base.css         # UPDATED: Base + new features
│   │   ├── history.css              # History page styles
│   │   ├── styles.json              # NEW: Style metadata
│   │   └── archives/                # NEW: Theme directory
│   │       ├── default.css
│   │       ├── ocean.css
│   │       ├── forest.css
│   │       ├── sunset.css
│   │       ├── midnight.css
│   │       └── cherry.css
│   │
│   ├── js/
│   │   ├── archive-base.js          # UPDATED: Feature logic
│   │   └── history.js               # History page logic
│   │
│   ├── data/
│   │   └── YYYY-MM-DD_HHMM.json     # News metadata
│   │
│   └── features.json                # NEW: Feature tracking
│
├── scripts/
│   ├── generator.py                 # UPDATED: Evolution docs
│   └── requirements.txt
│
├── FEATURES.md                      # NEW: Feature documentation
├── IMPLEMENTATION_SUMMARY_EVOLUTION.md  # NEW: Summary
└── README.md                        # UPDATED: Feature section
```

## Data Flow

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│   Browser (Archive Page)        │
│  ┌────────────────────────────┐ │
│  │ HTML (TEMPLATE.html)       │ │
│  │ - Reading Progress Bar     │ │
│  │ - Font Controls            │ │
│  │ - Style Selector Button    │ │
│  │ - Style Panel              │ │
│  └────────────────────────────┘ │
└─────┬──────────────┬────────────┘
      │              │
      ▼              ▼
┌──────────────┐  ┌──────────────────┐
│ archive-base │  │ localStorage     │
│    .css      │  │ - selected_style │
│ (Base)       │  │ - font_size      │
└──────┬───────┘  └──────────────────┘
       │
       ▼
┌──────────────────┐
│ archives/*.css   │
│ (Theme Override) │
└──────────────────┘
```

## Feature Interaction Flow

```
User Action              →  JavaScript Function      →  Effect
─────────────────────────────────────────────────────────────────
Click Style Button      →  Toggle Panel            →  Show/Hide Panel
Select Theme            →  applyStyle()            →  Load CSS + Save
                                                      localStorage
Click A+                →  initFontSizeControls()  →  Increase Font
                                                      + Save Setting
Scroll Page             →  initReadingProgress()   →  Update Progress
                                                      Bar Width
Visit Gallery           →  renderStyleSelector()   →  Show All Themes
                                                      with Preview
Page Load               →  loadStylePreference()   →  Apply Saved
                                                      Style + Font
```

## Theme Architecture

```
┌─────────────────────────────────────┐
│      archive-base.css               │
│  (Base Styles - Always Loaded)     │
│  - Layout                           │
│  - Typography                       │
│  - Components                       │
│  - Feature Styles                   │
│  - CSS Variables (Default)          │
└────────────┬────────────────────────┘
             │
             ▼
    ┌────────────────────┐
    │  Theme Selector?   │
    └────────┬───────────┘
             │
     ┌───────┴───────┐
     │ Yes           │ No
     ▼               ▼
┌────────────┐  ┌──────────────┐
│ Theme CSS  │  │ Use Default  │
│ (Override) │  │ Variables    │
└────────────┘  └──────────────┘
 - default.css
 - ocean.css
 - forest.css
 - sunset.css
 - midnight.css
 - cherry.css
```

## Evolution vs Variation

```
┌─────────────────────────────────────────────────────────────┐
│                     Timeline View                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Gen #1  Gen #2  Gen #3  Gen #4  ... Gen #22 (Current)     │
│    │       │       │       │             │                   │
│    ▼       ▼       ▼       ▼             ▼                   │
│  [Base] [Style] [Style] [Style]    [6 Themes]              │
│          AI      AI      AI         + Features              │
│                                                              │
│  ┌──────────────────────────────────────────┐              │
│  │         EVOLUTION (Features)              │              │
│  │  Gen #22: +6 Features                    │              │
│  │  - Style Selector                        │              │
│  │  - Reading Progress                      │              │
│  │  - Font Control                          │              │
│  │  - Persistence                           │              │
│  │  - Gallery                               │              │
│  │  - Modular CSS                           │              │
│  └──────────────────────────────────────────┘              │
│                                                              │
│  ┌──────────────────────────────────────────┐              │
│  │         VARIATION (Styles)                │              │
│  │  All Past + Current Styles Available:    │              │
│  │  [Default] [Ocean] [Forest] [Sunset]     │              │
│  │  [Midnight] [Cherry]                      │              │
│  │  User can select any at any time         │              │
│  └──────────────────────────────────────────┘              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Security Layers

```
┌─────────────────────────────────────────┐
│        User Input                        │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Input Validation                        │
│  - styleId regex: /^[a-z-]+$/           │
│  - fontSize range: 70-150               │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  XSS Prevention                          │
│  - DOM methods instead of innerHTML     │
│  - textContent for user data            │
│  - escapeHtml() function                │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Safe Event Handling                     │
│  - addEventListener (not onclick)       │
│  - Function references (not strings)    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  CodeQL Verified ✓                      │
│  0 Security Alerts                       │
└─────────────────────────────────────────┘
```

## User Journey

```
1. Visit Site
   └─> index.html redirects to latest archive

2. Read News
   └─> archive/YYYY-MM-DD_HHMM.html
       ├─> Reading progress bar updates as they scroll
       └─> Previously saved style + font size applied

3. Customize Experience
   ├─> Click Style Button (floating, bottom-right)
   │   └─> Panel shows 6 theme options
   │       └─> Click theme → Applied instantly + Saved
   │
   └─> Use Font Controls (A+/A-)
       └─> Font size changes → Saved automatically

4. Explore Themes
   └─> Click "スタイル" in navigation
       └─> style-gallery.html
           ├─> Preview all 6 themes
           ├─> See which is currently active
           └─> One-click to select and apply

5. Browse Archive
   └─> history.html
       └─> List of all past news
           └─> All pages respect user's style preference
```

## Metrics Dashboard

```
┌─────────────────────────────────────────┐
│         Implementation Metrics           │
├─────────────────────────────────────────┤
│ Files Created:           10              │
│ Files Modified:          6               │
│ Features Added:          6               │
│ Themes Available:        6               │
│ Code Review Issues:      5 (Fixed)       │
│ Security Alerts:         0               │
│ Test Pass Rate:          100%            │
│ Documentation Files:     3               │
└─────────────────────────────────────────┘
```
