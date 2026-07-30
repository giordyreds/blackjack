# blackjack

A single-player, terminal-driven blackjack game: one human player against a computer dealer.

See [`CONTEXT.md`](./CONTEXT.md) for the domain glossary and [`docs/adr/`](./docs/adr/) for
architectural decisions.

## Development

```sh
pip install -e ".[dev]" pytest
pytest
```

## Running

```sh
blackjack
```

Feature work is tracked as GitHub issues labeled `ready-for-agent` and solved via
[`parallel-issue-solver`](../parallel-issue-solver) (see `.parallel-solver.yml`).
