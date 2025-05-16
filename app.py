from dash import html, Input, Output, State, callback, page_container
from dash_extensions import WebSocket
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import asyncio
from quart import websocket
import base64
import os
import time
from PIL import Image

from server import app, webcam_server
from components.CameraInterfaceAIO import CameraInterfaceAIO
from components.FrequencyGeneratorInterfaceAIO import FrequencyGeneratorInterfaceAIO
from controllers.cameras.ThorCam import ThorCam
from controllers.streamer import WebcamStreamer
from devices import *
from themes import *

img1 = "./static/img/thorcam_1.jpeg"
img2 = "./static/img/thorcam_2.jpeg"

# def make_layout():
#     return dmc.MantineProvider(
#         [dmc.Flex(
#             [
#         # CameraInterfaceAIO(aio_id='webcam_1', camera=thorcam_1),
#         # CameraInterfaceAIO(aio_id='webcam_2', camera=thorcam_2),
#         CameraInterfaceAIO(aio_id='webcam_1', placeholder=img1),
#         CameraInterfaceAIO(aio_id='webcam_2', placeholder=img2),
#         FrequencyGeneratorInterfaceAIO(aio_id='anapico_1', name='Example DDS'),
#         WebSocket(url=f"ws://127.0.0.1:5000/stream1", id="ws1"),
#         WebSocket(url=f"ws://127.0.0.1:5000/stream2", id="ws2"),
#             ]),
#     ])

def make_layout():
    logo = "https://github.com/user-attachments/assets/c1ff143b-4365-4fd1-880f-3e97aab5c302"
    buttons = [
        dmc.Anchor(
            dmc.Button("Home", variant="subtle", color="gray"),
            href='/'),
        dmc.Anchor(
            dmc.Button("Monitors", variant="subtle", color="gray"),
            href='/monitors'),
        dmc.Anchor(
            dmc.Button("Loading", variant="subtle", color="gray"),
                        href='/loading'),
        dmc.Button("Cavity", variant="subtle", color="gray"),
        dmc.Button("Detection", variant="subtle", color="gray"),
        dmc.Button("System Info", variant="subtle", color="gray"),
    ]

    theme_toggle = dmc.Switch(
        offLabel=DashIconify(icon="radix-icons:sun", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][8]),
        onLabel=DashIconify(icon="radix-icons:moon", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][6]),
        id="color-scheme-switch",
        persistence=True,
        color="grey",
    )

    layout = dmc.AppShell(
        [
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                dmc.Image(src=logo, h=40),
                                dmc.Title("Demo App", c="blue"),
                                theme_toggle
                            ]
                        ),
                        dmc.Group(
                            children=buttons,
                            ml="xl",
                            gap=0,
                            visibleFrom="sm",
                        ),
                    ],
                    justify="space-between",
                    style={"flex": 1},
                    h="100%",
                    px="md",
                ),
            ),
            dmc.AppShellMain(
                page_container
            ),
        ],
        header={"height": 60},
        padding="md",
        id="appshell",
    )

    return dmc.MantineProvider([layout],
                               theme=theme)

# def close_app():
#     global thorcam_1, thorcam_2, thorSDK
#     time.sleep(1)
#     del thorcam_1
#     time.sleep(1)
#     del thorcam_2
#     time.sleep(1)
#     del thorSDK


from components.callbacks import *
