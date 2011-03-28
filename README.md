The core Perl implementation of TagTime itself is in the following files:

* tagtimed.pl -- the TagTime daemon
* launch.pl -- launches the pinger by popping up an xterm
* ping.pl -- prompts for the tags
* util.pl -- utility functions
* settings.pl.template -- user-specific settings

In addtion are the following files:

* install.py -- install script
* grppings.pl -- grep your tagtime log file
* cntpings.pl -- tally pings in your log file matching given criteria

* tskedit.pl -- task editor / to-do list that integrates with TagTime
* tskproc.pl -- helper script used by tskedit.pl
* tasks.vim.template -- vim macros needed for the task editor

* merge.pl -- just a stub, for fixing/merging tagtime logs

The scripts directory contains various scripts we've used, like for various games and contests and commitment contracts and whatnot. 
Basically, incentive schemes for getting ourselves to procrastinate less.

The src directory currently contains Python code contributed by Jonathan Chang for a new back-end for TagTime. It hasn't yet been integrated.
It also contains the source for an Android app by Bethany Soule (bsoule).

Thanks also to Jesse Aldridge, Kevin Lochner, and Rob Felty for contributions.

For install instructions and other info about this project, see 
<http://padm.us/timepie>
