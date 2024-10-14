from API_Items import get_item
from API_Ressources import get_ressources



def main():
    user_choice = input("What do you want to do (actualize_item/_ressources/_recipes) ? ")

    if user_choice == "actualize_item":
        get_item()
    if user_choice == "actualize_ressources":
        get_ressources()




if __name__ == "__main__":
    main()