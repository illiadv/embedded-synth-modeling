import argparse
import os
import shutil
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=str, help="Input directory")
    parser.add_argument("output_dir", type=str, help="Output directory")
    return parser.parse_args()


def extract_metrics(input_dir: str, img_dir: str, audio_dir: str):
    table = list()
    images = list()
    audio = list()

    artifacts = list(filter(lambda s: s.startswith("output_"), os.listdir(input_dir)))
    artifacts.sort()
    for subdir in artifacts:
        metrics = dict()
        subdir_path = os.path.join(input_dir, subdir)
        if not os.path.isdir(subdir_path):
            print(f"Error: {subdir} is not a directory")
            exit(1)

        build_name = subdir[7:]
        metrics["name"] = build_name

        # Copy spectrum image into img_dir
        img_name = f"spectrum_{build_name}.png"
        src_img_path = os.path.join(subdir_path, img_name)
        if os.path.isfile(src_img_path):
            shutil.copy2(src_img_path, os.path.join(img_dir, img_name))
            images.append(img_name)

        # Copy audio files into audio_dir
        audio_name = f"audio_{build_name}.wav"
        src_audio_path = os.path.join(subdir_path, audio_name)
        if os.path.isfile(src_audio_path):
            shutil.copy2(src_audio_path, os.path.join(audio_dir, audio_name))
            audio.append(audio_name)

        metrics_file = os.path.join(subdir_path, f"metrics_{build_name}.txt")
        with open(metrics_file, "r") as f:
            for line in f.readlines():
                if "SNR_dB:" in line:
                    metrics["snr"] = line.split()[-1]
                if "THD_dB:" in line:
                    metrics["thd"] = line.split()[-1]
                if "THD_percent:" in line:
                    metrics["thd_p"] = line.split()[-1]
                if "THD+N_dB:" in line:
                    metrics["thd_n"] = line.split()[-1]
                if "Instructions:" in line:
                    metrics["inst_count"] = line.split()[-1]

        build_log = os.path.join(subdir_path, f"build_{build_name}.log")
        with open(build_log, "r") as f:
            for line in f.readlines():
                if "RAM:" in line:
                    metrics["ram"] = line.split()[1]
                if "FLASH:" in line:
                    metrics["flash"] = line.split()[1]

        table.append(metrics)
    return table, images, audio


def create_html_image_list(images):
    items = "\n".join(
        f"        <li>\n"
        f"          <p>{img}</p>\n"
        f"          <img src='img/{img}' alt='{img}'>\n"
        f"        </li>"
        for img in images
    )
    return f"      <ul>\n{items}\n      </ul>"


def create_html_table(metrics_table, audio_list):
    table = "<table id='metricsTable' border='1'>"
    table += """<thead><tr>
    <th>Build name</th>
    <th>Impl. name</th>
    <th>Sampling rate</th>
    <th>Optimization</th>
    <th>RAM</th>
    <th>FLASH</th>
    <th>Instructions</th>
    <th>SNR, dB</th>
    <th>THD, dB</th>
    <th>THD, %</th>
    <th>THD+N, dB</th>
    <th>Audio</th>
    </tr></thead>"""
    table += "<tbody>"

    for i, row in enumerate(metrics_table):
        build_name :str = row['name']
        flags = build_name.split('_')[-1]
        rate = build_name.split('_')[-2]
        impl_name = build_name[:(build_name.index(rate)-1)]
        html_row = "<tr>"
        html_row += f"<td><b>{build_name}</b></td>"
        html_row += f"<td><b>{impl_name}</b></td>"
        html_row += f"<td>{rate}</td>"
        html_row += f"<td>{flags}</td>"
        html_row += f"<td>{row['ram']}</td>"
        html_row += f"<td>{row['flash']}</td>"
        html_row += f"<td>{row['inst_count']}</td>"
        html_row += f"<td>{row['snr']}</td>"
        html_row += f"<td>{row['thd']}</td>"
        html_row += f"<td>{row['thd_p']}</td>"
        html_row += f"<td>{row['thd_n']}</td>"
        html_row += f"<td><audio controls><source src='audio/{audio_list[i]}' type='audio/wav'>Audio not supported</audio></td>"
        html_row += "</tr>"

        table += html_row

    table += "</tbody></table>"
    table += "</table>"

    return table

def create_html_doc(image_list_html, html_table):
    # Added inline CSS to show a pointer cursor and a small JS sorting script
    html_template = f"""<!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Report</title>
        <link rel="stylesheet" href="style.css">
        <style>
          th {{
            cursor: pointer;
            user-select: none;
            background-color: #f2f2f2;
          }}
          th:hover {{
            background-color: #ddd;
          }}
        </style>
      </head>
      <body>
        <h1>Modeling report</h1>
        <p>Created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <h2>Metrics</h2>
        {html_table}
        <h2>Spectrum plots</h2>
        {image_list_html}

      <script>
        document.querySelectorAll('#metricsTable th').forEach((header, colIndex) => {{
          header.addEventListener('click', () => {{
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const isAsc = header.dataset.asc !== "true";

            rows.sort((rowA, rowB) => {{
              const cellA = rowA.children[colIndex].innerText.trim();
              const cellB = rowB.children[colIndex].innerText.trim();

              const valA = parseFloat(cellA);
              const valB = parseFloat(cellB);

              // Sort numerically if both are valid numbers, otherwise sort alphabetically
              if (!isNaN(valA) && !isNaN(valB)) {{
                return isAsc ? valA - valB : valB - valA;
              }}
              return isAsc ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            }});

            // Toggle sort direction for next click
            table.querySelectorAll('th').forEach(th => delete th.dataset.asc);
            header.dataset.asc = isAsc;

            // Append reordered rows back to the table body
            rows.forEach(row => tbody.appendChild(row));
          }});
        }});
      </script>
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

    audio_dir = os.path.join(args.output_dir, "audio")

    if not os.path.isdir(audio_dir):
        os.mkdir(audio_dir)

    table, images, audio = extract_metrics(args.input_dir, img_dir, audio_dir)
    image_list_html = create_html_image_list(images)
    html_table = create_html_table(table, audio)
    document = create_html_doc(image_list_html, html_table)

    report_path = os.path.join(args.output_dir, "index.html")

    with open(report_path, "w") as out_file:
        out_file.write(document)


if __name__ == "__main__":
    main()
