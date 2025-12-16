# pi

Python Intelligence -- a better ✨ tool chain for humans and agents.


## Configuration

1. Add `PI_LLM_API_KEY=` env var with your OpenRouter, OpenAI, or Anthropic
   API key.

2. Add `PI_LLM_MODEL=` with the name of the model you want to use.


E.g.:

```shell
export PI_LLM_API_KEY="vck_jlasdfkjajkfhieu..."
export PI_LLM_MODEL="anthropic/claude-sonnet-4.5"
```


## Development

1. Clone the repo `git clone --recursive git@github.com:geldata/pi.git`

2. `cd pi`

3. `uv sync`

4. `uv run pre-commit install`

5. `uv run pi`

6. Run `realpath $(uv run which pi)` and use the path it returned to create an
   alias in your shell: `alias pi="<relpath output>"`. Now you are able to run
   `pi` from anywhere in your system.


## Running tests

1. `uv run pytest` will do the job.
