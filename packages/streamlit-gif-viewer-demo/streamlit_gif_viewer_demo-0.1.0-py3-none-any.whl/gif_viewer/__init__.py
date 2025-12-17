import os
import streamlit.components.v1 as components

# Set to False during development, True for production
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "gif_viewer",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("gif_viewer", path=build_dir)


def gif_viewer(
    gif_url: str,
    caption: str = "",
    width: int = None,
    height: int = None,
    autoplay: bool = True,
    loop: bool = True,
    key: str = None,
):
    """Display a GIF in Streamlit with optional controls.

    Parameters
    ----------
    gif_url : str
        The URL or path to the GIF image to display.
    caption : str, optional
        An optional caption to display below the GIF.
    width : int, optional
        The width of the GIF in pixels. If None, uses natural width.
    height : int, optional
        The height of the GIF in pixels. If None, uses natural height.
    autoplay : bool, optional
        Whether to autoplay the GIF animation. Default is True.
    loop : bool, optional
        Whether to loop the GIF animation. Default is True.
    key : str or None, optional
        An optional key that uniquely identifies this component.

    Returns
    -------
    dict
        A dictionary containing component state:
        - 'loaded': bool - Whether the GIF has finished loading
        - 'playing': bool - Whether the GIF is currently playing
    """
    component_value = _component_func(
        gif_url=gif_url,
        caption=caption,
        width=width,
        height=height,
        autoplay=autoplay,
        loop=loop,
        key=key,
        default={"loaded": False, "playing": autoplay},
    )

    return component_value

