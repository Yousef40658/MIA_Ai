# Dataset Exploration Notes

## Results Dataset (`results.csv`)

- 49520 matches is very reliable for data extraction.
- Mean home score is 1.75 while mean away score is 1.18, makes sense that teams at home have better chances, is it due to confidence or some laser shit like Egypt vs Senegal?
- Until the 99 percentile, data is kinda realistic. Maximum home score and maximum away score are weird tho 31 and 21.
- Only 2 NULL values :O and 0 duplicated cols -> makes us sure that no match was entered twice [date differs].
- Data is severely skewed, std is close to mean and there is about 1.5% outliers, hmm so 1.5% of the matches end with more than 7 goals.
- More than i expected anyway.
- Weak correlation between both teams scores, but it being negative indicates that when the other team scores more, the other team tends to score less [since it's very weak its negligible but i would say it represents "morals"].

---

## Former Names Dataset (`former_names.csv`)

- Okay so this will be used to map them to their current name to get accurate results.

---

## Goal Scorers Dataset (`goalscorers.csv`)

- Half the goals occur between the 28m and 73m, with the fastest goal at 1 minute and the most clutch goal at 122m.
- 99% goals occur between the 90 minute mark, makes extra sense because not all matches have extra time.
- There are some null values regarding the minute.
- Own goals are almost 2% of football goals (7pipy M.hany).
- Some of the goals are duplicated, i've searched in Google and its very few players that scored 2 goals in the same minute, with most of them in the Premier League not WC.
- So this part of the data need to be removed.
- Very small skewness, distribution of goals is symmetric so there is no tendency of goals in general happening early or late [maybe different strategies balance out].
- Penalities make up for 6.82% of the goals.

---

## Shootouts Dataset (`shootouts.csv`)

- 683 shootouts making about 1.4% of total matches.
- Most first shooter information is missing.
- Egypt is the most frequent winner of shootout, would be useful to study if it's due to us winning there or us reaching it far more than others | Bayes'.