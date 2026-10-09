# Answer correctness evaluation

Model: `llama3.1:8b`   Date: 2026-10-09   Questions: 31/31

Correct answers were checked by hand against the sources in `data/answer_test.csv`.

## Overall

| Method | Correct | Wrong | No guess | Searches |
|---|---|---|---|---|
| Memory only | 19/31 (61%) | 8 | 4 | 0 |
| Always search | 26/31 (83%) | 3 | 2 | 31 |
| Router (both checks) | 25/31 (80%) | 4 | 2 | 15 |

## Correct answers by question type

| Question type | Memory only | Always search | Router (both checks) |
|---|---|---|---|
| Stable, well known | 15/15 | 15/15 | 15/15 |
| Stable, rare (incomplete) | 2/9 | 5/9 | 5/9 |
| Changes over time (outdated) | 2/7 | 6/7 | 5/7 |

## Wrong answers (for manual review)

- **Memory only**, Q16 *Who wrote the Swahili novel Kufa Kuzikana?* (expected: Walibora): The Swahili novel "Kufa Kuzikana" was written by Muhajir.
- **Always search**, Q17 *Who was the first Kenyan woman to earn a PhD?* (expected: Maathai): Florence Oloo [4].
- **Router (both checks)**, Q17 *Who was the first Kenyan woman to earn a PhD?* (expected: Maathai): Florence Oloo [4].
- **Memory only**, Q20 *Which small river flows through the centre of Gangneung?* (expected: Namdaecheon): The small river that flows through the centre of Gangneung is the Gyeonggang River.
- **Always search**, Q21 *What is the height in metres of Ulsanbawi rock in Seoraksan?* (expected: 873): The height of Ulsanbawi rock in Seoraksan is 874 m [1].
- **Router (both checks)**, Q21 *What is the height in metres of Ulsanbawi rock in Seoraksan?* (expected: 873): The height of Ulsanbawi rock in Seoraksan is 874 m [1].
- **Memory only**, Q23 *What traditional song is the melody of the Kenyan national anthem based on?* (expected: Pokomo): The melody of the Kenyan national anthem is based on the traditional song "Ee Mungu Nguvu Yetu", which is a Swahili hymn.
- **Memory only**, Q24 *What is the Korean name of the red snow crab caught near Sokcho?* (expected: hongge): The Korean name for the red snow crab is "chunhae" (, ).
- **Always search**, Q24 *What is the Korean name of the red snow crab caught near Sokcho?* (expected: hongge): The Korean name of the red snow crab caught near Sokcho is "daege" [6].
- **Router (both checks)**, Q24 *What is the Korean name of the red snow crab caught near Sokcho?* (expected: hongge): The Korean name of the red snow crab caught near Sokcho is "daege" [6].
- **Memory only**, Q25 *Who is the CEO of Naver?* (expected: Choi Soo-yeon): The CEO of Naver is Lee Hae-joon.
- **Router (both checks)**, Q25 *Who is the CEO of Naver?* (expected: Choi Soo-yeon): The CEO of Naver is Lee Hae-joon.
- **Memory only**, Q26 *Who manages Kakao these days?* (expected: Chung Shin-a): Kakao is a South Korean company, and its management is led by Lee Jae-uk, who serves as the CEO.
- **Memory only**, Q27 *Who leads SK hynix?* (expected: Kwak Noh-jung): The CEO of SK hynix is Lee Seok-hee.
- **Memory only**, Q30 *Who is the prime minister of Japan?* (expected: Takaichi): The current Prime Minister of Japan is Fumio Kishida. He has been in office since October 2021.

**Scoring:** *correct* = the answer contains an accepted answer; *no guess* = the system said it could not find or does not know; *wrong* = a confident answer that is wrong or outdated. Automatic matching can make mistakes - check `answer_evaluation.csv`.
