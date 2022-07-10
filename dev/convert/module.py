
def execute(image_path: str, format: str = "png", width: int = None, height: int = None):
    from PIL import Image
    try:
        print("Opening image...")
        result_kwargs = {}
        try:
            img = Image.open(image_path)
        except:
            print("Unable to open image")
            return
        if width and height:
            img = img.resize((width, height))
        elif width:
            img = img.resize((width, img.size[1]))
        elif height:
            img = img.resize((img.size[0], height))

        new_image_path = ".".join(image_path.split(".")[:-1]) + "." + format

        if format == "jpeg":
            img = img.convert("RGB")
        elif format == "ico":
            result_kwargs["sizes"] = []
            for size in [128, 256]:
                result_kwargs["sizes"].append((size, size))

        img.save(new_image_path, format=format, **result_kwargs)
        print("Image converted")
    except Exception as e:
        print("An error occurred while converting image")
        print("Error", e)


MODULE = execute
