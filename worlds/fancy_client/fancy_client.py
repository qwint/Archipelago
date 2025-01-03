from CommonClient import get_base_parser, server_loop, gui_enabled
import asyncio

tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext
    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperContext


def run_fancy_textclient():
    class TextContext(SuperContext):
        # Text Mode to use !hint and such with games that have no text entry
        tags = SuperContext.tags | {"TextOnly"}
        game = ""  # empty matches any game since 0.3.2
        items_handling = 0b111  # receive all items for /received
        want_slot_data = False  # Can't use game specific slot_data

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
            old_print_json = ctx.ui.print_json

            def new_print_json(data):
                flags = [part["flags"] for part in data if "flags" in part]
                if flags and not all(flag & 0b001 for flag in flags):
                    # if we're looking at an itemsend that is not prog don't print anything
                    return
                old_print_json(data)
            ctx.ui.print_json = new_print_json
        ctx.run_cli()

        await ctx.exit_event.wait()
        await ctx.shutdown()

    import colorama

    parser = get_base_parser(description="Gameless Archipelago Client, for text interfacing.")
    args, _ = parser.parse_known_args()
    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()
