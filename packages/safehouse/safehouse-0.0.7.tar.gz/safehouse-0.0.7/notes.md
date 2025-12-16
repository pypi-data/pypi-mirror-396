psql -h localhost -p 5432 -U safehouse -d postgres

Next:
1. figure out configurator / more general docker configuration stuff so that safehouse services are installed and then metabase is configured to look at that db
2. figure out safehouse console, and how it should manage local services, and what options and mental model it should present to the user
3. figure out how to publish safehouse console as a package, goal is install one package, run safehouse console to run in `local` mode and install demo app (tic-tac-toe)

TODO:
CHECK 1. reorganize into `shared/trunk` for now
1. prototype events service, python sdk, build event taxonomy
1. figure out flow for us developers right now (clone from bit bucket, ...?)
1. figure out flow for customers
1. write up state of stuff for Ivan, Kevin... hopefully can publish in Discord and Confluence
1. organize into new repositories in bitbucket (need permission)
1. document standalone->local->live pattern of our services in Confluence (include diagrams)
1. document our services


### Services ###
## Modes ##
# Standalone
- Persist data to disk; transitionling to Local or Live will populate with that data.

# Local
- Run service(s) locally in docker containers; transitioning to Local will persist data, transitioning to live will auto-configure live version of the service.

# Live
- Paid version; live services are available via the internet and therefore can be player facing. Transitioning to Local auto-configures the local service; transferring to Standalone persists the data.


### Products ###
Products are feature-sets built on top of services that provide value on their own and as Safehouse plugins.


---------

  384  pip install hatch
  386  hatch --version
  388  hatch new --init
  426  hatch new --init
  430  hatch shell
  432  hatch shell
  434  hatch shell
  445  hatch version
  446  hatch version 0.0.4
  447  hatch build
  449  hatch build
  457  hatch publish
  583  hatch publish
  584  hatch build
  585  hatch publish
  586  hatch publish
  587  hatch publish
  588  hatch publish
  589  hatch publish
  603  hatch build
  604  hatch publish

# package workflow
- activate venv
- pip install -r requirements
- update safhouse version number
- install locally (pip install -e .)
- work against depending codebase in this vent
- when ready to ship, pulish new safehouse package version, commit changes to depending codebase