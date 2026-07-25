from typing import TYPE_CHECKING
from BaseClasses import CollectionState, Entrance, Location, Region
from NetUtils import JSONMessagePart
from .classes import HKClause

if TYPE_CHECKING:
    from . import HKWorld

def parse_clause(self: "HKWorld", clause:HKClause, parent_region: Region, state: CollectionState) -> list[JSONMessagePart]:
    l_return:list[JSONMessagePart] = []
    for item,count in clause.hk_item_requirements.items():
        valid = state.has(item,self.player,count)
        l_return.append({"type":"color","color":"green" if valid else "red","text":item if count==1 else f"{item}:{count}"})
        l_return.append({"type":"text","text":", "})
    for region in clause.hk_region_requirements:
        valid = state.can_reach_region(region,self.player)
        l_return.append({"type":"color","color":"green" if valid else "red","text":region})
        l_return.append({"type":"text","text":", "})
    if clause.hk_state_requirements and parent_region:
        valid = state.can_reach_region(parent_region.name,self.player) and state._hk_test_fake_state(clause,parent_region)
        l_return.append({"type":"color","color":"green" if valid else "red","text":str(clause.hk_state_requirements)})
        l_return.append({"type":"text","text":", "})
    l_return.pop() # Remove the last comma
    return l_return

def explain_path(self: "HKWorld", entrance: Entrance, state: CollectionState) -> list[JSONMessagePart]:
    hk_rule = getattr(entrance,"hk_rule",None)
    if not isinstance(hk_rule,list):
        return [] # Empty list to tell UT to use normal entrance handeling
    l_return:list[JSONMessagePart] = [{"type":"color","color":"blue","text":entrance.name}]
    for index,clause in enumerate(hk_rule):
        if not isinstance(clause,HKClause):
            continue #maybe fix later?
        l_return.append({"type":"text","text":f"\nClause {index+1} - "})
        l_return.extend(parse_clause(self,clause,entrance.parent_region,state))
    return l_return

def explain_spot(self: "HKWorld", location: Location, state: CollectionState) -> list[JSONMessagePart]:
    hk_rule = getattr(location,"hk_rule",None)
    if not isinstance(hk_rule,list):
        return [] # Empty list to tell UT to use normal location handeling
    l_return:list[JSONMessagePart] = [{"type":"color","color":"green","text":f" -> {location.name}"}]
    for index,clause in enumerate(hk_rule):
        if not isinstance(clause,HKClause):
            continue #maybe fix later?
        l_return.append({"type":"text","text":f"\nClause {index+1} - "})
        l_return.extend(parse_clause(self,clause,location.parent_region,state))
    return l_return


def explain_rule(self: "HKWorld", target_name: str, state: CollectionState) -> list[JSONMessagePart]:
    l_return:list[JSONMessagePart] = []

    target = None
    parent_region = None
    if target_name in self.multiworld.regions.region_cache[self.player]:
        target = self.get_region(target_name)
        parent_region = target
        # Regions have to be dealt with differently, but they don't directly have rules or costs so it's fine
        for ent in target.entrances:
            ent_path = self.explain_path(ent,state)
            if ent_path:
                l_return.extend(ent_path)
                l_return.append({"type":"text","text":f"\n"})
            else: # Default entrance rule
                l_return.append({"type":"text","text":f"{ent.name} - "})
                passable = ent.access_rule(state)
                l_return.append({"type":"color","text":"Passable" if passable else "Impassable","color":"green" if passable else "red"})
                l_return.append({"type":"text","text":f"\n"})
        l_return.pop() # Remove the last newline
        return l_return
    elif target_name in self.multiworld.regions.entrance_cache[self.player]:
        target = self.get_entrance(target_name)
        parent_region = target.parent_region
    elif target_name in self.multiworld.regions.location_cache[self.player]:
        target = self.get_location(target_name)
        parent_region = target.parent_region

    if target is None or parent_region is None:
        return []
    hk_rule = getattr(target,"hk_rule",None)
    if not isinstance(hk_rule,list):
        l_return.append({"type":"text","text":"Default Access"})
    else:
        for index,clause in enumerate(hk_rule):
            if not isinstance(clause,HKClause):
                continue
            l_return.append({"type":"text","text":f"\nClause {index+1} - "})
            l_return.extend(parse_clause(self, clause,parent_region,state))
    costs = getattr(target,"costs",None)
    if isinstance(costs,dict):
        l_return.append({"type":"text","text":"\nCosts - ["})
        for cost,count in costs.items():
            if cost == "GEO":
                valid = state.has("Can_Replenish_Geo", self.player)
            else:
                valid = state.has(cost,self.player,count)
            l_return.append({"type":"color","color":"green" if valid else "red","text":f"{cost}:{count}"})
            l_return.append({"type":"text","text":", "})
        l_return.pop() #Remove the last comma
        l_return.append({"type":"text","text":"]"}) #And replace with a close bracket
    return l_return