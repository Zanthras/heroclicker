"""
    Clicker Hero Bot
    Copyright (C) 2015  Joel Whitcomb

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


def program(gs):
    
    # We are going to make the first hero we buy be frostleaf so we make a variable to track this
    first_hero = False
    # First we need to test to see if the bot knows about frostleaf (since on start it scans all the heroes)
    if "Frostleaf" in gs.hero.heroes:
        # then we check to see what level frostleaf is, if its below 400 i want to bring it up to level 400
        if gs.hero.heroes['Frostleaf'].level < 400:
            # we now assign frostleaf to the variable
            first_hero = gs.hero.heroes['Frostleaf']

    damage_upgrades = False
    damage_upgrades_upgrade = True
    gd = [5, 6, 8, 14, 16, 20, 21, 24, 25]
    for heroname in gs.hero.heroes:
        if gs.hero.heroes[heroname].order in gd:
            if gs.hero.heroes[heroname].level < 200:
                if not damage_upgrades:
                    damage_upgrades = gs.hero.heroes[heroname]
                else:
                    if damage_upgrades.order < gs.hero.heroes[heroname].order:
                        damage_upgrades = gs.hero.heroes[heroname]
            if not gs.hero.heroes[heroname].upgraded:
                damage_upgrades_upgrade = False

    # the next step will be to buy tons of samurai, 2400 of them to be precise
    buy_to_ranger = False
    # im going to combine the existance check and hte level check into a single call
    if "Frostleaf" in gs.hero.heroes and gs.hero.heroes["Frostleaf"].level < 1500:
        # and set my variable is both are true
        buy_to_ranger = gs.hero.heroes["Frostleaf"]

    # because we want to execute all the bot steps in order, we are going to chain them all into an if/elif/elif/elif/elif/else type statement
    # this way it only excutes the first available instruction and slowly works through them all
    # to start with we work on our first hero
    if first_hero:
        # this is what is printed out on the console as we work on this step
        gs.step = "Buying Frostleaf up to 400"
        # we set the tracked hero to be frostleaf, tracking is important if you want to see the details on the console and to have a proper buy timer
        gs.hero.tracked = first_hero
        # if he isnt hidden we will just try to buy up to 400 (smartly buys as much as possible at a time)
        gs.hero.tracked.buy_up_to(400)
        # also if progression is turned off we will attempt to turn it on
    if not gs.progression_state:
            gs.window.click(gs.progression_coord)
    elif damage_upgrades:
        gs.hero.tracked = damage_upgrades
        gs.hero.tracked.buy_up_to(200)
    elif not damage_upgrades_upgrade:
        gs.hero.upgrade()
    # its up to ranger time
    elif buy_to_ranger:
        # as usual set the step
        gs.step = "Buying 1500 frostleaf"
        # set the tracking
        gs.hero.tracked = buy_to_ranger
        # new feature time... it might take a looong time to buy 2400, to so to save cpu cycles (its not free) we set a simple adaptive timer
        # which slows down the buying attempts when they fail, and speeds them up on success so we test if the buy timer wants us to try to buy
        if gs.hero.tracked.buy_timer():
            # if wants us to buy we buy
            gs.hero.tracked.buy_up_to(1500)
            # finally if for whatever reason progression mode got turned off after we buy 25 more heroes we turn it back on..
            # every heros level is captured when progression mode gets turned off, we can access what level it was at "gs.hero.tracked.progression_level"
            if gs.hero.tracked.level - gs.hero.tracked.progression_level >= 25 and not gs.progression_state:
                gs.window.click(gs.progression_coord)
    # now that we have bought a ton of samurai its time to move on to terra, the bot probably hasnt seen terra yet (it appeared while buying samurai)
    elif "Terra" not in gs.hero.heroes:
        # so if it hasnt seen it we should just scroll to the very bottom of the hero list to discover it
        gs.step = "Trying to locate Terra"
        gs.hero.scroll_to_bottom()
    # and the final step which we will setup with no end condition
    else:
        # we are going to buy alot of terra as the step indicates
        gs.step = "Buying inf Terra"
        final_hero = gs.hero.heroes["Terra"]
        # set the tracked as usual
        gs.hero.tracked = final_hero
        # scroll to if required (in case some human flips tabs to check on a new relic or something)
        if final_hero.ishidden:
            final_hero.scroll_to()
        # we do want this guy to be upgraded so lets upgrade him after level 200
        elif not final_hero.upgraded and final_hero.level >= 200:
            gs.step = "Upgrading Terra"
            gs.hero.upgrade()
        # finally we wont buy_up_to, we will directly try_buy in steps of 25 since thats the smallest step that matters
        elif final_hero.try_buy(25):
            # after every buy of 25 heroes we check and see if progression was turned off and turn it back on
            if not gs.progression_state:
                # print("\nunlocking progression, 25 heroes bought")
                gs.window.click(gs.progression_coord)