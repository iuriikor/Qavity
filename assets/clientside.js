if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {
    update_plot: function(n_intervals, data, config) {
        // If no data, return empty figure
        if (!data || !data.channel_data || Object.keys(data.channel_data).length === 0) {
            return {
                'data': [],
                'layout': {
                    'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0},
                    'plot_bgcolor': "#25262b",
                    'paper_bgcolor': "#25262b",
                    'font': {'color': "#c1c2c5"},
                    'xaxis': {
                        'showgrid': true,
                        'gridcolor': "#373A40",
                        'title': "Time (s)",
                        'range': [0, config.buffer_length]
                    },
                    'yaxis': {
                        'showgrid': true,
                        'gridcolor': "#373A40",
                        'title': "Voltage (V)"
                    },
                    'showlegend': false
                }
            };
        }

        // Process data
        const channel_data = data.channel_data;
        const channels = Object.keys(channel_data);

        // Get first channel's data to determine length
        const first_channel = channels[0];
        const data_length = channel_data[first_channel].length;

        // Generate x-axis values based on sample rate
        const x_values = Array.from({length: data_length}, (_, i) => i / config.sample_rate);

        // Create traces for each channel
        const traces = channels.map((channel, i) => {
            const color = config.colors[i % config.colors.length];
            return {
                x: x_values,
                y: channel_data[channel],
                mode: 'lines',
                name: channel,
                type: 'scattergl',
                line: {color: color, width: 1},
                hoverinfo: 'none'
            };
        });

        // Create layout
        const layout = {
            margin: {l: 0, r: 0, t: 0, b: 0},
            plot_bgcolor: "#25262b",
            paper_bgcolor: "#25262b",
            font: {color: "#c1c2c5"},
            xaxis: {
                showgrid: true,
                gridcolor: "#373A40",
                title: "Time (s)",
                range: [0, config.buffer_length]
            },
            yaxis: {
                showgrid: true,
                gridcolor: "#373A40",
                title: "Voltage (V)"
            },
            showlegend: false
        };

        // Set Y-axis range if not auto-scaling
        if (!config.auto_scale) {
            layout.yaxis.range = [config.y_min, config.y_max];
        }

        return {
            data: traces,
            layout: layout
        };
    }
};

window.dash_clientside.clientside.handle_data_acquisition = function(n_intervals, current_data) {
    // Only fetch data when needed (every X intervals)
    if (n_intervals % 5 !== 0 && current_data && Object.keys(current_data).length > 0) {
        return window.dash_clientside.no_update;
    }

    // This will trigger the server-side callback to fetch new data
    return current_data || {};
}

// Create a client-side data accumulator
window.dash_clientside.clientside.accumulate_data = function(new_data, current_data, config) {
    // Initialize if empty
    if (!current_data || !current_data.channel_data) {
        current_data = {channel_data: {}};
    }

    // If we have new data
    if (new_data && new_data.channel_data) {
        const max_points = config.buffer_length * config.sample_rate;

        // For each channel, append new data and trim to max length
        Object.keys(new_data.channel_data).forEach(channel => {
            if (!current_data.channel_data[channel]) {
                current_data.channel_data[channel] = [];
            }

            // Append new data
            current_data.channel_data[channel] =
                current_data.channel_data[channel].concat(new_data.channel_data[channel]);

            // Trim to max length
            if (current_data.channel_data[channel].length > max_points) {
                current_data.channel_data[channel] =
                    current_data.channel_data[channel].slice(-max_points);
            }
        });
    }

    return current_data;
}


// Callbacks for clientside plotting and data storage
// Add this to your existing clientside.js file
window.dash_clientside.clientside.handle_data_acquisition = function(n_intervals, current_data) {
    // Only fetch data when needed (every X intervals)
    if (n_intervals % 5 !== 0 && current_data && Object.keys(current_data).length > 0) {
        return window.dash_clientside.no_update;
    }

    // This will trigger the server-side callback to fetch new data
    return current_data || {};
}

// Create a client-side data accumulator
window.dash_clientside.clientside.accumulate_data = function(new_data, current_data, config) {
    // Initialize if empty
    if (!current_data || !current_data.channel_data) {
        current_data = {channel_data: {}};
    }

    // If we have new data
    if (new_data && new_data.channel_data) {
        const max_points = config.buffer_length * config.sample_rate;

        // For each channel, append new data and trim to max length
        Object.keys(new_data.channel_data).forEach(channel => {
            if (!current_data.channel_data[channel]) {
                current_data.channel_data[channel] = [];
            }

            // Append new data
            current_data.channel_data[channel] =
                current_data.channel_data[channel].concat(new_data.channel_data[channel]);

            // Trim to max length
            if (current_data.channel_data[channel].length > max_points) {
                current_data.channel_data[channel] =
                    current_data.channel_data[channel].slice(-max_points);
            }
        });
    }

    return current_data;
}