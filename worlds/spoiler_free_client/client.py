import asyncio
from CommonClient import CommonContext, server_loop, gui_enabled, ClientCommandProcessor, logger, get_base_parser


class SpoilerFreeCommandProcessor(ClientCommandProcessor):
    # def _cmd_test(self):
    #     pass
    pass


class SpoilerFreeContext(CommonContext):
    command_processor = SpoilerFreeCommandProcessor
    game = ""
    tags = {"Text Client"}
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


async def main(args):
    ctx = SpoilerFreeContext(args.connect, args.password)
    ctx.auth = args.name

    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    await ctx.exit_event.wait()
    await ctx.shutdown()


def launch():
    parser = get_base_parser("For text interfacing without seeing item and location names from other games.")
    parser.add_argument('--name', default=None, help="Slot Name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")
    args = parser.parse_args()

    import colorama
    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()
