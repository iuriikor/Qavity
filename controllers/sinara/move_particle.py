from artiq.experiment import *  # imports everything from the artiq experiment library
class AOM_ctr(EnvExperiment):
    """Loading AOM Control"""

    def build(self):  # This code runs on the host device
        # Core device
        self.setattr_device("core")  # sets core device drivers as attributes
        # Urukul
        self.setattr_device('urukul0_cpld')
        self.setattr_device("urukul0_ch0")  # Channel 0 drives Loading chamber AOM
        self.setattr_device("urukul0_ch1")  # Channel 1 drives Science chamber AOM

    @kernel  # This code runs on the FPGA
    def run(self):
        # Externally set parameters
        detuning = 100.0 # Conveyor belt detuning, <0 for transport to science chamber
        transport_time = 10.0 # time for which to move the particle
        # Loading AOM (CH0)
        # freq_load = 110000000
        freq_load = 300000.0
        amp_load = 0.8
        att_load = 5.0
        # Science AOM (CH1)
        amp_sci = 0.8
        att_sci = 5.0

        self.core.reset()
        self.urukul0_cpld.init()  # initialises CPLD
        self.urukul0_cpld.get_att_mu() # Needed to not reset attenuation to default during the init phase
        delay(50 * us) # Slack needed after the get_att_mu() function

        # Loading side AOM
        self.urukul0_ch0.set_att(att_load)  # writes attenuation to urukul channel
        self.urukul0_ch0.set(frequency=freq_load,
                             amplitude=amp_load)  # writes frequency and amplitude variables to urukul channel thus outputting function
        # Science side AOM
        self.urukul0_ch1.set_att(att_sci)  # writes attenuation to urukul channel
        self.urukul0_ch1.set(frequency=freq_load,
                             amplitude=amp_sci)

        self.urukul0_ch0.sw.on()  # switches urukul channel on
        self.urukul0_ch1.sw.on()  # switches urukul channel on

        self.urukul0_ch1.set(frequency=freq_load+detuning,
                             amplitude=amp_sci)
        delay(transport_time)
        self.urukul0_ch1.set(frequency=freq_load,
                             amplitude=amp_sci)


