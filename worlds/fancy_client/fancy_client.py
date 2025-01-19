from CommonClient import get_base_parser, server_loop, gui_enabled, logger
import asyncio

tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext
    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperContext


class FancyCommandProcessor(SuperContext.command_processor):
    def _cmd_prog(self, value=""):
        """Toggles if Only Prog are shown in the client. Can set to true/false or be toggled without a value."""
        if value.lower() in ("true", "false",):
            target = value.lower() == "true"
        else:
            target = not self.ctx.prog_only
        self.ctx.prog_only = target
        logger.info(f"Prog Only set to {target}")

    def _cmd_me(self, value=""):
        """Toggles if Only Messages related to the current slot are shown in the client. Can set to true/false or be toggled without a value."""
        if value.lower() in ("true", "false",):
            target = value.lower() == "true"
        else:
            target = not self.ctx.only_me
        self.ctx.only_me = target
        logger.info(f"Only Me set to {target}")

    def _cmd_watch_players(self, *names):
        """
        Takes a list of player names to filter by, not compatible with Only Me and will be ignored when Only Me is set.
        When used without a name it will clear the list and disable the function.
        """
        if not self.ctx.slot_info:
            logger.info("Please set watch players after connecting.")
            return
        if not names:
            logger.info("Watch Players filter cleared.")
            self.ctx.filter_for = set()
            return
        slot_ids = {slot_id for slot_id, slot in self.ctx.slot_info.items() if slot.name in names}
        group_ids = {slot_id for slot_id, slot in self.ctx.slot_info.items()
                     if any(s in slot.group_members for s in slot_ids)}
        self.ctx.filter_for = slot_ids | group_ids
        if self.ctx.filter_for:
            logger.info("Watching Players list updated for slots"
                        f"{self.ctx.slot_info[slot].name for slot in self.ctx.filter_for}")
        else:
            logger.info("No matching slots found for those player names, Watch Players filter cleared.")


def run_fancy_textclient():
    class TextContext(SuperContext):
        # Text Mode to use !hint and such with games that have no text entry
        tags = SuperContext.tags | {"TextOnly"}
        game = ""  # empty matches any game since 0.3.2
        command_processor = FancyCommandProcessor
        items_handling = 0b111  # receive all items for /received
        want_slot_data = False  # Can't use game specific slot_data

        prog_only = False
        only_me = False
        filter_for = set()

        def make_gui(self):
            ui = super().make_gui()

            class CCApp(ui):
                def print_json(self, data):
                    text = self.json_to_kivy_parser(data)
                    # this is called up here because some parser dominos I couldn't follow
                    # need the ref count set on __call__ properly even if the text is not displayed

                    if self.ctx.prog_only:
                        flags = [part["flags"] for part in data if "flags" in part]
                        if flags and not all(flag & 0b001 for flag in flags):
                            # if we're looking at an itemsend that is not prog don't print anything
                            return
                    if self.ctx.only_me:
                        players = [part["player"] for part in data if "player" in part]
                        if any(self.ctx.slot_concerns_self(slot) for slot in players):
                            pass
                        else:
                            return
                    elif self.ctx.filter_for:  # ignored when only me is set
                        players = [part["player"] for part in data if "player" in part]
                        if not players or any(player in self.ctx.filter_for for player in players):
                            pass
                        else:
                            print(data)
                            return

                    self.log_panels["Archipelago"].on_message_markup(text)
                    self.log_panels["All"].on_message_markup(text)

            return CCApp

# from here down is generic text client stuff

        async def server_auth(self, password_requested: bool = False):
            if password_requested and not self.password:
                await super(TextContext, self).server_auth(password_requested)
            await self.get_username()
            await self.send_connect()

        def on_package(self, cmd: str, args: dict):
            super().on_package(cmd, args)
            if cmd == "Connected":
                self.game = self.slot_info[self.slot].game

        async def disconnect(self, allow_autoreconnect: bool = False):
            self.game = ""
            await super().disconnect(allow_autoreconnect)

    async def main(args):
        ctx = TextContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")

        if tracker_loaded:
            ctx.run_generator()
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        await ctx.shutdown()

    import colorama

    parser = get_base_parser(description="Gameless Archipelago Client, for text interfacing.")
    args, _ = parser.parse_known_args()
    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()
