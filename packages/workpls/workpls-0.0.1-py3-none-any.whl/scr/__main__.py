import argparse

cmd = argparse.ArgumentParser()

cmd.add_argument("-hello")
cmd.add_argument("-hello2")

comp = cmd.parse_args()

if comp.hello:
    print("hello")
elif comp.hello2:
    print("hello butt better")
else:
    print("uknown comman d")