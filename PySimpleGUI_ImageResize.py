import PySimpleGUI as sg
from PIL import Image
import pathlib
import os


def image_resize(source_path, destination_path, image_size):

    new_size = image_size
    dir_path = pathlib.Path(source_path)
    save_path = pathlib.Path(destination_path)
    num_of_files = 0

    if not dir_path.exists():
        sg.popup_quick("Source Folder does not exist", title="Error")
        return

    if not save_path.exists():
        create_folder = sg.popup_yes_no("The destination folder does not exist. "
                                        "Do you want to create it?",
                                        title="Create Save Folder")
        if create_folder in ("No", None):
            return

        pathlib.Path(save_path).mkdir()

    display_text = "Conversion Summary"
    for filename in dir_path.iterdir():
        # filename here is the full path of the file including extension
        if filename.suffix.lower() in (".jpg", ".png") and filename.is_file():
            im = Image.open(filename)
            original_dimension = im.size
            original_size = round(os.stat(str(filename)).st_size / 1024, 1)

            # png files with transparency (RGBA) can't be saved to jpeg
            # convert file to RGB first
            if im.mode == "RGBA":
                im = im.convert("RGB")

            try:
                im.thumbnail(new_size, Image.ANTIALIAS)
                save_file_dimension = im.size

                # filename.stem is the file name only without extension or path
                save_file_name = save_path.joinpath(f"{filename.stem}.jpg")
                im.save(save_file_name)
                save_file__size = round(os.stat(str(save_file_name)).st_size / 1024, 1)
                compression_percent = round((save_file__size/original_size) * 100, 2)

                display_text = f"{display_text}\n" \
                               f"{original_dimension} {original_size} KB "\
                               f"Converted to {save_file_dimension} {save_file__size} KB "\
                               f"{compression_percent}% of original"

                window.find_element("FileList").update(display_text)
                window.Refresh()

                num_of_files += 1

            except IOError:
                print(f"error occurred on file {filename.name}")

    display_text = f"{display_text}\n"\
                   f"Converted {num_of_files} files"
    window.find_element("FileList").update(display_text)

    # sg.popup(f"Converted {num_of_files} files")


def gui_layout():
    sg.ChangeLookAndFeel("Light Green")

    dimensions_frame_layout = [
        [sg.Text("Resize Images to (W x H)"),
         sg.Input("1920", size=(7, 1), key="InputWidth"),
         sg.Text("x"),
         sg.Input("1080", size=(7, 1), key="InputHeight")
         ],

        # Buttons with standard dimensions
        [sg.Button("720p", size=(5, 1)),
         sg.Button("1080p", size=(5, 1)),
         sg.Button("1440p", size=(5, 1)),
         sg.Button("4K", size=(5, 1)),
         sg.Button("8K", size=(5, 1))],
    ]

    layout = [
              [sg.Text(f"Source Folder".ljust(19)),
               sg.Input(os.getcwd()), sg.FolderBrowse()],
              [sg.Text("Destination Folder"),
               sg.Input(""), sg.FolderBrowse()],

              [sg.Frame("Select a new size for your images", dimensions_frame_layout)],

              [sg.OK("Start Converting", key="OK")],
              [sg.Cancel("Exit")],
              [sg.Multiline("Warning: \nAny files in the destination folder with the "
                            "same filename will be deleted without warning.",
                            size=(70, 5), disabled=True, key="FileList")],
              ]

    return sg.Window("Image Resizer").Layout(layout)


def event_loop():

    global window
    window = gui_layout()

    while True:
        button, values = window.Read(100)

        if button == "Exit" or values is None:
            break

        if button == "OK":  # This is the start converting button
            source = values[0]
            destination = values[1]
            width = int(values["InputWidth"])
            height = int(values["InputHeight"])
            new_size = (width, height)
            if destination == "":
                sg.popup_ok("You need to specify a destination path",
                            title="Destination Path")
            else:
                image_resize(source, destination, new_size)

        # If any of the "size" buttons are clicked, update the width and height text boxes
        # 720p = 1280 x 720
        # 1080p = 1920 x 1080
        # 1440p = 2560 x 1440
        # 4K or 2160p = 3840 x 2160
        # 8K or 4320p = 7680 x 4320

        if button == "720p":
            window.find_element("InputWidth").update("1280")
            window.find_element("InputHeight").update("720")
        elif button == "1080p":
            window.find_element("InputWidth").update("1920")
            window.find_element("InputHeight").update("1080")
        elif button == "1440p":
            window.find_element("InputWidth").update("2560")
            window.find_element("InputHeight").update("1440")
        elif button == "4K":
            window.find_element("InputWidth").update("3840")
            window.find_element("InputHeight").update("2160")
        elif button == "8K":
            window.find_element("InputWidth").update("7680")
            window.find_element("InputHeight").update("4320")


def main():
    event_loop()


if __name__ == "__main__":
    main()

# To do
# set width and height to numeric input only
# save last used source and destination path
