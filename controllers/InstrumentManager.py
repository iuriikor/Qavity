class InstrumentManager:
    def __init__(self):
        self.instruments = {}

    def add_instrument(self, name, instrument):
        self.instruments[name] = instrument
        return instrument

    def connect_all(self):
        for name, instrument in self.instruments.items():
            try:
                instrument.connect()
                print(f"Connected to {name}")
            except Exception as e:
                print(f"Failed to connect to {name}: {e}")

    def disconnect_all(self):
        for name, instrument in self.instruments.items():
            if hasattr(instrument, 'connected') and instrument.connected:
                try:
                    instrument.disconnect()
                    print(f"Disconnected from {name}")
                except Exception as e:
                    print(f"Error disconnecting from {name}: {e}")

    def __enter__(self):
        self.connect_all()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect_all()


# Usage:
manager = InstrumentManager()
manager.add_instrument("signal_gen1", AnaPicoAPMS06G(address1))
manager.add_instrument("signal_gen2", AgilentFrequencyGenerator(address2))
manager.add_instrument("scope", SomeOscilloscope(address3))

with manager:
    # All instruments are now connected
    manager.instruments["signal_gen1"].set_frequency(1e9)
    manager.instruments["signal_gen2"].set_frequency(2e9)
    manager.instruments["scope"].capture_trace()

    # More operations using multiple instruments...

# Outside the 'with' block, all instruments are disconnected
