import hmac
import hashlib
import random
import time
import string
import sys
import random
from tkinter import Tk,Frame,Button,Label,RIGHT,BOTTOM,CENTER
from os import system
from pandas.io.formats.style import Styler
from IPython.display import clear_output
from PIL import Image, ImageTk, ImageFile

def to_superscript(num):
    superscript_map = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
        '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    }
    return ''.join(superscript_map.get(char, char) for char in str(num))

def sha256_encrypt(input_string: str) -> str:
    # Create a sha256 hash object
    sha256_hash = hashlib.sha256()
    
    # Update the hash object with the bytes of the input string
    sha256_hash.update(input_string.encode('utf-8'))
    
    # Return the hexadecimal representation of the hash
    return sha256_hash.hexdigest()

def generate_server_seed():
    possible_characters:str = string.hexdigits
    seed:str = "".join([random.choice(possible_characters) for _ in range(64)])
    return seed

def generate_client_seed():
    possible_characters:str = string.hexdigits
    seed:str = "".join([random.choice(possible_characters) for _ in range(20)])
    return seed

def seeds_to_hexadecimals(server_seed:str,client_seed:str,nonce:int) -> list[str]:
    messages:list[str] = [f"{client_seed}:{nonce}:{x}" for x in range(2)]
    hmac_objs:list[hmac.HMAC] = [hmac.new(server_seed.encode(),message.encode(),hashlib.sha256) for message in messages]
    return [hmac_obj.hexdigest() for hmac_obj in hmac_objs]

def hexadecimal_to_bytes(hexadecimal:str) -> list[int]:
    return list(bytes.fromhex(hexadecimal))

def bytes_to_basic_number(bytes_list: list[int]) -> int:
    # Calculate a weighted index based on the first four bytes
    number:float = ((float(bytes_list[0]) / float(256**1)) +
              (float(bytes_list[1]) / float(256**2)) +
              (float(bytes_list[2]) / float(256**3)) +
              (float(bytes_list[3]) / float(256**4)))
    return number

def bytes_to_number(bytes_list: list[int], weights: list[float]) -> int:
    # Calculate a weighted index based on the first four bytes
    number:float = ((float(bytes_list[0]) / float(256**1)) +
              (float(bytes_list[1]) / float(256**2)) +
              (float(bytes_list[2]) / float(256**3)) +
              (float(bytes_list[3]) / float(256**4)))
    
    cumulative_weights:list[float] = [sum(weights[:i+1]) for i in range(len(weights))]
    total_weight:float = cumulative_weights[-1]
    weighted_number:float = number * total_weight
    
    for i, weight in enumerate(cumulative_weights):
        if weighted_number <= weight:
            return i
    return len(weights) - 1

def seeds_to_results(server_seed:str,client_seed:str,nonce:int) -> list[list[str]]:
    prizes:list[str] = ['cherry.jpg', 'lemon.jpg', 'bell.jpg', 'clover.jpg', 'diamond.jpg', 'star.jpg', 'caterpillar.jpg', 'butterfly.jpg']
    weights:list[float] = [0.2, 0.18, 0.15, 0.13, 0.12, 0.1, 0.07, 0.05]
    hexs = seeds_to_hexadecimals(server_seed=server_seed,client_seed=client_seed,nonce=nonce)
    bytes_lists:list[list[int]] = [hexadecimal_to_bytes(current_hex) for current_hex in hexs]
    rows:list[list[int]] = []
    current_row:list[int] = []
    for bytes_list in bytes_lists:
        for index in range(0,len(bytes_list),4):
            if(len(current_row)==3):
                rows.append(current_row.copy())
                current_row.clear()
            current_row.append(prizes[bytes_to_number(bytes_list[index:index+4],weights)])
            if(index==4 and bytes_lists.index(bytes_list)==len(bytes_lists)-1):
                break
    return rows

def spin_wheel() -> list[list[str]]:
    symbols:list[str] = ['cherry.jpg', 'lemon.jpg', 'bell.jpg', 'clover.jpg', 'diamond.jpg', 'star.jpg', 'caterpillar.jpg', 'butterfly.jpg', 'angel_butterfly.jpg']
    return [random.choices(symbols,k=3),random.choices(symbols,k=3),random.choices(symbols,k=3)]

