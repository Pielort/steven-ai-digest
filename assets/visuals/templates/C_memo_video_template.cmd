@echo off
setlocal
set FFMPEG=C:\Users\Administrator\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe
set OUT=C:\Users\Administrator\.openclaw\workspace\steven-ai-digest\assets\visuals\templates\C_memo_video_template.mp4

set FILTER=[0:v][1:v]blend=all_mode=screen:all_opacity=0.35,gblur=sigma=18,zoompan=z='min(1.07\,1+0.0009*on)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=450:s=1080x1080,format=yuv420p,drawtext=font='Segoe UI':text='STEVEN AI DIGEST':x=70:y=80:fontsize=52:fontcolor=white@0.95,drawtext=font='Segoe UI':text='DAILY MEMO':x=72:y=140:fontsize=26:fontcolor=white@0.55,drawtext=font='Segoe UI':text='YOUR HEADLINE HERE':x=70:y=780:fontsize=60:fontcolor=white@0.95,drawtext=font='Segoe UI':text='One clean takeaway. No hype.':x=72:y=850:fontsize=30:fontcolor=white@0.62

"%FFMPEG%" -y -f lavfi -i color=c=#0B0F18:s=1080x1080:d=15:r=30 -f lavfi -i color=c=#1B123D:s=1080x1080:d=15:r=30 -filter_complex "%FILTER%" -c:v libx264 -crf 18 -preset medium -t 15 "%OUT%"

echo Wrote %OUT%
