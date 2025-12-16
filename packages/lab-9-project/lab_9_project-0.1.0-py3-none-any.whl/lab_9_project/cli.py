import argparse
import random
import os

# Set the parser for the command(s)
parser = argparse.ArgumentParser(prog='Don_comando', description='Create a dnd character or assign skill points to one.', epilog='<insert last message(could be an example of usage)>')
group = parser.add_mutually_exclusive_group()
group.add_argument('-cr', '--create', help='Creates a random RPG character with specific stat distribution based on a class, race and sex.', nargs='*')
group.add_argument('-st', '--stats', help='Choose which stats to increase with the available skill points.', action='store_true')
args = parser.parse_args()

def random_names(char:dict, race:str, is_male:bool):
    """ 
    Returns a dictionary that contains name and last name selected randomly based on its sex and race.
    char must be a dictionary, race must be a string, is_male must be a boolean value.
    """
    # Batches of randomly generated names according to race
    if race == 'Human':
        first_names_f = 'Yvaine,Esvele,Ginevra,Willow,Sylvia,Minerva,Lyra,Wynne,Anya,Juniper,Briony,Iris,Sabine,Faye,Adelaide'.split(',')
        first_names_m = 'Quentin,Icarus,Torin,Jorah,Corbin,Harlan,Davin,Jarrett,Darian,Lorcan,Darian,Merric,Tristan,Nolan,Orson'.split(',')
        last_names_f = 'Thornfield,Whitecliff,Cragmire,Jasperhill,Mistral,Goldforge,Xanwood,Quickbrook,Valewalker,Lionheart,Stormwind,Firestone,Frostwood,Palebrook'.split(',')
        last_names_m = 'Stormwind,Whitecliff,Greenfield,Hartfield,Frostmane,Rivershield,Longwood,Westfall,Greenfield,Bramblethorn,Wolfsbane,Greycastle,Bearclaw,Hightower,Oakheart'.split(',')
    elif race == 'Elf':
        first_names_f = 'Eldaloth,Jhanandra,Undomiel,Thalia,Belthania,Beleril,Uruviel,Gilraeniel,Celebrindal,Hithriel,Saelihn,Wingeloth,Ithilwen,Olorwen,Tathariel'.split(',')
        first_names_m = 'Bregedur,Rathlorian,Valarion,Kithrelion,Erevan,Dorlomin,Erevan,Galadorn,Quelamar,Quarion,Jarindel,Valarion,Erdan,Neldoreth,Findulias'.split(',')
        last_names_f = 'Starflower,Zirendil,Narqueli,Haldurian,Windrider,Neldoril,Wingelond,Meliamne,Illuvandor,Bregedur,Ithildur,Caladril,Aeloroth,Findulian,Rathlorel'.split(',')
        last_names_m = 'Zirendil,Yavandor,Tatharior,Telperind,Aranthas,Aeloroth,Rivendur,Xarduril,Quenandil,Stargazer,Bregedur,Valarand,Uruvandor,Ithildur,Aerendur'.split(',')
    elif race == 'Dwarf':
        first_names_f = 'Tova,Loni,Torgga,Hlin,Vigga,Brunhild,Oddrun,Ylfa,Iris,Thordis,Gerdrun,Petra,Helga,Lifdis,Bera'.split(',')
        first_names_m = 'Wulgar,Frostbeard,Uthor,Thrym,Stigandr,Orsik,Mordak,Ozruk,Magni,Arngrim,Ptorik,Kragnar,Skaldi,Ulfred,Hrothgar'.split(',')
        last_names_f = 'Earthrend,Diamondhand,Jaggedpeak,Flintfinder,Wyrmslayer,Zirconhand,Runehand,Stoneshould,Coalheart,Nidavellir,Rocksplitter,Earthshaker,Orehammer,Koboldsbane,Lodestone'.split(',')
        last_names_m = 'Furnacehear,Ironfist,Valleyforge,Hardstone,Adamantite,Moldforge,Nidavellir,Xenostone,Glimmerdeep,Bloodforge,Nobleforge,Craghelm,Grimstone,Stonefist,Brimstone'.split(',')

    # Randomly select names according to the character's sex
    if is_male:
        char['Name'] = random.choice(first_names_m)
        char['Surname'] = random.choice(last_names_m)
    else:
        char['Name'] = random.choice(first_names_f)
        char['Surname'] = random.choice(last_names_f)
    
    return char

