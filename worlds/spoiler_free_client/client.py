import asyncio
import typing
from CommonClient import CommonContext, server_loop, gui_enabled, ClientCommandProcessor, logger, get_base_parser


class SpoilerFreeCommandProcessor(ClientCommandProcessor):
    pass


class SpoilerFreeContext(CommonContext):
    command_processor = SpoilerFreeCommandProcessor
    game = ""
    tags = {"TextOnly"}
    items_handling = 0b111

    def __init__(self, server_address, password):
        super().__init__(server_address, password)

    def run_gui(self):
        from kvui import GameManager

        class SpoilerFreeManager(GameManager):
            logging_pairs = [("Client", "Archipelago")]
            base_title = "Archipelago Spoiler Free Client"

        self.ui = SpoilerFreeManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(SpoilerFreeContext, self).server_auth(password_requested)

        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        if cmd == "Connected":
            pass
        elif cmd == "PrintJSON":
            msg_type = args.get("type")
            print("test")


def launch():
    async def main():
        parser = get_base_parser("For text interfacing without seeing item and location names from other games.")
        parser.add_argument('--name', default=None, help="Slot Name to connect as.")
        parser.add_argument("url", nargs="?", help="Archipelago connection url")
        args = parser.parse_args()
        ctx = SpoilerFreeContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        await ctx.shutdown()

    import colorama
    colorama.init()
    asyncio.run(main())
    colorama.deinit()
