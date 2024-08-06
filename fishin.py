import streamlit as st
import time
import random
import pandas as pd
import copy
from datetime import datetime
import json
import os

script_dir = os.oath.dirname(__file__)

USER_DATA_FILE = os.path.join(script_dir, "data", "users.json")
#USER_DATA_FILE = 'data/users.json'


def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    
    with open(USER_DATA_FILE, "r") as file:
        return json.load(file)

if "loaded_data" not in st.session_state:
    st.session_state.loaded_data = load_user_data()

def collect_data():
    fish_inventory = st.session_state.fish_inventory
    bait_inventory = st.session_state.bait_inventory
    wallet = st.session_state.wallet
    collection = st.session_state.collection

def save_user_data(user_data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

def add_user(username, password):
    user_data = load_user_data()
    user_data[username] = {"password" : password,
                           "data" : {
                                "fish_inventory" : st.session_state.fish_inventory,
                                "bait_inventory" : st.session_state.bait_inventory,
                                "wallet" : st.session_state.wallet,
                                "collection" : st.session_state.collection
                                }
                        }
    save_user_data(user_data)

def get_user_info(username, password):
    user_data = load_user_data()
    if username in user_data and user_data[username]["password"] == password:
        return user_data[username]["data"]
    return None







st.title("Let's go Fishin'!")
st.title("")

def random_number(min, max):
    random_number = random.randint(min, max)
    return random_number

if "wallet" not in st.session_state:
    st.session_state.wallet = 0

if "fish_inventory" not in st.session_state:
    st.session_state.fish_inventory = {}

fish = {
    #fish_name : (scale in cm, prize €/g, bait, place)
    "Sea Bass" : ([30, 100], 0.05, "shrimp", "coast"),
    "Carp" : ([30, 100], 0.01, "fly", "lake"),
    "Northern Pike" : ([40, 150], 0.04, "fish", "lake"),
    "Catfish" : ([100, 300], 0.04, "fish", "lake"),
    "Sole" : ([25, 50], 0.03, "worm", "coast"),
    "Bream" : ([20, 50], 0.04, "shrimp", "coast"),
    # Additional fish entries
    "Trout" : ([30, 80], 0.02, "worm", "river"),
    "Tuna" : ([100, 250], 0.10, "squid", "ocean"),
    "Mackerel" : ([20, 60], 0.03, "fish", "ocean"),
    "Halibut" : ([50, 200], 0.07, "squid", "coast"),
    "Red Snapper" : ([30, 80], 0.06, "shrimp", "ocean"),
    "Anglerfish" : ([40, 100], 0.08, "fish", "deep sea"),
    "Goldfish" : ([10, 20], 0.15, "bread", "pond"),
    "Grouper" : ([50, 150], 0.09, "squid", "reef"),
    "Pufferfish" : ([20, 50], 0.12, "shrimp", "reef"),
    "Swordfish" : ([100, 300], 0.11, "fish", "ocean"),
    "Clownfish" : ([5, 15], 0.20, "worm", "reef"),
    "Eel" : ([30, 70], 0.05, "fish", "river"),
}

rarities = {
    "common" : "gray",
    "uncommon" : "blue",
    "rare" : "purple",
    "epic" : "red",
    "mythical" : "orange"
}

rarity_upprice = {
    "common" : 1,
    "uncommon" : 1.5,
    "rare" : 2,
    "epic" : 3,
    "mythical" : 5
}

if "fish" not in st.session_state:
    st.session_state.fish = fish

if "locations" not in st.session_state:
    st.session_state.locations = set()
    for key, values in st.session_state["fish"].items():
        st.session_state["locations"].add(values[3])

if "bait" not in st.session_state:
    st.session_state.bait = set()
    for key, values in st.session_state["fish"].items():
        st.session_state["bait"].add(values[2])

if "bait_inventory" not in st.session_state:
    st.session_state.bait_inventory = {}
    random_start_bait = random_number(0, len(list(st.session_state["bait"]))-1)
    available_baits = list(st.session_state["bait"])
    st.session_state.bait_inventory[available_baits[random_start_bait]] = 5

if "bait_prices" not in st.session_state:
    st.session_state.bait_prices = {}
    for bait in list(st.session_state.bait):
        random_prize = round(random.uniform(2.5, 12.0), 2)
        st.session_state.bait_prices[bait] = random_prize

if "fish_counter" not in st.session_state:
    st.session_state["fish_counter"] = 1

def check_rarity(fish_name, fish_size):
    ratio = fish_size / st.session_state["fish"][fish_name][0][1]
    
    if ratio >= 0.98:
        return "mythical", rarities["mythical"], ratio
    elif ratio >= 0.95:
        return "epic", rarities["epic"], ratio 
    elif ratio >= 0.90:
        return "rare", rarities["rare"], ratio 
    elif ratio >= 0.70:
        return "uncommon", rarities["uncommon"], ratio 
    else:
        return "common", rarities["common"], ratio 

#add all baits to check if player has run out
def bait_warning():
    if st.session_state.bait_inventory == {}:
        return True
    bait_sum = 0
    for key, values in st.session_state.bait_inventory.items():
        bait_sum += values
    if bait_sum == 0:
        st.session_state.bait_inventory = {}
        return True
    else:
        return False

#find fish that live in current location
def fish_pool(location):
    active_fish_pool = []
    for key, values in st.session_state["fish"].items():
        if values[3] == location:
            active_fish_pool.append(key)
    return active_fish_pool

#generate random time in seconds for fish to bite
def bite_time():
    random_time = random_number(1, 30)
    return random_time

def generate_fish(active_fish, bait):
    baitable_fish = []
    for fish in active_fish:
        if st.session_state["fish"][fish][2] == bait:
            baitable_fish.append(fish)
    if baitable_fish == []:
        return False
    random_fish_number = random_number(0, len(baitable_fish)-1)
    hooked_fish = baitable_fish[random_fish_number]
    random_size = random.uniform(st.session_state["fish"][hooked_fish][0][0], st.session_state["fish"][hooked_fish][0][1])
    fish_size = round(random_size, 4)
    caught_fish = [hooked_fish, fish_size]
    return caught_fish

def fish_weight(fish_size):
    weight = fish_size * 0.035
    return weight

def fish_worth(fish_name, fish_weight):
    worth = st.session_state["fish"][fish_name][1] * fish_weight * 100
    return worth

def sell_fish(inventory):
    if inventory == {}:
        return False, False
    
    total_sum = 0
    sold_items = {}
    for key, values in inventory.items():
        total_sum += round(values[2], 2)
        #create dictionary for sold fishes
        if values[0] not in sold_items.keys():
            sold_items[values[0]] = 1
        else:
            sold_items[values[0]] += 1
    return total_sum, sold_items


def check_wallet():
    st.write(f"You currently have {st.session_state.wallet:.2f}€ in your account.")

def check_inventory():
    st.divider()
    #st.text(st.session_state.fish_inventory)

    st.subheader("Inventory:")

    if st.session_state["fish_inventory"] == {}:
        html_fish_list_content = '<li style="padding-left: 30px;">no fish caught yet.</li>'
    else:
        html_fish_list_content = ''
        for key, values in st.session_state.fish_inventory.items():
            html_fish_list_content += f'<li style="color: {values[3]}; padding-left: 30px;">{values[0]}: Size {values[1]:.2f}cm</li>'

    html_fish_list_shell = f'''
<ul>
    <li>Fish</li>
    <ul>
        {html_fish_list_content}
    </ul>
</ul>
'''
    st.markdown(html_fish_list_shell, unsafe_allow_html=True)

    if bait_warning():
        html_bait_list_content = '<li style="padding-left: 30px;">no bait left.</li>'
    else:
        html_bait_list_content = ''
        for key, values in st.session_state.bait_inventory.items():
            html_bait_list_content += f'<li style="padding-left: 30px;">{key}: {values}x</li>'


    html_bait_list_shell = f'''
<ul>
    <li>Bait</li>
    <ul>
        {html_bait_list_content}
    </ul>
</ul>
'''
    st.markdown(html_bait_list_shell, unsafe_allow_html=True)
    temporary_copy = copy.deepcopy(st.session_state.bait_inventory)
    for key, values in temporary_copy.items():
        if values == 0:
            del st.session_state.bait_inventory[key]


    st.divider()


if "collection" not in st.session_state:
    st.session_state.collection = {}
    for key, items in st.session_state.fish.items():
        st.session_state.collection[key] = None

if "stat_button_clicked" not in st.session_state:
    st.session_state.stat_button_clicked = None

if "rerun_check" not in st.session_state:
    st.session_state.rerun_check = False


if st.session_state.rerun_check == True:
    st.session_state.rerun_check = False
    st.rerun()


@st.dialog("Here are the infos on your catch!")
def see_collection_stats(fish_name):
    st.session_state.rerun_check = True
    fish_size = st.session_state.collection[fish_name][0]
    rarity = st.session_state.collection[fish_name][1]
    color = st.session_state.collection[fish_name][2]
    time_stamp = st.session_state.collection[fish_name][3]
    location = st.session_state.collection[fish_name][4]
    bait = st.session_state.collection[fish_name][5]
    weight = st.session_state.collection[fish_name][6]
    ratio = st.session_state.collection[fish_name][7]
    st.write(f"<h1 style='color: {color}; font-size: 50px'>{rarity} {fish_name}!</h1>", unsafe_allow_html=True)
    st.markdown(f"**Size:** *{fish_size:.2f}cm* out of possible {st.session_state.fish[fish_name][0][1]}cm, weighing *{weight:.2f}kg!*")
    st.markdown(f"**Rarity:** only *1 in {round(1/(1-round(ratio, 4)), 2)}* {fish_name} is bigger!")
    st.markdown(f"**Caught**: *{time_stamp}* at *{location}* with *{bait}*")
    st.session_state.stat_button_clicked = None
    if st.button("Go back fishin'", use_container_width=True):
        st.session_state.rerun_check = False
        st.rerun()

def check_collection():
    col1, col2 = st.columns(2, gap="small")
    i = 0
    for key, values in st.session_state["collection"].items():
        if i % 2 == 0:
            with col1:
                if values == None:
                    st.button(f"{key}", disabled=True, key=f"{key}_collection_button", use_container_width=True)
                else:
                    if st.button(f"{key}", type="primary", disabled=False, key=f"{key}_collection_button", use_container_width=True):
                        st.session_state.stat_button_clicked = key
        if i % 2 != 0:
            with col2:
                if values == None:
                    st.button(f"{key}", disabled=True, key=f"{key}_collection_button", use_container_width=True)
                else:
                    if st.button(f"{key}", type="primary", disabled=False, key=f"{key}_collection_button", use_container_width=True):
                        st.session_state.stat_button_clicked = key
        i += 1


@st.dialog("That's not gonna work..")
def fishing_error():
    st.title("You don't have any bait left.")
    st.markdown("Visit the local shop to buy more bait!")
    if st.button("understood", use_container_width=True):
        st.rerun()

@st.dialog("Good job! You caught:")
def congratulations(fish_name, fish_size, location, bait):
    time_stamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    rarity, color, ratio = check_rarity(fish_name, fish_size)
    st.write(f"<h1 style='color: {color}; font-size: 50px'>{rarity} {fish_name}!</h1>", unsafe_allow_html=True)
    weight = fish_weight(fish_size)
    st.markdown(f"it's {fish_size:.2f}cm big and weighs roughly {weight:.2f}kg.")
    one_in = round(1 / (1 - round(ratio, 4)), 2)
    st.markdown(f"That makes it a 1/{one_in} rare fish!")
    if st.button("Add to inventory", use_container_width=True, type="primary"):
        weight = fish_weight(fish_size)
        worth = fish_worth(fish_name, weight) * rarity_upprice[rarity]
        if st.session_state["collection"][fish_name] != None:
            if fish_size > st.session_state["collection"][fish_name][0]:
                st.session_state["collection"][fish_name] = [fish_size, rarity, color, time_stamp, location, bait, weight, ratio]
        else:
            st.session_state["collection"][fish_name] = [fish_size, rarity, color, time_stamp, location, bait, weight, ratio]

        st.session_state["fish_inventory"][st.session_state["fish_counter"]] = [fish_name, fish_size, worth, color, rarity]
        st.session_state["fish_counter"] += 1
        st.rerun()
    wikipedia_link = f"https://wikipedia.org/wiki/{fish_name}"
    wikipedia_link_button = st.link_button("Look up online!", wikipedia_link, use_container_width=True)

@st.dialog("Hmh. Nothing bit.")
def fail(bait):
    st.subheader(f"They don't seem to like your {bait} as bait.")
    st.write("Maybe try something else?")
    if st.button("understood", use_container_width=True):
        st.rerun()

@st.dialog("Local Fish Market")
def sell_action(total_sum, sold_items, inventory):
    if total_sum == False:
        st.subheader(f"You don't have any fish to sell!")
        st.write("")
        st.write("get out there and go get fishin'!")
        if st.button("understood", use_container_width=True):
            st.rerun()
    else:
        st.subheader("Inventory:")
        for key, values in inventory.items():
            st.markdown(f'**{values[0]}** *({values[4]})*: Size: {values[1]:.2f}cm, Worth *(x{rarity_upprice[values[4]]})*: {values[2]:.2f}€')
        st.write("")
        st.subheader(f"Do you want to sell")
        for key, values in sold_items.items():
            st.write(f"{values}x '{key}'")
        st.write("")
        st.write(f"for a total of {total_sum:.2f}€")
        if st.button("Add cash to my wallet", use_container_width=True, type="primary"):
            st.session_state["wallet"] += total_sum
            st.session_state["fish_inventory"] = {}
            st.session_state["fish_counter"] = 1
            st.rerun()
        if st.button("Leave Shop", type="secondary", use_container_width=True):
            st.rerun()
    
if "shopping_cart" not in st.session_state:
    st.session_state.shopping_cart = {bait : 0 for bait in st.session_state.bait_prices}

if "total_bait_price" not in st.session_state:
    st.session_state.total_bait_price = 0

def calculate_total_price():
    total = sum(st.session_state.shopping_cart[bait] * price for bait, price in st.session_state.bait_prices.items())
    st.session_state.total_bait_price = total


@st.dialog("Local Bait Shop")
def buy_action():
    con_1 = st.container()
    con_2 = st.container()
    
    #st.button(f"Your total is {st.session_state.total}€", disabled=True, use_container_width=True)
    for bait, price in list(st.session_state.bait_prices.items()):
        with con_1:
            st.session_state.shopping_cart[bait] = st.number_input(
                f"{bait}: {price}€/piece",
                min_value=0,
                step=1,
                key=f"{bait}_input",
                on_change=calculate_total_price()
            )
            calculate_total_price()
    with con_2:
        #st.text(st.session_state.shopping_cart)
        st.button(f"Your total is {st.session_state.total_bait_price:.2f}€", disabled=True, use_container_width=True)

    if st.session_state.wallet <= st.session_state.total_bait_price:
        check_out_button = st.button("Not enough funds", use_container_width=True, type="primary", disabled=True)
    else:
        check_out_button = st.button("Check out", use_container_width=True, type="primary")
    if check_out_button:
        for bait, number in st.session_state.shopping_cart.items():
            if number != 0:
                if bait in st.session_state.bait_inventory:
                    st.session_state.bait_inventory[bait] += number
                else:
                    st.session_state.bait_inventory[bait] = number
        
        st.session_state.wallet -= st.session_state.total_bait_price
        del st.session_state.total_bait_price
        del st.session_state.shopping_cart
        st.rerun()
    if st.button("Leave Shop", use_container_width=True, type="secondary"):
        st.rerun()

@st.dialog("Save your progress by signing up!")
def sign_up_action():
    con1 = st.container()
    con2 = st.container()
    with con1:
        col1, col2 = st.columns(2, gap="small")
        with col1:
            username_input = st.text_input("username")
        with col2:
            password_input = st.text_input("password", type="password")
    with con2:
        sign_up = st.button("Sign up now!", type="primary", use_container_width=True)
        leave_button = st.button("Maybe later", type="secondary", use_container_width=True)
    if leave_button:
        st.rerun()
    if sign_up:
        if username_input in st.session_state.loaded_data:
            with con1:
                st.error("The selected username already exists.")
        else:
            add_user(username_input, password_input)
            st.session_state.logged_in = username_input
            st.rerun()

#st.text(st.session_state.bait_inventory)

main_con_1 = st.container()
st.title("")
main_con_2 = st.container()

with main_con_1:
    con1_col1, con1_col2 = st.columns(2, gap = "large")
    
    with con1_col1:
        location_select = st.selectbox("Where are we headin'?", st.session_state.locations )
    
    with con1_col2:
        bait_select = st.selectbox("What bait we usin'?", st.session_state.bait_inventory)

#print which fish are at active_fish_pool
    available_fish = st.popover("Fish you can find here:", use_container_width=True)
    with available_fish:
        for fish_name in fish_pool(location_select):
            st.markdown(f"{fish_name}")

if "hook_thrown" not in st.session_state:
    st.session_state.hook_thrown = False
def click_hook():
    if bait_warning():
        fishing_error()
    else:
        st.session_state.hook_thrown = True


if "spinner_activate" not in st.session_state:
    st.session_state.spinner_activate = True

with main_con_2:
    start_fishing_button = st.button("Throw out line!", use_container_width=True, on_click=click_hook)
    if st.session_state.hook_thrown:
        hook_col_1, hook_col_2, hook_col_3 = st.columns([4, 2, 4])
        with hook_col_2:
            if st.session_state.spinner_activate == True:
                with st.spinner("Wait for fish to bite.."):
                    time.sleep(bite_time())
        hook_fish = st.button("REEL 'EM IN!", use_container_width=True, type="primary")
        st.session_state.spinner_activate = False
        if hook_fish:
            st.session_state.hook_thrown = False
            st.session_state.spinner_activate = True
            caught_fish = generate_fish(fish_pool(location_select), bait_select)
            st.session_state.bait_inventory[bait_select] -= 1
            if caught_fish != False:
                congratulations(caught_fish[0], caught_fish[1], location_select, bait_select)
            else:
                fail(bait_select)

sidebar = st.sidebar
with sidebar:
    login_con = st.container()
    side_con_1 = st.container(border=True)
    side_con_2 = st.container()

    #money_increase = st.button("+10")
    #if money_increase:
    #    add_money()

    #money_decrease = st.button("-5")
    #if money_decrease:
    #    sub_money()

    with side_con_2:

        collection_expander = st.expander("View Collection", expanded=False)
        with collection_expander:
            check_collection()
            if st.session_state.stat_button_clicked != None:
                see_collection_stats(st.session_state.stat_button_clicked)

        check_inventory()
        sell_fish_button = st.button("Sell fish at the market", type="primary", use_container_width=True)
        if sell_fish_button:
            total_sum, sold_items = sell_fish(st.session_state["fish_inventory"])
            sell_action(total_sum, sold_items, st.session_state.fish_inventory)
        bait_shop_button = st.button("Visit bait Shop", use_container_width=True)
        if bait_shop_button:
            buy_action()

        cheat_input = st.text_input("", label_visibility="collapsed")
        if cheat_input == "cheats_enabled True":
            st.session_state.cheats_enabled = True
        if cheat_input == "cheats_enabled False":
            st.session_state.cheats_enabled = False
        if cheat_input == "master_fisher":
            if bait_warning():
                fishing_error()
            else:
                st.session_state.bait_inventory[bait_select] -= 1
                caught_fish = generate_fish(fish_pool(location_select), bait_select)
                if caught_fish != False:
                    congratulations(caught_fish[0], caught_fish[1], location_select, bait_select)
                else:
                    fail(bait_select)
        if cheat_input == "master_baiter":
            for bait, price in list(st.session_state.bait_prices.items()):
                st.session_state.bait_inventory[bait] = 20
        if cheat_input == "gold_fisher":
            st.session_state.wallet += 100

    with login_con:
        if "logged_in" not in st.session_state:
            col_login, col_signup = st.columns(2, gap="small")
            with col_login:
                login_button = st.button("Log in", type="primary", use_container_width=True)
            with col_signup:
                signup_button = st.button("Sign up", type="secondary", use_container_width=True)
                if signup_button:
                    sign_up_action()
        else:
            login_info_button = st.button(f"Welcome back {st.session_state.logged_in}!", use_container_width=True)

    with side_con_1:
        check_wallet()

st.divider()

if "cheats_enabled" not in st.session_state:
    st.session_state.cheats_enabled = False

if st.session_state.cheats_enabled:
    bait_test = st.button("test bait", use_container_width=True)
    if bait_test:
        for bait, price in list(st.session_state.bait_prices.items()):
            st.session_state.bait_inventory[bait] = 20

    test = st.button("test fish", use_container_width=True)
    if test:
        if bait_warning():
            fishing_error()
        else:
            st.session_state.bait_inventory[bait_select] -= 1
            caught_fish = generate_fish(fish_pool(location_select), bait_select)
            if caught_fish != False:
                congratulations(caught_fish[0], caught_fish[1], location_select, bait_select)
            else:
                fail(bait_select)
