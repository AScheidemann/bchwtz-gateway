import time
from gatewayn.hub.hub import Hub

hub = Hub()
hub.discover_tags()

testtag = hub.get_tag_by_name("Ruuvi 048B")
testtag.get_time()
testtag.get_config()
testtag.config.set_samplerate(10)
testtag.set_config()
testtag.get_config()
print(testtag.__dict__)
print(testtag.config.__dict__)
print(testtag.time)
# testtag.set_time_to_now()