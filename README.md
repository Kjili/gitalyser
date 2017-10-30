# Writing Progress Gitalyser

This project implements a text writing progress tracker based on 
existing git commit messages. Results include textual and visualised 
information about daily average, remarkable changes and progress.
It will also provide you with some motivational comments to keep going.

It analyses all git log messages from a given file that contain a 
keyword followed by a number with a space in between. The default use 
case is to track writing progress in fractions of pages
with the number representing the current page at the time of the 
commit.
Those keywords must of course be manually introduced to the commits.

So far keywords can only be changed directly in (line 9 of) the source 
code.

An example when using the default keywords ('S.', 'Seite') and 
calling the program from a git repository with a git log containing 
167 commits that include the keyword number pattern using:

```python ../gitalyse/gitalyse.py filename -r -t 300 -n 5```

results in the following output:

	Detected 167 commits, failed to detect 46 commits.
	Between: 
	9dc2bc4	2017-10-16T18:20:19+02:00	filename: S. 303
	77b76ee	2016-10-01T20:05:05+02:00	filename S. 6
	380 days total passed while writing 297 pages
	That is an average of 0.781578947368421 pages per day
	For the last 5 commits:
	9dc2bc4	2017-10-16T18:20:19+02:00	filename: S. 303
	b03af46	2017-10-16T01:13:52+02:00	filename: S. 295
	5a021af	2017-10-15T21:39:39+02:00	filename: S. 294
	ce5ffae	2017-10-15T17:46:49+02:00	filename: S. 291
	9fba437	2017-10-14T17:14:39+02:00	filename: S. 291
	3 days total passed while writing 12 pages
	That is an average of 4.0 pages per day
	 - great, keep going! :D

and the following visualisation:

![alt text](https://github.com/Kjili/gitalyser/raw/master/example-fig.png "Example Figure")

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
