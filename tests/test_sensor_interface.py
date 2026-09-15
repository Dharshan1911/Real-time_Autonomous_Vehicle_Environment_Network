from simulation.synthetic_adapter import SyntheticDHT11

def test_synthetic_dht11():
    sensor = SyntheticDHT11()
    assert sensor.connect() == True
    reading = sensor.read()
    assert reading.sensor_id == "dht11_1"
    assert reading.status == 'VALID'
    assert len(reading.values) == 2
