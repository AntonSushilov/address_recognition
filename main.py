import os
import glob
from pdf2image import convert_from_path
import pytesseract
import cv2

poppler_path = "poppler-0.68.0\\bin"
pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR\\tesseract.exe'


def dir_pdf(input_dir, img_dirs, main_dir):
    for file in os.listdir(input_dir):
        print(file)
        img_dir = os.path.join(img_dirs, file.split(".")[0])
        os.mkdir(img_dir)
        pdf_to_image(input_dir, file, img_dir, main_dir)


def pdf_to_image(input_dir, file, img_dir, main_dir):
    input_file = os.path.join(input_dir, file)
    pages = convert_from_path(input_file, 350, poppler_path=poppler_path)

    for i, page in enumerate(pages):
        image_name = file.split(".")[0] + "_page " + str(i+1) + ".jpg"
        page.save(os.path.join(img_dir, image_name), "JPEG")
    res_dir = os.path.join(main_dir, "words")
    image_to_text(img_dir, res_dir, file)


def image_to_text(img_dir, output_dir, file):
    name = file.split(".")[0] + '.txt'
    files = len(os.listdir(img_dir))
    dir_name = os.path.split(img_dir)[-1]
    files = [dir_name + "_page " + str(i + 1) + ".jpg" for i in range(files)]
    for file in files:
        image = os.path.join(img_dir, file)
        img = cv2.imread(image)
        # percent by which the image is resized
        scale_percent = 50
        # calculate the 50 percent of original dimensions
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        # dsize
        dsize = (width, height)
        # resize image
        small_img = cv2.resize(img, dsize)
        crop_img = small_img[300:400, 220:1400]
        #cv2.imshow("address", crop_img)
        #cv2.waitKey(0)
        img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
        config = r'--oem 3 --psm 6 -c page_separator='''
        text = pytesseract.image_to_string(img, lang='rus', config=config).replace("\n", " ").strip()
        text = text.split(",")
        text = text[1:]
        for i, t in enumerate(text):
            t = t.strip().split(" ")
            print(t)
            if len(t) > 1:
                if t[1] == "р-н" or t[1] == "обл" or t[0] == "дом" or t[0] == "корпус":
                    continue
                else:
                    t.insert(0, t.pop())
                    t[0] = t[0] + "."
                    text[i] = " ".join(t)
        text = ", ".join(text)
        text = file + "+" + text.strip().replace("  ", " ")
        print(text)
        path = os.path.join(output_dir, name)
        f = open(path, 'a')
        f.writelines(text + "\n")
        f.close()


def main():
    main_dir = os.getcwd()
    input_dir = os.path.join(main_dir, "pdfs")
    img_dir = os.path.join(main_dir, "img")
    dir_pdf(input_dir, img_dir, main_dir)
    dirs = glob.glob(os.path.join(img_dir, r'*'))
    for i in dirs:
        files = glob.glob(os.path.join(i, r'*'))
        for j in files:
            os.remove(j)
        os.rmdir(i)


if __name__ == '__main__':
    main()


