# live ghosting

live ghosting performance

run `python3 main.py --ip 127.0.0.1 --port 57120`

# commands

you can type these commands while the program is running

- `::SET_FPS <frame>`, set framerate (will be clampped to a range between 10-60fps)
- `::BYE`, quit program

# structures

- `/dataset`, a pre-trained neural-network data for using in `synth.scd`
- `synth.scd`, a synth engine ([`FluCoMa`](https://github.com/flucoma/flucoma-sc) lib is required)

# prerequisites

- Korg - NanoKontrol1
