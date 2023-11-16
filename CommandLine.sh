#!/bin/bash

# Question 1: Which country offers the most Master's Degrees? Which city?
most_masters_country=$(awk -F '\t' '{if ($2 == "Master") print $7}' final_merged_courses.tsv | sort | uniq -c | sort -nr | head -n 1 | awk '{print $2}')
most_masters_city=$(awk -F '\t' -v country="$most_masters_country" '{if ($2 == "Master" && $7 == country) print $6}' final_merged_courses.tsv | sort | uniq -c | sort -nr | head -n 1 | awk '{print $2}')

echo "1. Country with the most Master's Degrees: $most_masters_country"
echo "   City with the most Master's Degrees: $most_masters_city"

# Question 2: How many colleges offer Part-Time education?
part_time_colleges_count=$(awk -F '\t' '{if ($9 == "Part-Time") print $1}' final_merged_courses.tsv | sort | uniq | wc -l)
echo "2. Number of colleges offering Part-Time education: $part_time_colleges_count"

# Question 3: Print the percentage of courses in Engineering
total_courses=$(awk 'END {print NR}' final_merged_courses.tsv)
engineering_courses_count=$(awk -F '\t' '{if (tolower($3) ~ /engineer/) print}' final_merged_courses.tsv | wc -l)
percentage_engineering_courses=$(echo "scale=2; ($engineering_courses_count / $total_courses) * 100" | bc)

echo "3. Percentage of courses in Engineering: $percentage_engineering_courses%"
