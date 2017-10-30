# Writing Progress Gitalyser

This project implements a text writing progress tracker based on 
existing git commit messages. Results include textual and visualised 
information about daily average, remarkable changes and progress.

It analyses all git log messages from a given file that contain a 
keyword followed by a number with a space in between. The default use 
case is to track writing progress in fractions of pages
with the number representing the current page at the time of the 
commit.
Those keywords must of course be manually introduced to the commits.

For example using the default keywords ('S.', 'Seite') and calling the 
program from a git repository with a git log containing three entries 
with messages including the following

	- S. 15
	- S. 7
	- S. 3

will show you some analysis on a progress of 12 pages in total 
respecting the date of the commit.
It will also provide you with some motivational comments to keep going.

So far keywords can only be changed directly in (line 9 of) the source 
code.

Using the help by calling `python gitalyser.py -h` is highly 
recommended to explore additional features.

# Requirements:

	- python >= 3.6 (not tested for lower versions)
	- python-dateutil
	- python-matplotlib (optional)
	- git (and commits with the specified keyword number patterns)

Limiting the amount of characters on a page to a fixed number (e.g. 
1800), setting the font size to a fixed value and defining a fixed font 
is highly recommended. Primarily the first as otherwise pages may vary 
(e.g. due to software updates) and become infeasible for analysis.
Changing the keyword and not relying on pages would be an alternative 
but has not been a use case yet.

# License

This project is licensed under the MIT License.
