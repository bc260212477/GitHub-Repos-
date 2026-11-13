# GitHub-Repos-

For AI research and agent architecture discovery.

## Filtered catalog

The full list of catalog repositories with fewer than 2,000 stars is available here:

- [repositories-under-2000-stars.csv](repositories-under-2000-stars.csv) — 136 unique repositories

The file is derived from `all-categories-a-to-z.csv`, de-duplicated by repository URL,
and sorted from highest to lowest star count. The catalog is a research index; review
license, maintenance, security, and quality before using any repository.

- [repositories-over-2000-stars.csv](repositories-over-2000-stars.csv) — 1,690 unique repositories

### Hermes and agent skills

- [hermes-skills-over-2000-stars.csv](hermes-skills-over-2000-stars.csv) — 476 matching repositories
- [hermes-skills-gallery.md](hermes-skills-gallery.md) — screenshot-matched Hermes skill index
- [Hermes Projects dashboard preview](https://github.com/bc260212477/hermes-agent/blob/feature/projects-dashboard/assets/projects-dashboard-preview.png)

This focused list uses the `>2,000 stars` catalog and matches `hermes`, `skill`,
or `agent` in repository metadata. It is a discovery list, not an endorsement.

## Preview

![Agent Foundry dashboard](assets/agent-foundry-dashboard.png)

## Agent Architecture Builder

Generate a proposed stack from the catalog without API keys or external services:

```bash
python agent_architect.py "autonomous research assistant"
python agent_architect.py "coding agency" --per-capability 3
```

Start the backend API:

```bash
python agent_api.py
open http://127.0.0.1:8787
curl http://127.0.0.1:8787/health
curl 'http://127.0.0.1:8787/api/repositories?q=agent%20memory&limit=5'
curl -X POST http://127.0.0.1:8787/api/architecture \
  -H 'Content-Type: application/json' \
  -d '{"product":"autonomous research assistant","per_capability":2}'
```

The tool searches the catalog across orchestration, memory, research, coding,
automation, business apps, and safety. It de-duplicates repositories and includes
license metadata where available. Recommendations are starting points; review
licenses, maintenance, dependencies, and security before using code in a product.

Run the focused tests with:

```bash
python -m unittest test_agent_architect.py
```
