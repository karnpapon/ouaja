# ouaja

ouaja (วาจา, /waː˧.t͡ɕaː˧/ pronouced as 'waa-jaa', a Thai word for "speech" ).

<img src="img/ss3.png">


NOTE: This tool is intended for live performance, So it's an audio-engine agnostic by design (I'm using `SuperCollider`). You'll need to supply your own preferred audio engine backend.

## prerequisites
- `OpenAI` API token
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/), a python package
- OPTIONAL [`SuperCollider`](https://supercollider.github.io/), audio engine
  - [`FluCoMa`](https://github.com/flucoma/flucoma-sc), additional algorithms 
  - [`ddwMixerChannel`](https://github.com/jamshark70/ddwMixerChannel), mixer channel

## usage

- `cp .env.example .env`, to create `.env` from example
- put your token in `.env`
- put details or the `CONTEXT_CHARACTER` in `.env` (an example prompt is provided in `.env.example`)
- `uv sync`
- `source .venv/bin/activate`
- `python main.py` default port is `57120`, if you wanted to configure the ip/port use eg. `python main.py --ip 127.0.0.1 --port 8080`
- execute `sound-engine.scd` or your preferred audio engine.


## OSC Msg
to communicate with audio engine i'm using OSC, here's my currently used OSC msg list 
- `/synth_shot_opening`
- `/synth_shot`
- `/synth_coord`
- `/synth_shot_nodes`

## Shortcut
- `Ctrl + f`, toggle fullscreen 

## Commands

- `;;set_fps`
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


# Credits
- `Nicer Nightie` font,  https://unfilledflag.itch.io/nicer-nightie
- `hexany`, UI panel https://hexany-ives.itch.io/hexanys-1-bit-ui-panels