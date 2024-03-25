import contextlib
import glob
import os
import shutil

import requests
from PIL import Image


async def download_images(data, images_path, uid, request_url_base, file_type, modulo=5, **kwargs) -> None:
    """
    Downloads images from a list of URLs and saves them to a directory.

    Args:
        data (list): The list of image data.
        images_path (str): The path to the directory to save images.
        uid (str): The unique identifier for the images.
        request_url_base (str): The base URL for the image requests.
        file_type (str): The file type of the images.
        module (int): How many frames to skip.

    Kwargs:
        send_progress (bool, optional): Whether to send progress updates. Defaults to True.
        embed (Embed, optional): The embed message to update with progress. Required if `send_progress` is True.
        msg (Message, optional): The message object to edit with progress. Required if `send_progress` is True.
        ctx (Context, optional): The context of the command. Defaults to None. Required if `send_dropped_frames_error` is True.
        send_dropped_frames_error (bool, optional): Whether to send an error message if images cannot be obtained. Defaults to False.
    """
    send_progress = kwargs.get('send_progress', True)
    embed = kwargs.get('embed', None)
    msg = kwargs.get('msg', None)
    ctx = kwargs.get('ctx', None)
    send_dropped_frames_error = kwargs.get('send_dropped_frames_error', False)
    
    if send_progress and (embed is None or msg is None):
        raise ValueError("embed and msg are required when send_progress is True.")
    
    data_len = len(data)
    count = 0
    error_count = 0
    for image in data:
        if count == 0 or count % modulo == 0:
            if send_progress and (count == 0 or count % 20 == 0):
                embed.description = (
                    f"```\nFetching images ({round(count/data_len*100)}%)...\n```"
                )
                await msg.edit(embed=embed)

            resp = requests.get(
                f"{request_url_base}{image['url']}", stream=True
            )
            if resp.status_code == 200:
                with open(f"{images_path}/{count}-{uid}.{file_type}", "wb") as f:
                    shutil.copyfileobj(resp.raw, f)
            else:
                error_count += 1
            del resp
        count += 1
    
    if send_dropped_frames_error and error_count > 0 and ctx is not None:
        await ctx.send(f"Couldn't obtain {error_count} image(s), the GIF may not look complete.")




async def compile_images_to_gif(images_path, _uid, output_file_name, input_image_file_type, **kwargs) -> None:
    """
    Compiles images into a GIF file.

    Args:
        images_path (str): The path to the directory containing the images.
        _uid (str): The unique identifier for the images.
        output_file_name (str): The name of the output GIF file.
        input_image_file_type (str): The file type of the input images.
    Kwargs:
        send_progress (bool, optional): Whether to send progress updates. Defaults to False. Requires `embed` and `msg`.
        embed (discord.Embed, optional): The embed message for progress updates. Defaults to None.
        msg (discord.Message, optional): The message object for progress updates. Defaults to None.
    """
    send_progress = kwargs.get('send_progress', False)
    embed = kwargs.get('embed', None)
    msg = kwargs.get('msg', None)
    
    with contextlib.ExitStack() as stack:
        if send_progress and embed is not None and msg is not None:
            embed.description = "```\nFetching all local images...\n```"
            await msg.edit(embed=embed)
        
        images = []
        for f in sorted(glob.glob(f"{images_path}/*-{_uid}.{input_image_file_type}")):
            with Image.open(f) as img:
                creation_time = os.path.getctime(f)
                images.append((creation_time, img.copy()))

        images.sort(key=lambda x: x[0])  # Sort images by creation time, if you don't do this, the GIF has random frames pop in out of order.
        
        if send_progress and embed is not None and msg is not None:
            embed.description = "```\nCombining into one GIF...\n```"
            await msg.edit(embed=embed)
        
        sorted_images = [img for _, img in images]

        sorted_images[0].save(
            fp=output_file_name,
            format="GIF",
            append_images=sorted_images[1:],
            save_all=True,
            duration=150,
            loop=0,
        )

