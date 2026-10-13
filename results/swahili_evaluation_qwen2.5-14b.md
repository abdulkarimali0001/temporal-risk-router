# Swahili questions

Model `qwen2.5:14b` · 2026-10-12 · 32 Swahili questions (answers verified 2026-10-09). Search: Wikipedia + live web.

| Method | Correct | Wrong | No guess | Searched |
|---|---|---|---|---|
| Memory only | 10/32 (31%) | 22 | 0 | 0 |
| Search: English Wikipedia only | 20/32 (62%) | 12 | 0 | 32 |
| Search: own language + English | 27/32 (84%) | 4 | 1 | 32 |
| Router (both checks) | 26/32 (81%) | 5 | 1 | 25 |

| Question type | n | Memory only | Search: English Wikipedia only | Search: own language + English | Router (both checks) |
|---|---|---|---|---|---|
| General knowledge | 10 | 6/10 | 6/10 | 8/10 | 8/10 |
| Local / rare facts | 10 | 1/10 | 4/10 | 9/10 | 8/10 |
| Changes over time | 12 | 3/12 | 10/12 | 10/12 | 10/12 |

## Wrong answers

- **Memory only**, sw02 Mlima mrefu zaidi barani Afrika ni upi? (expected Kilimanjaro): Mlima mrefu kabisa barani Afrika ni Mlima Everest, ambao ni njia ya Asia.
- **Search: English Wikipedia only**, sw02 Mlima mrefu zaidi barani Afrika ni upi? (expected Kilimanjaro): Mlima mrefu zaidi barani Afrika ni Aconcagua [2].
- **Memory only**, sw03 Ziwa kubwa zaidi barani Afrika ni lipi? (expected Victoria): Ziwa zaidi barani Afrika ni katika mataja ya jijini na mifumo miwili kati ya America, Rusia, Kanada na ujuzi wa pia za Antarktika.
- **Search: English Wikipedia only**, sw03 Ziwa kubwa zaidi barani Afrika ni lipi? (expected Victoria): Ziwa kubwa zaidi barani Afrika ni Greenland [1].
- **Search: English Wikipedia only**, sw06 Kenya ilipata uhuru mwaka gani? (expected 1963): Kenya ilipata uhuru mwaka 2002 [1].
- **Memory only**, sw08 Tanzania hutumia sarafu gani? (expected shilingi): Tanzania hutumia chfumu kama sarafu mkuu yake, ikiwa ni jinsi unatafsiri kwa kawaida, bali hutumia pia sarafu za wengine kama US Dollar kwa ajili ya biashara na
- **Memory only**, sw10 Mto mrefu zaidi duniani ni upi? (expected Nile): Mto mrefu mkuu duniani ni Amazon ya Afrika Kusini.
- **Search: English Wikipedia only**, sw10 Mto mrefu zaidi duniani ni upi? (expected Nile): Mto mrefu zaidi duniani kulingana na maadili yanayotolewa katika maelezo yanayopatikana ni Amazon [1].
- **Search: own language + English**, sw10 Mto mrefu zaidi duniani ni upi? (expected Nile): Mto mrefu zaidi duniani ni Amazon [1].
- **Router (both checks)**, sw10 Mto mrefu zaidi duniani ni upi? (expected Nile): Mto mrefu zaidi duniani ni Amazon [1].
- **Memory only**, sw11 Nani aliandika riwaya ya Kufa Kuzikana? (expected Ken Walibora): Ernest Hemingway aliandika riwaya ya "The Old Man and the Sea" (Kufa Kuzikana).
- **Search: English Wikipedia only**, sw11 Nani aliandika riwaya ya Kufa Kuzikana? (expected Ken Walibora): Riwaya ya Kufa Kuzikana aliandikwa na Harper Lee [3].
- **Memory only**, sw12 Nani aliandika riwaya ya Rosa Mistika? (expected Euphrase Kezilahabi): Rosa Mistika hii ni riwaya kuu na majina yasiyoyapitikana kwa uingilishi kabla ya kusoma au kuja na vituo vya kujifunza. Sina mauduio sahihi kuhusu nani aliandi
- **Search: English Wikipedia only**, sw12 Nani aliandika riwaya ya Rosa Mistika? (expected Euphrase Kezilahabi): Riwaya ya Rosa Mistika aliandika na Steven Saylor [1].
- **Search: own language + English**, sw12 Nani aliandika riwaya ya Rosa Mistika? (expected Euphrase Kezilahabi): Mwandishi wa riwaya ya Rosa Mistika ni Shaaban Robert [1]. Bado ni Shaaban Robert kwa sababu hii ni maelezo wa kusafirishwa na hapa huchangia kuonekana maelezo 
- **Router (both checks)**, sw12 Nani aliandika riwaya ya Rosa Mistika? (expected Euphrase Kezilahabi): Mwandishi wa riwaya ya Rosa Mistika ni Shaaban Robert [1]. Bado ni Shaaban Robert kwa sababu hii ni maelezo wa kusafirishwa na hapa huchangia kuonekana maelezo 
- **Memory only**, sw13 Nani aliandika riwaya ya Siku Njema? (expected Ken Walibora): Elialesi Ikimonde aliandika riwaya ya Siku Njema.
- **Search: English Wikipedia only**, sw13 Nani aliandika riwaya ya Siku Njema? (expected Ken Walibora): Neil Gaiman aliandika riwaya ya Siku Njema [1].
- **Memory only**, sw14 Shaaban Robert alizaliwa mwaka gani? (expected 1909): Shaaban Robert alizaliwa mwaka 1934.
- **Memory only**, sw15 Nani aliandika riwaya ya Utengano? (expected Said Ahmed Mohamed): Utengano uliandwiwa na Mark Twain.
- **Search: English Wikipedia only**, sw15 Nani aliandika riwaya ya Utengano? (expected Said Ahmed Mohamed): Katie Kitamura aliandika riwaya ya Utengano [1].
- **Memory only**, sw16 Nani aliandika riwaya ya Kiu? (expected Mohammed Suleiman Mohammed): Kiu una kuandwa na mwanzo wa ushairi wa China, Lu Xun. Basi sisi tutaonyesha kuhusu Kiu kama kitabu kikamilisho, ni zaruni zote za kifupi zinazohusu historia ya
- **Search: English Wikipedia only**, sw16 Nani aliandika riwaya ya Kiu? (expected Mohammed Suleiman Mohammed): John aliandika riwaya ya Kiu [1].
- **Memory only**, sw17 Mji wa Kale wa Lamu uliorodheshwa kuwa Urithi wa Dunia wa UNESCO mwaka gani? (expected 2001): Mji wa Kale wa Lamu uliorodheshwa kuwa Urithi wa Dunia wa UNESCO mwaka 2011.
- **Router (both checks)**, sw17 Mji wa Kale wa Lamu uliorodheshwa kuwa Urithi wa Dunia wa UNESCO mwaka gani? (expected 2001): Mji wa Kale wa Lamu uliorodheshwa kuwa Urithi wa Dunia wa UNESCO mwaka 2011. (Note: this can change over time. Please check an official source.)
- **Memory only**, sw19 Nani aliandika riwaya ya Dunia Uwanja wa Fujo? (expected Euphrase Kezilahabi): George Orwell aliandika riwaya ya "Dunia Uwanja wa Fujo".
- **Search: English Wikipedia only**, sw19 Nani aliandika riwaya ya Dunia Uwanja wa Fujo? (expected Euphrase Kezilahabi): Max Brooks aliandika riwaya ya Dunia Uwanja wa Fujo [1].
- **Memory only**, sw20 Mlima Kenya una urefu wa mita ngapi? (expected 5199): Mlima Kenya una urefu wa kati ya miaka 5,100 sana na 5,900 sana.
- **Memory only**, sw22 Naibu Rais wa sasa wa Kenya ni nani? (expected Kithure Kindiki): Kumbuka kuwa sifa yangu ni ya kusoma na kujibu kusaidia kwa ujuzi, sijapewa vituo vya taarifa kawaida kama vile habari za kila siku au taarifa za kimataifa kabl
- **Memory only**, sw24 Makamu wa Rais wa sasa wa Tanzania ni nani? (expected Deogratius Ndejembi): Makamu wa Rais wa sasa wa Tanzania ni Samia Suluhu Hassan kwa wakati huo.
- **Memory only**, sw25 Waziri Mkuu wa sasa wa Tanzania ni nani? (expected Mwigulu Nchemba): Sijapewa taarifa zinazozungumiza kuwasilisha waziri mkuu wa Tanzania kwa sasa kama wewe uthibitisha historia hii. Ingawa ninaweza kusaidia kujaribu kufikiria au
- **Memory only**, sw27 Gavana wa sasa wa Benki Kuu ya Kenya ni nani? (expected Kamau Thugge): Gavana wa sasa wa Benki Kuu ya Kenya ni Mr. James Gichuru.
- **Search: own language + English**, sw27 Gavana wa sasa wa Benki Kuu ya Kenya ni nani? (expected Kamau Thugge): Gavana wa sasa wa Benki Kuu ya Kenya ni Daktari Patrick Njoroge [1].
- **Router (both checks)**, sw27 Gavana wa sasa wa Benki Kuu ya Kenya ni nani? (expected Kamau Thugge): Gavana wa sasa wa Benki Kuu ya Kenya ni Daktari Patrick Njoroge [1].
- **Memory only**, sw28 Afisa Mkuu Mtendaji (CEO) wa sasa wa Safaricom ni nani? (expected Peter Ndegwa): Safaricom inahitaji kuweka vituo vingine kuhusu afisa mkuu mtendaji (CEO) wakati huu kwa ushirikiano wazi. Tafadhali tuma vizito kwenye chaguo la kutoa maupdate
- **Memory only**, sw29 Timu gani ilishinda Ligi Kuu ya Kenya (FKF Premier League) msimu wa 2025/26? (expected Gor Mahia): Timu gani ilishinda Ligi Kuu ya Kenya (FKF Premier League) msimu wa 2025/26 hujapendelea kwa utafiti wazi wangu. Tafadhali jaribu kusoma vituo vya taarifa au ku
- **Memory only**, sw30 Timu gani ilishinda Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26? (expected Young Africans): Timu gani ilishinda Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26 hutoa taarifa zaidi kusikia jibu la swali hili kwa ushirikiano na maelezo ya
- **Search: English Wikipedia only**, sw30 Timu gani ilishinda Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26? (expected Young Africans): Timu liyoshinda Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26 ni Polisi Tanzania [1].
- **Search: own language + English**, sw30 Timu gani ilishinda Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26? (expected Young Africans): Timu liyoshinda Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26 ni Polisi Tanzania [1].
- **Router (both checks)**, sw30 Timu gani ilishinda Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26? (expected Young Africans): Timu liyoshinda Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26 ni Polisi Tanzania [1].
- **Memory only**, sw31 Nchi gani ilishinda Kombe la Dunia la FIFA mwaka 2026? (expected Spain): Nchi unayoshinda kushoto kama Brazil, Argentina au Portugal kufikia Kombe la Dunia la FIFA mwaka 2026 kulingana na siri ya athletikani.
- **Search: English Wikipedia only**, sw31 Nchi gani ilishinda Kombe la Dunia la FIFA mwaka 2026? (expected Spain): Nchi inachangia Kombe la Dunia la FIFA mwaka 2026 ni Espania [1].
- **Memory only**, sw32 Rais wa sasa wa Zanzibar ni nani? (expected Hussein Ali Mwinyi): Kumbuka kwani maelezo yanayoyotoa yanaweza kuzalisha, sijapewa taarifa kuhusu rais wa Zanzibar kwa sasa. Tafadhali tuma swali lako kwa kimataifa au chombo chech
