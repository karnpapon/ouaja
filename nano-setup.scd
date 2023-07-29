// 1. press play btn to setup fx.
// 2. press button 8 (lower btn) to play sample.

// fader[0]: freqshift                | knob[0]: freq
// fader[1]: LPF                      | knob[1]: loBoost
// fader[2]: HPF                      | knob[2]: hiBoost
// fader[3]: sub                      | knob[3]: freq
// fader[4]: grain(wet+grainsize)     | knob[4]: rand + feedback
// fader[5]: *BROKEN*                 | knob[5]: *BROKEN*
// fader[6]: reverb                   | knob[6]: time
// fader[7]: shape                    | knob[7]: hi
// fader[8]: NOOP                     | knob[8]: NOOP
(
~webmaster = {
var root = "/Users/karnpaponboonput/Desktop/codes/live-ghosting";

  (
    init: {|self|
      self.registerController; // setup nanoKontrol to match with params.
      self.setupBusses; // setup bus (sliders/knobs/button for nanoKontrol)

      // Set initial state for fader positions
      self.controlBusses.faders.at(0).set(0.0); // freqshift
      self.controlBusses.faders.at(1).set(1.0); // LPF
      self.controlBusses.faders.at(2).set(1.0); // HPF
    },

    // setup fx chain.
    patch: {|self|
      var namebase = 'webmaster_';
      self.synthgroup = s;

      s.makeBundle(nil, {

        // SOURCE
        Synth.tail(self.synthgroup,
          namebase ++ 'lpf',
          [ 'cutoff', self.controlBusses.faders.at(1).asMap ]
        );

        Synth.tail(self.synthgroup,
          namebase ++ 'hpf',
          [ 'cutoff', self.controlBusses.faders.at(2).asMap ]
        );

        Synth.tail(self.synthgroup,
          namebase ++ 'grain',
          [
          'drywet', self.controlBusses.faders.at(4).asMap,
          'grainsize', self.controlBusses.faders.at(4).asMap,
          'grainrand', self.controlBusses.knobs.at(4).asMap,
          'fbGain', self.controlBusses.knobs.at(4).asMap
          ]
        );

        Synth.tail(self.synthgroup,
          namebase ++ 'freqshift',
           [
           'drywet', self.controlBusses.faders.at(0).asMap,
           'freq', self.controlBusses.knobs.at(0).asMap
           ]
        );


        Synth.tail(self.synthgroup,
          namebase ++ 'eq',
          [
          'q', 1,
          'loBoost', self.controlBusses.knobs.at(1).asMap,
          'hiBoost', self.controlBusses.knobs.at(2).asMap
          ]
        );

        Synth.tail(self.synthgroup,
          namebase ++ 'comp',
          [ 'slopeBelow', 0.6 ]
        );

        Synth.tail(self.synthgroup,
          namebase ++ 'sub',
          [
          'subamp', self.analysis.amp.asMap,
          'drywet', self.controlBusses.faders.at(3).asMap,
          'freq', self.controlBusses.knobs.at(3).asMap,
          ]
        );

        h = Synth.tail(self.synthgroup, namebase ++ 'shape',['hi', self.controlBusses.knobs.at(7).asMap]);

        // VERB
        Synth.tail(self.synthgroup,
          namebase ++ 'verb',
          [
          'drywet', self.controlBusses.faders.at(6).asMap,
          'time', self.controlBusses.knobs.at(6).asMap,
          ]
        );

          // OUTPUT
        Synth.tail(self.synthgroup, namebase ++ 'out');
      });
    },

		get_synthgroup: {|self|
			self.synthgroup;
		},

    setupBusses: {|self|

      var defaultKnobValue = 0.0;
      var defaultFaderValue = 0.0;

      self.controlBusses = ();

      self.analysis = ();
      self.analysis.amp = Bus.control(s,1);
      self.analysis.hiAmp = Bus.control(s,1);
      self.analysis.loAmp = Bus.control(s,1);


      // Create fader value busses
      self.controlBusses.faders = Array.fill(9,
          {Bus.control(s,1).set(defaultFaderValue)}
      );

      // Create value busses
      self.controlBusses.knobs = Array.fill(9,
          {Bus.control(s,1).set(defaultKnobValue)}
      );

      // Create value busses
      self.controlBusses.downBtns = Array.fill(9, {Bus.control(s,1)});

      // Create value busses
	  self.controlBusses.upBtns = Array.fill(9, {Bus.control(s,1)});

    },

    clearBus: {|self|
      self.controlBusses.do{|sc|
        sc.do{|bus| bus.free};
      };
    },


    registerController: {|self|
      // var synths;
      n = NanoKontrol();

      // FADERS
      n.faders.do{|fader, i |
        fader.onChange = {|fadervalue|
          self.controlBusses.faders.at(i).set(fadervalue/127);
					// self.oscSender("/fader" ++ i, fadervalue/127);
        }
      };

      // KNOBS
      n.knobs.do{|knob, i |
        knob.onChange = {|knobvalue|
          self.controlBusses.knobs.at(i).set(knobvalue/127);
					// self.oscSender("/knob" ++ i, knobvalue/128);
        }
      };

      // TRANSPORT
      n.playBtn.onPress = {|val|
        //
      };

      n.stopBtn.onPress = {|val|
		self.dealloc;
      };

      n.recBtn.onPress = {|val|
        "Rec button pressed".postln;
      };

      n.downBtns[7].onPress = {|val|
        h.set(\shape, (0.4,0.5 .. 0.8).choose);
      };

      n.downBtns[7].onRelease = {|val|
        h.set(\shape, 0);
      };


      // start
		n.upBtns[8].onPress = {|val|
			// self.controlBusses.stopPlay.set(1);
            "upBtns[8]Pressed".postln;
            "setup fx chain".postln;
			self.patch;
			// self.oscSender("/playButton", "pressed!");

    	};

    	n.upBtns[8].onRelease = {|val|
			"upBtns[8]Release".postln;
    	};

    	n.downBtns[8].onPress = {|val|
				// self.patchSource;
    		"downBtns[8]Pressed".postln;
    	};

    	n.downBtns[8].onRelease = {|val|
			"downBtns[8]Release".postln;
    	};

      n.cycleBtn.onPress = {|val|
        "looped button pressed".postln;
      };

    },

	dealloc: {|self|
		self.controlBusses.stopPlay.set(0);
		self.controlBusses.upBtns.at(8).set(0.0);
		self.controlBusses.downBtns.at(8).set(0.0);
        "Stop button pressed".postln;
			// s.stopRecording;
        self.synthgroup.free;
	},

)};

~webmaster.value.init;
)