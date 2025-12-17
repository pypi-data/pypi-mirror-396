# cl-wrangler

A CLI tool to easily switch between multiple Cloudflare/Wrangler accounts.

## Installation

```bash
pip install cl-wrangler
```

## Usage

```bash
# Save your current wrangler account
cl add

# List saved accounts
cl list

# Switch accounts (interactive)
cl switch

# Switch with fuzzy matching
cl switch work
cl switch hamid

# Remove an account
cl remove
```

## Features

- **Save accounts** - Store multiple Wrangler authentication configs
- **Quick switch** - Switch between accounts with fuzzy matching
- **Interactive mode** - Select accounts from a list
- **Auto-save** - Automatically saves token updates before switching

## More Info

For full documentation, visit [docs.groo.dev/cl-wrangler](https://docs.groo.dev/cl-wrangler).

## License

MIT
