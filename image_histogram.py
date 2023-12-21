#! ./env/bin/python
from PIL import Image
import colorspacious as cs
import matplotlib.pyplot as plt
import termplotlib as tpl

def rgb_to_lab(rgb_values):
    lab_values = cs.cspace_convert(rgb_values, start={"name": "CIELab"}, end={"name": "CIELab"})
    return lab_values

def map_lab_to_icc(lab_values):
    # Implement your mapping logic to ICC standard colors here
    # This will depend on the specific ICC standard you are referring to
    # You might need additional libraries or specifications for ICC color mapping

    # Placeholder: return the input LAB values for now
    return lab_values

def image_to_histogram(image_path:str) -> list:
    image = Image.open(image_path)
    r,g,b = image.split()
    return [r.histogram(), g.histogram(), b.histogram()]

    return rgb_histogram

def main():
    image_path = "python.png"
    rgb_histograms = image_to_histogram(image_path)

    # Transform RGB values to LAB color space
    # lab_histograms = [rgb_to_lab((r, g, b)) for r, g, b in zip(rgb_histogram[0:256], rgb_histogram[256:512], rgb_histogram[512:])]

    # Map LAB values to ICC standard colors
    #icc_colors = [map_lab_to_icc(lab) for lab in lab_histogram]

    # Visualize the results or perform further processing as needed
    # Example: plot ICC colors
    # plt.scatter(range(len(icc_colors)), icc_colors, marker='.')
    # plt.show()
    print(rgb_histograms[0])

if __name__ == "__main__":
    main()