def spin(slot_labels:list[Label]):
    slots = ['cherry.jpg', 'lemon.jpg', 'bell.jpg', 'clover.jpg', 'diamond.jpg', 'star.jpg', 'caterpillar.jpg', 'butterfly.jpg', 'angel_butterfly.jpg']
    result = [random.choice(slots) for _ in range(9)]
    for idx, label in enumerate(slot_labels):
        img = Image.open(result[idx])
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        label.config(image=tk_img)
        label.image = tk_img  # Keep a reference to prevent garbage collection

def spin_animation(slot_labels:list[Label], end_time:float, root:Tk):
    if time.time() < end_time:
        spin(slot_labels)
        root.after(100, spin_animation, slot_labels, end_time, root)

def check_for_wins(rows:list[list[str]]) -> list[str]:
    wins = []
    # icons = ["🍒", "🍋", "🔔", "🍀", "💎", "⭐", "🐛", "🦋"]
    # Check rows for 3 in a row
    for i in range(3):
        if rows[i][0] == rows[i][1] == rows[i][2]:  # If all three in the row are the same
            symbol = rows[i][0]
            wins.append(symbol)
            
    for i in range(3):
        if rows[0][i] == rows[1][i] == rows[2][i]:  # If all three in the column are the same
            symbol = rows[0][i]
            wins.append(symbol)
    
    # Check diagonals for 3 in a row
    if rows[0][0] == rows[1][1] == rows[2][2]:  # Top-left to bottom-right
        symbol = rows[0][0]
        wins.append(symbol)
    
    if rows[0][2] == rows[1][1] == rows[2][0]:  # Top-right to bottom-left
        symbol = rows[0][2]
        wins.append(symbol)

    return wins

def check_for_wins_receipt(rows:list[list[str]]) -> list[str]:
    wins = []
    icons = ['cherry.jpg', 'lemon.jpg', 'bell.jpg', 'clover.jpg', 'diamond.jpg', 'star.jpg', 'caterpillar.jpg', 'butterfly.jpg', 'angel_butterfly.jpg']
    multipliers:list[int] = [4, 5, 7, 10, 15, 25, 40, 100]
    # Check rows for 3 in a row
    for i in range(3):
        if rows[i][0] == rows[i][1] == rows[i][2]:  # If all three in the row are the same
            symbol = rows[i][0]
            wins.append(f"Row {i+1} contains 3 {symbol} in a row. Increase multiplier by {multipliers[icons.index(symbol)]}")
    
    # Check diagonals for 3 in a row
    if rows[0][0] == rows[1][1] == rows[2][2]:  # Top-left to bottom-right
        symbol = rows[0][0]
        wins.append(f"Diagonal from top left to bottom right contains 3 {symbol} in a row. Increase multiplier by {multipliers[icons.index(symbol)]}")
    
    if rows[0][2] == rows[1][1] == rows[2][0]:  # Top-right to bottom-left
        symbol = rows[0][2]
        wins.append(f"Diagonal from bottom left to top right contains 3 {symbol} in a row. Increase multiplier by {multipliers[icons.index(symbol)]}")
    
    if len(wins)>0:
        return wins
    return ["No winning combinations. Multiplier set to 0."]

def calculate_winnings(wins:list[str],bet_amount:int) -> int:
    icons = ['cherry.jpg', 'lemon.jpg', 'bell.jpg', 'clover.jpg', 'diamond.jpg', 'star.jpg', 'caterpillar.jpg', 'butterfly.jpg', 'angel_butterfly.jpg']
    multipliers:list[float] = [1.3, 2.25, 3.00, 5.00, 10.0, 25,  50.0, 125.0, 5000]
    total_winnings = 0
    
    for win in wins:
        # Find the index of the win symbol in the icons list
        index = icons.index(win)
        total_winnings += multipliers[index]
    
    return int(total_winnings*bet_amount)

