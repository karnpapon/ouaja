(
b = Buffer.alloc(s,1024);
c = Buffer.read(s, Platform.resourceDir +/+ "sounds/Number1-1chan.wav");
)

(
SynthDef(\scratchPlayer, {
	|buf, bufnum=0, amp = 0.5, lagTime = 0.1, xpos = 0.5, speed = 0, freeze = 0|

	// var xpos = MouseX.kr(0, 1);
	// var speed = MouseY.kr(-2, 2);
	var bufFrames = BufFrames.kr(buf);
	var pos = xpos * bufFrames;
	var smoothedPos = Lag.kr(pos, lagTime);
	var phasor = Phasor.ar(
		rate: speed,
		start: 0,
		end: bufFrames - 1,
		resetPos: smoothedPos
	);
	var sig = BufRd.ar(1, buf, phasor, loop: 1);
	var chain = FFT(bufnum, sig);
	chain = PV_Freeze(chain, freeze > 0.5 );
	Out.ar(0, IFFT(chain).dup * amp);
}).add;
)

(
var synth;
synth = Synth(\scratchPlayer, [\buf, c, \bufnum, b.bufnum]);
synth.set(\freeze, 0.6)


OSCdef(\touchX, { |msg|
	var xpos = msg[1];
	var speed = msg[2];
	synth.set(\xpos, xpos, \speed, speed);
}, '/synth_shot_node_line');

OSCdef(\touchY, { |msg|
	var freeze = msg[1];
	synth.set(\freeze, freeze);
}, '/synth_shot_nodes');
)



