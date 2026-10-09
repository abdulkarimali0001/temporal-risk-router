# Korean questions

Model `qwen2.5:7b` · 2026-10-09 · 34 Korean questions (answers verified 2026-10-08). Search: Wikipedia + live web.

| Method | Correct | Wrong | No guess | Searched |
|---|---|---|---|---|
| Memory only | 9/34 (26%) | 25 | 0 | 0 |
| Search: English Wikipedia only | 17/34 (50%) | 8 | 9 | 34 |
| Search: Korean + English | 32/34 (94%) | 2 | 0 | 34 |
| Router (both checks) | 28/34 (82%) | 6 | 0 | 27 |

| Question type | n | Memory only | Search: English Wikipedia only | Search: Korean + English | Router (both checks) |
|---|---|---|---|---|---|
| General knowledge | 10 | 8/10 | 8/10 | 10/10 | 10/10 |
| Local / rare facts | 10 | 1/10 | 2/10 | 10/10 | 6/10 |
| Changes over time | 14 | 0/14 | 7/14 | 12/14 | 12/14 |

## Wrong answers

- **Memory only**, ko03 남한에서 가장 높은 산은 무엇인가요? (expected 한라산): 남한에서 가장 높은 산은 백두산입니다.
- **Search: English Wikipedia only**, ko03 남한에서 가장 높은 산은 무엇인가요? (expected 한라산): 남한에서 가장 높은 산은 지리산입니다 [1].
- **Memory only**, ko08 대한민국의 화폐 단위는 무엇인가요? (expected 원): 대한민국의 화폐 단위는 원입니다.
- **Search: English Wikipedia only**, ko10 김치는 주로 어떤 채소로 만드나요? (expected 배추): 김치는 주로 캔파프리카, 대파, 무, 양파, 청경채, 인도산 무 등 다양한 채소로 만듭니다. [4]
- **Memory only**, ko11 설악산 국립공원의 최고봉 이름은 무엇인가요? (expected 대청봉): 설악산 국립공원의 최고봉 이름은 백두산입니다.但实际上，根据您的问题，正确的回答应该是： 설악산 국립공원의 최고봉 이름은 설악산입니다.
- **Memory only**, ko12 설악산 대청봉의 높이는 몇 미터인가요? (expected 1708): 설악산 대청봉의 높이는 약 1,950미터입니다.
- **Router (both checks)**, ko12 설악산 대청봉의 높이는 몇 미터인가요? (expected 1708): 설악산 대청봉의 높이는 약 1,950미터입니다.
- **Memory only**, ko13 강릉단오제가 유네스코 인류무형문화유산에 등재된 해는 몇 년인가요? (expected 2005): 강릉단오제가 유네스코 인류무형문화유산에 등재된 해는 2014년입니다.
- **Router (both checks)**, ko13 강릉단오제가 유네스코 인류무형문화유산에 등재된 해는 몇 년인가요? (expected 2005): 강릉단오제가 유네스코 인류무형문화유산에 등재된 해는 2014년입니다.
- **Memory only**, ko15 속초 엑스포 타워가 있는 석호의 이름은 무엇인가요? (expected 청초호): 속초 엑스포 타워가 있는 석호의 이름은 속초만입니다.
- **Memory only**, ko16 강릉 오죽헌에서 태어난 율곡 이이의 어머니는 누구인가요? (expected 신사임당): 율곡 이이의 어머니는 정씨입니다.
- **Memory only**, ko17 대한민국 최초의 국립공원은 어디인가요? (expected 지리산): 대한민국 최초의 국립공원은 백두산国立公园(백두산国立公园在1970年被指定为国营自然保护区，但如果是按照韩国的标准，应该是1970년에 설립된 첫 번째 국립공원인 백두산国立公园).
- **Memory only**, ko18 훈민정음 해례본이 발견된 해는 몇 년인가요? (expected 1940): 훈민정음 해례본이 발견된 해는 1446년입니다.
- **Router (both checks)**, ko18 훈민정음 해례본이 발견된 해는 몇 년인가요? (expected 1940): 훈민정음 해례본이 발견된 해는 1446년입니다. (Note: this can change over time. Please check an official source.)
- **Memory only**, ko19 강원특별자치도가 출범한 날짜는 언제인가요? (expected 2023년 6월 11일): 강원특별자치도가 출범한 날짜는 2005년 12월 1일입니다.
- **Router (both checks)**, ko19 강원특별자치도가 출범한 날짜는 언제인가요? (expected 2023년 6월 11일): 강원특별자치도가 출범한 날짜는 2005년 12월 1일입니다.
- **Memory only**, ko20 국보 제1호였던 문화유산은 무엇인가요? (expected 숭례문): 국보 제1호는괘위장입니다.
- **Memory only**, ko21 현재 대한민국 대통령은 누구인가요? (expected 이재명): 현재 대한민국 대통령은 문재인 대통령입니다. 하지만 이 정보는 2026년 10월 8일 기준으로, 실제 답변과 다를 수 있습니다.
- **Memory only**, ko22 현재 대한민국 국무총리는 누구인가요? (expected 김민석): 현재 대한민국 국무총리는 권영진 총리가 맡고 있습니다. 하지만 이 정보는 가상의 답변이며, 실제 날짜에 따라 달라질 수 있으니 참고하시기 바랍니다.
- **Search: English Wikipedia only**, ko22 현재 대한민국 국무총리는 누구인가요? (expected 김민석): 현재 대한민국 국무총리는 한성숙입니다 [2].
- **Search: Korean + English**, ko22 현재 대한민국 국무총리는 누구인가요? (expected 김민석): 현재 대한민국 국무총리는 한성숙입니다 [1] [2].
- **Router (both checks)**, ko22 현재 대한민국 국무총리는 누구인가요? (expected 김민석): 현재 대한민국 국무총리는 한성숙입니다 [1] [2].
- **Memory only**, ko23 현재 서울특별시장은 누구인가요? (expected 오세훈): 현재 서울특별시장은 이재명입니다.
- **Memory only**, ko24 현재 강원특별자치도지사는 누구인가요? (expected 우상호): 현재 강원특별자치도지사는 송영길입니다.
- **Memory only**, ko25 현재 속초시장은 누구인가요? (expected 이병선): 현재 속초시장은 김동준입니다.
- **Memory only**, ko26 현재 한국은행 총재는 누구인가요? (expected 신현송): 현재 한국은행 총재는 이정현입니다.
- **Memory only**, ko27 현재 국회의장은 누구인가요? (expected 조정식): 현재의 국회의장은 안민석입니다.
- **Memory only**, ko28 삼성전자의 현재 대표이사는 누구인가요? (expected 전영현): 삼성전자의 현재 대표이사는 김현석 사장입니다. 하지만 이 정보는 변경될 수 있으므로, 최신 정보를 확인하시기 바랍니다.
- **Search: English Wikipedia only**, ko28 삼성전자의 현재 대표이사는 누구인가요? (expected 전영현): 삼성전자의 현재 대표이사는 이재용입니다. [4]
- **Memory only**, ko29 SK하이닉스의 현재 대표이사(CEO)는 누구인가요? (expected 곽노정): SK하이닉스의 현재 대표이사는 김석진입니다.
- **Memory only**, ko30 네이버의 현재 대표이사는 누구인가요? (expected 최수연): 네이버의 현재 대표이사는 윤정수입니다.
- **Search: English Wikipedia only**, ko30 네이버의 현재 대표이사는 누구인가요? (expected 최수연): 네이버의 현재 대표이사는 이해진입니다. [1]
- **Search: Korean + English**, ko30 네이버의 현재 대표이사는 누구인가요? (expected 최수연): 네이버의 현재 대표이사는 한성숙입니다 [7].
- **Router (both checks)**, ko30 네이버의 현재 대표이사는 누구인가요? (expected 최수연): 네이버의 현재 대표이사는 한성숙입니다 [7].
- **Memory only**, ko31 손흥민의 현재 소속팀은 어디인가요? (expected LAFC): 손흥민의 현재 소속팀은 토트넘 홋스퍼 FC입니다.
- **Search: English Wikipedia only**, ko31 손흥민의 현재 소속팀은 어디인가요? (expected LAFC): 손흥민의 현재 소속팀은 토트넘 홋스퍼입니다 [3]।
- **Memory only**, ko32 올해 한국의 최저임금(시급)은 얼마인가요? (expected 10,320): 2026년 한국의 최저임금은 매일 8,460원입니다.
- **Search: English Wikipedia only**, ko32 올해 한국의 최저임금(시급)은 얼마인가요? (expected 10,320): 올해 2026년 한국의 최저임금은 7,530 원입니다. [4]
- **Memory only**, ko33 가장 최근 KBO 한국시리즈 우승팀은 어디인가요? (expected LG 트윈스): 2026년 한국시리즈 우승팀은 아직 결정되지 않았습니다. 최신 정보를 확인하려면 2026년 10월을 기다려보세요.
- **Memory only**, ko34 가장 최근 K리그1 우승팀은 어디인가요? (expected 전북 현대): 2026년 10월 8일 현재의 가장 최근 K리그1 우승팀은 2026년 시즌 종료 시점에서 결정될 것입니다. 이전 시즌의 우승 팀은 해당 정보가 주어지지 않았습니다.
- **Search: English Wikipedia only**, ko34 가장 최근 K리그1 우승팀은 어디인가요? (expected 전북 현대): Gen.G가 2026 LCK 시즌에서 우승하여 가장 최근 K리그1 우승팀이기도 합니다.[2]
