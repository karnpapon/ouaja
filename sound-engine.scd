(

Window.closeAll;
// MIDIClient.init;
// s.options.outDevice = "Scarlett 2i4 USB";
// s.options.outDevice = "Audient iD14";
s.options.outDevice ="MacBook Pro Speakers";
// s.options.outDevice ="External Headphones";
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

	(
		s.newBusAllocators;
		~srcMixerChannel = MixerChannel(\channel_1, s, 2, 2, 1);
		~src2MixerChannel = MixerChannel(\channel_2, s, 2, 2, 1);
		~reverbMixerChannel = MixerChannel(\channel_fx_rvb, s, 2, 2, level: 1,
			completionFunc: { |chan|
				~rvb = chan.playfx { |outbus, revtime=0.4|
					var sig = In.ar(outbus, 2);
					var freez = TRand.kr(-1, 1, Dust.kr(0.5));
					// var revtime = 0.8;
					var drywet = 1;
					var damping = 0.3;
					MiVerb.ar(sig, revtime, drywet, damping, freeze: freez)
				}
			}
		); // reverb is being add here

		~delayMixerChannel = MixerChannel(\channel_fx_delay, s, 2, 2, level: 1,
			completionFunc: { |chan|
				~del = chan.playfx {|outbus,maxdelaytime=0.25,decaytime=4|
					Mix.arFill(4, { CombL.ar(In.ar(outbus, 1), maxdelaytime, LFNoise1.kr(Rand(0, 0.1), 0.1, 0.2), decaytime) })
				};
			}
		); // delay is being add here
	);

	(
		~reverbMixerChannel.fadergroup.moveToTail(s.defaultGroup);
		~delayMixerChannel.fadergroup.moveToTail(s.defaultGroup);
	);

	~board = MixingBoard("x", nil,~srcMixerChannel, ~src2MixerChannel, ~reverbMixerChannel, ~delayMixerChannel );

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
			~synth = Synth(basename ++ 'main_synth', [\out, ~src2MixerChannel.asBus], target: ~src2MixerChannel.asTarget);
			if ( mlp_cached_path != "", { mlp.read(mlp_cached_path); },{});
		}, { ~synth.free; });
	};

	s.sync;



	(
		SynthDef.new(basename ++ 'main_synth', {
			arg predicting = 0, mod_base1=1, mod_base2=1, mod_base3=1, out;
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

			Out.ar(out,LeakDC.ar([osc1,osc2],mul:0.3));
			LocalOut.ar([osc1,osc2]);
		}).add;

		SynthDef("fm-gong", {
			arg freq = 300, dr = 5.0, amp = 1.0, pan = 0, out;
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
			Out.ar(out, Pan2.ar(carsig * ampenv * amp, pan));
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

	/*	b = BufFiles.new(s, "/Users/karnpaponboonput/Desktop/unorganised-music-master/sounds", actionWhenDone: {
	defer{ b.gui }
	});*/

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
			\amp, 0.3,
			\out, ~srcMixerChannel.asBus
		], target: ~srcMixerChannel.asTarget);
	}, '/synth_shot');

	OSCdef(\shot_opening, {
		arg msg;
		Synth("fm-gong", [
			\freq, 204.2,
			\dr, 8,
			\pan, 0,
			\amp, 0.3,
			\out, ~srcMixerChannel.asBus
		], target: ~srcMixerChannel.asTarget);
	}, '/synth_shot_opening');

	OSCdef(\shot_nodes, {
		arg msg;
		var freqs = [281.4, 312, 342.9, 381.2, 418.9, 461.9, 510, 564, 620, 684.3, 756.8, 835];

		var weights = freqs.collect { |val|
			if (val < 564) { 5 } { 1 }
		};

		var totalWeight = weights.sum;
		var normWeights = weights.collect { |w| w / totalWeight };

		var chosen = freqs.wchoose(normWeights);
		var dr = [6,8, 2, 2.5, 3,3.25, 4.25].choose;

		// msg.postln;

		Synth("fm-gong", [
			\freq, chosen,
			\dr, dr,
			\pan, rrand(-1.0, 1.0),
			\amp, [0.2,0.15,0.1,0.25].choose,
			\out, ~srcMixerChannel.asBus
		], target: ~srcMixerChannel.asTarget);
	}, '/synth_shot_nodes');

	OSCdef(\shot_nodes, {
	arg msg;
		// msg.postln;
	}, '/synth_shot_node_line');
};
)
