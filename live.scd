(
var seq = Pseq([1,2,3],inf).asStream;
r = Routine { arg inval;
	loop {
		// ~synth.set(\mod_base1, [1,2,0.5].choose);
		seq.next.postln;
		1.wait;
	}
}.play;
)

r.stop