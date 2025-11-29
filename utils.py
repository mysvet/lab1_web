from PIL import Image, ImageDraw
import numpy as np
import matplotlib
matplotlib.use('Agg')  # важно для Windows!
import matplotlib.pyplot as plt

from PIL import Image, ImageDraw

def draw_cross(input_path, output_path, orientation, color):
    """
    Рисует "настоящий" крест:
    - Вертикальный крест: длинная вертикальная линия (на всю высоту) +
                          короткая горизонтальная (например, 1/3 ширины)
    - Горизонтальный крест: длинная горизонтальная линия (на всю ширину) +
                            короткая вертикальная (например, 1/3 высоты)
    """
    img = Image.open(input_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Толщина линий — 2% от минимальной стороны
    thickness = max(1, int(min(w, h) * 0.02))

    if orientation == 'vertical':
        # Длинная вертикальная линия (на всю высоту)
        x1 = w // 2 - thickness // 2
        x2 = x1 + thickness
        draw.rectangle([x1, 0, x2, h], fill=color)

        # Короткая горизонтальная линия (1/3 ширины, по центру)
        short_w = w // 3
        y1 = h // 2 - thickness // 2
        y2 = y1 + thickness
        hx1 = (w - short_w) // 2
        hx2 = hx1 + short_w
        draw.rectangle([hx1, y1, hx2, y2], fill=color)

    else:  # orientation == 'horizontal'
        # Длинная горизонтальная линия (на всю ширину)
        y1 = h // 2 - thickness // 2
        y2 = y1 + thickness
        draw.rectangle([0, y1, w, y2], fill=color)

        # Короткая вертикальная линия (1/3 высоты, по центру)
        short_h = h // 3
        x1 = w // 2 - thickness // 2
        x2 = x1 + thickness
        vy1 = (h - short_h) // 2
        vy2 = vy1 + short_h
        draw.rectangle([x1, vy1, x2, vy2], fill=color)

    img.save(output_path)

def plot_histograms(orig_path, proc_path, hist_orig_path, hist_proc_path):
    def get_hist(img_path):
        img = np.array(Image.open(img_path).convert('RGB'))
        r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        return r.flatten(), g.flatten(), b.flatten()

    plt.figure(figsize=(6, 3))
    r, g, b = get_hist(orig_path)
    plt.hist(r, bins=256, color='red', alpha=0.5, label='R')
    plt.hist(g, bins=256, color='green', alpha=0.5, label='G')
    plt.hist(b, bins=256, color='blue', alpha=0.5, label='B')
    plt.title('Исходное')
    plt.legend()
    plt.tight_layout()
    plt.savefig(hist_orig_path + '.png')
    plt.close()

    plt.figure(figsize=(6, 3))
    r, g, b = get_hist(proc_path)
    plt.hist(r, bins=256, color='red', alpha=0.5)
    plt.hist(g, bins=256, color='green', alpha=0.5)
    plt.hist(b, bins=256, color='blue', alpha=0.5)
    plt.title('После наложения креста')
    plt.tight_layout()
    plt.savefig(hist_proc_path + '.png')
    plt.close()
