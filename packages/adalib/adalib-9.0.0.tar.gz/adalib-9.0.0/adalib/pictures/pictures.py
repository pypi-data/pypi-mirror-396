import requests

from .. import adaboard


def get_picture(picture_id: int, output_file_path: str) -> None:
    """
    Get a picture from the picture database.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/pictures/get_picture.ipynb) to test this function or build upon it.

    :param picture_id: ID of the picture
    :type picture_id: int
    :param output_file_path: path to save the picture
    :type output_file_path: str
    :return: None
    :rtype: None
    """

    response = adaboard.request_adaboard(
        path=f"image/{picture_id}",
        method=requests.get,
    )

    content_type = response.headers.get("Content-Type")
    # Ensure that the content type matches the extension of the output file
    if content_type in ["image/jpeg", "image/jpg"]:
        ext = ".jpg"
    elif content_type == "image/png":
        ext = ".png"
    elif content_type == "image/svg+xml":
        ext = ".svg"
    else:
        raise ValueError(
            f"Unsupported content type '{content_type}' for picture with ID {picture_id}."
        )

    with open(output_file_path + ext, "wb") as f:
        f.write(response.content)

    return None


def post_picture(input_file_path: str) -> int:
    """
    Post an picture to the picture database.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/pictures/post_picture.ipynb) to test this function or build upon it.

    :param input_file_path: path to the picture file
    :type input_file_path: str
    :return: ID of the posted picture
    :rtype: int
    """

    filename = input_file_path.split("/")[-1]
    content_type = infer_type_from_extension(filename)
    with open(input_file_path, "rb") as image_file:
        files = {"image_file": (filename, image_file, content_type)}

        response = adaboard.request_adaboard(
            path="image",
            method=requests.post,
            omit_content_type=True,
            files=files,
        ).json()

    return response["id"]


def post_picture_url(picture_url: str) -> int:
    """
    Post a picture to the picture database using a URL.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/picutres/post_picture_url.ipynb) to test this function or build upon it.

    :param picture_url: URL of the picture to be uploaded
    :type picture_url: str
    :return: ID of the posted picture
    :rtype: int
    """

    # Prepare the payload for the POST request
    payload = {"image_url": picture_url}

    # Send the request to the FastAPI endpoint
    response = adaboard.request_adaboard(
        path="image_url",  # The endpoint defined in your FastAPI application
        method=requests.post,
        json=payload,  # Use json parameter to send the payload as JSON
    ).json()

    # Return the ID of the newly created image
    return response["id"]


def infer_type_from_extension(filename: str) -> str:
    if filename.endswith(".jpg"):
        return "image/jpeg"
    elif filename.endswith(".png"):
        return "image/png"
    elif filename.endswith(".svg"):
        return "image/svg+xml"
    else:
        raise ValueError(
            f"Unsupported file extension for file {filename}. Supported extensions are '.jpg', '.png', and '.svg'."
        )
