import dash

import dash_mantine_components as dmc

from components.CameraInterfaceAIO import CameraInterfaceAIO
from components.FrequencyGeneratorInterfaceAIO import FrequencyGeneratorInterfaceAIO

dash.register_page(__name__)

def layout():
    img1 = "./static/img/thorcam_1.jpeg"
    img2 = "./static/img/thorcam_2.jpeg"
    return dmc.MantineProvider(
        [dmc.Flex(
            [
        # CameraInterfaceAIO(aio_id='webcam_1', camera=thorcam_1),
        # CameraInterfaceAIO(aio_id='webcam_2', camera=thorcam_2),
        CameraInterfaceAIO(aio_id='webcam_1', placeholder=img1),
        CameraInterfaceAIO(aio_id='webcam_2', placeholder=img2),
        FrequencyGeneratorInterfaceAIO(aio_id='urukul_ch0', name='Loading AOM',
                                       device=urukul_ch0),
        FrequencyGeneratorInterfaceAIO(aio_id='urukul_ch1', name='Science AOM',
                                       device=urukul_ch1),
            ]),
    ])
