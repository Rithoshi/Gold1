import time
import pandas as pd
from packages.get_prices import get_prices
import pandas as pd
from datetime import date


def buy_metal(client, metal, quantity, check):

    # Open the inventory
    df = pd.read_csv(r'csv_file/inventory.csv')

    # Ensure that the first letter of the metal is big
    metal = metal.lower()
    nmetal = metal[:1].upper()+metal[1:]
    metal = nmetal

    presence = False

    result = False

    # Check if the metal is traded by us
    for i in range(0, 5):
        if df.loc[i, 'Metal'] == metal:
            presence = True
            break

    # Check if quantity contains only numbers, and so it is an integer

    int_number = '0123456789'
    sq = str(quantity)
    valid = True
    for n in sq:
        if n not in int_number:
            valid = False
            break

    if presence is False:
        # Say that we don't trade the metal
        print('Sorry, the metal that you want to buy is not traded by us.'
              '\n You can buy from us Gold, Silver, Platinum,'
              'Palladium and Rhodium. \n')

    elif valid is False:
        print('Error, you typed a letter or a special character'
              'in the quantity, we are able to trade only grams. \n')

    elif int(quantity) == 0:
        print('Sorry, but it is impossible to buy 0 grams of any metal.'
              'Please insert a valid number. \n')

    elif int(quantity) > 1000:
        # Say if the quantity requested is too much
        print('We are sorry, we are not able to supply'
              'you this amount of ', metal, '. We can supply'
              'you at most 1 kg. \n')

    else:

        # Metal and quantity are ok,
        # We open the wallet and change quantity to an integer

        quantity = int(quantity)

        w = pd.read_csv(r'csv_file/wallet.csv')

        # Check if we have enough metal in the inventory

        if quantity <= df.loc[i, 'Quantity']:

            # We have enough metal, we can sell it without buying it
            # We ask to type the cvc of the credit card to confirm the purchase

            if check is False:
                success = False
                print('We are sorry, the purchase was abort. \n')

            else:

                success = True
                df.loc[i, 'Quantity'] = df.loc[i, 'Quantity']-quantity

                # Calculate the selling price with a profit of 5%

                p = round((quantity * df.loc[i, 'Price'] * 1.05), 3)

                # Record on the wallet the cash inflow and new balance

                w.loc[0, 'Inflow'] = w.loc[0, 'Inflow'] + p
                w.loc[0, 'Balance'] = w.loc[0, 'Balance'] + p

                # Succesful transaction

                result = True
                print('Thank you so much, you have just bought ',
                      quantity, 'g of ', metal, ' at the price of ',
                      p, ' EUR. \n')

        else:

            # Buy new metal to have the inventory full

            print('We are buying new metals for you, wait a second please. \n')

            # Call the function get prices to call the API
            # We're buying new metal at the actual price

            success, new = get_prices()

            # Check if the API is online and so we are able to buy new metal

            if success is False:
                print('We are sorry, because of an internal problem we are'
                      'not able to buy enough metal now. If you'
                      'make an order of at most', df.loc[i, 'Quantity'],
                      ' ', metal, ' we will be able to'
                      'provide it to you. \n')

            else:

                # Before proceeding we check the cvc of the client

                if check is False:
                    success = False
                    print('We are sorry, the purchase was abort. \n')

                else:
                    # We've just bought new metal, need to update the inventory

                    p1 = df.loc[i, 'Price']
                    q1 = df.loc[i, 'Quantity']
                    p2 = round(new[metal], 3)
                    q2 = 1000 - q1

                    # Control if we have enough cash

                    acq_price = round((q2 * p2), 3)
                    if w.loc[0, 'Balance'] < acq_price:

                        # Ask a loan to be able to buy the new metals

                        delta = acq_price - w.loc[0, 'Balance']
                        w.loc[0, 'Bank_Loan'] = w.loc[0, 'Bank_Loan'] + delta
                        w.loc[0, 'Balance'] = w.loc[0, 'Balance'] + delta

                    # Calculate the weighted mean of the price and update it

                    new_p = round((((p1 * q1) + (p2 * q2)) / 1000), 3)
                    df.loc[i, 'Price'] = new_p

                    # Register the cash outflow

                    w.loc[0, 'Outflow'] = w.loc[0, 'Outflow'] + acq_price
                    w.loc[0, 'Balance'] = w.loc[0, 'Balance'] - acq_price
                    df.loc[i, 'Quantity'] = 1000 - quantity

                    # Calculate the selling price with a profit of 5%

                    p = round((quantity * new_p * 1.05), 3)

                    # Register cash inflow and new balance

                    w.loc[0, 'Inflow'] = w.loc[0, 'Inflow'] + p
                    w.loc[0, 'Balance'] = w.loc[0, 'Balance'] + p

                    # Succesful transaction

                    time.sleep(5)
                    result = True
                    print('Thank you so much, you have'
                          'just bought ', quantity, 'g of ', metal,
                          ' at the price of ', p, ' EUR. \n')
                          
    return result