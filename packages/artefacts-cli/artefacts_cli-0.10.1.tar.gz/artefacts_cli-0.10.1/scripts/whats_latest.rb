#!/usr/bin/env ruby

#
# Parse our CHANGELOG.md file to get the latest release "block"
# and prints it to stdout.
#

cl = open("CHANGELOG.md").read
start = cl.index /## \[Unreleased\]/
finish = cl.index /## \[\d\.\d+\.\d+\] - \d{4}-\d{2}-\d{2}/
print cl[start...finish].chomp
