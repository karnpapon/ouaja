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
	// var chain = FFT(bufnum, sig);
	// chain = PV_Freeze(chain, freeze > 0.5 );
	var chain = MiClouds.ar(sig, 0, position, 0.1, 1, 0.5, drywet: 1, freeze: freeze, mode: 2);
	Out.ar(0, chain.dup * amp);
}).add;
)

(
var synth;
synth = Synth(\scratchPlayer, [\buf, c, \bufnum, b.bufnum]);

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



OSCdef(\touchX).free

(
b = BufFiles.new(s, "/Users/karnpaponboonput/Desktop/samples/Stockhausenisms/sharp-attack",actionWhenDone: {
	defer{ b.gui }
})
)

(
SynthDef(\polybuf_sampler,{|out=0, amp=0.5, mode, pit=0, position=0.5, tex=0.5, buffer, bufnum, rate=1, freeze=0|
	var in = XPlayBuf.ar(numChannels:2, bufnum:buffer, rate:rate * BufRateScale.kr(buffer), trigger:1.0, startPos:0.0, loop:0.0);
	var chain = MiClouds.ar(in, pit, position, 0.5, 1, tex, drywet: 0.5, freeze: freeze, mode: mode);
	Out.ar(out, chain.dup * amp);
}).add
)

f = Buffer.alloc(s,1024);
// f.bufnum;

NetAddr("127.0.0.1", 57120).sendMsg("/synth_shot_nodes", 13, 0);

(
~polybufLastSynth = nil;

~playChoke = { |buf, freeze = 0.0, mode, amp = 0.5|
	if (~polybufLastSynth.notNil) {
		~polybufLastSynth.free;
	};

	// Play new one and store reference
	~polybufLastSynth = Synth(\polybuf_sampler, [
		\buffer, buf.bufnum,
		\bufnum, f.bufnum,
		\freeze, freeze,
		// \position, ~position,
		// \tex, ~tex,
		\mode, mode,
		// \pit, ~pit,
		\amp, amp
	]);
};
)

(
OSCdef(\playSample, { |msg, time, addr, recvPort|
	var index = msg[1];
	var freeze = msg[2];
	var mode = msg[3];

	if (index >= 0 and: { index < b.size }) {
		var buf = b[index];
		~playChoke.(buf, freeze, mode);
	} {
		"Invalid buffer index: %".format(index).warn;
	}
}, '/synth_shot_nodes');

/*OSCdef(\playSampleWithMod, { |msg, time, addr, recvPort|
	var position = msg[1];
	var tex = msg[2];
	var pit = msg[3];
	~position = position;
	~tex = tex;
	~pit = pit;
}, '/synth_shot_node_line');*/
)