def random_points(char:dict, b_class:str):
    """
    Returns a dictionary that contains skill values randomly selected in a specific range, values based on its class. 
    char must be a dictionary, b_classs must be  a string. 
    """
    if b_class == 'Rogue':
        char['Skills']['Vitality']=random.randint(5,9)
        char['Skills']['Strength']=random.randint(4,8)
        char['Skills']['Dexterity']=random.randint(10,16)
        char['Skills']['Resistance']=random.randint(6,9)
        char['Skills']['Intelligence']=random.randint(8,11)
        char['Skills']['Wisdom']=random.randint(4,7)
        char['Skills']['Luck']=random.randint(10,14)
    elif b_class == 'Cleric':
        char['Skills']['Vitality']=random.randint(5,9)
        char['Skills']['Strength']=random.randint(4,8)
        char['Skills']['Dexterity']=random.randint(5,9)
        char['Skills']['Resistance']=random.randint(5,9)
        char['Skills']['Intelligence']=random.randint(5,9)
        char['Skills']['Wisdom']=random.randint(5,9)
        char['Skills']['Luck']=random.randint(5,9)
    elif b_class == 'Fighter':
        char['Skills']['Vitality']=random.randint(9,14)
        char['Skills']['Strength']=random.randint(12,18)
        char['Skills']['Dexterity']=random.randint(6,9)
        char['Skills']['Resistance']=random.randint(8,12)
        char['Skills']['Intelligence']=random.randint(4,6)
        char['Skills']['Wisdom']=random.randint(3,5)
        char['Skills']['Luck']=random.randint(7,10)
    return char

def create(base_class:str=None, race:str='Human', is_male:bool=True):
    """
    Returns a string that contains class, race and stats information randomly selected based on the character. 
    base_clase must be a string, race must a string, is_male must be a boolean value. 
    """
    classes = ('Rogue', 'Fighter', 'Cleric') # Add more later on...
    races = ('Human', 'Elf', 'Dwarf')        # That should be enough races...
    # Data structure to store the character's info.
    # Every character begins at lvl 1.
    character = {'Name':'', 'Surname':'', 'Sex':'Male' if is_male else 'Female', 'Race':'', 'Class':'', 'Level':'1', 'Skills':{'Vitality':0, 'Strength':0, 'Dexterity':0, 'Resistance':0, 'Intelligence':0, 'Wisdom':0, 'Luck':0}}
    # Randomly choose a class for the character
    if base_class == None:
        base_class = random.choice(classes)
        character['Class'] = base_class[:]  # Get the value instead of a reference
    elif base_class not in classes:
        print("Unknown class. Selecting one at random...")
        base_class = random.choice(classes)
        character['Class'] = base_class[:]  # Get the value instead of a reference

    if race not in races:
        print("Unknown race. Selecting one at random...")
        race = random.choice(races)
        character['Race'] = race[:]         # Get the value instead of a reference

    # Finish updating the character dictionary
    character.update({'Race': race, 'Class': base_class})
    character.update(random_names(character, race, is_male))
    character.update(random_points(character, base_class))
    
    return f"""\n{character['Name']} {character['Surname']}
Sex: {character['Sex']}
Race: {character['Race']}
Class: {character['Class']}\n
Level: {character['Level']}
Vitality: {character['Skills']['Vitality']}
Strength: {character['Skills']['Strength']}
Dexterity: {character['Skills']['Dexterity']}
Resistance: {character['Skills']['Resistance']}
Intelligence: {character['Skills']['Intelligence']}
Wisdom: {character['Skills']['Wisdom']}
Luck: {character['Skills']['Luck']}\n"""

def main():
    """
    The main function compiles the previous info in order to create a new file for it if not already existing.
    """
    # Create a character with command line arguments
    if len(args.create) == 3:
        created_character = create(args.create[0], args.create[1], eval(args.create[2]))
    elif len(args.create) == 2:
        created_character = create(args.create[0], args.create[1])
    elif len(args.create) == 1:
        created_character = create(args.create[0])
    else:
        # Create with default values
        created_character = create()
    try:
        # If the file already exists...
        if os.path.exists('character_spreadsheet.txt'):
            if os.path.isfile('character_spreadsheet.txt'):\
                # Append to the file
                with open('character_spreadsheet.txt', 'a') as out:
                    out.write(created_character)
                print(f"Successfully appended to the '{out.name}' file!")
            else:
                print("The given path is not a valid file.")
        # If the file does not exists...
        else:
            # Create and write the file
            with open('character_spreadsheet.txt', 'x') as out:
                out.write(created_character)
            print(f"Successfully created the '{out.name}' file!")
    except FileNotFoundError:
        print(f"Error: Could not find the {out.name} file.")
    except PermissionError: 
        print(f"You do not have permission to open {out.name} the file")
    except: 
        print(f"Could not open the {out.name} file")   
    print(created_character)

if __name__ == "__main__": 
    print(args)
    print('--create: ',args.create)
    print('Length of create: ',len(args.create))
    print('--stats: ',args.stats)
    main()