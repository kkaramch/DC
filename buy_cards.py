from copy import deepcopy

import cards
import deck


"""
Finds cards in the lineup to buy with given power that maximizes VP gain
*ONLY CALL WHEN A SOLUTION EXISTS*
Parameter list:
    power: buying power
    lineup: lineup (any sorting)
Return:
    list of cards to buy
"""
def max_vp_lineup(power, lineup, lineup1):
    """
    lineup is sorted by vp value, highest to lowest, with the tiebreaker for cards with
    equal value being cards with lowest cost first
    lineup1 is sorted by vp value/cost ratio, highest to lowest, with the tiebreaker for
    cards with equal ratio being cards with highest cost first 
    """
    cards_to_buy_val = [] #cards bought by sorting by val
    cards_to_buy_ratio = [] #cards bought by sorting by ratio
    val_buy_total = 0 #value of cards bought by sorting by val
    ratio_buy_total= 0 #value of cards bought by sorting by ratio
    leftovers = []
    #Buy in order as we can the highest values
    while len(lineup) > 0:
        if power > lineup[0].get_power(): #if we can buy the most vp
            card = lineup.remove[0] #most vp left on lineup
            power -= card.get_power()
            val_buy_total += card.get_vp
            cards_to_buy_val.append(card) #add most vp to cards to buy
        else: #if we can't buy it, add it to leftovers
            leftovers.append(lineup.remove[0])
    #bought the entire lineup so can just return
    if len(leftovers) < 1:
        return cards_to_buy_val

    while len(lineup1) > 0:
        if power > lineup1[0].get_power(): #if we can buy the most vp
            card = lineup1.remove[0] #most vp left on lineup
            power -= card.get_power()
            ratio_buy_total += card.get_vp
            cards_to_buy_ratio.append(card) #add most vp to cards to buy
        else: #if we can't buy it, add it to leftovers
            leftovers.append(lineup1.remove[0])
    if val_buy_total > ratio_buy_total: #if we get higher victory points sorting by val, return that
        return cards_to_buy_val
    else:
        return cards_to_buy_ratio #otherwise return the cards bought by sorting by ratio



"""
Wrapper for card.get_vp for the sort function
"""
def vp(card):
    return card.get_vp()

"""
Sorts the lineup by vp values (method doesn't really matter, the list will only be at most 8 or 9 cards)
Parameter list:
    lineup: lineup to sort
Return:
    lineup: lineup sorted by vp values
"""
def sort_by_vp(lineup):
    lineup.sort(key=vp, reverse=True) #sorts lineup in place based on result of vp called on its elements
    return lineup

"""
Checks if it can end the game and returns whether it can and the cards to buy.
Doesn't need kick deck because kicks are worth at most 1 vp
Parameter list:
    power: buying power
    super_villain: super villain card
    super_deck_size: cards left in super deck
    main_deck_size: cards left in main deck
    lineup:cards in lineup sorted by price
Return:
    boolean, cards_to_buy, remaining_power
"""
def check_end_game(power, super_villain, super_deck_size, main_deck_size, lineup):
    cards_to_buy = []
    if super_deck_size == 1 and super_villain.cost < power: #can buy the last super_villain
        cards_to_buy.append(super_villain)
        power -= super_villain.cost #less power to buy other stuff
        max_vp = max_vp_lineup(power, lineup()) #(cards_to_buy, power_left)
        cards_to_buy = cards_to_buy + max_vp[0] #add whatever other cards from lineup maximize power
        power = max_vp[1]
        return True, cards_to_buy, power

    needed_to_end = main_deck_size + 1  # number of cards to buy from the lineup to end the game
    if needed_to_end > 4: #can't buy enough cards to end game
        return False, []
    power_needed = 0
    for i in range(0, needed_to_end-1):
        power_needed += lineup[i] #minimum power needed to end game
    if power_needed < power: #not enough power
        return False, []
    #calculate max vp by backtracking we know there is at least one solution
    else:
        vp_lineup = sort_by_vp(lineup)
        sofar = [] #keep track of current guess
        index = 0
        attempt = 0
        power_left = power #remaining power to buy (can't go below 0 in a solution)
        while True:
            sofar.append(vp_lineup[index])
            power_left -= vp_lineup[index]
            if power_left >= 0:
                if len(sofar) == needed_to_end: #we have our solution
                    return True, sofar, power_left
                else: #we can still potentially build a solution off of this
                    index += 1
                    continue
            else: #current attempt cannot be the solution
                attempt += 1 #track number of attempts
                index = attempt #continue with next attempt ignoring the most costly card
                sofar = [] #reset sofar
                power_left = power #reset power_left
                continue
    return False, [] #should never reach this line, but I'll leave it here just in case

"""
Takes the amount of buying power along with the super villain, and the lineup in order by cost
and returns a list of cards to buy based on our algorithm for buying cards.
Parameter list:
    power: buying power from playing cards
    super_villain_deck: current super villain deck
    main_deck: current main deck
    kick_deck: current kick deck
    own_deck: current own deck
    lineup: list of cards available to buy
"""
def buy_cards(power, super_villain_deck, main_deck, kick_deck, own_deck, lineup):
    #first, we'll play to try to end the game when possible
    cards_to_buy = []
    #(bool can_end_game, cards_to_buy, remaining_power)
    end_game = check_end_game(power, super_villain_deck.peek(), super_villain_deck.num_size, main_deck.size, lineup)
    if end_game[0]:
        cards_to_buy += end_game[1]
        kicks = end_game[2]//3 #of kicks able to buy with remaining power
        for i in range(1, kicks):
            if kick_deck.size == 0:
                break
            #TODO add kicks to cards to buy (not certain how this will look based on how other stuff is implemented)
        return cards_to_buy

    #can buy super_villain
    if super_villain_deck.peek().get_cost() <= power:
        power -= super_villain_deck.peek().get_cost()
        cards_to_buy.append(super_villain_deck.peek()) #add the super villain to the cards to buy
        if power <= 1: #buying super spent all power so no need to check other stuff
            return cards_to_buy

    #end game coming soon, but cannot end it on our turn
    if super_villain_deck.num_cards <= 3 or main_deck.num_cards <= 15:
        #cards to add to cards to buy from lineup
        max_vp = max_vp_lineup(power, lineup)
        spent = 0
        #figure out the cost of the cards
        for card in max_vp:
            spent += card.get_vp()
        power -= spent #get leftover power
        cards_to_buy.extend(max_vp[0])
        #TODO add as many kicks as possible

    return None