#! ./env/bin/python

"""Program that takes a set of images and generates histograms of the LAB values
of the images. The histograms are then saved to a CSV file for further analysis.
The program also generates a summary CSV file that contains the average LAB
values of the images and the difference between the pre-op and post-op images."""


from PIL import Image, ImageCms
import colorspacious as cs
import matplotlib.pyplot as plt
import termplotlib as tpl
from argparse import ArgumentParser
import csv


def map_lab_to_icc(lab_values):
    """Takes a given LAB value and maps it to the nearest ICC standard color"""
    # Take array of LAB values and map them to ICC standard colors
    # ICC standard colors are defined in the sRGB color space
    # Convert LAB to sRGB
    srgb_values = cs.cspace_convert(lab_values, start={"name": "CIELab"}, end={"name": "sRGB"})
    # Convert sRGB to ICC standard colors
    icc_values = cs.cspace_convert(srgb_values, start={"name": "sRGB"}, end={"name": "ICC"})
    return icc_values

def average_value_from_histogram(hist: list):
    """Returns the average value of the colors in the histogram."""
    num_pixels = float(sum(hist))
    weighted_sum = float(sum(i * hist[i] for i in range(len(hist))))
    weighted_avg = weighted_sum / num_pixels
    return weighted_avg

def lab_hist_weighed_average(hist):
    """Returns the weighed average of the LAB values in the histogram. Accounts
    for different representations of the different channels. L is 0-100, a and b
    are -128 to 127."""
    l_hist = hist[0]
    a_hist = hist[1]
    b_hist = hist[2]

    l_weighed_average = average_value_from_histogram(l_hist) / 2.55
    # The a and b channels should range from -128 to 127, but the histogram
    # values are from 0 to 255. We need to adjust the values to be centered
    a_weighed_average = average_value_from_histogram(a_hist) - 128
    b_weighed_average = average_value_from_histogram(b_hist) - 128

    return round(l_weighed_average, 2), round(a_weighed_average, 2), round(b_weighed_average, 2)

def image_to_lab_histogram(image_path:str) -> list:
    image = Image.open(image_path).convert('RGB')
    srgb_prof = ImageCms.createProfile('sRGB')
    lab_prof = ImageCms.createProfile('LAB', 6500)
    rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_prof, lab_prof, "RGB", "LAB")
    lab = ImageCms.applyTransform(image, rgb2lab)
    return [x.histogram() for x in lab.split()]

def generate_raw_output(prl: list, prr: list, pol: list, por: list, output_file: str) -> list:
    """Generates a CSV of the LAB histograms"""
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

def generate_final_report(prl: list, prr: list, pol: list, por: list, output_file: str) -> list:
    """Creates the averages output for usage in analysis"""
    fname=output_file+"_summary.csv"
    headers=["id", "desc", "avgL", "avgA", "avgB"]
    rows=[]
    id=1
    l, a, b = lab_hist_weighed_average(prl)
    rows.append([id, "Pre-op left-side", l, a, b])
    id+=1
    if pol and len(pol) > 0:
        prel, prea, preb = lab_hist_weighed_average(prr)
        for i in range(len(pol)):
            pol_h=pol[i]
            l, a, b = lab_hist_weighed_average(pol_h)
            rows.append([id, f"Post-op {i + 1} left-side", l, a, b])
            id+=1
            rows.append([id, f"Difference Post-op {i + 1} left-side vs Pre-op left side", l-prel, a-prea, b-preb])
            id+=1

    if prr and len(prr)>0:
        l, a, b = lab_hist_weighed_average(prr)
        rows.append([id, "Pre-op right-side", l, a, b])
        id+=1
    if por and len(por) > 0:
        prel, prea, preb = lab_hist_weighed_average(prr)
        for i in range(len(por)):
            por_h=por[i]
            l, a, b = lab_hist_weighed_average(por_h)
            rows.append([id, f"Post-op {i + 1} right-side", l, a, b])
            id+=1
            rows.append([id, f"Difference Post-op {i + 1} right-side vs Pre-op right side", l-prel, a-prea, b-preb])
            id+=1
    csv_file = open(fname, 'w')
    writer = csv.writer(csv_file)
    writer.writerow(headers)
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
    generate_raw_output(pre_l_hist, pre_r_hist, post_l_hist, post_r_hist, output)
    generate_final_report(pre_l_hist, pre_r_hist, post_l_hist, post_r_hist, output)

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