#! ./env/bin/python
from PIL import Image, ImageCms
import colorspacious as cs
import matplotlib.pyplot as plt
import termplotlib as tpl
from argparse import ArgumentParser
import csv

def rgb_to_lab(rgb_values):
    lab_values = cs.cspace_convert(rgb_values, start={"name": "sRGB"}, end={"name": "CIELab"})
    return lab_values

def map_lab_to_icc(lab_values):
    # Implement your mapping logic to ICC standard colors here
    # This will depend on the specific ICC standard you are referring to
    # You might need additional libraries or specifications for ICC color mapping

    # Placeholder: return the input LAB values for now
    return lab_values

def image_to_lab_histogram(image_path:str) -> list:
    image = Image.open(image_path).convert('RGB')
    srgb_prof = ImageCms.createProfile('sRGB')
    lab_prof = ImageCms.createProfile('LAB')
    rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_prof, lab_prof, "RGB", "LAB")
    lab = ImageCms.applyTransform(image, rgb2lab)
    return [x.histogram() for x in lab.split()]

def raw_output(prl: list, prr: list, pol: list, por: list, output_file: str) -> list:
    header = ["pre_left_L", "pre_left_a", "pre_left_b"]
    rows=[]
    if prr and len(prr) > 0:
        header += ["pre_right_L", "pre_right_a", "pre_right_b"]
    if pol and len(pol) > 0:
        for i in range(len(pol)):
            header += [f"post_left_{i}_L", f"post_left_{i}_a", f"post_left_{i}_b"]
    if por and len(por) > 0:
        for i in range(len(por)):
            header += [f"post_right_{i}_L", f"post_right_{i}_a", f"post_right_{i}_b"]
    for i in range(len(prl[0])):
        row=[prl[0][i], prl[1][i], prl[2][i]]
        if prr and len(prr) > 0:
            row += [prr[0][i], prr[1][i], prr[2][i]]
        if pol and len(pol) > 0:
            for pol_img in pol:
                row += [pol_img[0][i], pol_img[1][i], pol_img[2][i]]
        if por and len(por) > 0:
            for por_img in por:
                row += [por_img[0][i], por_img[1][i], por_img[2][i]]
        rows.append(row)
    csv_file = open(output_file + ".csv", 'w')
    writer = csv.writer(csv_file)
    writer.writerow(header)
    writer.writerows(rows)
    csv_file.close()




def main(pre_l: str, pre_r: str, post_l: list, post_r: list, output: str):
    pre_l_hist, pre_r_hist, post_l_hist, post_r_hist = [], [], [], []
    pre_l_hist = image_to_lab_histogram(pre_l)
    if pre_r:
        pre_r_hist = image_to_lab_histogram(pre_r)
    if post_l:
        post_l_hist = [image_to_lab_histogram(x) for x in post_l]
    if post_r:
        post_r_hist = [image_to_lab_histogram(x) for x in post_r]
    raw_output(pre_l_hist, pre_r_hist, post_l_hist, post_r_hist, output)

    # Map LAB values to ICC standard colors
    #icc_colors = [map_lab_to_icc(lab) for lab in lab_histogram]

    # Visualize the results or perform further processing as needed
    # Example: plot ICC colors
    # plt.scatter(range(len(icc_colors)), icc_colors, marker='.')
    # plt.show()

if __name__ == "__main__":
    parser = ArgumentParser(description="")
    parser.add_argument("--preop-left",
        help="Left-side pre-op photograph",
        required=True)
    parser.add_argument("--output", "-o",
        help="Name to use for the output files. Should not include a file extension",
        required=True)
    parser.add_argument("--preop-right",
        help="Right-side pre-op photograph")
    parser.add_argument("--postop-left",
        nargs="+",
        help="Left-side post-op photographs.")
    parser.add_argument("--postop-right",
        nargs="+",
        help="Right-side post-op photographs")

    args = parser.parse_args()
    main(args.preop_left, args.preop_right, args.postop_left, args.postop_right, args.output)