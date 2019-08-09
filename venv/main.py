from PIL import Image, ImageFilter
import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

PLAYERX = 0
PLAYERY = 0
WALLS = []
STALACTITES = []

def draw_sprite(sprite, position, center_x, target):
    sprite = Image.open("bin/" + sprite + ".bmp")
    #offsets the position so that the "center" is in the center
    relative_pos = (position[0] - center_x + 400, position[1])
    # relative_pos = (position[0], position[1])
    box = (relative_pos[0], relative_pos[1], relative_pos[0] + 50, relative_pos[1] + 50)
    target.paste(sprite, box)
    return target



def receive_level(soc):

    conn, addr = soc.accept()
    wall_str = ''
    while True:
        data = conn.recv(4096)
        if not data:
            # print("end of received transmission")
            break
        else:
            wall_str = wall_str + data.decode()
    # print(received)
    conn.close()

    conn, addr = soc.accept()
    stalactite_str = ''
    while True:
        data = conn.recv(4096)
        if not data:
            # print("end of received transmission")
            break
        else:
            stalactite_str = stalactite_str + data.decode()

    wall_str = wall_str.split(",")
    stalactite_str = stalactite_str.split(",")

    # print(wall_str)
    # print(stalactite_str)

    walls = []
    for e in wall_str:
        if e and e != 'False':
            walls.append(int(e))

    stalactites = []
    for e in stalactite_str:
        if e:
            stalactites.append(int(e))

    return (walls, stalactites)

def parse_message(message_str):
    # message_str = message_str.decode()
    message_str = message_str.split(",")
    should_receive_level = False
    if message_str[2] == "True":
        should_receive_level = True
    message = (int(message_str[0]), int(message_str[1]), should_receive_level)
    # print(message)
    return message


def recive_update(soc):
    conn, addr = soc.accept()
    message = ''

    while True:
        data = conn.recv(4096)
        if not data:
            # print("end of received transmission")
            break
        else:
            message = message + data.decode()
    conn.close()

    PLAYERX, PLAYERY, level_incoming = parse_message(message)
    WALLS = []
    STALACTITES = []
    if level_incoming:
        WALLS, STALACTITES = receive_level(soc)
    return (PLAYERX, PLAYERY, WALLS, STALACTITES)

# def send_render()

def main():
    # //playerx, playery, walls, stalactites
    globalx = 0
    globaly = 0
    globalwall = []
    globalstalc = []


    # for i in range(400):
    #     render = draw_sprite("Stalactite", (i, 40+i), 10, background_img)

    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.bind((HOST, PORT))
    #     s.listen()
    #
    #     # The program loop
    #     while True:
    #         #recives the list
    #         conn, addr = s.accept()
    #         received = ''
    #         while True:
    #             data = conn.recv(4096)
    #             if not data:
    #                 print("end of received transmission")
    #                 break
    #             else:
    #                 received = received + str(data)
    #         print(received)
    #
    #         # sends the previous rendered file
    #         renderfile = open('render.bmp', 'rb')
    #         bytes = renderfile.read()
    #         # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         # s.connect((HOST, PORT))
    #         s.sendall(bytes)
    #         s.close()

            #parse the request
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:

            background_img = Image.open("background.bmp")

            returns = recive_update(s)
            globalx = returns[0]
            globaly= returns[1]
            if returns[2]:
                globalwall = returns[2]
                globalstalc = returns[3]

            print(globalx)
            # print("\n\n\n")

            #render the file
            # print(globalx, glo)
            f =open("render.bmp", "w")
            f.close()
            render = draw_sprite("Explorer", (globalx, globaly), globalx, background_img)
            for i in range(len(globalwall)//2):
                render = draw_sprite("CavePlatform", (globalwall[i*2], globalwall[i*2+1]), globalx, background_img)
            for i in range(len(globalstalc)//2):
                render = draw_sprite("Stalactite", (globalstalc[i*2], globalstalc[i*2+1]), globalx, background_img)
            # render.show()
            render.save("render.bmp")

            myfile = open('render.bmp', 'rb')
            bytes = myfile.read()
            # print(bytes)
            conn, addr = s.accept()
            conn.sendall(bytes)
            # print("Sent all")
            conn.close()

    # render.show()

if __name__ == "__main__":
    main()
