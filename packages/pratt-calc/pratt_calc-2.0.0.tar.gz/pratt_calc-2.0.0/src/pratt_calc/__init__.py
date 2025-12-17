from typing import Annotated

import typer

from pratt_calc.evaluator import Evaluator
from pratt_calc.repl import Repl


def app():
    """Entry-point for project script."""

    # Note that the name of this particular function is insigificant,
    # as the function only serves to wrap the logic used by
    # 'typer.run'
    def cli(
        interactive: Annotated[
            bool, typer.Option("--interactive", "-i", help="Launch the REPL.")
        ] = False,
        exp: Annotated[
            str, typer.Option("--eval", "-e", help="Evaluate the given expression.")
        ] = "",
        filename: Annotated[str, typer.Argument(help="Path to source file.")] = "",
    ):
        """Pratt Calc application.

        Without FILENAME or --eval/-e, launch the REPL.

        Use --interactive/-i to launch the REPL even when FILENAME or
        '-e/--eval' are provided.

        This is useful for interactively inspecting the state of the
        program.

        """

        ev = Evaluator()

        if exp != "":
            print(ev.evaluate(exp))

        if filename != "":
            try:
                print(ev.evaluate_file(filename))
            except Exception as e:
                print(e)
                raise typer.Abort()

        launch_repl = interactive or (filename == "" and exp == "")

        if launch_repl:
            Repl(ev).cmdloop()

    typer.run(cli)
