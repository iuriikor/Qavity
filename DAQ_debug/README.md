# DAQ Debug Monitor

This is a minimal working example to reproduce and debug the DAQ data display delay issue.

## Overview

The debug app tests your DAQ setup with:
- **Real NI DAQ Device** (`controllers/DAQ/NI_cDAQ9174.py`): Uses actual NI cDAQ9174 hardware
- **Real DAQ Streamer** (`controllers/streamers/DAQDataStreamer.py`): Same streaming logic as main app
- **Debug App** (`simple_debug.py`): Single-page Dash app with 4 plots displaying the data

## Features

- **Adjustable Update Rate**: Control how frequently data is sent (1-100 Hz)
- **Configurable Display Samples**: Choose how many samples to display (100-2000)
- **Real-time Performance**: Same data transfer architecture as your main app
- **Binary Protocol**: Uses the same struct-based binary format for efficiency

## Usage

1. Run the debug app:
   ```bash
   cd DAQ_debug
   python simple_debug.py
   ```

2. Open your browser to `http://127.0.0.1:8050`

3. Click "Start Streaming" to begin data acquisition

4. Adjust the update rate to test different streaming speeds

5. Monitor the browser console for timing information and potential delays

## Files

- `simple_debug.py`: **Main app** - Fixed version without callback conflicts
- `fake_device.py`: Simulated DAQ device with sine wave generation
- `fake_streamer.py`: WebSocket data streaming (matches your DAQDataStreamer)
- `debug_app.py`: Alternative version (may have callback conflicts)
- `run_debug.py`: Requires hypercorn dependency
- `README.md`: This documentation

## Testing Delay Issues

To reproduce the delay issue:

1. Start with a low update rate (5-10 Hz)
2. Gradually increase the update rate (20-50 Hz)
3. Check browser console for timing warnings
4. Monitor if plots start lagging behind real-time data


## Key Differences from Main App

- Uses the same NI DAQ device and streamer as main app
- Single page instead of multi-page app
- Simplified to focus on the core delay issue
- All components in one directory for easy debugging

## Next Steps

1. Test at different update rates to find when delays occur
2. Monitor browser console for performance warnings
3. Compare with your webcam streaming performance
4. Use this as a baseline to test potential fixes