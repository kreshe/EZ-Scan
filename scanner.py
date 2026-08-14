import glob
import time

from evdev import InputDevice, ecodes


KEY_MAP = {

    "KEY_A":"A",
    "KEY_B":"B",
    "KEY_C":"C",
    "KEY_D":"D",
    "KEY_E":"E",
    "KEY_F":"F",
    "KEY_G":"G",
    "KEY_H":"H",
    "KEY_I":"I",
    "KEY_J":"J",
    "KEY_K":"K",
    "KEY_L":"L",
    "KEY_M":"M",
    "KEY_N":"N",
    "KEY_O":"O",
    "KEY_P":"P",
    "KEY_Q":"Q",
    "KEY_R":"R",
    "KEY_S":"S",
    "KEY_T":"T",
    "KEY_U":"U",
    "KEY_V":"V",
    "KEY_W":"W",
    "KEY_X":"X",
    "KEY_Y":"Y",
    "KEY_Z":"Z",


    "KEY_0":"0",
    "KEY_1":"1",
    "KEY_2":"2",
    "KEY_3":"3",
    "KEY_4":"4",
    "KEY_5":"5",
    "KEY_6":"6",
    "KEY_7":"7",
    "KEY_8":"8",
    "KEY_9":"9",


    "KEY_SPACE":" ",
    "KEY_MINUS":"-",
    "KEY_DOT":".",
    "KEY_COMMA":","

}

RU_TO_EN = {
    "а":"f",
    "б":",",
    "в":"d",
    "г":"u",
    "д":"l",
    "е":"t",
    "ё":"`",
    "ж":";",
    "з":"p",
    "и":"b",
    "й":"q",
    "к":"r",
    "л":"k",
    "м":"v",
    "н":"y",
    "о":"j",
    "п":"g",
    "р":"h",
    "с":"c",
    "т":"n",
    "у":"e",
    "ф":"a",
    "х":"[",
    "ц":"w",
    "ч":"x",
    "ш":"i",
    "щ":"o",
    "ъ":"]",
    "ы":"s",
    "ь":"m",
    "э":"'",
    "ю":".",
    "я":"z"
}


def fix_layout(text):

    result=""

    for char in text:

        low=char.lower()

        if low in RU_TO_EN:

            new=RU_TO_EN[low]

            if char.isupper():
                new=new.upper()

            result+=new

        else:
            result+=char


    return result

# русская раскладка -> английская

RU = """
йцукенгшщзхъ
фывапролджэ
ячсмитьбю
"""


EN = """
qwertyuiop[]
asdfghjkl;'
zxcvbnm,.
"""


RU_TO_EN={}


for r,e in zip(
        RU.replace("\n",""),
        EN.replace("\n","")
):

    RU_TO_EN[r]=e
    RU_TO_EN[r.upper()]=e.upper()



def fix_layout(text):

    result=""

    for c in text:

        if c in RU_TO_EN:
            result+=RU_TO_EN[c]

        else:
            result+=c


    return result



def normalize(text):

    text=fix_layout(text)

    text=text.upper()

    text=" ".join(
        text.split()
    )

    return text





def find_scanner():

    devices=glob.glob(
        "/dev/input/by-id/usb-Scanner_Scanner_20230429-event-kbd"
    )


    if devices:

        print(
            "Scanner:",
            devices[0]
        )

        return devices[0]


    return None





def read_scanner(callback):


    device=find_scanner()


    if not device:

        print(
            "Сканер не найден"
        )

        return



    dev=InputDevice(device)



    buffer=""



    print(
        "Ожидание QR..."
    )



    for event in dev.read_loop():


        if event.type != ecodes.EV_KEY:
            continue



        if event.value != 1:
            continue



        key=ecodes.KEY[event.code]



        if key=="KEY_ENTER":


            if buffer:


                code=normalize(
                    buffer
                )


                print(
                    "SCAN:",
                    code
                )


                callback(
                    code
                )


                buffer=""


        elif key in KEY_MAP:


            buffer+=KEY_MAP[key]



        time.sleep(0.001)
