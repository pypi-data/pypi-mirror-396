import logging
from typing import Optional

from . import command
from .. import configurations, projects
from ..configurations import cmake, compilers, platforms, targets


logger = logging.getLogger()


class Configure(command.Command):
    def __init__(self):
        super().__init__()
        self.configuration: Optional[configurations.Configuration] = None

    def __str__(self) -> str:
        return f"configure {self.configuration}"

    def configureFromArguments(self):
        self.parser.add_argument(
            '--compiler',
            dest='compiler',
            help='Use the specified compiler-version.',
            required=False,
        )
        self.parser.add_argument(
            "--no_graphics",
            "--nogfx",
            default=False,
            dest="no_graphics",
            help="Build with no graphics functionality (may not be supported by all builds).",
            required=False,
        )
        self.parser.add_argument(
            '--project',
            choices=projects.names,
            dest='project',
            help='The project to configure.',
        )
        self.parser.add_argument(
            '--secure',
            '--s',
            default=False,
            dest='secure',
            help='Generate a secure build.',
            required=False,
        )
        self.parser.add_argument(
            '--target',
            dest='target',
            help='Build target configuration.',
            required=False,
        )
        self.parser.add_argument(
            "--unity_build",
            "--unity",
            default=False,
            dest="unity_build",
            help="Generate a unity build.",
            required=False,
        )
        super().configureFromArguments()

    @property
    def description(self) -> str:
        return 'create a build configuration'

    def initialize_options(self):
        options = self.options
        if not options.project:
            raise Exception(f"no project specified; options are {','.join(projects.names)}")
        #if options.platform != platform.system().lower():
        #    raise Exception("cross-compiling not yet supported")
        self.platform = platforms.from_name(options.platform)
        if not self.platform:
            raise Exception(f"platform {options.platform} is not supported")
        self.compiler = compilers.from_versioned_name(options.compiler) if options.compiler else self.platform.default_compiler
        if not self.platform.supports_compiler(self.compiler):
            raise Exception(f"compiler {self.compiler} unsupported on {self.platform}")
        target_name = options.target if options.target else 'debug'
        self.target = targets.from_name(target_name)
        if not self.target:
            raise Exception(f"unknown target '{target_name}'")
        #if not self.compiler.supports_target(self.target):
        #    raise Exception(f"compiler {self.compiler} doesn't support target {self.target}")

    @property
    def name(self) -> str:
        return 'configure'

    def run(self) -> bool:
        self.configuration = configurations.from_options(self.options)
        print(self)
        # TIM - TODO: handle cmake failures
        cmake.generate_build_from_configuration(self.configuration)
        self.configuration.save()
        return True
