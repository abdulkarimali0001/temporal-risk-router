# Korean questions

Model `llama3.1:8b` · 2026-10-09 · 33 Korean questions (answers verified 2026-10-08). Search: Wikipedia + live web.

| Method | Correct | Wrong | No guess | Searched |
|---|---|---|---|---|
| Memory only | 10/33 (30%) | 23 | 0 | 0 |
| Search: English Wikipedia only | 19/33 (58%) | 9 | 5 | 33 |
| Search: Korean + English | 31/33 (94%) | 2 | 0 | 33 |
| Router (both checks) | 28/33 (85%) | 5 | 0 | 26 |

| Question type | n | Memory only | Search: English Wikipedia only | Search: Korean + English | Router (both checks) |
|---|---|---|---|---|---|
| General knowledge | 10 | 7/10 | 9/10 | 9/10 | 9/10 |
| Local / rare facts | 10 | 2/10 | 3/10 | 10/10 | 8/10 |
| Changes over time | 13 | 1/13 | 7/13 | 12/13 | 11/13 |

## Wrong answers

- **Memory only**, ko03 남한에서 가장 높은 산은 무엇인가요? (expected 한라산): 남한에서 가장 높은 산은 백두산입니다. 높이는 2,744m입니다.
- **Memory only**, ko04 이순신 장군이 사용한 거북 모양의 배 이름은 무엇인가요? (expected 거북선): 이순신 장군이 사용한 거북 모양의 배 이름은 무거와 진무입니다.
- **Memory only**, ko08 대한민국의 화폐 단위는 무엇인가요? (expected 원): 대한민국의 화폐 단위는 원입니다. 1 원은 100전으로 나뉘며, 1,000 원은 1 만 원입니다.
- **Search: English Wikipedia only**, ko08 대한민국의 화폐 단위는 무엇인가요? (expected 원): 대한민국의 화폐 단위는 원입니다. [1]
- **Search: Korean + English**, ko08 대한민국의 화폐 단위는 무엇인가요? (expected 원): 대한민국의 화폐 단위는 원입니다. [2]
- **Router (both checks)**, ko08 대한민국의 화폐 단위는 무엇인가요? (expected 원): 대한민국의 화폐 단위는 원입니다. [2]
- **Memory only**, ko11 설악산 국립공원의 최고봉 이름은 무엇인가요? (expected 대청봉): 설악산 국립공원의 최고봉은 백운대입니다. 높이는 1,708m입니다.
- **Router (both checks)**, ko11 설악산 국립공원의 최고봉 이름은 무엇인가요? (expected 대청봉): 설악산 국립공원의 최고봉은 백운대입니다. 높이는 1,708m입니다. (Note: this can change over time. Please check an official source.)
- **Memory only**, ko13 강릉단오제가 유네스코 인류무형문화유산에 등재된 해는 몇 년인가요? (expected 2005): 강릉단오제가 유네스코 인류무형문화유산에 등재된 해는 2018년입니다.
- **Search: English Wikipedia only**, ko13 강릉단오제가 유네스코 인류무형문화유산에 등재된 해는 몇 년인가요? (expected 2005): 2024년입니다. [2]
- **Memory only**, ko15 속초 엑스포 타워가 있는 석호의 이름은 무엇인가요? (expected 청초호): 속초 엑스포 타워가 있는 석호의 이름은 대청호입니다.
- **Search: English Wikipedia only**, ko15 속초 엑스포 타워가 있는 석호의 이름은 무엇인가요? (expected 청초호): 석호입니다. [2]
- **Memory only**, ko16 강릉 오죽헌에서 태어난 율곡 이이의 어머니는 누구인가요? (expected 신사임당): 율곡 이이의 어머니는 이씨입니다.
- **Memory only**, ko17 대한민국 최초의 국립공원은 어디인가요? (expected 지리산): 대한민국 최초의 국립공원은 1967년 10월 28일 설립된 주왕산 국립공원입니다.
- **Search: English Wikipedia only**, ko17 대한민국 최초의 국립공원은 어디인가요? (expected 지리산): 대한민국 최초의 국립공원은 경주국립공원입니다. [1]

