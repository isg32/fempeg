# fempeg: Flac to AAC Converter (this is to use it in Apple Music)

## Dependencies
```python
pip install -r requirements.txt
```

## PyInstaller Command to Compile to one file
```
python3 -m PyInstaller --name=FemPEG --onefile --windowed --icon=fempfp.jpg --add-data "fempfp.jpg;." --add-data "bin/ffmpeg.exe;bin" --noupx main.py
```

## BUGS:
- ~~Can't Maintain Artwork~~
