#!/bin/bash

mac="FA:74:6E:E8:6D:34" 

if bluetoothctl info "$mac" | grep -q 'Connected: yes'; then
    echo "$mac is connected"
else
    echo "$mac is not connected, connecting..."
    rfkill unblock bluetooth

    bluetoothctl power on
    bluetoothctl connect "$mac"
    sink=$(pactl list short sinks | grep bluez | awk '{print $2}')

    if [ -n "$sink" ]; then
        pacmd set-default-sink "$sink" && echo "OK default sink : $sink"
    else
        echo could not find bluetooth sink
        exit 1
    fi
fi
