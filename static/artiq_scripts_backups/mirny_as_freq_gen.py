from artiq.experiment import *
"""
This is a template script to scan the drive frequency of Mirny frequency generator.
The experiment-specific purpose of the script is to scan across the cavity resonance 
to measure TEM00-TEM01 separation, or to measure FSR, or to change detuning between
the tweezer and the cavity. The script is ran directly on Sinara and is executed 
with command artiq_run script_name.py.

For more details read Artiq manual.
"""



class TestMirny(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("mirny0_cpld")
        self.setattr_device('mirny0_ch0')

    @kernel
    def run(self):
        # Define output frequency and attenuation
        drive_freq_kHz = 488300.0
        att_dB = 27.0
        # Set the output on or off
        turn_on = False

        # Scan
        self.core.reset()
        #### Initialising cpld (Either of the 2 functions)
        self.mirny0_cpld.init()
        self.mirny0_cpld.set_att(0, att_dB * dB)
        delay(50 * us)
        self.mirny0_ch0.init()
        self.mirny0_ch0.set_att(att_dB * dB)
        self.mirny0_ch0.set_frequency(drive_freq_kHz * kHz)

        #### Turning ON the OUTPUT terminal
        if (turn_on):
            self.mirny0_ch0.sw.on()
        else: # Just to be sure
            self.mirny0_ch0.sw.off()

