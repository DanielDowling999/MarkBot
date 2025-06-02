import time

#Uses the MGBA API to send inputs directly to the console.
def press_button(client, button, n_times=1, delay=1):
    for i in range(n_times):
        #sockettest.send(button)
        client.send_command(button)
        time.sleep(delay)

def press_up(client, n_times=1):
    press_button(client, "pressUp", n_times)

def press_down(client, n_times=1):
    press_button(client, "pressDown", n_times)

def press_left(client, n_times=1):
    press_button(client, "pressLeft", n_times)

def press_right(client, n_times=1):
    press_button(client, "pressRight", n_times)

def press_a(client, n_times=1):
    press_button(client, "pressA", n_times)

def press_b(client, n_times=1):
    press_button(client, "pressB", n_times)

def press_l(client, n_times=1):
    press_button(client, "pressL", n_times)

def press_r(client, n_times=1):
    press_button(client, "pressR", n_times)

def press_sel(client, n_times=1):
    press_button(client, "pressSelect", n_times)

def press_start(client, n_times=1):
    press_button(client, "pressStart", n_times)

# Helper function that allows the bot to easily select the next character.
# Press L will highlight the next unit, and press a will select them


def next_unit(client):
    press_l(client)
    press_a(client)

# Each attack requires 3 a presses. One to confirm an attack. One to select a weapon.
# one to select an enemy. This function will not stay in this form.


def attack(client):
    press_a(client, 3)
    time.sleep(10)

# end move function. pressing up at the start of menuing will always bring you to the bottom of
# the menu provided no inputs get eaten


def end_move(client):
    press_up(client)
    press_a(client)


def end_turn(client):
    press_up(client)
    press_a(client)
    press_up(client)
    press_a(client)
