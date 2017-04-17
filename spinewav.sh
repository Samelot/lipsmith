#!/bin/bash
audio=$1
if [[ -f ${audio} ]]; then
    if [[ -f "spine-audio-plugin/play.jar" ]]; then
        #spineServer=$(/Applications/Spine/Spine.app/Contents/MacOS/Spine --server 4567) ; 
        /Applications/Spine/Spine.app/Contents/MacOS/Spine --server 4567 | while read -r out ; do
            echo "Processing $out"
            if [[ $out == "[audio] Listening on port: 4567" ]]; then
                echo "oo mm gg"
                java -jar spine-audio-plugin/play.jar 4567 "$audio" 
            fi &

        done
    else
        echo "no spine-audio-plugin"
        exit 1
    fi
else
    echo "please pass a wav file"
    exit 1
fi