def increase_credits(target_balance: int, current_balance: int, increment: int, root: Tk, label: Label):
    global bet_amount
    """
    Smoothly increase the balance displayed on the screen.
    """
    if current_balance < target_balance:
        current_balance += increment
        if current_balance > target_balance:
            current_balance = target_balance
        try:
            label.config(text=f"Credits per Spin: {bet_amount:,}\tCredits: {int(current_balance):,}")
            root.after(30, increase_credits, target_balance, current_balance, increment, root, label)  # Delay for smooth animation
        except:
            pass
    else:
        label.config(text=f"Credits per Spin: {bet_amount:,}\tCredits: {int(current_balance):,}")

def provably_fair_calculation_receipt(server_seed:str,client_seed:str,nonce:int,bet_amount:int) -> str:
    icons = ["🍒", "🍋", "🔔", "🍀", "💎", "⭐", "🐛", "🦋","🦋🦋"]
    pictures = ['cherry.jpg', 'lemon.jpg', 'bell.jpg', 'clover.jpg', 'diamond.jpg', 'star.jpg', 'caterpillar.jpg', 'butterfly.jpg', 'angel_butterfly.jpg']
    spin_result:Styler = seeds_to_results(server_seed,client_seed,nonce)
    weights:list[float] = [0.2, 0.18, 0.15, 0.13, 0.12, 0.1, 0.07, 0.045, 0.005]
    multipliers:list[float] = [1.3, 2.25, 3.00, 5.00, 10.0, 25.0, 50.0, 125.0, 5000]
    first_hex:str = seeds_to_hexadecimals(server_seed,client_seed,nonce)[0]
    second_hex:str = seeds_to_hexadecimals(server_seed,client_seed,nonce)[1]
    first_bytes:list[int] = hexadecimal_to_bytes(first_hex)
    second_bytes:list[int] = hexadecimal_to_bytes(second_hex)
    numbers:list[int] = [
            bytes_to_number(first_bytes[0:4],weights),
            bytes_to_number(first_bytes[4:8],weights),
            bytes_to_number(first_bytes[8:12],weights),
            bytes_to_number(first_bytes[12:16],weights),
            bytes_to_number(first_bytes[16:20],weights),
            bytes_to_number(first_bytes[20:24],weights),
            bytes_to_number(first_bytes[24:28],weights),
            bytes_to_number(first_bytes[28:32],weights),
            bytes_to_number(second_bytes[0:4],weights),
        ]
    if True:
        output:str = f"Fluttering Riches has been created for fun and fair entertainment. Every single outcome can be verified and reverse engineered. An example is provided below. To start, know that these are the icons and getting 3 in a row of any of these result in payout multiplier increases by the given amounts:\n"
        output += f"\t0 -> 🍒 -> x{multipliers[0]},\n\t1 -> 🍋 -> x{multipliers[1]},\n\t2 -> 🔔 -> x{multipliers[2]},\n\t3 -> 🍀 -> x{multipliers[3]},\n\t4 -> 💎 -> x{multipliers[4]},\n\t5 -> ⭐ -> x{multipliers[5]},\n\t6 -> 🐛 -> x{multipliers[6]},\n\t7 -> 🦋 -> x{multipliers[7]}\n\t7 -> 🦋🦋 -> x{multipliers[8]}\n"
        output += f"The maximum number of ways to win in a single spin is 5 (3 in a row horizontally across, and 3 in a row diagonally). Your multiplier increases when you have 3 in a row going across, and diagonally. Getting 3 in a row vertically does NOT win any prizes.\n"
        output += f"Here is a full breakdown of how the results are calculated while using your first spin as an example:\n\n"
        output += f"Provably Fair Calculation for Spin {nonce:,.0f}\n"
        output += f"Server Seed: {server_seed}\n"
        output += f"Server Seed (Hashed): {sha256_encrypt(server_seed)}\n"
        output += f"Client Seed: {client_seed}\n"
        output += f"Nonce: {nonce:,.0f}\n"
        output += f"Convert seeds plus nonce to hexadecimals (Numbers that can include any digit 0-9 plus any letter a-f):\n"
        output += f"\t{client_seed}:{nonce}:{0} -> {first_hex}\n"
        output += f"\t{client_seed}:{nonce}:{1} -> {second_hex}\n"
        output += f"Convert these hexadecimal values into bytes:\n"
        output += f"\t{first_hex} -> {first_bytes}\n"
        output += f"\t{second_hex} -> {second_bytes}\n"
        output += f"Split the bytes into groups of 4:\n"
        output += f"\t{[f'{num:03}' for num in first_bytes[:4]]}, {[f'{num:03}' for num in first_bytes[4:8]]}, {[f'{num:03}' for num in first_bytes[8:12]]},\n"
        output += f"\t{[f'{num:03}' for num in first_bytes[12:16]]}, {[f'{num:03}' for num in first_bytes[16:20]]}, {[f'{num:03}' for num in first_bytes[20:24]]},\n"
        output += f"\t{[f'{num:03}' for num in first_bytes[24:28]]}, {[f'{num:03}' for num in first_bytes[28:32]]}, {[f'{num:03}' for num in second_bytes[0:4]]},\n"
        output += f"Convert these bytes into numerical values:\n"
        output += f"\t[{first_bytes[0]:03}, {first_bytes[1]:03}, {first_bytes[2]:03}, {first_bytes[3]:03}] -> {first_bytes[0]:03}/256{to_superscript(1)} = {(float(first_bytes[0]) / float(256**1)):.10f}\n"
        output += f"\t                       +{first_bytes[1]:03}/256{to_superscript(2)} = {(float(first_bytes[1]) / float(256**2)):.10f}\n"
        output += f"\t                       +{first_bytes[2]:03}/256{to_superscript(3)} = {(float(first_bytes[2]) / float(256**3)):.10f}\n"
        output += f"\t                       +{first_bytes[3]:03}/256{to_superscript(4)} = {(float(first_bytes[3]) / float(256**4)):.10f}\n"
        output += f"\t\t                         = {bytes_to_basic_number(first_bytes[:4]):.10f}\n"
        output += f"\t[{first_bytes[4]:03}, {first_bytes[5]:03}, {first_bytes[6]:03}, {first_bytes[7]:03}] -> {first_bytes[4]:03}/256{to_superscript(1)} = {(float(first_bytes[4]) / float(256**1)):.10f}\n"
        output += f"\t                       +{first_bytes[5]:03}/256{to_superscript(2)} = {(float(first_bytes[5]) / float(256**2)):.10f}\n"
        output += f"\t                       +{first_bytes[6]:03}/256{to_superscript(3)} = {(float(first_bytes[6]) / float(256**3)):.10f}\n"
        output += f"\t                       +{first_bytes[7]:03}/256{to_superscript(4)} = {(float(first_bytes[7]) / float(256**4)):.10f}\n"
        output += f"\t\t                         = {bytes_to_basic_number(first_bytes[4:8]):.10f}\n"
        output += f"\t[{first_bytes[8]:03}, {first_bytes[9]:03}, {first_bytes[10]:03}, {first_bytes[11]:03}] -> {first_bytes[8]:03}/256{to_superscript(1)} = {(float(first_bytes[8]) / float(256**1)):.10f}\n"
        output += f"\t                       +{first_bytes[9]:03}/256{to_superscript(2)} = {(float(first_bytes[9]) / float(256**2)):.10f}\n"
        output += f"\t                       +{first_bytes[10]:03}/256{to_superscript(3)} = {(float(first_bytes[10]) / float(256**3)):.10f}\n"
        output += f"\t                       +{first_bytes[11]:03}/256{to_superscript(4)} = {(float(first_bytes[11]) / float(256**4)):.10f}\n"
        output += f"\t\t                         = {bytes_to_basic_number(first_bytes[8:12]):.10f}\n"
        output += f"\t[{first_bytes[12]:03}, {first_bytes[13]:03}, {first_bytes[14]:03}, {first_bytes[15]:03}] -> {first_bytes[12]:03}/256{to_superscript(1)} = {(float(first_bytes[12]) / float(256**1)):.10f}\n"
        output += f"\t                       +{first_bytes[13]:03}/256{to_superscript(2)} = {(float(first_bytes[13]) / float(256**2)):.10f}\n"
        output += f"\t                       +{first_bytes[14]:03}/256{to_superscript(3)} = {(float(first_bytes[14]) / float(256**3)):.10f}\n"
        output += f"\t                       +{first_bytes[15]:03}/256{to_superscript(4)} = {(float(first_bytes[15]) / float(256**4)):.10f}\n"
        output += f"\t\t                         = {bytes_to_basic_number(first_bytes[12:16]):.10f}\n"
        output += f"\t[{first_bytes[16]:03}, {first_bytes[17]:03}, {first_bytes[18]:03}, {first_bytes[19]:03}] -> {first_bytes[16]:03}/256{to_superscript(1)} = {(float(first_bytes[16]) / float(256**1)):.10f}\n"
        output += f"\t                       +{first_bytes[17]:03}/256{to_superscript(2)} = {(float(first_bytes[17]) / float(256**2)):.10f}\n"
        output += f"\t                       +{first_bytes[18]:03}/256{to_superscript(3)} = {(float(first_bytes[18]) / float(256**3)):.10f}\n"
        output += f"\t                       +{first_bytes[19]:03}/256{to_superscript(4)} = {(float(first_bytes[19]) / float(256**4)):.10f}\n"
        output += f"\t\t                         = {bytes_to_basic_number(first_bytes[16:20]):.10f}\n"
        output += f"\t[{first_bytes[20]:03}, {first_bytes[21]:03}, {first_bytes[22]:03}, {first_bytes[23]:03}] -> {first_bytes[20]:03}/256{to_superscript(1)} = {(float(first_bytes[20]) / float(256**1)):.10f}\n"
        output += f"\t                       +{first_bytes[21]:03}/256{to_superscript(2)} = {(float(first_bytes[21]) / float(256**2)):.10f}\n"
        output += f"\t                       +{first_bytes[22]:03}/256{to_superscript(3)} = {(float(first_bytes[22]) / float(256**3)):.10f}\n"
        output += f"\t                       +{first_bytes[23]:03}/256{to_superscript(4)} = {(float(first_bytes[23]) / float(256**4)):.10f}\n"
        output += f"\t\t                         = {bytes_to_basic_number(first_bytes[20:24]):.10f}\n"
        output += f"\t[{first_bytes[24]:03}, {first_bytes[25]:03}, {first_bytes[26]:03}, {first_bytes[27]:03}] -> {first_bytes[24]:03}/256{to_superscript(1)} = {(float(first_bytes[24]) / float(256**1)):.10f}\n"
        output += f"\t                       +{first_bytes[25]:03}/256{to_superscript(2)} = {(float(first_bytes[25]) / float(256**2)):.10f}\n"
        output += f"\t                       +{first_bytes[26]:03}/256{to_superscript(3)} = {(float(first_bytes[26]) / float(256**3)):.10f}\n"
        output += f"\t                       +{first_bytes[27]:03}/256{to_superscript(4)} = {(float(first_bytes[27]) / float(256**4)):.10f}\n"
        output += f"\t\t                         = {bytes_to_basic_number(first_bytes[24:28]):.10f}\n"
        output += f"\t[{first_bytes[28]:03}, {first_bytes[29]:03}, {first_bytes[30]:03}, {first_bytes[31]:03}] -> {first_bytes[28]:03}/256{to_superscript(1)} = {(float(first_bytes[28]) / float(256**1)):.10f}\n"
        output += f"\t                       +{first_bytes[29]:03}/256{to_superscript(2)} = {(float(first_bytes[29]) / float(256**2)):.10f}\n"
        output += f"\t                       +{first_bytes[30]:03}/256{to_superscript(3)} = {(float(first_bytes[30]) / float(256**3)):.10f}\n"
        output += f"\t                       +{first_bytes[31]:03}/256{to_superscript(4)} = {(float(first_bytes[31]) / float(256**4)):.10f}\n"
        output += f"\t\t                         = {bytes_to_basic_number(first_bytes[28:32]):.10f}\n"
        output += f"\t[{second_bytes[0]:03}, {second_bytes[1]:03}, {second_bytes[2]:03}, {second_bytes[3]:03}] -> {second_bytes[0]:03}/256{to_superscript(1)} = {(float(second_bytes[0]) / float(256**1)):.10f}\n"
        output += f"\t                       +{second_bytes[1]:03}/256{to_superscript(2)} = {(float(second_bytes[1]) / float(256**2)):.10f}\n"
        output += f"\t                       +{second_bytes[2]:03}/256{to_superscript(3)} = {(float(second_bytes[2]) / float(256**3)):.10f}\n"
        output += f"\t                       +{second_bytes[3]:03}/256{to_superscript(4)} = {(float(second_bytes[3]) / float(256**4)):.10f}\n"
        output += f"\t\t                         = {bytes_to_basic_number(second_bytes[:4]):.10f}\n\n"
        output += f"List out the weights of each icon from smallest to largest and take the cumulative sum of them:\n"
        output += f"\tOriginal Weights: {weights}\n"
        output += f"\tCumulative Sum Across Weights: {[sum(weights[:i+1]) for i in range(len(weights))]}\n"
        output += f"Match the bytes numbers to the largest position in the cumulative sum across weights list that does not exceed the cumulative weights value:\n"
        output += f"\t{bytes_to_basic_number(first_bytes[0:4]):.10f} -> {numbers[0]}\n"
        output += f"\t{bytes_to_basic_number(first_bytes[4:8]):.10f} -> {numbers[1]}\n"
        output += f"\t{bytes_to_basic_number(first_bytes[8:12]):.10f} -> {numbers[2]}\n"
        output += f"\t{bytes_to_basic_number(first_bytes[12:16]):.10f} -> {numbers[3]}\n"
        output += f"\t{bytes_to_basic_number(first_bytes[16:20]):.10f} -> {numbers[4]}\n"
        output += f"\t{bytes_to_basic_number(first_bytes[20:24]):.10f} -> {numbers[5]}\n"
        output += f"\t{bytes_to_basic_number(first_bytes[24:28]):.10f} -> {numbers[6]}\n"
        output += f"\t{bytes_to_basic_number(first_bytes[28:32]):.10f} -> {numbers[7]}\n"
        output += f"\t{bytes_to_basic_number(second_bytes[0:4]):.10f} -> {numbers[8]}\n"
        output += f"Place the final numbers in a 3x3 grid:\n"
        output += f"\t{numbers[0]}\t{numbers[1]}\t{numbers[2]}\n"
        output += f"\t{numbers[3]}\t{numbers[4]}\t{numbers[5]}\n"
        output += f"\t{numbers[6]}\t{numbers[7]}\t{numbers[8]}\n\n"
        output += f"Replace the numbers with their respective icon:\n"
        output += f"\t{icons[numbers[0]]}\t{icons[numbers[1]]}\t{icons[numbers[2]]}\n"
        output += f"\t{icons[numbers[3]]}\t{icons[numbers[4]]}\t{icons[numbers[5]]}\n"
        output += f"\t{icons[numbers[6]]}\t{icons[numbers[7]]}\t{icons[numbers[8]]}\n\n"
        output += f"Identify all the winning combinations and set the multiplier amount accordingly:\n"
        output += f"\t{'\n\t'.join(check_for_wins_receipt(spin_result))}\n"
        output += f"Add up all winning combination multipliers:\n"
        output += f"\t{'+'.join([str(multipliers[pictures.index(win)]) for win in check_for_wins(spin_result)])} = {sum([multipliers[pictures.index(win)] for win in check_for_wins(spin_result)])}\n"
        output += f"Deliver final payout:\n"
        output += f"\t{bet_amount:,} x {sum([multipliers[pictures.index(win)] for win in check_for_wins(spin_result)])} = {int(bet_amount*sum([multipliers[pictures.index(win)] for win in check_for_wins(spin_result)])):,.0f} Credits Paid Out.\n\n"
        output += f"Thank you for verifying your games with us. Please come play again soon."
    return output

