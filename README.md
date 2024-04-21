# Building

## For linux, on linux
```bash
$ pyinstaller --onefile main.py
```
## For windows, on linux

1. Install wine
2. Use wine to install python for windows
3. Install PyInstaller under wine
4. Use PyInstaller to create the app

```bash
$ sudo zypper install wine
$ wget https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe
$ wine python-3.9.13-amd64.exe
$ wine python -m pip install -r requirements.txt
$ wine ~/.wine/drive_c/users/jeff/AppData/Local/Programs/Python/Python39-32/Scripts/pyinstaller.exe --onefile main.py
```


# image_histogram
The image_histogram module is a stand-alone CLI application for generating
histogram data about an image or set of images in the CIELAB color space. It
will provide a raw output of the histogram for the image(s), as well as a final
output with average values based on those histograms.

## Example usages

### Single Image
When only a single image is passed, the output will indicate that this image is
the 'pre-operative left side' image. The tool was written to allow for
comparison between left and right side post-operative bruising, and the outputs
reflect this. No special processing is done here; it is only a textual
consideration

```bash
$ python image_histogram.py -p path-to-image -o output-name
```

This command will generate two output files:

**output-name_summary.csv**

Calculated averages for the channels. 
|id|desc|avgL|avgA|avgB|
|--|----|----|----|----|
|1|Pre-op left-side|38.35|14.0|9.74|

The averages for the a and b channels are calculated by multiplying the value in
each bucket of the histogram by that bucket's index. This number is then divided
by the total number of pixels to get the average value. Both channels have
values ranging from -128 to 127, but the index values will be between 0 and
255. To get the actual average value then, we subtract 128 from the initial
result.

The l chanel should have a value between 0 and 100, but again our histogram has
index values between 0 and 255. To get the desired l value then, we take the
initial average and then divide by 2.55.

**output-name.csv**

The raw histogram data for each channel:
|pre_left_L|pre_left_a|pre_left_b|
|----------|----------|----------|
|0|0|0|

### Complete Patient Image Collection
Running the script for a complete set of patient operative photographs,
including photos pre-operatively as well as on days 1 and 7 post-operative. 

```bash
$ python image_histogram.py \
> --preop-left test_images/PreOpLeft.png \
> --preop-right test_images/PreOpRight.png \
> --postop-left test_images/PostOpDay1Left.png test_images/PostOpDay7Left.png \
> --postop-right test_images/PostOpDay1Right.png test_images/PostOpDay7Right.png \
> --output patient_12345
```

**patient_12345_summary.csv**

Here we have added additional comparisons between the post-op photos and the
pre-op photo. Post-operative photos are simply labled by the order they are
passed in, which is why it is essential that the order is consistent between the
left and the right side. The comparisons are included here for convenience, but
can easyl be calculated from the values provided.
|id|desc|avgL|avgA|avgB|
|--|----|----|----|----|
|1|Pre-op left-side|38.36|14.01|9.75|
|2|Post-op 1 left-side|36.96|16.7|8.13|
|3|Difference Post-op 1 left-side vs Pre-op left side|-3.49|1.31|-6.72|
|4|Post-op 2 left-side|37.34|15.72|11.6|
|5|Difference Post-op 2 left-side vs Pre-op left side|-3.11|0.33|-3.25|
|6|Pre-op right-side|40.45|15.39|14.85|
|7|Post-op 1 right-side|40.83|16.34|7.7|
|8|Difference Post-op 1 right-side vs Pre-op right side|0.38|0.95|-7.15|
|9|Post-op 2 right-side|38.55|14.69|11.53|
|10|Difference Post-op 2 right-side vs Pre-op right side|-1.90|-0.70|-3.32|
