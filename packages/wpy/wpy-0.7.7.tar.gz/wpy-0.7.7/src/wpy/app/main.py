#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from wpy import ID
from wpy import __version__
import click

snowflake = ID.Snowflake(0)

def print_version(ctx, param, value):
    #  print(ctx, param, value)
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()

@click.command()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.option('-c', default=1)
def run(c):
    print(c)
    print(snowflake.generate(0))
    print("Hello World")

if __name__ == "__main__":
    run()
