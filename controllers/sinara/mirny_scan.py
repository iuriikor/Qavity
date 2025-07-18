from artiq.experiment import *
"""
This is a template script to scan the drive frequency of Mirny frequency generator.
The experiment-specific purpose of the script is to scan across the cavity resonance 
to measure TEM00-TEM01 separation, or to measure FSR, or to change detuning between
the tweezer and the cavity. The script is ran directly on Sinara and is executed 
with command artiq_run script_name.py.

For more details read Artiq manual.
"""



class MirnyRamp(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("mirny0_cpld")
        self.setattr_device('mirny0_ch0')
        # TTL channel to signal change of drive frequency
        self.setattr_device("ttl4")

    @kernel
    def run(self):
        # Define scan parameters
        start_freq_kHz = 388000.0
        end_freq_kHz = 388100.0
        # STEP HAS TO ALWAYS BE POSITIVE
        step_kHz = 1.0
        # Delay between steps, seconds
        step_delay = 0.1
        # Turn off the generator at the end
        turn_off = False

        # Scan
        self.core.reset()
        self.ttl4.output() # Set TTL4 port to output
        #### Initialising cpld (Either of the 2 functions)
        self.mirny0_cpld.init()
        # This line is crucial to not turn off channel output during device initialization
        # 27 dB is set specifically for my EOM (Cavity setup). Before using this script, check
        # that it does not fry whatever you're driving.
        self.mirny0_cpld.set_att(0, 25.0 * dB)
        delay(50 * us)
        self.mirny0_ch0.init()
        self.mirny0_ch0.set_att(25.0 * dB)
        self.mirny0_ch0.set_frequency(start_freq_kHz * kHz)

        #### Turning ON the OUTPUT terminal
        self.mirny0_ch0.sw.on()

        curr_freq_kHz = start_freq_kHz
        if (end_freq_kHz > start_freq_kHz):
            while(curr_freq_kHz <= end_freq_kHz):
                with parallel:
                    self.mirny0_ch0.set_frequency(curr_freq_kHz * kHz)
                    # delay(50 * us)
                    self.ttl4.pulse(100 * us) # Trigger for external acquisition
                    delay(step_delay)
                curr_freq_kHz += step_kHz  # Increase drive frequency
        elif (end_freq_kHz < start_freq_kHz):
            while (curr_freq_kHz >= end_freq_kHz):
                with parallel:
                    self.mirny0_ch0.set_frequency(curr_freq_kHz * kHz)
                    # delay(50 * us)
                    self.ttl4.pulse(100 * us) # Trigger for eternal acquisition
                    delay(step_delay)
                curr_freq_kHz -= step_kHz  # Reduce drive frequency

        if (turn_off):
            #### Turning OFF the OUTPUT terminal
            self.mirny0_ch0.sw.off()
