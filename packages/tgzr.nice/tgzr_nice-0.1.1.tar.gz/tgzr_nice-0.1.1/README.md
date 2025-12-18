# tgzr.nice
Components and tools for TGZR Nice apps

# Usage

## Static Files

### Register the assets and medias folders

```python
import tgzr.nice.static_files

tgzr.nice.static_files.register()

```
then, use like this:
```
# TODO: write this
```

Note: if you're using a tgzr.nice component which rely on static files to be
registered, it will have call `register()` and you won't need to do it. 

### Get a static file

```python
import tgzr.nice.static_files

tgz_thumbnail_path = tgzr.nice.static_files.get_asset_path(group='tgzr', name='tgzr_thumbnail.png')
tgzr_logo_svg_content = tgzr.nice.static_files.get_asset_content(group='tgzr', name='tgzr_logo_bgblack.svg')

some_video = tgzr.nice.static_files.get_media_path(group='group-name', name='video-name.mp4')

```
