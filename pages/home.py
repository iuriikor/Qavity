import dash

import dash_mantine_components as dmc

from components.CameraInterfaceAIO import CameraInterfaceAIO
from components.FrequencyGeneratorInterfaceAIO import FrequencyGeneratorInterfaceAIO

dash.register_page(__name__, path='/')

def layout():
    return dmc.MantineProvider(
        [dmc.Flex(
            "Home page of cavity experiment control software"),])

