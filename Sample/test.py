import base64

def convert(image):
    f = open(image)
    data = f.read()
    f.close()

    string = base64.b64encode(data)
    # print (string,'david')
    convert = base64.b64decode(string)

    t = open("example1.jpg", "w+")
    t.write(convert)
    t.close()

if __name__ == "__main__":
    convert("Obama.jpg")