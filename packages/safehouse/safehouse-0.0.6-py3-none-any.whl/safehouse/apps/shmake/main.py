#!/usr/bin/env python3

import logging
import os
import sys

from . import commands


logger = logging.getLogger()

'''
shmake (build/test/deploy), shevents and shanalytics (telemetry and analysis), shengine (engine),
sheditor (editor), shmoney (monetization), shtacktrace (crashes), shtore (distribution platform)
'''

'''
Instrument build system and analyze the events generated from that telemtry (shevents and shanalytics)
'''

'''
Scenarios:
- Running engine and/or editor locally
- Building and testing shared within a docker container
-- can the building and testing always be done in container, and the running is on host OS?
- can only test engine running locally or from docker container connected to host graphics card; can't easily display to host though
'''

'''
  `shmake configure --platform=<platform> --arch=<arch> --compiler=<compiler_name>-compiler-version>  --target=<target>`
  -- each platform will have a default compiler, the default target will be debug
  -- e.g.`shmake configure --platform=linux --arch=x86_x6 --compiler=llvm-19 --target=debug`
  `shmake configuration` # shows currently selected configuration
  `shmake select <platform>/<compiler_name>-<compiler_version>-<architecture>/<target>` # selects specified build configuration
  `shmake select (from or under directory that would be the path from the first version)` # selects that build configuration
  `shmake` # builds current build; if no current build prompts to configure/selet one
  `shmake build` # builds current build; if no current build prompts to configure/select one
  `shmake deploy <major|minor|micro|major.minor.micro` # deploys the next version for major|minor|micro, or exact version for major.minor.mico; fails if that version already exists
  -- versions relate to the build packages, and also the generated docker images
  -- deploy builds docker images locally by default; but same flow should be able to be used to deploy to AWS ECR or docker hub
  `shmake test <all|module>` builds and then runs tests associated with all modules, or specified module
'''


COMMANDS = { 
    'configure': commands.Configure,
}


def run():
    logging.basicConfig(
        filename='/tmp/shmake.log',
        level=logging.INFO,
    )
    command_class = commands.Configure
    if len(sys.argv) > 1:
        command_class_from_args = COMMANDS.get(sys.argv[1], command_class)
        if command_class_from_args:
            command_class = command_class_from_args
        
    try:
        command: commands.Command = command_class()
        command.configureFromArguments()
        command.run()
    except Exception as e:
        print(e)
        print("run shmake --help for more information")

if __name__ == "__main__":
    run()
