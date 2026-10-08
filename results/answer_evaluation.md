# Answer correctness evaluation

Model: `llama3.1:8b`   Date: 2026-10-08   Questions: 31/31

Correct answers were checked by hand against the sources in `data/answer_test.csv`.

## Overall

| Method | Correct | Wrong | No guess | Searches |
|---|---|---|---|---|
| Memory only | 19/31 (61%) | 8 | 4 | 0 |
| Always search | 19/31 (61%) | 3 | 9 | 31 |
| Router (both checks) | 21/31 (67%) | 3 | 7 | 15 |

## Correct answers by question type

| Question type | Memory only | Always search | Router (both checks) |
|---|---|---|---|
| Stable, well known | 15/15 | 13/15 | 15/15 |
| Stable, rare (incomplete) | 2/9 | 4/9 | 4/9 |
| Changes over time (outdated) | 2/7 | 2/7 | 2/7 |

## Wrong answers (for manual review)

- **Memory only**, Q16 *Who wrote the Swahili novel Kufa Kuzikana?* (expected: Walibora): The Swahili novel "Kufa Kuzikana" was written by Muhajir.
- **Memory only**, Q20 *Which small river flows through the centre of Gangneung?* (expected: Namdaecheon): The small river that flows through the centre of Gangneung is the Gyeonggang River.
- **Memory only**, Q23 *What traditional song is the melody of the Kenyan national anthem based on?* (expected: Pokomo): The melody of the Kenyan national anthem is based on the traditional song "Ee Mungu Nguvu Yetu", which is a Swahili hymn.
- **Memory only**, Q24 *What is the Korean name of the red snow crab caught near Sokcho?* (expected: hongge): The Korean name for the red snow crab is "chunhae" (, ).
- **Memory only**, Q25 *Who is the CEO of Naver?* (expected: Choi Soo-yeon): The CEO of Naver is Lee Hae-joon.
- **Always search**, Q25 *Who is the CEO of Naver?* (expected: Choi Soo-yeon): Han Seong-sook was the CEO of Naver Corporation from 2017 to 2021 [2].
- **Router (both checks)**, Q25 *Who is the CEO of Naver?* (expected: Choi Soo-yeon): The CEO of Naver is Lee Hae-joon. (Note: this can change over time. Please check an official source.)
- **Memory only**, Q26 *Who manages Kakao these days?* (expected: Chung Shin-a): Kakao is a South Korean company, and its management is led by Lee Jae-uk, who serves as the CEO.
- **Always search**, Q26 *Who manages Kakao these days?* (expected: Chung Shin-a): Kakao is managed by Kakao Entertainment, a subsidiary of Kakao, which was established in 2021 after the merger of KakaoPage and Kakao M. [2]
- **Router (both checks)**, Q26 *Who manages Kakao these days?* (expected: Chung Shin-a): Kakao is managed by Kakao Entertainment, a subsidiary of Kakao, which was established in 2021 after the merger of KakaoPage and Kakao M. [2]
- **Memory only**, Q27 *Who leads SK hynix?* (expected: Kwak Noh-jung): The CEO of SK hynix is Lee Seok-hee.
- **Always search**, Q27 *Who leads SK hynix?* (expected: Kwak Noh-jung): Chey Tae-won has been chairman of SK Hynix since 2012 [2].
- **Router (both checks)**, Q27 *Who leads SK hynix?* (expected: Kwak Noh-jung): Chey Tae-won has been chairman of SK Hynix since 2012 [2].
- **Memory only**, Q30 *Who is the prime minister of Japan?* (expected: Takaichi): The current Prime Minister of Japan is Fumio Kishida. He has been in office since October 2021.

**Scoring:** *correct* = the answer contains an accepted answer; *no guess* = the system said it could not find or does not know; *wrong* = a confident answer that is wrong or outdated. Automatic matching can make mistakes - check `answer_evaluation.csv`.
