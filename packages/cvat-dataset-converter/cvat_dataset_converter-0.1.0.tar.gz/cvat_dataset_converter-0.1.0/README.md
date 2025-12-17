# CVAT Dataset Converter Toolkit

This tool helps you to convert your CVAT datasets into other formats like YOLO, Pascal VOC, or TAO KITTI. Currently this only supports CVAT for images 1.1 format.

## Application Features

1. Convert labels only
This feature allows you to change the format of your annotations. You can convert from CVAT for images 1.1 to YOLO, Pascal VOC, or TAO KITTI. It does this without changing your images.

2. Resize and convert
You can use this to resize your images to a specific width and height. The application will also scale your annotations to match the new image size and convert them to the desired format.

3. Crop objects
You can use this to crop your labeled objects from the images. You can also add some padding around the objects if you want.

## Frontend

I have built the frontend using very simple tools.
1. HTML for the structure.
2. CSS for the styling.
3. JavaScript for the logic.

There are no complex frameworks used here. It is just simple and lightweight code.

## Backend

The backend API is designed to be simple and easy to use. It has three main parts.

1. Upload
You use this to send your dataset ZIP file and your settings. This starts the conversion job in the background.

2. Status
You can check this to see how your job is progressing. It will tell you when the job is running or finished.

3. Download
When your job is done, you can use this to get your result. It will give you a ZIP file with your converted data.