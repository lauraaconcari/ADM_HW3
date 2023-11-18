#!/bin/bash

# Merge course_i.tsv files
cat TSV/course_*.tsv | tr -d '\000' | sort -u > merged_courses.tsv

# Concatenate column_names.tsv and merged_courses.tsv
cat TSV/column_names.tsv merged_courses.tsv > merged_courses.tsv

# Set LANG to C to ensure a consistent interpretation of bytes
export LANG=C

# From now on, we will use the command "awk -F '\t'" to make sure that the .tsv created is tabulated well and that you can navigate within the column.

### Country with the highest number of Master's degrees
# Extract the 11th column (countries) from the TSV file, sort, count unique occurrences, sort again in descending order, 
# rearrange columns to display country, city, and count, and extract the first line.
most_courses_country=$(awk -F '\t' '{print $11}' merged_courses.tsv | LC_ALL=C sort | LC_ALL=C uniq -c | LC_ALL=C sort -nr | awk '{print $2 " " $3 " " $1}' | head -n 1)
echo "1. Country that offers the most Master's Degrees: $most_courses_country"

### City with the highest number of Master's degrees
# Similar process as above but for the 10th column (cities).
most_courses_city=$(awk -F '\t' '{print $10}' merged_courses.tsv | LC_ALL=C sort | LC_ALL=C uniq -c | LC_ALL=C sort -nr | awk '{print $2 " " $1}' | head -n 1)
echo "2. City offers the most Master's Degrees: $most_courses_city"

### Number of colleges with part-time education
# Extract colleges with "Part time" in the 4th column, sort, count unique occurrences.
num_part_time_colleges=$(awk -F '\t' '$4 ~ /Part time/ {print $2}' merged_courses.tsv | LC_ALL=C sort | LC_ALL=C uniq | wc -l)
echo "Number of colleges offer Part-Time education: $num_part_time_colleges"

### Percentage of courses in engineering
# Extract lines with "Engineering" or "Engineer" in the 1st column, count lines, and calculate the percentage.
engineering_courses=$(awk -F '\t' '$1 ~ /Engineering|Engineer/ {print}' merged_courses.tsv | wc -l)
percentage=$(awk "BEGIN {printf \"%.2f\", ($engineering_courses / 6000) * 100}")
echo "3. Percentage of courses in Engineering: $percentage%"














