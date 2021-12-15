#!/usr/bin/env python3
"""
Setup tool to register the PulseAudio sinks as primary and secondary audio outputs.

Run this once after installation. Can be re-run at any time to change the settings.
For more information see :ref:`userguide/audio:Audio Configuration`.
"""
import os
import argparse

import pulsectl

import misc.inputminus as pyil
from misc.inputminus import msg_highlight
from misc.simplecolors import Colors
import jukebox.cfghandler
import jukebox.plugs
jukebox.plugs.ALLOW_DIRECT_IMPORTS = True
import components.hostif.linux as host  # noqa: E402


def query_sinks():
    pulse = pulsectl.Pulse('jukebox-config')
    sinks = pulse.sink_list()
    msg_highlight('Available audio outputs')
    for idx, sink in enumerate(sinks):
        print(f"{Colors.lightgreen}{idx:2d}{Colors.reset}:"
              f"  {Colors.lightcyan}{sink.name}{Colors.reset}")
    print("")
    primary_idx = pyil.input_int("Primary audio output (no bluetooth)?", min=0, max=len(sinks) - 1,
                                 prompt_color=Colors.lightgreen,
                                 prompt_hint=True, blank=0)
    primary = sinks[primary_idx].name
    print(f"Primary audio output = {primary}\n")

    secondary = None
    toggle_on_connect = False
    if len(sinks) > 1:
        secondary_idx = pyil.input_int("Secondary audio output (typically bluetooth)? Set to -1 for empty.",
                                       min=-1, max=len(sinks) - 1,
                                       prompt_color=Colors.lightgreen,
                                       prompt_hint=True, blank=-1)
        if secondary_idx >= 0:
            secondary = sinks[secondary_idx].name
            print(f"Secondary audio output = {secondary}\n")
            toggle_on_connect = pyil.input_yesno("Automatically toggle output on connection of secondary device?",
                                                 prompt_color=Colors.lightgreen,
                                                 prompt_hint=True, blank=True)
    return primary, secondary, toggle_on_connect


def configure_jukebox(filename, primary, secondary, toggle_on_connect):
    cfg_jukebox = jukebox.cfghandler.get_handler('juke')
    cfg_jukebox.load(filename)

    cfg_jukebox.setn('pulse', 'toggle_on_connect', value=toggle_on_connect)

    cfg_jukebox.setn('pulse', 'outputs', value={})
    key = 'primary'
    cfg_jukebox.setn('pulse', 'outputs', key, 'alias', value='Speakers')
    cfg_jukebox.setn('pulse', 'outputs', key, 'volume_limit', value=100)
    cfg_jukebox.setn('pulse', 'outputs', key, 'pulse_sink_name', value=primary)

    if secondary is not None:
        key = 'secondary'
        cfg_jukebox.setn('pulse', 'outputs', key, 'alias', value='Bluetooth Headset')
        cfg_jukebox.setn('pulse', 'outputs', key, 'volume_limit', value=100)
        cfg_jukebox.setn('pulse', 'outputs', key, 'pulse_sink_name', value=secondary)

    cfg_jukebox.save()


def welcome(config_file):
    msg_highlight('The Jukebox audio output configuration tool')
    print("""
Please note:
 - Primary output must be available on system boot - i.e. not a bluetooth device
 - Secondary output is typically a bluetooth device
 - Connect your bluetooth device before running this script (or run it again later)""")
    print(f" - Will replace your audio output configuration in\n   '{config_file}'")
    print(""" - Exit all running Jukeboxes (including services) before continuing
     $ systemctl --user stop jukebox-daemon
 - Checkout the documentation page 'Audio Configuration'
 - If you are not sure which device is which, you can try them with
     $ paplay -d sink_name /usr/share/sounds/alsa/Front_Center.wav
 - To get a list of all sinks, check out below list or use
     $ pactl list sinks short
    """)


def goodbye():
    # Adjust Aliases and Volume Limits in the config file
    pass


def main():
    # Get absolute path of this script
    script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    default_cfg_jukebox = os.path.abspath(os.path.join(script_path, '../../shared/settings/jukebox.yaml'))

    argparser = argparse.ArgumentParser(description='The Jukebox audio configuration tool')
    argparser.add_argument('-c', '--conf', type=argparse.FileType('r'), default=default_cfg_jukebox,
                           help=f"jukebox configuration file [default: '{default_cfg_jukebox}'",
                           metavar="FILE")
    args = argparser.parse_args()

    welcome(args.conf.name)

    if host.is_any_jukebox_service_active():
        msg_highlight('Jukebox service is running!')
        print("\nPlease stop jukebox-daemon service and restart tool")
        print("$ systemctl --user stop jukebox-daemon\n\n")
        print("Don't forget to start the service again :-)")
        return

    primary, secondary, toggle_on_connect = query_sinks()
    configure_jukebox(args.conf.name, primary, secondary, toggle_on_connect)
    goodbye()


if __name__ == '__main__':
    main()
