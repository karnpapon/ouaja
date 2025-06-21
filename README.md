# ouaja

ouaja (วาจา, /waː˧.t͡ɕaː˧/ pronouced as 'waa-jaa', a Thai word for "speech" ), a tool for live (ghosting) performance.

# prerequisites
- `OpenAI` API token
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/), a python package
- [`SuperCollider`](https://supercollider.github.io/), audio engine
  - [`FluCoMa`](https://github.com/flucoma/flucoma-sc), additional algorithms 
  - [`ddwMixerChannel`](https://github.com/jamshark70/ddwMixerChannel), mixer channel

# usage

- `cp .env.example .env`, to create `.env` from example
- put your token in `.env`
- `uv sync`
- `source .venv/bin/activate`
- `python main.py` default port is `57120`, if you wanted to configure the ip/port use eg. `python main.py --ip 127.0.0.1 --port 8080`
- execute `sound-engine.scd`

## Commands

- `;;set_timeout_factor`
- `;;set_move_mode`
- `;;set_trigger_mode`
- `;;set_haunted_mode`
- `;;set_haunted_mode_lower_bound`
- `;;set_haunted_mode_upper_bound`
- `;;move_to`
- `;;set_activate_nodes`
- `;;set_max_speed`
- `;;stop`
- `;;bye`
