"""
    lager.hello.commands

    Say hello to gateway
"""
import click
from ..context import get_impl_path
from ..python.commands import run_python_internal
from ..dut_storage import resolve_and_validate_dut_with_name

@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--dut', required=False, hidden=True, help="Lagerbox name or IP")
def hello(ctx, box, dut):
    """Test gateway connectivity"""
    # Use box or dut (box takes precedence)
    dut = box or dut

    # Resolve and validate the DUT, keeping track of the original name
    original_dut_name = dut  # Save for username lookup
    resolved_dut, dut_name = resolve_and_validate_dut_with_name(ctx, dut)

    run_python_internal(
        ctx,
        get_impl_path('hello.py'),
        resolved_dut,
        image='',
        env=(),
        passenv=(),
        kill=False,
        download=(),
        allow_overwrite=False,
        signum='SIGTERM',
        timeout=0,
        detach=False,
        port=(),
        org=None,
        args=(resolved_dut,),  # Pass the resolved IP as an argument
        dut_name=dut_name,  # Pass DUT name for username lookup
    )
