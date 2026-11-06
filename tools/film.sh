#!/bin/bash
# Ambient loops from the client's own footage: seamless crossfade, no audio, poster = frame 0 of the encoded file.
# usage: film.sh <source-dir> <out-dir>
set -e
SRC="$1"; OUT="$2"; F=0.7
loop() { # name input duration prefilter
  local name=$1 in=$2 D=$3 pre=$4
  local A=$(python3 -c "print(round($D-$F,3))")
  local G="[0:v]${pre}split=3[m][t][h];[m]trim=start=$F:end=$A,setpts=PTS-STARTPTS[main];[t]trim=start=$A:end=$D,setpts=PTS-STARTPTS[tail];[h]trim=start=0:end=$F,setpts=PTS-STARTPTS[head];[tail][head]xfade=transition=fade:duration=$F:offset=0[bl];[main][bl]concat=n=2:v=1,format=yuv420p[o]"
  ffmpeg -nostdin -v error -y -i "$in" -filter_complex "$G" -map "[o]" -an -c:v libx264 -preset slow -crf 26 -maxrate 4500k -bufsize 9M -movflags +faststart "$OUT/$name-1080.mp4"
  ffmpeg -nostdin -v error -y -i "$OUT/$name-1080.mp4" -vf scale=1280:-2 -an -c:v libx264 -preset slow -crf 27 -maxrate 2500k -bufsize 5M -movflags +faststart "$OUT/$name-720.mp4"
  ffmpeg -nostdin -v error -y -i "$OUT/$name-1080.mp4" -frames:v 1 -q:v 3 "$OUT/$name-poster.jpg"
  ls -la "$OUT/$name"*
}
loop lagoon "$SRC/intro.mp4" 25.33 "eq=saturation=1.16:contrast=1.02:gamma=1.14,"
[ -n "$ONLY" ] && exit 0
loop sandbank "$SRC/sandbank-video-1.mp4" 15.83 "eq=saturation=1.03,"
# 4K60 slowed to half speed reads calmer and gives a longer loop
loop shark "$SRC/GX019312_1742539995799.mp4" 11.70 "setpts=2*PTS,fps=30,scale=1920:-2,"
