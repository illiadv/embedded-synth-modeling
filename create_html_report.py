import argparse
import os

def parse_args():  
    parser = argparse.ArgumentParser()  
    parser.add_argument("input_dir", type=str, help="Input directory")  
    parser.add_argument("output_dir", type=str, help="Output directory")  
    return parser.parse_args()  

def extract_metrics(input_dir: str):

    table = list()

    artifacts = filter(lambda s: s.startswith("output_"), os.listdir(input_dir))
    for subdir in artifacts:
        metrics = dict()
        if not os.path.isdir(os.path.join(input_dir, subdir)):
            print(f"Error: {subdir} is not a directory")
            exit(1)

        build_name = subdir[7:]
        metrics["name"] = build_name

        metrics_file = os.path.join(input_dir, subdir, f"metrics_{build_name}.txt")
        with open(metrics_file, "r") as f:
            for line in f.readlines():
                if "SNR:" in line:
                    metrics["snr"] = line.split()[-1]
                if "Instructions:" in line:
                    metrics["inst_count"] = line.split()[-1]

        build_log = os.path.join(input_dir, subdir, f"build_{build_name}.log")
        with open(build_log, "r") as f:
            for line in f.readlines():
                if "RAM:" in line:
                    metrics["ram"] = line.split()[1]
                if "FLASH:" in line:
                    metrics["flash"] = line.split()[1]

        table.append(metrics)
    return table

def create_html_table(metrics_table):
    table = "<table border='1'>"
    table += "<tr><th>Build name</th><th>RAM</th><th>FLASH</th><th>Instructions</th><th>SNR</th></tr>"

    for row in metrics_table:
        html_row = "<tr>"
        html_row += f"<td><b>{row['name']}</b></td>"
        html_row += f"<td>{row['ram']}</td>"
        html_row += f"<td>{row['flash']}</td>"
        html_row += f"<td>{row['inst_count']}</td>"
        html_row += f"<td>{row['snr']}</td>"
        html_row += "</tr>"

        table += html_row

    table += "</table>"

    return table

def create_html_doc(html_table):
    html_template = f"""<!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Report</title>
        <link rel="stylesheet" href="style.css">
      </head>
      <body>
      {html_table}
      </body>
    </html>"""

    return html_template


def main():
    args = parse_args()
    if not os.path.isdir(args.input_dir):
        print(f"Error: {args.input_dir} is not a directory")
        exit(1)

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)

    img_dir = os.path.join(args.output_dir, "img")

    if not os.path.isdir(img_dir):
        os.mkdir(img_dir)

    table = extract_metrics(args.input_dir)
    html_table = create_html_table(table)
    document = create_html_doc(html_table)

    report_path = os.path.join(args.output_dir, "report.html")
    
    with open(report_path, "w") as out_file:
        out_file.write(document)


if __name__ == "__main__":
    main()
