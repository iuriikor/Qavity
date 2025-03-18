from artiq.experiment import *  # imports everything from the artiq experiment library
class AOM_ctr(EnvExperiment):
    """Loading AOM Control"""

    def build(self):  # This code runs on the host device
        # Core device
        self.setattr_device("core")  # sets core device drivers as attributes
        # Urukul
        self.setattr_device('urukul0_cpld')
        self.setattr_device("urukul0_ch0")  # Channel 0
        self.setattr_device("urukul0_ch1")  # Channel 1
        self.setattr_device("urukul0_ch2")  # Channel 2
        self.setattr_device("urukul0_ch3")  # Channel 3

    @kernel  # This code runs on the FPGA
    def run(self):
        # Frequencies
        freq_ch0 = 300000.0
        freq_ch1 = 300000.0
        freq_ch2 = 300000.0
        freq_ch3 = 300000.0
        # Amplitudes
        amp_ch0 = 0.5
        amp_ch1 = 0.5
        amp_ch2 = 0.5
        amp_ch3 = 0.5
        # Attenuations
        att_ch0 = 10.0
        att_ch1 = 10.0
        att_ch2 = 10.0
        att_ch3 = 10.0
        # Output state
        ch0_on = False
        ch1_on = False
        ch2_on = False
        ch3_on = False

        self.core.reset()
        self.urukul0_cpld.init()  # initialises CPLD
        self.urukul0_cpld.get_att_mu() # Needed to not reset attenuation to default during the init phase
        delay(50 * us) # Slack needed after the get_att_mu() function

        # Channel 0 parameters
        self.urukul0_ch0.set_att(att_ch0)  # writes attenuation to urukul channel
        self.urukul0_ch0.set(frequency=freq_ch0,
                             amplitude=amp_ch0)  # writes frequency and amplitude variables to urukul channel thus outputting function
        delay(50 * us)
        # Channel 1 parameters
        self.urukul0_ch1.set_att(att_ch1)  # writes attenuation to urukul channel
        self.urukul0_ch1.set(frequency=freq_ch1,
                             amplitude=amp_ch1)
        delay(50 * us)
        # Channel 2 parameters
        self.urukul0_ch2.set_att(att_ch2)  # writes attenuation to urukul channel
        self.urukul0_ch2.set(frequency=freq_ch2,
                             amplitude=amp_ch2)
        delay(50 * us)
        # Channel 3 parameters
        self.urukul0_ch3.set_att(att_ch3)  # writes attenuation to urukul channel
        self.urukul0_ch3.set(frequency=freq_ch3,
                             amplitude=amp_ch3)
        delay(50 * us)

        self.urukul0_ch0.sw.off()
        self.urukul0_ch1.sw.off()
        self.urukul0_ch2.sw.off()
        self.urukul0_ch3.sw.off()

        if ch0_on: # switches urukul channel 0 on
            self.urukul0_ch0.sw.on()
        if ch1_on: # switches urukul channel 0 on
            self.urukul0_ch1.sw.on()
        if ch2_on: # switches urukul channel 0 on
            self.urukul0_ch2.sw.on()
        if ch3_on: # switches urukul channel 0 on
            self.urukul0_ch3.sw.on()



