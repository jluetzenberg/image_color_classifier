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

def hist_weighed_average(hist):
    """returns weighted averages of the colors in the histogram. based on https://stackoverflow.com/questions/7563315/how-to-loop-over-histogram-to-get-the-color-of-the-picture/7564929#7564929"""
    red_hist = hist[0]
    green_hist = hist[1]
    blue_hist = hist[2]

    red_weighed_sum = float(sum(i * red_hist[i] for i in range(len(red_hist))))
    green_weighed_sum = float(sum(i * green_hist[i] for i in range(len(green_hist))))
    blue_weighed_sum = float(sum(i * blue_hist[i] for i in range(len(blue_hist))))

    red_num_pixels = float(sum(red_hist))
    green_num_pixels = float(sum(green_hist))
    blue_num_pixels = float(sum(blue_hist))

    red_weighed_average = red_weighed_sum / red_num_pixels
    green_weighed_average = green_weighed_sum / green_num_pixels
    blue_weighed_average = blue_weighed_sum / blue_num_pixels
    return red_weighed_average, green_weighed_average, blue_weighed_average

def image_to_lab_histogram(image_path:str) -> list:
    image = Image.open(image_path).convert('RGB')
    srgb_prof = ImageCms.createProfile('sRGB')
    lab_prof = ImageCms.createProfile('LAB')
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
    l, a, b = hist_weighed_average(prl)
    rows.append([id, "Pre-op left-side", l, a, b])
    id+=1
    if pol and len(pol) > 0:
        prel, prea, preb = hist_weighed_average(prr)
        for i in range(len(pol)):
            pol_h=pol[i]
            l, a, b = hist_weighed_average(pol_h)
            rows.append([id, f"Post-op {i + 1} left-side", l, a, b])
            id+=1
            rows.append([id, f"Difference Post-op {i + 1} left-side vs Pre-op left side", l-prel, a-prea, b-preb])
            id+=1

    if prr and len(prr)>0:
        l, a, b = hist_weighed_average(prr)
        rows.append([id, "Pre-op right-side", l, a, b])
        id+=1
    if por and len(por) > 0:
        prel, prea, preb = hist_weighed_average(prr)
        for i in range(len(por)):
            por_h=por[i]
            l, a, b = hist_weighed_average(por_h)
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