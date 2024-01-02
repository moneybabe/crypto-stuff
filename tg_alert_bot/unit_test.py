import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from ordinals.classes.AddressMonitor import AddressMonitor
from tg_alert_bot.main import setup_address_monitors

def test_setup_address_monitors():
    whales_df, address_monitors = setup_address_monitors()
    assert len(whales_df) == 9
    assert len(address_monitors) == 9
    assert type(address_monitors) == dict
    for mon in address_monitors.values():
        assert type(mon) == AddressMonitor
        assert len(mon.activity) == 100