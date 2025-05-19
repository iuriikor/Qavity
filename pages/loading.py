import dash
from dash import callback, Input, Output, State, MATCH, ALL, callback_context, html

import dash_mantine_components as dmc

from components.CameraInterfaceAIO import CameraInterfaceAIO
from components.FrequencyGeneratorInterfaceAIO import FrequencyGeneratorInterfaceAIO
from components.RelayBoardAIO import RelayBoardAIO
from dash_extensions import WebSocket

from devices import *
from controllers.sinara.modify_experiment import update_script_values_by_lines
from controllers.sinara.run_artiq_script import run_artiq_in_clang64_visible

exp_path = r'C:\Users\CavLev\Documents\Qavity\controllers\sinara\move_particle.py'

dash.register_page(__name__)

def layout():
    img1 = "./static/img/thorcam_1.jpeg"
    img2 = "./static/img/thorcam_2.jpeg"


    loading_card = dmc.Card([], withBorder=True, padding='xs', style={'margin': '10px'})
    title = dmc.CardSection([dmc.Text('Particle loading control', size='xl')],
                            withBorder=True, py="xs", inheritPadding=True)
    sync_btn = dmc.Button("Update Urukul and run",
                          mt='sm', id='sync-all-button', loaderProps={"type": "dots"})
    aom_controls = dmc.Flex([
        FrequencyGeneratorInterfaceAIO(aio_id='urukul_ch0', name='Loading AOM',
                                       device=urukul_loading, ch=0),
        FrequencyGeneratorInterfaceAIO(aio_id='urukul_ch1', name='Science AOM',
                                       device=urukul_loading, ch=1)
    ], direction='column')
    script_runner_div = html.Div(id='script-runner', style={'display': 'none'})

    run_loading_card = dmc.Card([], withBorder=True, padding='xs')
    detuning_field = dmc.NumberInput(value=0, label='Detuning', thousandSeparator=" ",
                                w=150, stepHoldDelay=500, stepHoldInterval=100, suffix=' Hz',
                                debounce=True, radius=3,
                                id='detuning_ctrl')
    time_field = dmc.NumberInput(value=0, label='Time', thousandSeparator=" ",
                                     w=150, stepHoldDelay=500, stepHoldInterval=100, suffix=' s',
                                     debounce=True, radius=3,
                                     id='time_ctrl')
    info_field = dmc.Text(['Total distance: Not implemented yet'], id='distance-disp')
    move_particles_btn = dmc.Button('Move Particles', id='move-particles-btn', n_clicks=0)

    run_loading_card.children = [
        dmc.Flex([
            detuning_field,
            time_field
        ], direction='row', justify='space-between'),
        dmc.Flex([
            info_field
        ], justify='center'),
        dmc.Flex([
            move_particles_btn,
        ], justify='center')
    ]

    loading_card.children = [title, sync_btn, aom_controls, run_loading_card]

    relay_control_card = RelayBoardAIO(aio_id="relay_controller_interface",
                                       device=valve_control_board)
    # Sockets for handling streams from the cameras
    # websocket1 = WebSocket(url=f"ws://127.0.0.1:5000/stream1", id="ws1", connect=True, reconnect=True)
    # websocket2 = WebSocket(url=f"ws://127.0.0.1:5000/stream2", id="ws2", connect=True, reconnect=True)

    return dmc.MantineProvider(
        [dmc.Flex(
            [
                CameraInterfaceAIO(aio_id='webcam_1', camera=thorcam_1, streamer=streamer1, name='Loading chamber'),
                CameraInterfaceAIO(aio_id='webcam_2', camera=thorcam_2, streamer=streamer2,
                                   name='Science chamber outside'),
                html.Canvas(id="test_canvas", style={'width': '200px', 'height': '400px'}),
                # CameraInterfaceAIO(aio_id='webcam_3', camera=xenics_cam, streamer=streamer3,
                #                    name='Science chamber inside'),
                WebSocket(url=f"ws://127.0.0.1:5000/stream1", id="ws1"),
                WebSocket(url=f"ws://127.0.0.1:5000/stream2", id="ws2"),
                # websocket1,
                # websocket2,
                # WebSocket(url=f"ws://127.0.0.1:5000/stream3", id="ws3"),
                # CameraInterfaceAIO(aio_id='webcam_1', placeholder=img1),
                # CameraInterfaceAIO(aio_id='webcam_2', placeholder=img2),
                loading_card,
                relay_control_card,
                html.Div(children="", id="hidden_div_clientside", style={'display': 'none'}),
            ]),
        ])

#%% CALLBACKS DEFINITION
@callback(
    Input("sync-all-button", "n_clicks"),
    running=[(Output("sync-all-button", "loading"), True, False)],
    prevent_initial_call=True
)
def update_and_run_script(n_clicks):
    print('RUNNING SCRIPT CALLBACK')
    script_path_gen = 'C:/Users/CavLev/Documents/Qavity/controllers/sinara/urukul_as_freq_gen.py'
    starting_line = 17
    # if n_clicks is None:
    #     return dash.no_update
    urukul_loading.update_freq_gen_script(script_path_gen, starting_line)
    run_artiq_in_clang64_visible(script_path_gen)
    # This callback must return a list with one value for each matching output
    # Set all Update chips to True to indicate they have been updated
    # return 'Script ran successfully'

@callback(
    Output({'component': 'FrequencyGeneratorInterfaceAIO', 'subcomponent': 'output_updated', 'aio_id': ALL},
           'checked', allow_duplicate=True),
    Input("sync-all-button", "n_clicks"),
    prevent_initial_call=True
)
def update_all_generators(n_clicks):
    if n_clicks is None:
        return dash.no_update

    # Get all AIO instances that exist in the layout
    matching_outputs = [
        output for output in callback_context.outputs_list
        if output['id']['component'] == 'FrequencyGeneratorInterfaceAIO'
    ]
    # This callback must return a list with one value for each matching output
    # Set all Update chips to True to indicate they have been updated
    return [True] * len(matching_outputs)

@callback(
    Output('distance-disp', 'children'),
    Input('move-particles-btn', 'n_clicks'),
    State('detuning_ctrl', 'value'),
    State('time_ctrl', 'value'),
    prevent_initial_call=True
)
def move_particles(btn_clicked, detuning, time):
    # global exp_path
    print('BUTTON CLICKED')
    # update_dict = {
    #     15: detuning,
    #     16: time
    # }
    # update_script_values_by_lines(exp_path, update_dict)
    urukul_loading.move_particles(detuning, time)
    return ['Running...']
