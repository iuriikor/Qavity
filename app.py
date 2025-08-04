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
        dmc.Anchor(
            dmc.Button("Cavity", variant="subtle", color="gray"),
            href='/cavity'),
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

from components.callbacks import *
