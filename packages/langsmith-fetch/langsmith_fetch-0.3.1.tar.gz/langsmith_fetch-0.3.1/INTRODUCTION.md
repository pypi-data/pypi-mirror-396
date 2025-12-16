# Introducing LangSmith Fetch

LangSmith Fetch is a command-line tool designed to make retrieving and working with LangSmith data effortless. Whether you're debugging an agent, analyzing conversation flows, or building datasets from production traces, this CLI provides fast, flexible access to your LangSmith traces and threads. It bridges the gap between the LangSmith UI and your local workflow, letting you fetch data by ID when you know exactly what you want, or by time when you need to grab whatever just happened. With support for multiple output formats (human-readable panels, pretty JSON, or compact raw JSON), the tool adapts to your use case—whether you're inspecting data in the terminal, piping to `jq`, or feeding results to an LLM for analysis.

The tool shines in two key workflows. First, the "I just ran something" workflow: you execute your agent or chain, then immediately run `langsmith-fetch traces` to grab the most recent trace without hunting for IDs in the UI. Add temporal filters like `--last-n-minutes 30` to narrow your search, or use `--project-uuid` to target a specific project. Second, the bulk export workflow: when you need datasets for evaluation or analysis, commands like `langsmith-fetch threads ./my-data --limit 50` fetch multiple threads and save each as a separate JSON file, perfect for batch processing or building test sets. Here's what the quick-fetch workflow looks like:

```bash
# Just ran your agent? Grab the trace immediately
langsmith-fetch traces --format json

# Or grab the last 5 traces from a specific project
langsmith-fetch traces --project-uuid <your-uuid> --limit 5

# Need threads for evaluation? Bulk export to files
langsmith-fetch threads ./evaluation-data --limit 25 --last-n-minutes 60
```

Configuration is minimal but powerful. Store your project UUID and API key once with `langsmith-fetch config set project-uuid <uuid>`, then forget about them. The tool supports both individual fetches (when you have a specific trace or thread ID from the UI) and time-based searches (when you want "the most recent thing"). Output formats adapt to your needs: `--format pretty` for terminal viewing with Rich panels, `--format json` for readable structured data, or `--format raw` for piping to other tools. Whether you're a developer debugging traces, a researcher building datasets, or an LLM agent programmatically fetching conversation history, LangSmith Fetch provides the right interface for your workflow.
