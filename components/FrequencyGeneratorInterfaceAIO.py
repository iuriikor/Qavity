from dash import html
import uuid
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_daq as ddaq
from dash_iconify import DashIconify


# All-in-One Components should be suffixed with 'AIO'
class FrequencyGeneratorInterfaceAIO(html.Div):  # html.Div will be the "parent" component

    class ids:
        freq_ctrl = lambda aio_id: {
            'component': 'FrequencyGeneratorInterfaceAIO',
            'subcomponent': 'frequencyCtrl',
            'aio_id': aio_id
        }
        amp_ctrl = lambda aio_id: {
            'component': 'FrequencyGeneratorInterfaceAIO',
            'subcomponent': 'amp_ctrl',
            'aio_id': aio_id
        }
        phase_ctrl = lambda aio_id: {
            'component': 'FrequencyGeneratorInterfaceAIO',
            'subcomponent': 'phase_ctrl',
            'aio_id': aio_id
        }
        output_on = lambda aio_id: {
            'component': 'FrequencyGeneratorInterfaceAIO',
            'subcomponent': 'output_on',
            'aio_id': aio_id
        }
    ids = ids

    # Define the arguments of the All-in-One component
    def __init__(
            self,
            aio_id=None,
            name=None,
            freq_gen=None,
            gen_default_params=None
    ):
        self.name=name
        self._freq_gen = freq_gen
        self._output_on = False

        # Parse generator default parameters
        default_freq = gen_default_params['Frequency'] if gen_default_params else 0
        default_power = gen_default_params['Power'] if gen_default_params else 0
        default_phase = gen_default_params['Phase'] if gen_default_params else 0
        # Define the component's layout
        layout = []

        super().__init__(
            [dmc.Flex(
                [dmc.Flex([
                dmc.Text(self.name, size='lg', c='blue'),
                dmc.Switch(label="", labelPosition='top', onLabel="ON", offLabel="OFF",
                           size='lg', color="teal", style={'align-self': 'flex-end'},
                           id=self.ids.output_on(aio_id))
                                ], justify='space-between'),
                dmc.Flex(
                [
                dmc.NumberInput(value=default_freq, label='Frequency', thousandSeparator=" ",
                                w=150, stepHoldDelay=500, stepHoldInterval=100, suffix=' Hz',
                                debounce=True, radius=3,
                                id=self.ids.freq_ctrl(aio_id)),
                dmc.NumberInput(value=default_power, label='Power', suffix=' dBm',
                                w=100, debounce=True, radius=3, allowDecimal=True, decimalScale=2,
                                id=self.ids.amp_ctrl(aio_id)),
                dmc.NumberInput(value=default_phase, label='Phase', suffix=u'\N{DEGREE SIGN}',
                                w=80, debounce=True, radius=3, allowDecimal=False,
                                id=self.ids.phase_ctrl(aio_id)),
                # ddaq.PowerButton(id=self.ids.output_on(aio_id), on=False, color='#0000FF',
                #                  label='ON/OFF', labelPosition='bottom'),
                        ], justify='space-around', style={}, align='flex-end'),
                ], direction='column', style={'border': 'solid', 'border-radius': '10px',
                               'margin': '10px', 'padding': '10px', 'width': '380px'})
            ])

