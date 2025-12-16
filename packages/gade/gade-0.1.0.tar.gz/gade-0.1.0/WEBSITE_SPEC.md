# GADE Website Spec for Framer

Use this document to build the GADE landing page in Framer.

---

## Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Background | `#09090B` | Page background |
| Surface | `#18181B` | Cards, sections |
| Border | `#27272A` | Card borders |
| Text Primary | `#FAFAFA` | Headings |
| Text Secondary | `#A1A1AA` | Body text |
| Text Muted | `#71717A` | Captions |
| Accent | `#10B981` | Buttons, highlights |
| Accent Hover | `#059669` | Button hover |

---

## Typography

- **Font**: Inter (Google Fonts)
- **Headings**: Semi-bold (600), -2% letter spacing
- **Body**: Regular (400), 16px, 1.6 line height
- **Mono** (terminal): JetBrains Mono

---

## Section 1: Navigation

```
[Logo: G] GADE          [Features] [How it works] [FAQ]          [GitHub Button]
```

- Fixed top, blur background
- Logo: 32x32 emerald square with "G"

---

## Section 2: Hero

**Badge**: `🟢 Now in public beta`

**Headline**:
```
Focus AI on code
that actually matters
```

**Subheadline**:
```
GADE measures difficulty across your codebase and allocates compute 
where it's needed. 80% of tokens on 20% of difficulty.
```

**Buttons**:
- Primary: `Get Early Access` → scrolls to waitlist
- Secondary: `How it works` → scrolls to section

**Right side**: Terminal mockup showing:
```
$ gade analyze ./project --top 5

  RANK   SCORE    TIER       FILE
  ─────────────────────────────────────────
  #1     0.847    debate     paymentProcessor.ts
  #2     0.723    deep       authMiddleware.ts
  #3     0.651    deep       dataSync.ts
  #4     0.489    standard   apiRoutes.ts
  #5     0.182    compress   utils.ts

  ✓ 80% tokens allocated to top 20% difficulty
```

---

## Section 3: Features

**Headline**: `Built for serious developers`
**Subheadline**: `Stop wasting compute on trivial code.`

**6 Feature Cards (2x3 grid)**:

1. 📊 **Difficulty Scoring**
   5 signals combined via EMA smoothing into a single 0-1 score.

2. 🎯 **Smart Allocation**
   Top 20% difficulty regions get 80% of your token budget.

3. ⚡ **Instant Analysis**
   Scan entire repositories in seconds.

4. 🔌 **Model Agnostic**
   Works with OpenAI, Anthropic, or local models.

5. 💻 **CLI First**
   Headless. Integrates into any workflow or CI/CD.

6. 📈 **Track Progress**
   Before/after difficulty deltas show real improvement.

---

## Section 4: How It Works

**Headline**: `How it works`
**Subheadline**: `Three steps to smarter AI-assisted development.`

**3 Steps (vertical list with numbers)**:

1. **Analyze your codebase**
   Run GADE on any Git repository. It scans all files and extracts functions.

2. **Compute difficulty scores**
   Five signals are combined: edit churn, complexity, errors, uncertainty, gradient.

3. **Allocate AI compute**
   Hard code gets deep reasoning. Easy code gets summaries.

---

## Section 5: Signals

**Headline**: `Five signals, one score`

**5 Cards in a row**:

| Edit Churn | Complexity | Error Density | Uncertainty | Gradient |
|------------|------------|---------------|-------------|----------|
| Git volatility | AST depth | TODOs & smells | LLM confidence | Reasoning instability |

---

## Section 6: FAQ

**Headline**: `Frequently asked questions`

| Question | Answer |
|----------|--------|
| What is GADE? | CLI tool that measures code difficulty and allocates AI compute proportionally. |
| Which languages? | Python, JavaScript, TypeScript, Go, Rust. |
| Is it open source? | Yes, MIT license on GitHub. |
| What LLMs work? | OpenAI, Anthropic, local models via LiteLLM. |
| How is score calculated? | 5 signals normalized and combined via EMA smoothing. |

---

## Section 7: CTA / Waitlist

**Headline**: `Get early access`
**Subheadline**: `Join the waitlist for GADE Pro and VS Code extension.`

**Form**:
- Email input + "Join Waitlist" button

---

## Section 8: Footer

```
[G] GADE © 2024              GitHub | Docs | Contact
```

---

## Framer Tips

1. **Use Components**: Create reusable card, button, and section components
2. **Link anchors**: Use `#features`, `#how`, `#faq`, `#waitlist`
3. **Animations**: Fade-in on scroll for sections (subtle, 0.4s)
4. **Forms**: Use Framer's built-in form or connect to Mailchimp/Supabase
5. **Terminal**: Use a static image or Framer's code embed with styled div

---

## Recommended Framer Templates

Search for these on Framer:
- "SaaS landing page dark"
- "Developer tool landing"
- "Minimal dark theme"

Or start from the Cryptix template you liked and customize with GADE content above.