(Translation: The first national park in South Korea is Gyeongju National Park.)
- **Memory only**, ko18 훈민정음 해례본이 발견된 해는 몇 년인가요? (expected 1940): 훈민정음 해례본이 발견된 해는 1976년입니다.
- **Memory only**, ko19 강원특별자치도가 출범한 날짜는 언제인가요? (expected 2023년 6월 11일): 강원특별자치도가 출범한 날짜는 2026년 10월 8일입니다.
- **Router (both checks)**, ko19 강원특별자치도가 출범한 날짜는 언제인가요? (expected 2023년 6월 11일): 강원특별자치도가 출범한 날짜는 2026년 10월 8일입니다.
- **Memory only**, ko20 국보 제1호였던 문화유산은 무엇인가요? (expected 숭례문): 국보 제1호는 경주 불국사 삼층전입니다.
- **Search: English Wikipedia only**, ko20 국보 제1호였던 문화유산은 무엇인가요? (expected 숭례문): 현무문입니다. [1]
- **Memory only**, ko21 현재 대한민국 대통령은 누구인가요? (expected 이재명): 현재 대한민국 대통령은 윤석열입니다. 2022년 5월 10일부터 대통령직을 맡고 있습니다.
- **Memory only**, ko22 현재 대한민국 국무총리는 누구인가요? (expected 김민석): 현재 대한민국 국무총리는 한덕수입니다.
- **Search: English Wikipedia only**, ko22 현재 대한민국 국무총리는 누구인가요? (expected 김민석): 현재 대한민국 국무총리는 한성숙입니다. [2]
- **Search: Korean + English**, ko22 현재 대한민국 국무총리는 누구인가요? (expected 김민석): 현재 대한민국 국무총리는 한성숙입니다. [1]
- **Router (both checks)**, ko22 현재 대한민국 국무총리는 누구인가요? (expected 김민석): 현재 대한민국 국무총리는 한성숙입니다. [1]
- **Memory only**, ko24 현재 강원특별자치도지사는 누구인가요? (expected 우상호): 현재 강원특별자치도지사는 한정애입니다.
- **Memory only**, ko25 현재 속초시장은 누구인가요? (expected 이병선): 속초시장은 2026년 현재 이인제입니다.
- **Search: English Wikipedia only**, ko25 현재 속초시장은 누구인가요? (expected 이병선): 현재 속초시장은 Shim Woo-jung입니다. [1]
- **Memory only**, ko26 현재 한국은행 총재는 누구인가요? (expected 신현송): 현재 한국은행 총재는 이인제입니다.
- **Memory only**, ko27 현재 국회의장은 누구인가요? (expected 조정식): 현재 국회의장은 김진태입니다.
- **Memory only**, ko28 삼성전자의 현재 대표이사는 누구인가요? (expected 전영현): 삼성전자의 현재 대표이사는 오세혁입니다. 그는 2021년 5월 1일부터 현재까지 대표이사로 재직 중입니다.
- **Memory only**, ko29 SK하이닉스의 현재 대표이사(CEO)는 누구인가요? (expected 곽노정): SK하이닉스의 현재 대표이사는 권영세입니다. 그는 2022년 3월 1일부터 현재까지 CEO로 재직 중입니다.
- **Memory only**, ko31 손흥민의 현재 소속팀은 어디인가요? (expected LAFC): 현재 손흥민은 Tottenham Hotspur에서 뛰고 있습니다.
- **Search: English Wikipedia only**, ko31 손흥민의 현재 소속팀은 어디인가요? (expected LAFC): 손흥민의 현재 소속팀은 Tottenham Hotspur입니다. [3]
- **Memory only**, ko32 올해 한국의 최저임금(시급)은 얼마인가요? (expected 10,320): 2026년 현재 한국의 최저임금은 10,000원입니다.
- **Search: English Wikipedia only**, ko32 올해 한국의 최저임금(시급)은 얼마인가요? (expected 10,320): 2025년 기준으로, 한국의 최저임금은 11달러입니다. [1]
- **Router (both checks)**, ko32 올해 한국의 최저임금(시급)은 얼마인가요? (expected 10,320): 2026년 현재 한국의 최저임금은 10,000원입니다. (Note: this can change over time. Please check an official source.)
- **Memory only**, ko33 가장 최근 KBO 한국시리즈 우승팀은 어디인가요? (expected LG 트윈스): 2026년 10월 8일 현재 가장 최근 KBO 한국시리즈 우승팀은 SK 와이번스입니다.
- **Memory only**, ko34 가장 최근 K리그1 우승팀은 어디인가요? (expected 전북 현대): 2026년 10월 8일 현재 가장 최근 K리그1 우승팀은 FC 서울입니다.
