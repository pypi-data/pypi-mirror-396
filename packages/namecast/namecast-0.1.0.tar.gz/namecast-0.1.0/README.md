# Namecast

AI-powered brand name oracle. Generate, filter, and evaluate brand names with domain checks, social handles, similar company analysis, and dynamic persona perception forecasting.

## Features

- **Name Generation**: AI generates brand name candidates based on your project description
- **Domain Availability**: Checks .com, .io, .co, .ai, .app domains via WHOIS
- **Social Handle Checks**: Twitter/X and GitHub availability
- **Similar Company Search**: Finds existing companies with similar names
- **Pronunciation Analysis**: Syllable count, spelling difficulty, phonetic clarity
- **International Safety**: Checks for problematic meanings in 7 major languages
- **Dynamic Persona Perception**: AI role-plays as your target audience to forecast brand perception

## Installation

```bash
pip install namecast
```

Or from source:

```bash
git clone https://github.com/MaxGhenis/namecast
cd namecast
pip install -e ".[dev]"
```

Requires an Anthropic API key:

```bash
export ANTHROPIC_API_KEY=your-key-here
```

## Usage

### CLI

**Find names for a new project:**

```bash
namecast find "A SaaS tool for tracking carbon emissions"
```

**Include your own ideas:**

```bash
namecast find "Dog walking app" --ideas Waggle --ideas PupPath
```

**Evaluate a specific name:**

```bash
namecast eval Acme
```

**Evaluate with mission context:**

```bash
namecast eval Cloudify --mission "Cloud infrastructure automation for startups"
```

**Compare multiple names:**

```bash
namecast eval --compare Acme Globex Initech
```

### Claude Code Plugin

If you use [Claude Code](https://claude.ai/claude-code), Namecast is available as a plugin:

**Find names:**

```
/namecast:find A marketplace connecting local farmers with restaurants --ideas FarmLink,HarvestHub
```

**Evaluate a name:**

```
/namecast:evaluate Cloudify --mission Cloud infrastructure automation
```

The Claude Code plugin runs natively (no API calls) and is free with Claude Max.

## Methodology

### Scoring System

Names are scored on a 100-point scale:

| Category | Points | Description |
|----------|--------|-------------|
| Domain Availability | 40 | .com = 40pts, .io only = 25pts |
| Persona Perception | 40 | Average of memorability + professionalism ratings |
| Linguistic Quality | 20 | Pronunciation ease, international safety, uniqueness |

### Dynamic Persona Generation

Unlike static persona sets, Namecast generates **personas tailored to your specific project**. When you provide a company description, the AI identifies 5 relevant personas who would interact with your brand:

- **Primary customers/users** - Who will use the product?
- **Decision makers** - Who approves purchases?
- **Investors** - Who might fund the company?
- **Industry experts** - Who analyzes this space?
- **End consumers** - Who benefits ultimately?

For example, a B2B SaaS might get personas like:
- CFO (50s, enterprise, values ROI)
- Startup founder (30s, fast-mover, values innovation)
- Developer (25, technical, values ease of use)
- VC partner (40s, evaluates hundreds of startups)
- Industry analyst (45, writes about the space)

While a consumer app might get:
- College student (20, social media native)
- Working parent (35, values convenience)
- Small business owner (40, budget-conscious)

Each persona then evaluates your name on:
- **Memorability** (1-10): Will they remember it?
- **Professionalism** (1-10): Does it seem credible?
- **Trust**: Would they use a company with this name?
- **Industry guess**: What sector do they assume?
- **Gut reaction**: One-sentence impression

### Domain Checking

Checks WHOIS data for:
- `.com` (weighted highest)
- `.io` (popular for tech)
- `.co`
- `.ai`
- `.app`

Names where both .com and .io are taken are filtered out in the `find` workflow.

### Social Handle Verification

Checks availability on:
- Twitter/X
- GitHub

### Similar Company Analysis

Web searches for:
- Exact name matches
- Companies in similar industries
- Potential trademark conflicts

**Note:** This is informational only. Always consult a trademark attorney before finalizing your brand name.

### International Safety

Checks if the name has problematic meanings in:
- Spanish
- French
- German
- Mandarin
- Japanese
- Portuguese
- Arabic

### Pronunciation Analysis

Evaluates:
- **Syllable count**: Shorter is generally better
- **Spelling difficulty**: Easy/Medium/Hard
- **Phonetic clarity**: Would someone spell it correctly after hearing it?

## Architecture

```
namecast/
├── namecast/
│   ├── cli.py          # Click CLI commands
│   ├── evaluator.py    # BrandEvaluator and NamecastWorkflow
│   ├── perception.py   # Dynamic persona generation and analysis
│   ├── api.py          # FastAPI server (optional)
│   └── tests/          # pytest test suite
├── .claude-plugin/
│   ├── plugin.json     # Claude Code plugin manifest
│   ├── marketplace.json
│   └── commands/
│       ├── find.md     # /find command (native execution)
│       └── evaluate.md # /evaluate command (native execution)
└── src/                # React frontend (optional)
```

### CLI vs Plugin Alignment

Both the CLI and Claude Code plugin use the same methodology:

| Feature | CLI | Claude Code Plugin |
|---------|-----|-------------------|
| Dynamic personas | `perception.py` | Native Claude roleplay |
| Domain checks | `python-whois` | WebFetch to who.is |
| Social checks | `httpx` | WebFetch |
| Similar companies | `httpx` | WebSearch |
| API cost | Anthropic API credits | Free (Claude Max) |

The key difference: CLI calls the Anthropic API (costs credits), while the Claude Code plugin uses Claude's native capabilities (free with Claude Max subscription).

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check namecast/
```

## License

MIT

## Disclaimer

Namecast provides general information only and does not constitute legal advice. Domain availability and trademark searches are informational. Always consult a trademark attorney before finalizing your brand name.
