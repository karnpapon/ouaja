(

Window.closeAll;
MIDIClient.init;
// s.options.outDevice = "Scarlett 2i4 USB";
// s.options.outDevice = "Audient iD14";
// s.options.outDevice ="MacBook Pro Speakers";
s.options.outDevice ="External Headphones";
s.options.numInputBusChannels = 0;

s.waitForBoot{
	var synth, multislider, win, xyslider;
	var xydata = FluidDataSet(s);
	var paramsdata = FluidDataSet(s);
	var xybuf = Buffer.alloc(s,2);
	var paramsbuf = Buffer.alloc(s,10);
	var counter = 0;
	var window_w = 960;
	var mlp_cached_path = "";
	var basename = 'nano_';
	var numChans = 2;
	var lagtime = 0.1;

	// multi-layer perceptron
	var mlp = FluidMLPRegressor(s,
		[7],
		activation:FluidMLPRegressor.sigmoid,
		outputActivation:FluidMLPRegressor.sigmoid,
		maxIter: 1000,
		learnRate:0.1,
		batchSize:1,
		validation:0
	);

	win = Window("GhostSynth", Rect(0, 0, 960-220, 212)).front;
	multislider = MultiSliderView(win,Rect(10, 10, 400-100, (720*0.45)-130))
	.elasticMode_(1)
	.isFilled_(1)
	.action_({
		arg ms;
		paramsbuf.setn(0,ms.value);
	})
	.value_(0.5.dup(10));

	xyslider = Slider2D(win,Rect(420-100,10,(1280*0.3) - 100,(720*0.45)-130 ))
	.action_{
		arg view;
		// view.x.postln; //top-left: 0, bottom-right: 1
		// view.y.postln; //top-left: 1, bottom-right: 0
		xybuf.setn(0,[view.x,view.y]);
	};

	Button(win,Rect(window_w - 340,10,100,20))
	.states_([["Add Points"]])
	.action_{
		var id = "point-%".format(counter);
		xydata.addPoint(id,xybuf);
		paramsdata.addPoint(id,paramsbuf);
		counter = counter + 1;

		xydata.print;
		paramsdata.print;
	};

	Button(win,Rect(window_w - 340,35,100,20))
	.states_([["Save Data"]])
	.action_{
		FileDialog({
			arg folder;
			xydata.write(folder+/+"xydata.json");
			paramsdata.write(folder+/+"paramsdata.json");
		},{},2,0,true);
	};

	Button(win,Rect(window_w - 340,60,100,20))
	.states_([["Load Data"]])
	.action_{
		FileDialog({
			arg folder;
			xydata.read(folder+/+"xydata.json");
			paramsdata.read(folder+/+"paramsdata.json");
		},fileMode:2,acceptMode:0,stripResult:true);
	};

	Button(win,Rect(window_w - 340,85,100,20))
	.states_([["Train"]])
	.action_{
		mlp.fit(xydata,paramsdata,{
			arg loss;
			loss.postln;
		});
	};

	Button(win,Rect(window_w - 340,110,100,20))
	.states_([["Save MLP"]])
	.action_{
		Dialog.savePanel({
			arg path;
			if(PathName(path).extension != "json"){
				path = "%.json".format(path);
			};
			mlp.write(path);
		});
	};

	Button(win,Rect(window_w - 340,135,100,20))
	.states_([["Load MLP"]])
	.action_{
		Dialog.openPanel({
			arg path;
			mlp.read(path);
			mlp_cached_path = path;
		});
	};

	Button(win,Rect(window_w - 340,160,100,20))
	.states_([["Not Predicting"],["Predicting"]])
	.action_{
		arg but;
		but.value.postln;
		~synth.set(\predicting,but.value);
	};

	Button(win,Rect(window_w - 340,185,100,20))
	.states_([["Play"], ["Pause"]])
	.action_{
		arg but;
		if (but.value == 1, {
			~synth = Synth(basename ++ 'main_synth');
			if ( mlp_cached_path != "", { mlp.read(mlp_cached_path); },{});
		}, { ~synth.free; });
	};

	s.sync;

	(
		SynthDef.new(basename ++ 'main_synth', {
			arg predicting = 0, mod_base1=1, mod_base2=1, mod_base3=1;
			var osc1, osc2, feed1, feed2, base1=69, base2=69, base3 = 130, loud1, loud2;
			var val, xy, trig;

			xy = FluidBufToKr.kr(xybuf);
			trig = Mix(Changed.kr(xy));
			mlp.kr(trig * predicting,xybuf,paramsbuf);
			val = FluidBufToKr.kr(paramsbuf);
			SendReply.kr(Mix(Changed.kr(val)),"/paramsChanged",val);

			#feed2, feed1 = LocalIn.ar(2);

			loud1 = FluidLoudness.kr(feed1,[\loudness],1,0,hopSize:64);
			loud2 = FluidLoudness.kr(feed2,[\loudness],1,0,hopSize:64);

			osc1 = SinOsc.ar((((feed1 * val[0]) +  val[1]) * base1 * mod_base1).midicps,mul:(val[2] * 50).dbamp).atan;
			osc1 = MoogFF.ar(osc1,(( base3 * mod_base3 )-(val[3]*(loud2.clip(-120,0)+120))).lag(128/44100).midicps,val[4]*3.5);

			osc2 = SinOsc.ar((((feed2 * val[5]) +  val[6]) * base2 * mod_base2).midicps,mul: (val[7] * 50).dbamp).atan;
			osc2 = MoogFF.ar(osc2,(base3-(val[8]*(loud1.clip(-120,0)+120))).lag(128/44100).midicps,val[9]*3.5);

			Out.ar(0,LeakDC.ar([osc1,osc2],mul:0.1));
			LocalOut.ar([osc1,osc2]);
		}).add;

		SynthDef(basename ++ 'amp', {|envatt = 0.01, envrel = 0.01, bus, outbus|
			var sig = In.ar(bus, numChans).sum;
			sig = Amplitude.kr(sig, envatt, envrel);
			Out.kr(outbus, sig);
		}, lagtime.dup(2)).add;


		SynthDef(basename ++ 'low_amp', {|envatt = 0.01, envrel = 0.01, bus, outbus|
			var sig = In.ar(bus, numChans).sum;
			sig = LPF.ar(sig, 250);
			sig = Amplitude.kr(sig, envatt, envrel);
			Out.kr(outbus, sig);
		}, lagtime.dup(2)).add;

		SynthDef(basename ++ 'high_amp', {|envatt = 0.01, envrel = 0.01, bus, outbus|
			var sig = In.ar(bus, numChans).sum;
			sig = HPF.ar(sig, 1500);
			sig = Amplitude.kr(sig, envatt, envrel);
			Out.kr(outbus, sig);
		}, lagtime.dup(2)).add;

		SynthDef(basename ++ 'lpf' , {|cutoff = 1, bus|
			var sig = LPF.ar(In.ar(bus, numChans), cutoff.linexp(0.0, 1.0, 40, 20000));
			ReplaceOut.ar(bus, sig)
		}, lagtime).add;

		SynthDef(basename ++ 'hpf' , {|cutoff = 1, bus|
			var sig = HPF.ar(In.ar(bus, numChans), cutoff.linexp(0.0, 1.0, 20000, 40));
			ReplaceOut.ar(bus, sig)
		}, lagtime).add;

		SynthDef(basename ++ 'comp' , {|slopeBelow = 1, bus|
			var sig = In.ar(bus, numChans);
			sig =  Compander.ar(sig, sig,
				thresh: 0.9,
				slopeBelow: slopeBelow,
				slopeAbove: 0.5, // Ratio, 1/3 == 3: 1
				clampTime:  0.01,
				relaxTime:  0.1
			);
			ReplaceOut.ar(bus, sig)
		}, lagtime).add;

		SynthDef(basename ++ 'eq' , {|loBoost = 0, hiBoost = 0, q = 0.3, hiFreq = 3000,  loFreq = 250, bus|
			var sig = In.ar(bus, numChans);
			sig = MidEQ.ar(sig, loFreq, q.linlin(0.0, 1.0, 0.1, 1.0), loBoost.linlin(0.0, 1.0, - 12.0, 12.0));
			sig = MidEQ.ar(sig, hiFreq, q.linlin(0.0, 1.0, 0.1, 1.0), hiBoost.linlin(0.0, 1.0, - 12.0, 12.0));
			ReplaceOut.ar(bus, sig)
		}, lagtime.dup(5)).add;

		SynthDef(basename ++ 'shape', {
			|out, shape = 0, amp = 1.0,  amp_compensation_amount = 0.99, lo = 1, hi = 0, offset = 0, lo_thresh = 0, hi_thresh = 0|
			var abs, diff;
			var signal = In.ar(out, 2);
			shape = min(shape, 1.0 - 4e-10).explin(0.001, 1, 0.0, 0.999999);
			amp_compensation_amount = amp_compensation_amount.linlin(0.0,1.0,0.0001,1.0);
			amp = 1.0 - (amp_compensation_amount * shape / (shape +amp_compensation_amount )) * amp;
			shape = (1.0 * shape) / (1.0 - shape);
			signal = (1 + shape) * signal / (1 + (shape * abs(signal)));
			offset = offset.linlin(0.0,1.0,1.0,5.0);
			hi = hi * offset; lo = lo * offset;
			abs = hi - lo;
			lo_thresh = lo_thresh.linlin(0.0,1.0,-1.0,1.0);
			lo = lo + (abs * lo_thresh);
			hi_thresh = hi_thresh.linlin(0.0,1.0,-1.0,1.0);
			hi = hi - (abs * hi_thresh);
			signal = Fold.ar(signal, lo, hi);
			diff = 1 - (lo - hi + (hi * lo));
			ReplaceOut.ar(out, Limiter.ar(LeakDC.ar(signal * (amp+diff))));
		}).add;

		SynthDef(basename ++ 'waveloss' , {|drywet = 0, loss = 1, bus|
			var in = In.ar(bus, numChans);
			var sig =  WaveLoss.ar(in, drop: loss.linlin(0.0, 1.0, 0, 10), outof: 10, mode: 2);
			XOut.ar(bus, drywet, sig)
		}, lagtime.dup(4)).add;

		SynthDef(basename ++ 'freqshift' , {|drywet = 0, freq = 0.5, bus|
			var in = In.ar(bus, numChans);
			var sig = FreqShift.ar(in, freq: freq.linexp(0.0, 1.0, 40, 4000), phase: 0);
			XOut.ar(bus, drywet, sig)
		}, lagtime.dup(2)).add;

		SynthDef(basename ++ 'verb', {|time = 1, size = 1, drywet = 0, modDepth = 0.1, bus|
			var sig = In.ar(bus, numChans);
			sig = JPverb.ar(sig, t60: time,
				damp: 1 - drywet,
				size: size.linlin(0.0, 1.0, 0.1, 5.0),
				earlyDiff: modDepth.linlin(0.0, 1.0, 1.0, 0.5),
				modDepth: modDepth.linlin(0.0, 1.0, 0.01, 1.0),
				modFreq: 2,
				lowcut: 500, highcut: 2000);
			XOut.ar(bus, drywet, sig);
		}, lagtime.dup(4)).add;

		SynthDef(basename ++ 'sub', {|freq = 0.5, subamp, drywet = 0, bus|
			var dry = In.ar(bus, numChans);
			var sig = SinOsc.ar(freq.linlin(0.0, 1.0, 40, 120),
				0,
				(subamp * 4).clip(0, 1)
			);
			sig = LPF.ar(sig, 150);
			sig = dry + sig;
			sig = LeakDC.ar(sig);
			XOut.ar(bus, drywet, sig);
		}, lagtime.dup(3)).add;


		SynthDef(basename ++ 'grain', {|grainsize = 0.25, grainrand = 0.8, drywet = 1, fbGain = 0, bus|
			var input = In.ar(bus, numChans);
			var bufLength = 1.0;
			var localBuf = LocalBuf(bufLength * SampleRate.ir, numChans).clear;

			var warp = Warp1.ar(
				numChans,
				localBuf,
				LFSaw.ar(1/bufLength).range(0, 1),
				Drand([ 2, - 2 ], inf),
				grainsize.linlin(0.0, 1.0, 2.0, 0.31),
				- 1,
				2,
				grainrand.linlin(0.0, 1.0, 0.2, 1.0),
				4
			);
			// record w/ feedback
			RecordBuf.ar(tanh(input + HPF.ar(tanh(warp * fbGain), 30)), localBuf);
			warp = warp.tanh;
			warp = HPF.ar(warp * 0.5, 150);
			warp = warp.sanitize;
			XOut.ar(bus, drywet, warp);
		}, lagtime.dup(4)).add;

		SynthDef(basename ++ 'pitchshift', {|drywet = 0, shift = 1, size = 0.2, bus|
			var dry = In.ar(bus, numChans);
			var sig;
			sig = PitchShift.ar(in: dry,
				windowSize: 0.25, //drywet.linlin(0.0, 1.0, 0.01, 0.4),
				pitchRatio: shift.linlin(0.0, 1.0, 0.01, 2.0),
				pitchDispersion: drywet.linlin(0.0, 1.0, 0.1, 1.0),
				timeDispersion: 0);
			XOut.ar(bus, drywet, sig);
		}, lagtime.dup(3)).add;


		SynthDef(basename ++ 'out', {|bus|
			var in = In.ar(bus, numChans);
			// apply limiter
			var sig = Compander.ar(in, in,
				thresh: 0.75,
				slopeBelow: 1,
				slopeAbove: 0.1,
				clampTime:  0.01,
				relaxTime:  0.01
			);
			ReplaceOut.ar(0, sig * 0.5)
		}).add;

		SynthDef("fm-gong", {
			arg freq = 300, dr = 5.0, amp = 1.0, pan = 0;
			var mod1sig, mod1f = freq * 1.16;
			var mod2sig, mod2f = freq * 3.14;
			var mod3sig, mod3f = freq * 1.005;
			var idx1a = 0.01 * mod1f;
			var idx1b = 0.30 * mod1f;
			var idx1scaler   = idx1b - idx1a;

			var idx2a = 0.01 * mod2f;
			var idx2b = 0.38 * mod2f;
			var idx2scaler   = idx2b - idx2a;

			var idx3a = 0.01 * mod3f;
			var idx3b = 0.50 * mod3f;
			var idx3scaler   = idx3b - idx3a;

			var mod1env, mod2env, mod3env, ampenv;
			var carsig;
			var lfo;

			lfo = SinOsc.ar(3, 0, XLine.kr(freq*0.005, freq*0.05, dr));

			mod1env = EnvGen.kr(
				Env(levels: [0,1,1,0], times: [0.75*dr, 0.24*dr, 0.01*dr]),
				doneAction: 2);

			mod2env = EnvGen.kr(
				Env(levels: [0,1,0], times: [0.02*dr, 0.98*dr]),
				doneAction: 2);

			mod3env = EnvGen.kr(
				Env(levels: [ 0, 0.3, 1, 0.5, 0], times: [0.15 * dr, 0.15 *dr, 0.45*dr, 0.25*dr]),
				doneAction: 2);

			// Exp curve...
			ampenv = EnvGen.kr(
				Env(levels: [ 0, 1, 0.001], times: [0.002, dr - 0.002], curve: \exp),
				doneAction: 2);

			mod1sig = SinOsc.ar(freq: mod1f);
			// envelope the signal, afterwards
			mod1sig = mod1sig * ((idx1a + idx1scaler) * mod1env);

			mod2sig = SinOsc.ar(freq: mod2f);
			// envelope the signal, afterwards
			mod2sig = mod2sig * ((idx2a + idx2scaler) * mod2env);

			mod3sig = SinOsc.ar(freq: mod3f);

			// envelope the signal, afterwards
			mod3sig = mod3sig * ((idx3a + idx3scaler) * mod3env);
			carsig = SinOsc.ar(freq + lfo + mod1sig + mod2sig + mod3sig);
			Out.ar(0, Pan2.ar(carsig * ampenv * amp, pan));
		}).send;

		SynthDef("saybufGrn", { |out, amp = 0.1, pan, pos,
			buf, endPause = 0.2, rate = 1,
			tilt = 0, speed = 1, grDur = 0.1|

			var dur2 = BufDur.ir(buf) - endPause / speed;
			var ratesig = Line.kr(rate - tilt, rate + tilt, dur2 * rate);
			var snd, posSig;

			var startpos = (ratesig.sign * pos * BufSampleRate.ir(buf))
			// add tiny offset so neg rate does not reach doneAction immediately
			+ (rate.sign * 0.01)
			// ... and wrap to legal range
			.wrap(0, BufFrames.ir(buf) - 1);

			posSig = Line.kr(startpos / dur2, 1 + pos - 0.1,  dur2, doneAction: 2);

			snd = GrainBuf.ar(1,
				Impulse.ar(2 / grDur),
				grDur,
				buf,
				ratesig,
				posSig,
				4
			);

			Out.ar(out,
				Pan2.ar(snd, pan, amp)
			)
		}).add;


	);

	b = BufFiles.new(s, "/Users/karnpaponboonput/Desktop/unorganised-music-master/sounds", actionWhenDone: {
		defer{ b.gui }
	});

	OSCdef(\paramsChanged,{
		arg msg;
		defer{
			multislider.value_(msg[3..]);
		};
	},"/paramsChanged");

	OSCdef(\coordChanged, {
		arg msg;
		// msg[0].postln;
		defer {
			xyslider.setXY(msg[1], msg[2]);
			xybuf.setn(0,[msg[1],msg[2]]);
		};
	}, '/synth_coord');

	/*OSCdef(\shot, {
	arg msg;
	var str = msg[2].asString;
	// var alphabet = if(str.matchRegexp("^[a-zA-Z]$")) { str } { "c" };
	var sbp = SayBuf.prepare((type: \say, text: str.toLower,wordrate: 1,voice: "Xander"));
	var sbb = sbp.buf;

	Synth("saybufGrn", [
	\buf: sbb,
	\rate: 0.95,
	\speed: 0.25,
	\amp: 0.67,
	\grDur: 0.04,
	]);
	}, '/synth_shot');*/
	OSCdef(\shot, {
		arg msg;
		var freqs = [50,55.5,64.5,84.2,93.4,124.6, 281.4, 312, 342.9, 381.2, 418.9, 461.9, 510, 564, 620, 684.3, 756.8, 835];

		var weights = freqs.collect { |val|
			if (val < 564) { 5 } { 1 }
		};

		var totalWeight = weights.sum;
		var normWeights = weights.collect { |w| w / totalWeight };

		var chosen = freqs.wchoose(normWeights);
		var dr = (msg[1] == 2).if { [6,8, 2, 2.5, 3,3.25, 4.25].choose } { [24,18,12,8,6,4].choose };

		Synth("fm-gong", [
			\freq, chosen,
			\dr, dr,
			\pan, rrand(-1.0, 1.0),
			\amp, 0.3
		]);
	}, '/synth_shot');

	OSCdef(\shot_opening, {
		arg msg;
		Synth("fm-gong", [
			\freq, 204.2,
			\dr, 8,
			\pan, 0,
			\amp, 0.5
		]);
	}, '/synth_shot_opening');

	OSCdef(\shot_nodes, {
		arg msg;
		var freqs = [50,55.5,64.5,84.2,93.4,124.6, 281.4, 312, 342.9, 381.2, 418.9, 461.9, 510, 564, 620, 684.3, 756.8, 835];

		var weights = freqs.collect { |val|
			if (val < 564) { 5 } { 1 }
		};

		var totalWeight = weights.sum;
		var normWeights = weights.collect { |w| w / totalWeight };

		var chosen = freqs.wchoose(normWeights);
		var dr = [6,8, 2, 2.5, 3,3.25, 4.25].choose;

		Synth("fm-gong", [
			\freq, chosen,
			\dr, dr,
			\pan, rrand(-1.0, 1.0),
			\amp, [0.2,0.15,0.1,0.25].choose
		]);
	}, '/synth_shot_nodes');

	/*OSCdef(\shot_nodes, {
		arg msg;
		b.playRandom;
	}, '/synth_shot_nodes');*/
};
)
