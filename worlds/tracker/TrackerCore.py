class TrackerCore():
    def regen_slots(self, world, slot_data, tempdir: str | None = None) -> bool:
        if callable(getattr(world, "interpret_slot_data", None)):
            temp = world.interpret_slot_data(slot_data)

            # back compat for worlds that trigger regen with interpret_slot_data, will remove eventually
            if temp:
                self.player_id = 1
                self.re_gen_passthrough = {self.game: temp}
                self.run_generator(slot_data, tempdir)
            return True
        else:
            return False

    @classmethod
    def find_tracker(cls, connected_cls, slot_data):
        if getattr(connected_cls, "disable_ut", False):
            raise Exception("World Author has requested UT be disabled on this world, please respect their decision")
        # first check if we don't need a yaml
        if getattr(connected_cls, "ut_can_gen_without_yaml", False):
            with tempfile.TemporaryDirectory() as tempdir:
                self.write_empty_yaml(self.game, slot_name, tempdir)
                self.player_id = 1
                world = None
                temp_isd = inspect.getattr_static(connected_cls, "interpret_slot_data", None)
                if isinstance(temp_isd, (staticmethod, classmethod)) and callable(temp_isd):
                    world = connected_cls
                else:
                    self.re_gen_passthrough = {self.game: slot_data}
                    self.run_generator(slot_data, tempdir)
                    if self.multiworld is None:
                        raise Exception("Internal world was not able to be generated, check your yamls and relaunch\n"
                                        "If this issue persists, reproduce with the debug launcher and post the error message to the discord channel")
                    world = self.multiworld.worlds[self.player_id]
                self.regen_slots(world, slot_data, tempdir)
                if self.multiworld is None:
                    raise Exception("Internal world was not able to be generated, check your yamls and relaunch\n"
                                    "If this issue persists, reproduce with the debug launcher and post the error message to the discord channel")

        else:
            if self.launch_multiworld is None:
                raise Exception("Internal world was not able to be generated, check your yamls and relaunch\n"
                                "If this issue persists, reproduce with the debug launcher and post the error message to the discord channel")

            if slot_name in self.launch_multiworld.world_name_lookup:
                internal_id = self.launch_multiworld.world_name_lookup[slot_name]
                if self.launch_multiworld.worlds[internal_id].game == self.game:
                    self.multiworld = self.launch_multiworld
                    self.player_id = internal_id
                    self.regen_slots(self.multiworld.worlds[self.player_id], slot_data)
                elif self.launch_multiworld.worlds[internal_id].game == "Archipelago":
                    if not self.regen_slots(connected_cls, slot_data):
                        raise Exception("TODO: add error - something went very wrong with interpret_slot_data")
                else:
                    world_dict = {name: self.launch_multiworld.worlds[slot].game for name, slot in self.launch_multiworld.world_name_lookup.items()}
                    tb = f"Tried to match game '{args['slot_info'][str(args['slot'])][1]}'" + \
                         f" to slot name '{args['slot_info'][str(args['slot'])][0]}'" + \
                         f" with known slots {world_dict}"
                    self.gen_error = tb
                    logger.error(tb)
                    return
            else:
                raise Exception(f"Player's Yaml not in tracker's list. Known players: {list(self.launch_multiworld.world_name_lookup.keys())}")
                return

    def updateTracker(ctx: TrackerGameContext) -> CurrentTrackerState:
        if ctx.player_id is None or ctx.multiworld is None:
            logger.error("Player YAML not installed or Generator failed")
            ctx.set_page(f"Check Player YAMLs for error; Tracker {UT_VERSION} for AP version {__version__}")
            return

        state = CollectionState(ctx.multiworld)
        prog_items = Counter()
        all_items = Counter()

        callback_list = []

        item_id_to_name = ctx.multiworld.worlds[ctx.player_id].item_id_to_name
        location_id_to_name = ctx.multiworld.worlds[ctx.player_id].location_id_to_name
        for item_name, item_flags, item_loc in [(item_id_to_name[item.item],item.flags,item.location) for item in ctx.tracker_items_received] + [(name,ItemClassification.progression,-1) for name in ctx.manual_items]:
            try:
                world_item = ctx.multiworld.create_item(item_name, ctx.player_id)
                if item_loc>0:
                    world_item.location = ctx.multiworld.get_location(location_id_to_name[item_loc],ctx.player_id)
                world_item.classification = world_item.classification | item_flags
                state.collect(world_item, True)
                if world_item.advancement:
                    prog_items[world_item.name] += 1
                if world_item.code is not None:
                    all_items[world_item.name] += 1
            except Exception:
                ctx.log_to_tab("Item id " + str(item_name) + " not able to be created", False)
        state.sweep_for_advancements(
            locations=[location for location in ctx.multiworld.get_locations(ctx.player_id) if (not location.address)])

        ctx.clear_page()
        regions = []
        locations = []
        readable_locations = []
        glitches_locations = []
        hints = []
        hinted_locations = []
        if f"_read_hints_{ctx.team}_{ctx.slot}" in ctx.stored_data:
            from NetUtils import HintStatus
            hints = [ hint["location"] for hint in ctx.stored_data[f"_read_hints_{ctx.team}_{ctx.slot}"] if hint["status"] != HintStatus.HINT_FOUND and ctx.slot_concerns_self(hint["finding_player"]) ]
        for temp_loc in ctx.multiworld.get_reachable_locations(state, ctx.player_id):
            if temp_loc.address is None or isinstance(temp_loc.address, list):
                continue
            elif ctx.hide_excluded and temp_loc.progress_type == LocationProgressType.EXCLUDED:
                continue
            elif temp_loc.address in ctx.ignored_locations:
                continue
            try:
                if (temp_loc.address in ctx.missing_locations):
                    # logger.info("YES rechable (" + temp_loc.name + ")")
                    region = ""
                    if temp_loc.parent_region is not None:
                        region = temp_loc.parent_region.name
                    temp_name = temp_loc.name
                    if temp_loc.address in ctx.location_alias_map:
                        temp_name += f" ({ctx.location_alias_map[temp_loc.address]})"
                    if ctx.output_format == "Both":
                        if temp_loc.progress_type == LocationProgressType.EXCLUDED:
                            ctx.log_to_tab("[color="+get_ut_color("excluded") + "]" +region + " | " + temp_name+"[/color]", True)
                        elif temp_loc.address in hints:
                            ctx.log_to_tab("[color="+get_ut_color("hinted") + "]" +region + " | " + temp_name+"[/color]", True)
                            hinted_locations.append(temp_loc)
                        else:
                            ctx.log_to_tab(region + " | " + temp_name, True)
                        readable_locations.append(region + " | " + temp_name)
                    elif ctx.output_format == "Location":
                        if temp_loc.progress_type == LocationProgressType.EXCLUDED:
                            ctx.log_to_tab("[color="+get_ut_color("excluded") + "]" +temp_name+"[/color]", True)
                        elif temp_loc.address in hints:
                            ctx.log_to_tab("[color="+get_ut_color("hinted") + "]" +temp_name+"[/color]", True)
                            hinted_locations.append(temp_loc)
                        else:
                            ctx.log_to_tab(temp_name, True)
                        readable_locations.append(temp_name)
                    if region not in regions:
                        regions.append(region)
                        if ctx.output_format == "Region":
                            ctx.log_to_tab(region, True)
                            readable_locations.append(region)
                    callback_list.append(temp_loc.name)
                    locations.append(temp_loc.address)
            except Exception:
                ctx.log_to_tab("ERROR: location " + temp_loc.name + " broke something, report this to discord")
                pass
        events = [location.item.name for location in state.advancements if location.player == ctx.player_id]

        ctx.locations_available = locations
        glitches_item_name = getattr(ctx.multiworld.worlds[ctx.player_id],"glitches_item_name","")
        if glitches_item_name:
            try:
                world_item = ctx.multiworld.create_item(glitches_item_name, ctx.player_id)
                state.collect(world_item, True)
            except Exception:
                ctx.log_to_tab("Item id " + str(glitches_item_name) + " not able to be created", False)
            else:
                state.sweep_for_advancements(
                    locations=[location for location in ctx.multiworld.get_locations(ctx.player_id) if (not location.address)])
                for temp_loc in ctx.multiworld.get_reachable_locations(state, ctx.player_id):
                    if temp_loc.address is None or isinstance(temp_loc.address, list):
                        continue
                    elif ctx.hide_excluded and temp_loc.progress_type == LocationProgressType.EXCLUDED:
                        continue
                    elif temp_loc.address in ctx.ignored_locations:
                        continue
                    elif temp_loc.address in locations:
                        continue # already in logic
                    try:
                        if (temp_loc.address in ctx.missing_locations):
                            glitches_locations.append(temp_loc.address)
                            region = ""
                            if temp_loc.parent_region is not None:  
                                region = temp_loc.parent_region.name
                            temp_name = temp_loc.name
                            if temp_loc.address in ctx.location_alias_map:
                                temp_name += f" ({ctx.location_alias_map[temp_loc.address]})"
                            if ctx.output_format == "Both":
                                if temp_loc.progress_type == LocationProgressType.EXCLUDED:
                                    ctx.log_to_tab("[color="+get_ut_color("out_of_logic_glitched") + "]" +region + " | " + temp_name+"[/color]", True)
                                elif temp_loc.address in hints:
                                    ctx.log_to_tab("[color="+get_ut_color("hinted_glitched") + "]" +region + " | " + temp_name+"[/color]", True)
                                    hinted_locations.append(temp_loc)
                                else:
                                    ctx.log_to_tab("[color="+get_ut_color("glitched") + "]" +region + " | " + temp_name+"[/color]", True)
                                readable_locations.append(region + " | " + temp_name)
                            elif ctx.output_format == "Location":
                                if temp_loc.progress_type == LocationProgressType.EXCLUDED:
                                    ctx.log_to_tab("[color="+get_ut_color("out_of_logic_glitched") + "]" +temp_name+"[/color]", True)
                                elif temp_loc.address in hints:
                                    ctx.log_to_tab("[color="+get_ut_color("hinted_glitched") + "]" +temp_name+"[/color]", True)
                                    hinted_locations.append(temp_loc)
                                else:
                                    ctx.log_to_tab("[color="+get_ut_color("glitched") + "]" +temp_name+"[/color]", True)
                                readable_locations.append(temp_name)
                            if region not in regions:
                                regions.append(region)
                                if ctx.output_format == "Region":
                                    ctx.log_to_tab("[color="+get_ut_color("glitched")+"]"+region+"[/color]", True)
                                    readable_locations.append(region)
                    except Exception:
                        ctx.log_to_tab("ERROR: location " + temp_loc.name + " broke something, report this to discord")
                        pass
        ctx.glitched_locations = glitches_locations
        if ctx.tracker_page:
            ctx.tracker_page.refresh_from_data()
        if ctx.update_callback is not None:
            ctx.update_callback(callback_list)
        if ctx.region_callback is not None:
            ctx.region_callback(regions)
        if ctx.events_callback is not None:
            ctx.events_callback(events)
        if ctx.glitches_callback is not None:
            ctx.glitches_callback(glitches_locations)
        if len(ctx.ignored_locations) > 0:
            ctx.log_to_tab(f"{len(ctx.ignored_locations)} ignored locations")
        if len(callback_list) == 0:
            ctx.log_to_tab("All " + str(len(ctx.checked_locations)) + " accessible locations have been checked! Congrats!")
        if ctx.tracker_world is not None and ctx.ui is not None:
            # ctx.load_map()
            for location in ctx.server_locations:
                relevent_coords = ctx.coord_dict.get(location, [])
                
                if location in ctx.checked_locations or location in ctx.ignored_locations:
                    status = "completed"
                elif location in ctx.locations_available:
                    status = "in_logic"
                elif location in ctx.glitched_locations:
                    status = "glitched"
                else:
                    status = "out_of_logic"
                if location in hints:
                    status = "hinted_"+status
                for coord in relevent_coords:
                    coord.update_status(location, status)
        if ctx.quit_after_update:
            name = ctx.player_names[ctx.slot]
            if ctx.print_count:
                logger.error(f"Game: {ctx.game} | Slot Name : {name} | In logic locations : {len(locations)}")
            if ctx.print_list:
                for i in readable_locations:
                    logger.error(i)
            ctx.exit_event.set()

        if hasattr(ctx, "tracker_total_locs_label"):
            ctx.tracker_total_locs_label.text = f"Locations: {len(ctx.checked_locations)}/{ctx.total_locations}"
        if hasattr(ctx, "tracker_logic_locs_label"):
            ctx.tracker_logic_locs_label.text = f"In Logic: {len(locations)}"
        if hasattr(ctx, "tracker_glitched_locs_label"):
            ctx.tracker_glitched_locs_label.text = f"Glitched: [color={get_ut_color("glitched")}]{len(glitches_locations)}[/color]"
        if hasattr(ctx, "tracker_hinted_locs_label"):
            ctx.tracker_hinted_locs_label.text = f"Hinted: [color={get_ut_color("hinted_in_logic")}]{len(hinted_locations)}[/color]"

        return CurrentTrackerState(all_items, prog_items, glitches_locations, events, state)

    def get_logical_path(ctx: TrackerGameContext, dest_name: str):
        if ctx.player_id is None or ctx.multiworld is None:
            logger.error("Player YAML not installed or Generator failed")
            ctx.set_page(f"Check Player YAMLs for error; Tracker {UT_VERSION} for AP version {__version__}")
            return
        dest_id = ctx.multiworld.worlds[ctx.player_id].location_name_to_id[dest_name]
        if dest_id not in ctx.server_locations:
            logger.error("Location not found")
            return

        state = updateTracker(ctx).state
        location = ctx.multiworld.get_location(dest_name, ctx.player_id)
        if location.can_reach(state):

            # stolen from core
            from BaseClasses import Region
            from typing import Tuple, Iterator
            from itertools import zip_longest

            def flist_to_iter(path_value) -> Iterator[str]:
                while path_value:
                    region_or_entrance, path_value = path_value
                    yield region_or_entrance

            def get_path(state: CollectionState, region: Region) -> list[Union[Tuple[str, str], Tuple[str, None]]]:
                reversed_path_as_flist = state.path.get(region, (str(region), None))
                string_path_flat = reversed(list(map(str, flist_to_iter(reversed_path_as_flist))))
                # Now we combine the flat string list into (region, exit) pairs
                pathsiter = iter(string_path_flat)
                pathpairs = zip_longest(pathsiter, pathsiter)
                return list(pathpairs)

            paths = get_path(state=state, region=location.parent_region)
            for k, v in paths:
                if v:
                    logger.info(v)

        else:
            logger.info("Location not in logic")


    @staticmethod
    def write_empty_yaml(game, player_name, tempdir):
        path = os.path.join(tempdir, f'{game}_{player_name}.yaml')
        with open(path, 'w') as f:
            f.write('name: ' + player_name + '\n')
            f.write('game: ' + game + '\n')
            f.write(game + ': {}\n')

    @staticmethod
    def move_slots(args: "Namespace", slot_name: str):
        """
        helper function to copy all the proper option values into slot 1,
        may need to change if/when multiworld.option_name dicts get fully removed
        """
        player = {name: i for i, name in args.name.items()}[slot_name]
        if player == 1:
            return args
        for option_name, option_value in args._get_kwargs():
            if isinstance(option_value, dict) and player in option_value:
                setattr(args, option_name, {1: option_value[player]})
        return args

    @staticmethod
    def _set_host_settings():
        from . import TrackerWorld
        tracker_settings = TrackerWorld.settings
        report_type = "Both"
        if tracker_settings['include_location_name']:
            if tracker_settings['include_region_name']:
                report_type = "Both"
            else:
                report_type = "Location"
        else:
            report_type = "Region"
        return tracker_settings['player_files_path'], report_type, tracker_settings[
            'hide_excluded_locations'], tracker_settings["use_split_map_icons"]

    def run_generator(self, slot_data: dict | None = None, override_yaml_path: str | None = None):
        try:
            from . import TrackerWorld
            yaml_path = TrackerWorld.settings.players_files_path
            # strip command line args, they won't be useful from the client anyway
            sys.argv = sys.argv[:1]
            args = mystery_argparse()
            if override_yaml_path:
                args.player_files_path = override_yaml_path
            elif yaml_path:
                args.player_files_path = yaml_path
            args.skip_output = True

            if self.quit_after_update:
                from logging import ERROR
                args.log_level = ERROR

            g_args, seed = GMain(args)
            if slot_data or override_yaml_path:
                if slot_data and slot_data in self.cached_slot_data:
                    print("found cached multiworld!")
                    index = next(i for i, s in enumerate(self.cached_slot_data) if s == slot_data)
                    self.multiworld = self.cached_multiworlds[index]
                    return
                if not self.game:
                    raise "No Game found for slot, this should not happen ever"
                g_args.multi = 1
                g_args.game = {1: self.game}
                g_args.player_ids = {1}

                # TODO confirm that this will never not be filled
                g_args = self.move_slots(g_args, self.slot_info[self.slot].name)

                self.multiworld = self.TMain(g_args, seed)
                assert len(self.cached_slot_data) == len(self.cached_multiworlds)
                self.cached_multiworlds.append(self.multiworld)
                self.cached_slot_data.append(slot_data)
            else:
                # skip worlds that we know will regen on connect
                g_args.game = {
                    slot: game if game not in REGEN_WORLDS else "Archipelago"
                    for slot, game in g_args.game.items()
                    }
                # TODO empty out generic options for slots we moved to "Archipelago"
                self.launch_multiworld = self.TMain(g_args, seed)
                self.multiworld = self.launch_multiworld

            temp_precollect = {}
            for player_id, items in self.multiworld.precollected_items.items():
                temp_items = [item for item in items if item.code is None]
                temp_precollect[player_id] = temp_items
            self.multiworld.precollected_items = temp_precollect
        except Exception as e:
            tb = traceback.format_exc()
            self.gen_error = tb
            logger.error(tb)

    def TMain(self, args, seed=None):
        from worlds.AutoWorld import World
        gen_steps = filter(
            lambda s: hasattr(World, s),
            # filter out stages that World doesn't define so we can keep this list bleeding edge
            (
                "generate_early",
                "create_regions",
                "create_items",
                "set_rules",
                "connect_entrances",
                "generate_basic",
                "pre_fill",
            )
        )

        multiworld = MultiWorld(args.multi)

        multiworld.generation_is_fake = True
        if self.re_gen_passthrough is not None:
            multiworld.re_gen_passthrough = self.re_gen_passthrough

        multiworld.set_seed(seed, args.race, str(args.outputname) if args.outputname else None)
        multiworld.game = args.game.copy()
        multiworld.player_name = args.name.copy()
        multiworld.set_options(args)
        multiworld.state = CollectionState(multiworld)

        for step in gen_steps:
            AutoWorld.call_all(multiworld, step)
            if step == "set_rules":
                for player in multiworld.player_ids:
                    exclusion_rules(multiworld, player, multiworld.worlds[player].options.exclude_locations.value)
            if step == "generate_basic":
                break

        return multiworld
