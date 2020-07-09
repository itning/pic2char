import binascii
import os
from PIL import Image


def char2bit(text_str):
    keys = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]
    target = []
    for x in range(len(text_str)):
        text = text_str[x]
        rect_list = [] * 16
        for i in range(16):
            rect_list.append([] * 16)
        gb2312 = text.encode('gb2312')
        hex_str = binascii.b2a_hex(gb2312)
        result = str(hex_str, encoding='utf-8')
        area = eval('0x' + result[:2]) - 0xA0
        index = eval('0x' + result[2:]) - 0xA0
        offset = (94 * (area - 1) + (index - 1)) * 32
        with open("HZK16", "rb") as f:
            f.seek(offset)
            font_rect = f.read(32)
        for k in range(len(font_rect) // 2):
            row_list = rect_list[k]
            for j in range(2):
                for i in range(8):
                    asc = font_rect[k * 2 + j]
                    flag = asc & keys[i]
                    row_list.append(flag)
        output = []
        for row in rect_list:
            for i in row:
                if i:
                    output.append('1')
                else:
                    output.append('0')
        target.append(''.join(output))
    return target


def head2char(work_space, images_path, rollback_image, lattice_data):
    # 将工作路径转移至头像文件夹
    os.chdir(images_path)
    # 获取文件夹内头像列表
    img_list = os.listdir(images_path)
    # 设置头像裁剪后尺寸
    each_size = 100
    # 变量n用于循环遍历头像图片，即当所需图片大于头像总数时，循环使用头像图片
    n = 0
    # 初始化颜色列表，用于背景着色
    color_list = ['#f8f8f8']
    # index用来改变不同字的背景颜色
    index = 0
    canvas_list = []
    # 每个item对应不同字的点阵信息
    for item in lattice_data:
        # 将工作路径转到头像所在文件夹
        os.chdir(images_path)
        # 新建一个带有背景色的画布，16*16点阵，每个点处填充2*2张头像图片，故长为16*2*100
        # 如果想要白色背景，将colorlist[index]改为'#FFFFFF'
        canvas = Image.new('RGB', (3200, 3200), color_list[index])  # 新建一块画布
        # 每个16*16点阵中的点，用四张100*100的头像来填充
        for i in range(16 * 16):
            # 点阵信息为1，即代表此处要显示头像来组字
            if item[i] == "1":
                # 循环读取连续的四张头像图片
                x1 = n % len(img_list)
                x2 = (n + 1) % len(img_list)
                x3 = (n + 2) % len(img_list)
                x4 = (n + 3) % len(img_list)
                # 以下四组try,将读取到的四张头像填充到画板上对应的一个点位置
                # 点阵处左上角图片1/4
                img = None
                try:
                    img = Image.open(img_list[x1])  # 打开图片
                except IOError:
                    print("有1张图片读取失败，已使用备用图像替代")
                    img = Image.open(rollback_image)
                finally:
                    img = img.resize((each_size, each_size), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, ((i % 16) * 2 * each_size, (i // 16) * 2 * each_size))  # 拼接图片
                # 点阵处右上角图片2/4
                try:
                    img = Image.open(img_list[x2])  # 打开图片
                except IOError:
                    print("有1张图片读取失败，已使用备用图像替代")
                    img = Image.open(rollback_image)
                finally:
                    img = img.resize((each_size, each_size), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, (((i % 16) * 2 + 1) * each_size, (i // 16) * 2 * each_size))  # 拼接图片
                # 点阵处左下角图片3/4
                try:
                    img = Image.open(img_list[x3])  # 打开图片
                except IOError:
                    print("有1张图片读取失败，已使用备用图像替代")
                    img = Image.open(rollback_image)
                finally:
                    img = img.resize((each_size, each_size), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, ((i % 16) * 2 * each_size, ((i // 16) * 2 + 1) * each_size))  # 拼接图片
                # 点阵处右下角图片4/4
                try:
                    img = Image.open(img_list[x4])  # 打开图片
                except IOError:
                    print("有1张图片读取失败，已使用备用图像替代")
                    img = Image.open(rollback_image)
                finally:
                    img = img.resize((each_size, each_size), Image.ANTIALIAS)  # 缩小图片
                    canvas.paste(img, (((i % 16) * 2 + 1) * each_size, ((i // 16) * 2 + 1) * each_size))  # 拼接图片
                # 调整n以读取后续图片
                n = (n + 4) % len(img_list)
        os.chdir(work_space)
        # 创建文件夹用于存储输出结果
        if not os.path.exists('{}_out'.format(user)):
            os.mkdir('{}_out'.format(user))
        os.chdir('{}_out'.format(user))
        canvas_list.append(canvas)
    width, height = canvas_list[0].size
    result = Image.new(canvas_list[0].mode, (width * len(canvas_list), height))
    for i, im in enumerate(canvas_list):
        result.paste(im, box=(i * width, 0))
    result.save('result.jpg', quality=100)


# fork from https://github.com/pengfexue2/pic2char
if __name__ == "__main__":
    # 将想转化的字赋给字符串
    src_text = "曹操出行"
    # 将字转化为汉字库的点阵数据
    lattices = char2bit(src_text)
    # 获取当前文件夹路径
    workspace = os.getcwd()
    # 用于拼接的图片所在文件夹名称
    user = "images"
    # 获取图片文件夹所在路径
    folder = "{}\\{}".format(workspace, user)
    # 若读取图片失败，用于替代的备用图片路径
    rollback = workspace + "\\" + "rollback.jpg"
    # 运行后将生成 user_输出 文件夹
    head2char(workspace, folder, rollback, lattices)
    print("success")
