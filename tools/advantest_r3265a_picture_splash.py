from PIL import Image
from pymeasure.adapters import PrologixAdapter

file = "PALLASCATJPG.jpg"
img = Image.open(file)
size = 100
img = img.resize((size, size))
img.convert("1")
# img.show()

offset_x = 300
offset_y = 100


adv = PrologixAdapter("ASRL3::INSTR", 10)
adv.write("SCRATCH\r\n")
adv.write("LOAD START\r\n")
adv.write("OUTPUT 31;\"VS3\"\r\n")
adv.write("CLS 1\r\n")
counter = 0

program = (
    f"FOR X={offset_x+1} TO {offset_x+(size*3)} STEP 3\r\n"
           f"FOR Y={offset_y+1} TO {offset_y+(size*3)} STEP 3\r\n"
           "READ S\r\n"
           "GPOINT(S,X,Y)\r\n"
           "NEXT Y\r\n"
           "NEXT X\r\n")

data_max = 20
adv.write(program)

for x in range(size):
    data = ""
    data_str = "DATA "
    data_counter = 0
    for y in range(size):
        pixel = img.getpixel((x, y))
        px = 0
        if pixel != (255, 255, 255):
            px = 1

        data_str += str(px) + ","
        data_counter += 1

        if data_counter == data_max:
            data_counter = 0
            data += data_str[0:-1] + "\r\n"
            data_str = "DATA "

    adv.write(data[0:-1])
    counter += 1

adv.write("LOAD END\r\n")
