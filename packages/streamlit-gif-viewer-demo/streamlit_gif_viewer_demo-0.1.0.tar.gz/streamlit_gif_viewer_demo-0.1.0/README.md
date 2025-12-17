# 🎬 Streamlit GIF Viewer Component

A custom Streamlit component for displaying GIFs with beautiful styling and smooth animations.

## Features

- ✨ Beautiful, modern UI with hover effects
- 🎨 Automatic theme integration with Streamlit
- 📐 Customizable width and height
- 💬 Optional captions
- 🔄 Loading states and error handling
- 🎯 Simple, intuitive API

## Installation

### Development Mode

1. **Install the Python package:**
   ```bash
   pip install -e .
   ```

2. **Install frontend dependencies:**
   ```bash
   cd gif_viewer/frontend
   npm install
   ```

3. **Start the frontend dev server:**
   ```bash
   npm start
   ```

4. **Run the Streamlit app (in another terminal):**
   ```bash
   streamlit run example.py
   ```

## Usage

```python
import streamlit as st
from gif_viewer import gif_viewer

# Basic usage
gif_viewer(
    gif_url="https://media.giphy.com/media/example/giphy.gif",
    caption="My awesome GIF!"
)

# With custom dimensions
gif_viewer(
    gif_url="https://media.giphy.com/media/example/giphy.gif",
    caption="Resized GIF",
    width=300,
    height=200
)
```

## API Reference

### `gif_viewer(gif_url, caption="", width=None, height=None, autoplay=True, loop=True, key=None)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `gif_url` | str | required | URL or path to the GIF image |
| `caption` | str | `""` | Optional caption below the GIF |
| `width` | int | `None` | Width in pixels (uses natural width if None) |
| `height` | int | `None` | Height in pixels (uses natural height if None) |
| `autoplay` | bool | `True` | Whether to autoplay the animation |
| `loop` | bool | `True` | Whether to loop the animation |
| `key` | str | `None` | Unique identifier for the component |

### Returns

A dictionary containing:
- `loaded` (bool): Whether the GIF has finished loading
- `playing` (bool): Current playback state

## Building for Production

1. Build the frontend:
   ```bash
   cd gif_viewer/frontend
   npm run build
   ```

2. Set `_RELEASE = True` in `gif_viewer/__init__.py`

3. Build the package:
   ```bash
   python setup.py sdist bdist_wheel
   ```

## License

MIT

