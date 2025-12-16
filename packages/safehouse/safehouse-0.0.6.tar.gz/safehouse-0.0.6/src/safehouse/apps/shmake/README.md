= Safe House Make (shmake) =
== configure ==
  default to identifying platform and "preferred" compiler for that platform,
  default architexture (x86_64) default build target (debug)
  `shmake configure --platform=linux --arch=x86_x6 --compiler=llvm --target=debug`


== select ==
  select the current build
  `shmake select ./builds/linux/gcc_x86_64/debug`


== build (default) ==
  compile the translation units for the current build and link them
  default to current build, if no current build defined prompts user to select one or configure one
  `shmake` # defaults to current build
  `shmake build` # defaults to current build
  `shmake build ./builds/linux/gcc_x86_64/debug` # selects ./builds/linux/gcc_x86_64/debug as current build and builds it


== clean ==
  default to current build, if no current build defined prompts user to select one or configure one

== current ==
  show information about currently selected build

== all synonym for `build` ==

== test ==
TIM - TBD HOW TO RESTRUCTURE TESTS TO MAKE THIS WORKABLE
  `shmake test` # runs all test binaries
  `shmake test all` # runs all test binaries


== package ==


== deploy ==


---
"cross compile" builds by running commands from docker containers
express dependencies betwee `shared`, `external`, `editor` and `engine` so that shmake knows what needs to be rebuilt