def make_fullscreen(root:Tk,event=None):
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", exit_fullscreen)
    
def exit_fullscreen(root:Tk,event=None):
    root.attributes("-fullscreen", False)
    root.bind("<F11>", make_fullscreen)

def display_results(slot_labels: list[Label], results: list[list[str]], end_time: float, root: Tk):
    global nonce, balance, bet_amount, insufficient_funds_label, balance_label, server_seed, client_seed, nonce
    system('cls')
    with open("Slots_Results.txt","a",encoding='utf-8') as slots_results_file:
        slots_results_file.write(f"{server_seed}:{client_seed}:{nonce}:{0}\n")
        slots_results_file.write(provably_fair_calculation_receipt(server_seed, client_seed, nonce, bet_amount))
        slots_results_file.write(f"\n\n{'-'*100}\n\n")
    delay:int = int((end_time-time.time()+0.05)*1000)
    if bet_amount > balance:
        return
    balance -= bet_amount
    balance_label.destroy()
    balance_label = Label(root, text=f"Credits per Spin: {bet_amount:,}\tCredits: {int(balance):,}", 
                          activebackground='white', font=('Arial', 24, 'bold'), background='white', justify=CENTER)
    balance_label.pack(side=RIGHT, pady=10, padx=0)
    
    def update_images():
        global nonce, balance, bet_amount, insufficient_funds_label, balance_label
        current_row = 0
        current_col = 0
        winnings = calculate_winnings(check_for_wins(results), bet_amount)
        new_balance = balance + winnings
        for idx, label in enumerate(slot_labels):
            img = Image.open(results[current_row][current_col])
            img = img.resize((200,200), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            label.config(image=tk_img)
            label.image = tk_img  # Keep a reference to prevent garbage collection
            if current_col == 2:
                current_col = 0
                current_row += 1
            else:
                current_col += 1
        nonce += 1
        
        increase_credits(new_balance, balance, increment=7, root=root, label=balance_label)
        balance = new_balance  # Update global balance after animation

    spin_animation(slot_labels, end_time, root)  # Ensure all parameters are passed correctly
    root.after(delay, update_images)  # Add a delay based on `end_time` in milliseconds

if __name__ == "__main__":
    server_seed:str = generate_server_seed()
    client_seed:str = generate_client_seed()
    nonce:int = 1
    balance:int = 10_000
    bet_amount:int = 200

    root = Tk()
    root.title("FLUTTERING RICHES")
    root.configure(background='white')

    make_fullscreen(root)
    root.bind("<F11>", make_fullscreen)
    # root.bind("<Escape>", exit_fullscreen)
    balance_label = Label(root,text=f"FLUTTERING RICHES",activebackground='white',font=('Arial',40,'bold'),background='white',justify=CENTER).pack(side='top',pady=50)

    frame = Frame(root,background='white')
    frame.pack(pady=20)

    slot_labels = []
    for row in range(3):
        for col in range(3):
            label = Label(frame,background='white',activebackground='white',foreground='white')
            label.grid(row=row, column=col, padx=10, pady=10)
            slot_labels.append(label)

    # Display initial slots
    spin(slot_labels)

    spin_button:Button = Button(root, text="Spin", command=lambda: display_results(slot_labels,seeds_to_results(server_seed,client_seed,nonce),time.time()+2,root), font=("Helvetica 50 bold"),
                            bg="blue", fg="white", activebackground="blue", activeforeground="white",
                            relief="raised", bd=5)
    spin_button.pack(side=RIGHT, padx=200, pady=50)  # Moved to the right side and up slightly

    balance_label:Label = Label(root,text=f"Credits per Spin: {bet_amount:,}\tCredits: {balance:,}",activebackground='white',font=('Arial',24,'bold'),background='white',justify=CENTER)
    balance_label.pack(side=RIGHT,pady=10,padx=0)
    insufficient_funds_label = Label(root,text="Insufficient Funds!").destroy()
    root.mainloop()