import socket
import math
import base64
import codecs
import time
import zlib

ircsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "irc.root-me.org"
port = 6667
channel = "#root-me_challenge"
username = "VoltK"
receiver = "candy"

ircsocket.connect((server, port))
ircsocket.send(bytes(f"USER {username} {username} {username} {username}\n", "UTF-8"))
ircsocket.send(bytes(f"NICK {username}\n", "UTF-8"))


def join_channel(channel):
    ircsocket.send(bytes(f"JOIN {channel}\n", "UTF-8"))
    ircmsg = ""
    while ircmsg.find("IP MODE") == -1:
        ircmsg = ircsocket.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip('\n\r')
        print("----------------Joining channel------------------")
        print(ircmsg)


def ping(message):
    ircsocket.send(bytes(f"PONG :{message[1]}\n", "UTF-8"))

def send_pm(msg, target=channel):
    print(f"Sending msg: {msg}")
    ircsocket.send(bytes(f"PRIVMSG {target} :{msg}\n", "UTF-8"))

def ep1(message):
    nums = list(map(int, message.split("/")))
    return round(math.sqrt(nums[0]) * nums[1], 2)

def ep2(message):
    return base64.b64decode(message).decode("UTF-8")

def ep3(message):
    return codecs.decode(message, "rot-13")

def ep4(message):
    # Because I decode all messages first in this challenge,
    # it's necessary to encode them back to bytes and then decode again and decompress =)
    return zlib.decompress(base64.decodebytes(message.encode())).decode("UTF-8")

def make_answer(answer):
    return f" -rep {answer}"

def main():
    join_channel(channel)

    levels = {"!ep1": "", "!ep2": "", "!ep3": "", "!ep4": ""}

    keys = list(levels.keys())
    keys.sort()

    for key in keys:
        msg = key

        while True:
            print("----------------WE ARE IN MAIN LOOP--------------")
            send_pm(msg, receiver)

            ircmsg = ircsocket.recv(2048).decode("UTF-8")
            ircmsg = ircmsg.strip('\n\r')
            print(ircmsg)

            # parse response in usable form
            if ircmsg.find("PRIVMSG") != -1:
                # get everything before ! and skip : at index 0
                name = ircmsg.split('!', 1)[0][1:]
                # use string after PRIVMSG and then split it to skip destination(username)
                message = ircmsg.split('PRIVMSG', 1)[1].split(':', 1)[1]
                print(f"{name}: {message}")

                if "BANNED" in message:
                    print("We got banned. Sleeping for 30 sec")
                    msg = key
                    time.sleep(30)
                    continue

                # Right answer is the last element in msg string
                if "You can validate the challenge" in message:
                    answer = message.split()[-1]
                    levels[key] = answer
                    break
                else:
                    if key == "!ep1":
                        if "/" in message:
                            msg += make_answer(ep1(message))
                    elif key == "!ep2":
                        msg += make_answer(ep2(message))
                    elif key == "!ep3":
                        msg += make_answer(ep3(message))
                    elif key == "!ep4":
                        msg += make_answer(ep4(message))
            # send PONG to confirm connection
            elif ircmsg.find("PING") != -1:
                ping(ircmsg)

    return levels

if __name__ == '__main__':
    levels = main()
    # sort and print answers
    print("\nANSWERS:")
    for key, value in sorted(levels.items(), key=lambda x: x[0]):
        print(f"{key} : {value}")

    # Close connection
    ircsocket.send(bytes("QUIT \n", "UTF-8"))